# -*- coding: utf-8 -*-
# 二分类：至少3个正文页的相同背景水印；仅通篇模板拒绝；前10页抽检。
"""办公文档本地质检。Python 3.10+，直接运行启动中文界面。
仅依赖：python -m pip install "PyMuPDF>=1.24,<2"
运行时不联网、不调用AI、不需要账号。Word/PPT需本机LibreOffice。
三个阶段均为本地规则检查，不是三轮AI。通过仅表示本地规则未发现问题。
扫描图片内的水印/论文/模板无法可靠判断，进入人工复核，不承诺90%准确率。
"""
import argparse
import collections
import copy
import csv
import hashlib
import html
import json
import math
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
SUPPORTED = {'.pdf', '.doc', '.docx', '.ppt', '.pptx'}
RULE_VERSION = 'offline-ocr-2026-11-10-body3-binary-v5'
PROMO = re.compile('关注|公众号|下载|试用|文库|预览|watermark|trial|sample|evaluation|unregistered', re.I)
EXPLICIT_WATERMARK = re.compile('水印|试用版|试用版本|仅供预览|未经注册|未注册|watermark|trial\\s*(?:version|copy)|evaluation\\s*copy|unregistered', re.I)
PLACEHOLDER = re.compile('_{3,}|□|\\[\\s*填写.*?\\]|【\\s*填写.*?】|请填写|待填写|\\{\\{.*?\\}\\}|\\bXX{1,}\\b', re.I)
FORM_LABELS = re.compile('姓名|性别|出生日期|身份证|联系电话|申请人|被申请人|工作经历|教育经历|签字|盖章|年\\s*月\\s*日|填写|审批意见|事实[与和]理由')

@dataclass
class Settings:
    image_long_edge: int = 1200
    thumbnail_edge: int = 300
    evidence_pages: int = 8
    soffice_path: str = ''
    ocr_enabled: bool = True
    tessdata_path: str = ''
    ocr_dpi: int = 200
    ocr_long_edge: int = 2800
    ocr_retry: bool = True
    pdf_page_limit: int = 10

def require_runtime():
    try:
        import pymupdf
        if not callable(getattr(pymupdf, 'open', None)):
            raise ImportError('安装不完整')
        return pymupdf
    except (ImportError, OSError) as exc:
        raise RuntimeError('当前解释器缺少或无法加载PyMuPDF：' + sys.executable + '\n请安装："' + sys.executable + '" -m pip install "PyMuPDF>=1.24,<2"') from exc

def save_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    temporary.replace(path)

def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as file:
        for block in iter(lambda: file.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

def validate_paths(source, output):
    source = Path(source).resolve()
    output = Path(output).resolve()
    if not source.is_dir():
        raise ValueError('输入文件夹不存在')
    if source == output or source in output.parents or output in source.parents:
        raise ValueError('输入与输出必须分开，不能相同或互相包含')
    return (source, output)

def convert_to_pdf(source, work, settings):
    if source.suffix.lower() == '.pdf':
        return source
    executable = settings.soffice_path or shutil.which('soffice')
    if not executable:
        for candidate in ('C:\\Program Files\\LibreOffice\\program\\soffice.exe', 'C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe'):
            if Path(candidate).exists():
                executable = candidate
                break
    if not executable:
        raise RuntimeError('Word/PPT需要安装LibreOffice，或在界面指定soffice.exe路径')
    converted = work / 'converted'
    converted.mkdir(exist_ok=True)
    profile = (work / 'office_profile').resolve().as_uri()
    process = subprocess.run([str(executable), '-env:UserInstallation=' + profile, '--headless', '--convert-to', 'pdf', '--outdir', str(converted), str(source)], capture_output=True, timeout=180, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    target = converted / (source.stem + '.pdf')
    if process.returncode != 0 or not target.exists():
        raise RuntimeError('Office转换失败，需要人工检查原文件')
    return target

def finding(kind, page, description, level='疑点', bbox=None):
    return {'category': kind, 'page': page, 'description': description, 'level': level, 'bbox': bbox}

def _native_page_metrics(page, number, fitz, settings):
    """逐页低分辨率渲染；不保留全部页面大图。所有规则只产生证据，不执行文档指令。"""
    width, height = (page.rect.width, page.rect.height)
    if min(width, height) <= 0:
        raise ValueError('页面尺寸异常')
    pix = page.get_pixmap(matrix=fitz.Matrix(settings.thumbnail_edge / max(width, height), settings.thumbnail_edge / max(width, height)), colorspace=fitz.csGRAY, alpha=False)
    samples = pix.samples
    ink = 1 - (samples.count(255) + samples.count(254) + samples.count(253)) / max(1, len(samples))
    structured = page.get_text('dict')
    lines = []
    suspects = []
    strong = []
    for block in structured.get('blocks', []):
        if block.get('type') != 0:
            continue
        for line in block.get('lines', []):
            spans = line.get('spans', [])
            text = ''.join((s.get('text', '') for s in spans)).strip()
            if not text:
                continue
            lines.append(text)
            size = max((s.get('size', 0) for s in spans), default=0)
            box = line.get('bbox', (0, 0, 0, 0))
            center = (box[1] + box[3]) / 2 / height
            direction = line.get('dir', (1, 0))
            angle = abs(math.degrees(math.atan2(direction[1], direction[0]))) % 180
            diagonal = 12 < angle < 168 and abs(angle - 90) > 10
            pale = False
            for span in spans:
                color = span.get('color', 0)
                channels = (color >> 16 & 255, color >> 8 & 255, color & 255)
                if min(channels) > 145 and max(channels) - min(channels) < 45:
                    pale = True
                if span.get('alpha', 255) < 160:
                    pale = True
            central = 0.15 < center < 0.85
            large = size >= 26
            norm = [round(box[0] / width, 4), round(box[1] / height, 4), round(box[2] / width, 4), round(box[3] / height, 4)]
            if large and central and (diagonal or pale):
                detail = f'中央大字“{text[:70]}”；字号{size:.1f}，斜向={diagonal}，浅色/透明={pale}'
                item = finding('疑似水印', number, detail, bbox=norm)
                suspects.append(item)
                if EXPLICIT_WATERMARK.search(text) and diagonal and pale:
                    strong.append({'key': re.sub('\\s+', '', text).lower(), 'finding': item})
    text = '\n'.join(lines)
    chars = len(re.sub('\\s+', '', text))
    blank = chars == 0 and ink < 0.0001
    image_only = chars < 20 and ink >= 0.0001
    placeholders = len(PLACEHOLDER.findall(text))
    labels = len(FORM_LABELS.findall(text))
    standalone_labels = sum((bool(re.fullmatch('(?:姓名|性别|出生日期|身份证(?:号|号码)?|联系电话|申请人|被申请人|工作经历|教育经历|审批意见|签字|盖章|单位名称|地址|邮编|民族|文化程度|事实[与和]理由)[：:\\s]*', line)) for line in lines))
    return {'number': number, 'chars': chars, 'ink_ratio': round(ink, 6), 'blank': blank, 'image_only': image_only, 'placeholders': placeholders, 'form_labels': labels, 'standalone_labels': standalone_labels, 'text': text, 'suspects': suspects, 'strong_watermarks': strong}

def safe_cell(value):
    value = str(value)
    return "'" + value if value[:1] in ('=', '+', '-', '@', '\t', '\r') else value

def report(run, records, inventory, stopped=False):
    summary = {'inventory_count': inventory, 'recorded_count': len(records), 'stopped': stopped, 'local_check_completed': sum((bool(r.get('complete')) for r in records)), 'failed_or_incomplete': sum((not r.get('complete', False) for r in records)), 'counts': dict(collections.Counter((r['decision'] for r in records))), 'rule_version': RULE_VERSION, 'python': sys.executable, 'ai_calls': 0, 'note': '完全本地规则及中英文OCR，无外部AI；OCR可读性分数不是置信概率，不保证90%准确率。'}
    summary['ocr_pages'] = sum((p.get('ocr_used', False) for r in records for p in r.get('page_metrics', [])))
    summary['ocr_readable_pages'] = sum((p.get('ocr_accepted', False) for r in records for p in r.get('page_metrics', [])))
    summary['sampled_pdf_files'] = sum((r.get('sampled', False) and Path(r.get('file', '')).suffix.lower() == '.pdf' for r in records))
    summary['sampled_files'] = sum((r.get('sampled', False) for r in records))
    summary['uninspected_pages'] = sum((r.get('uninspected_pages', 0) for r in records))
    summary['note'] += ' 文档默认最多检查前10页，无单页提前拒绝，按文档整体及跨页规则判定；complete表示指定范围完成，不表示全文检查完成。'
    save_json(run / 'run_info.json', summary)
    save_json(run / 'results.json', records)
    with (run / 'summary.csv').open('w', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['文件', '结果', '原因', '总页数', '扫描页数', '指定范围完成', '检查范围', '全文检查', '未检查页数', '重复原件', '错误'])
        for r in records:
            writer.writerow([safe_cell(v) for v in [r['file'], r['decision'], r['reason'], r['total_pages'], r['checked_pages'], r['complete'], r.get('inspection_scope', ''), r.get('full_document_checked', False), r.get('uninspected_pages', 0), r.get('duplicate_of', ''), json.dumps(r['errors'], ensure_ascii=False)]])
    with (run / 'rule_notes.csv').open('w', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['sha256', '文件', '分类', '判定依据', '备注'])
        for r in records:
            writer.writerow([r.get('sha256', ''), safe_cell(r['file']), r['decision'],r.get('decision_basis',''),safe_cell('\n'.join(r.get('notes',[])))])
    esc = lambda v: html.escape(str(v), quote=True)
    parts = ['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>本地文档质检报告</title>', '<style>body{font:16px system-ui;max-width:1080px;margin:30px auto;padding:15px;background:#f4f6f8}details{background:white;padding:16px;margin:12px 0;border-radius:8px}pre{white-space:pre-wrap}img{max-width:95%;max-height:850px}a{color:#1658a2}</style>', '<h1>本地文档质检报告 · 不调用AI</h1><p>通过只表示本地规则未发现问题。正文背景水印须至少3个不同正文页；局部空表不拒绝。识别不足仅记备注，技术失败明确拒绝。不保证90%准确率。</p>', '<pre>' + esc(json.dumps(summary, ensure_ascii=False, indent=2)) + '</pre>']
    for r in records:
        parts.append('<details><summary>' + esc(r['decision'] + ' · ' + r['file']) + '</summary><p>' + esc(r['reason']) + '</p>')
        if r.get('notes'):parts.append('<pre>备注：\n'+esc('\n'.join(r['notes']))+'</pre>')
        if r.get('output_file'):
            parts.append('<p><a href="' + quote(Path(r['output_file']).as_posix()) + '">打开原文件副本</a></p>')
        parts.append(f"<p>范围：{esc(r.get('inspection_scope', '未完成'))}；本地扫描 {r['checked_pages']}/{r['total_pages']}页；未检查：{r.get('uninspected_pages', 0)}页；指定范围完成：{r['complete']}；全文检查：{r.get('full_document_checked', False)}</p>")
        if r.get('duplicate_of'):
            parts.append('<p>完全相同文件，复用检查证据：' + esc(r['duplicate_of']) + '</p>')
        ocr_pages = [p for p in r.get('page_metrics', []) if p.get('ocr_used')]
        if ocr_pages:
            parts.append(f"<p>本地OCR：{len(ocr_pages)}页；按可读性规则识读充分：{sum((p.get('ocr_accepted', False) for p in ocr_pages))}页（不是准确率）。</p>")
            for p in ocr_pages[:20]:
                txt = Path(r['ocr_evidence_dir']) / f"page_{p['number']:05d}.txt"
                if txt.exists():
                    relative = txt.relative_to(run.resolve()).as_posix()
                    parts.append(f'''<a href="{quote(relative)}">第{p['number']}页OCR文字</a>\u3000''')
        for stage in r['stages']:
            parts.append('<p>' + esc(json.dumps(stage, ensure_ascii=False)) + '</p>')
        for f in r['findings']:
            parts.append('<p>' + esc(f"第{f['page']}页 · {f['category']} · {f['level']}：{f['description']}") + '</p>')
        if r['errors']:
            parts.append('<pre>' + esc(json.dumps(r['errors'], ensure_ascii=False, indent=2)) + '</pre>')
        for image in r['page_images']:
            relative = Path(image['path']).relative_to(run.resolve()).as_posix()
            parts.append(f'''<details><summary>证据：第{image['page']}页原图</summary><img loading="lazy" src="{quote(relative)}"></details>''')
        parts.append('</details>')
    parts.append('</html>')
    (run / 'report.html').write_text('\n'.join(parts), encoding='utf-8')
    return summary

def run_folder(source, output, settings=None, log=print, cancelled=lambda: False):
    require_runtime()
    source, output = validate_paths(source, output)
    settings = settings or Settings()
    if settings.ocr_enabled:
        resolve_tessdata(settings)
    files = sorted((p for p in source.rglob('*') if p.is_file() and (not p.is_symlink()) and (not any(((source / parent).is_symlink() for parent in p.relative_to(source).parents)))))
    if not files:
        raise ValueError('输入文件夹没有找到文件，未开始检查')
    run = output / ('offline_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    for folder in ('通过', '不通过', 'reports', '.staging'):
        (run / folder).mkdir(parents=True, exist_ok=True)
    records = []
    cache = {}
    log(f'完全本地扫描：{len(files)}份文件；外部AI调用0次；输出：{run}')
    for index, path in enumerate(files, 1):
        if cancelled():
            break
        name = str(path.relative_to(source))
        log(f'[{index}/{len(files)}] {name}')
        digest = ''
        try:
            digest = sha256(path)
            cache_key = (digest, path.suffix.lower())
            if cache_key in cache:
                previous = cache[cache_key]
                record = copy.deepcopy(previous)
                record['duplicate_of'] = previous['file']
                log('    内容完全相同，复用已有检查结果')
            else:
                identity = hashlib.sha256(name.encode()).hexdigest()[:8]
                record = inspect_file(path, run / 'reports' / (digest[:16] + '_' + identity), settings, cancelled, log)
            record.update(file=name, sha256=digest)
            if sha256(path) != digest:
                record.update(decision='不通过', reason='检查期间原文件发生变化，请重新运行', complete=False,decision_basis='technical_failure')
            staged = run / '.staging' / name
            staged.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, staged)
            if sha256(staged) != digest:
                record.update(decision='不通过', reason='副本内容与检查内容不一致，请重新运行', complete=False,decision_basis='technical_failure')
            target = run / record['decision'] / name
            target.parent.mkdir(parents=True, exist_ok=True)
            staged.replace(target)
            record['output_file'] = str(target.relative_to(run))
            if record.get('complete') and (not record.get('errors')) and (cache_key not in cache):
                cache[cache_key] = copy.deepcopy(record)
        except Exception as exc:
            record = {'file': name, 'sha256': digest, 'decision': '不通过', 'reason': '处理或复制失败；原文件仍保留','decision_basis':'technical_failure', 'total_pages': 0, 'checked_pages': 0, 'complete': False, 'stages': [], 'findings': [], 'errors': [{'error': type(exc).__name__ + ': ' + str(exc)[:300]}], 'page_images': []}
        records.append(record)
        save_json(run / 'results.json', records)
        log('    → ' + record['decision'] + '：' + record['reason'])
    summary = report(run, records, len(files), cancelled())
    save_json(run / 'unprocessed.json', [str(p.relative_to(source)) for p in files[len(records):]])
    log(f"本地检查结束：按指定范围完成{summary['local_check_completed']}份，未完成/失败{summary['failed_or_incomplete']}份；未处理{len(files) - len(records)}份")
    log('报告：' + str(run / 'report.html'))
    return (records, run)

def gui():
    """Local desktop interface; all inspection runs on the worker thread."""
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    from tkinter.scrolledtext import ScrolledText

    window = tk.Tk()
    window.title('办公文档本地质检')
    window.geometry('1060x800')
    window.minsize(880, 680)
    bg, ink, muted, blue = '#F3F5FB', '#19243B', '#627087', '#3478F6'
    window.configure(bg=bg)
    window.option_add('*Font', ('Microsoft YaHei UI', 10))
    style = ttk.Style(window)
    style.theme_use('clam')
    style.configure('QC.TEntry', padding=9, fieldbackground='#F6F8FC', bordercolor='#DFE5F0', lightcolor='#DFE5F0', darkcolor='#DFE5F0')
    style.map('QC.TEntry', bordercolor=[('focus', blue)])
    style.configure('QC.TButton', padding=(16, 10), background='#EDF2FF', foreground='#315DA8', borderwidth=0)
    style.map('QC.TButton', background=[('active', '#DFE9FF')], foreground=[('disabled', '#9AA5B7')])
    style.configure('Primary.QC.TButton', background=blue, foreground='white', padding=(24, 11))
    style.map('Primary.QC.TButton', background=[('disabled', '#A8BFE9'), ('active', '#2365DB')], foreground=[('disabled', 'white')])
    style.configure('QC.Horizontal.TProgressbar', background=blue, troughcolor='#E8EDF7', borderwidth=0, thickness=6)
    messages, stop = queue.Queue(), threading.Event()
    state = {'running': False, 'run': None, 'total': 0, 'processed': 0, 'passed': 0, 'rejected': 0}
    variables = {key: tk.StringVar() for key in ('input', 'output', 'soffice', 'tessdata')}
    shell = tk.Frame(window, bg=bg)
    shell.pack(fill='both', expand=True, padx=28, pady=22)

    def label(parent, text='', size=10, color=ink, bold=False, **kw):
        return tk.Label(parent, text=text, bg=parent.cget('bg'), fg=color,
                        font=('Microsoft YaHei UI', size, 'bold' if bold else 'normal'), **kw)

    def card(parent):
        canvas = tk.Canvas(parent, bg=bg, highlightthickness=0, bd=0)
        canvas.pack(fill='x', pady=(0, 14))
        inner = tk.Frame(canvas, bg='white')
        item = canvas.create_window(20, 17, window=inner, anchor='nw')
        def layout(event=None):
            width = canvas.winfo_width()
            height = inner.winfo_reqheight() + 34
            canvas.configure(height=height)
            canvas.itemconfigure(item, width=max(1, width-40))
            canvas.delete('surface')
            r = 18
            points = [r,1,width-r,1,width-1,1,width-1,r,width-1,height-r,width-1,height-1,width-r,height-1,r,height-1,1,height-1,1,height-r,1,r,1,1]
            canvas.create_polygon(points, smooth=True, fill='white', outline='#E5EAF4', tags='surface')
            canvas.tag_lower('surface')
        canvas.bind('<Configure>', layout)
        inner.bind('<Configure>', layout)
        return inner

    header = tk.Frame(shell, bg=bg)
    header.pack(fill='x', pady=(0, 20))
    label(header, '办公文档本地质检', 24, bold=True).pack(side='left')
    label(header, '  ●  完全本地 · 离线运行  ', 10, '#4267AC', padx=12, pady=8).pack(side='right')
    label(shell, '让文档整理更有序，让每一次检查都有记录。', 10, muted).pack(anchor='w', pady=(0, 18))
    paths = card(shell)
    label(paths, '选择工作文件夹', 13, bold=True).grid(row=0, column=0, columnspan=3, sticky='w', pady=(0, 12))
    paths.columnconfigure(1, weight=1)
    def path_row(parent, row, key, title):
        label(parent, title, color=muted).grid(row=row, column=0, sticky='w', padx=(0, 16), pady=6)
        entry = ttk.Entry(parent, textvariable=variables[key], style='QC.TEntry')
        entry.grid(row=row, column=1, sticky='ew', pady=6)
        def choose():
            value = filedialog.askopenfilename(parent=window, title='选择 soffice.exe') if key == 'soffice' else filedialog.askdirectory(parent=window, title=title)
            if value:
                variables[key].set(value)
        ttk.Button(parent, text='浏览…', command=choose, style='QC.TButton').grid(row=row, column=2, padx=(12, 0), pady=6)
    path_row(paths, 1, 'input', '原始文件夹')
    path_row(paths, 2, 'output', '结果文件夹')
    label(paths, '结果文件夹需与原始文件夹分开，原文件不会被修改。', 9, muted).grid(row=3, column=1, columnspan=2, sticky='w', pady=(4, 8))
    advanced = tk.Frame(paths, bg='white')
    advanced.columnconfigure(1, weight=1)
    path_row(advanced, 0, 'soffice', 'LibreOffice 路径')
    path_row(advanced, 1, 'tessdata', 'OCR 模型目录')
    label(advanced, '通常留空即可自动查找。运行环境：' + sys.executable, 9, muted, wraplength=690, justify='left').grid(row=2, column=0, columnspan=3, sticky='w', pady=(6, 0))
    def toggle_advanced():
        if advanced.winfo_manager():
            advanced.grid_remove()
            advanced_button.configure(text='高级设置  ▾')
        else:
            advanced.grid(row=5, column=0, columnspan=3, sticky='ew', pady=(8, 0))
            advanced_button.configure(text='收起设置  ▴')
    advanced_button = ttk.Button(paths, text='高级设置  ▾', command=toggle_advanced, style='QC.TButton')
    advanced_button.grid(row=4, column=0, sticky='w', pady=(5, 0))
    def rules():
        messagebox.showinfo('检查规则', '每份文档最多检查前10页，不足10页全文检查。\n\n同一背景水印特征需出现在至少3个正文页；封面与单页装饰不据此拒绝。空白模板按整体判断，正文中局部空表不直接拒绝；超过10页不能据抽样断定通篇空模板。\n\n图片使用本地中英文OCR。识读不足写入报告备注。通过表示当前检查范围内未触发拒绝规则，不代表全文无问题。', parent=window)
    ttk.Button(paths, text='查看检查规则', command=rules, style='QC.TButton').grid(row=4, column=2, sticky='e', pady=(5, 0))

    task = card(shell)
    top = tk.Frame(task, bg='white'); top.pack(fill='x')
    status = label(top, '准备就绪', 13, bold=True); status.pack(side='left')
    count = label(top, '已处理 0  ·  通过 0  ·  不通过 0', 10, muted); count.pack(side='right')
    progress = ttk.Progressbar(task, style='QC.Horizontal.TProgressbar', mode='determinate')
    progress.pack(fill='x', pady=(16, 14))
    controls = tk.Frame(task, bg='white'); controls.pack(fill='x')
    def open_result():
        if state['run']:
            os.startfile(str(state['run']))
    def request_stop():
        stop.set()
        status.configure(text='正在停止，请等待当前检查结束…')
        halt.configure(state='disabled')
    def start():
        if state['running']:
            return
        try:
            require_runtime()
            source, destination = (variables[k].get().strip() for k in ('input', 'output'))
            if not source or not destination:
                raise ValueError('请选择原始文件夹和结果文件夹')
            validate_paths(source, destination)
            settings = Settings(soffice_path=variables['soffice'].get().strip(), tessdata_path=variables['tessdata'].get().strip())
            resolve_tessdata(settings)
        except Exception as exc:
            messagebox.showerror('无法开始', str(exc), parent=window)
            return
        stop.clear()
        state.update(running=True, run=None, total=0, processed=0, passed=0, rejected=0)
        begin.configure(state='disabled'); halt.configure(state='normal'); reveal.configure(state='disabled')
        status.configure(text='正在扫描文件…'); count.configure(text='已处理 0  ·  通过 0  ·  不通过 0')
        progress.configure(mode='indeterminate'); progress.start(15)
        output.configure(state='normal'); output.delete('1.0', 'end'); output.configure(state='disabled')
        def worker():
            try:
                records, run = run_folder(source, destination, settings, messages.put, stop.is_set)
                messages.put(('done', records, run))
            except Exception as exc:
                messages.put(('error', str(exc)))
        threading.Thread(target=worker, daemon=False).start()
    begin = ttk.Button(controls, text='开始本地质检', style='Primary.QC.TButton', command=start); begin.pack(side='left')
    halt = ttk.Button(controls, text='停止并保留结果', style='QC.TButton', command=request_stop, state='disabled'); halt.pack(side='left', padx=12)
    reveal = ttk.Button(controls, text='打开结果文件夹', style='QC.TButton', command=open_result, state='disabled'); reveal.pack(side='right')
    log_card = tk.Frame(shell, bg='white', highlightbackground='#E5EAF4', highlightthickness=1)
    log_card.pack(fill='both', expand=True)
    label(log_card, '运行记录', 12, bold=True).pack(anchor='w', padx=18, pady=(12, 8))
    output = ScrolledText(log_card, height=7, state='disabled', bg='white', fg='#44536C', relief='flat', bd=0,
                          font=('Microsoft YaHei UI', 10), padx=14, pady=8, wrap='word', insertbackground=blue)
    output.pack(fill='both', expand=True, padx=4, pady=(0, 8))
    label(shell, '本地 OCR  /  前 10 页检查  /  通过与不通过分类  /  无外部 AI 调用', 9, muted).pack(anchor='w', pady=(12, 0))

    def append(text):
        output.configure(state='normal'); output.insert('end', str(text) + '\n'); output.see('end'); output.configure(state='disabled')
    def poll():
        for _ in range(150):
            try:
                message = messages.get_nowait()
            except queue.Empty:
                break
            if isinstance(message, tuple):
                state['running'] = False
                progress.stop(); progress.configure(mode='determinate')
                begin.configure(state='normal'); halt.configure(state='disabled')
                if message[0] == 'error':
                    status.configure(text='检查中断，请查看记录')
                    append('错误：' + message[1])
                    messagebox.showerror('检查中断', message[1], parent=window)
                else:
                    records, run = message[1:]
                    state['run'] = run
                    passed = sum(r.get('decision') == '通过' for r in records)
                    rejected = sum(r.get('decision') == '不通过' for r in records)
                    count.configure(text=f'已记录 {len(records)}  ·  通过 {passed}  ·  不通过 {rejected}')
                    status.configure(text='已停止，现有结果已保留' if stop.is_set() else ('检查完成' if records else '未发现可处理文件'))
                    if not stop.is_set() and state['total']:
                        progress.configure(value=state['total'])
                    reveal.configure(state='normal')
                    append('结果文件夹：' + str(run))
            else:
                text = str(message); append(text)
                match = re.search(r'本地扫描：(\d+)份', text)
                if match:
                    state['total'] = int(match[1]); progress.stop(); progress.configure(mode='determinate', maximum=max(1, state['total']), value=0)
                match = re.match(r'\[(\d+)/(\d+)\]\s*(.*)', text)
                if match:
                    status.configure(text=f'正在检查 {match[1]} / {match[2]}')
                if '→ 通过：' in text or '→ 不通过：' in text:
                    state['processed'] += 1
                    state['passed' if '→ 通过：' in text else 'rejected'] += 1
                    progress.configure(value=state['processed'])
                    count.configure(text=f"已处理 {state['processed']}  ·  通过 {state['passed']}  ·  不通过 {state['rejected']}")
        window.after(100, poll)
    def close():
        if state['running']:
            request_stop()
            messagebox.showinfo('正在停止', '已请求停止，请等待当前页面或Office转换结束后关闭。', parent=window)
        else:
            window.destroy()
    window._qc_ui = dict(variables=variables, start=start, state=state, toggle_advanced=toggle_advanced)
    window.protocol('WM_DELETE_WINDOW', close)
    poll()
    window.mainloop()


def main():
    parser = argparse.ArgumentParser(description='本地规则和中英文OCR，无外部AI。无参数启动图形界面。')
    parser.add_argument('--input', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--soffice', default='', help='LibreOffice soffice.exe路径，可选')
    parser.add_argument('--tessdata', default='', help='中英文OCR模型目录，默认Python文件旁的tessdata')
    parser.add_argument('--no-ocr', action='store_true', help='关闭OCR，仅执行文字/版式规则')
    parser.add_argument('--pdf-page-limit', type=int, default=10, help='PDF最多检查前多少页，默认10；0表示全文')
    args = parser.parse_args()
    if args.input is None and args.output is None:
        gui()
        return
    if not args.input or not args.output:
        parser.error('--input 和 --output 必须同时提供')
    if args.pdf_page_limit < 0:
        parser.error('--pdf-page-limit不能为负数')
    run_folder(args.input, args.output, Settings(soffice_path=args.soffice, tessdata_path=args.tessdata, ocr_enabled=not args.no_ocr, pdf_page_limit=args.pdf_page_limit))

def resolve_tessdata(settings):
    """只找本地模型；运行期间不下载。显式路径写错时不悄悄换另一个目录。"""
    if settings.tessdata_path:
        candidates = [Path(settings.tessdata_path)]
    else:
        candidates = [Path(__file__).resolve().parent / 'tessdata']
        if os.environ.get('TESSDATA_PREFIX'):
            candidates.append(Path(os.environ['TESSDATA_PREFIX']))
        candidates.extend([Path('C:\\Program Files\\Tesseract-OCR\\tessdata'), Path('/usr/share/tesseract-ocr/5/tessdata')])
    for directory in candidates:
        if all(((directory / (lang + '.traineddata')).is_file() for lang in ('chi_sim', 'eng'))):
            return str(directory.resolve())
    raise RuntimeError('缺少中英文OCR模型。请把tessdata文件夹放在本Python文件旁，里面应包含chi_sim.traineddata和eng.traineddata，或在界面选择模型目录。')

def ocr_quality(text):
    chars = [c for c in text if not c.isspace()]
    useful = sum((c.isalnum() or '㐀' <= c <= '鿿' for c in chars))
    replacements = text.count('�')
    good = useful >= 40 and useful / max(len(chars), 1) >= 0.65 and (replacements / max(len(chars), 1) < 0.02)
    return {'usable_characters': useful, 'character_count': len(chars), 'readable_by_rule': good}

def extract_ocr(page, fitz, settings, cancelled=lambda: False):
    import statistics
    tessdata = resolve_tessdata(settings)
    width, height = (page.rect.width, page.rect.height)
    max_edge = settings.ocr_long_edge
    attempts = [(min(settings.ocr_dpi / 72, max_edge / max(width, height)), 0)]
    if settings.ocr_retry:
        attempts += [(min(300 / 72, 3600 / max(width, height)), 0), (min(settings.ocr_dpi / 72, max_edge / max(width, height)), 90), (min(settings.ocr_dpi / 72, max_edge / max(width, height)), 270)]
    best = None
    attempts_done = 0
    attempt_errors = []
    for scale, angle in attempts:
        if cancelled():
            raise InterruptedError('用户停止')
        attempts_done += 1
        try:
            pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale).prerotate(angle), colorspace=fitz.csRGB, alpha=False)
            with fitz.open() as doc:
                raster = doc.new_page(width=pix.width, height=pix.height)
                raster.insert_image(raster.rect, stream=pix.tobytes('png'))
                tp = raster.get_textpage_ocr(language='chi_sim+eng', dpi=72, full=True, tessdata=tessdata)
                text = raster.get_text(textpage=tp)
                blocks = raster.get_text('dict', textpage=tp).get('blocks', [])
            lines = []
            for block in blocks:
                for line in block.get('lines', []):
                    value = ''.join((span.get('text', '') for span in line.get('spans', []))).strip()
                    if not value:
                        continue
                    box = line['bbox']
                    mapped = []
                    for x, y in ((box[0], box[1]), (box[0], box[3]), (box[2], box[1]), (box[2], box[3])):
                        u, v = (x / pix.width, y / pix.height)
                        if angle == 90:
                            u, v = (v, 1 - u)
                        elif angle == 270:
                            u, v = (1 - v, u)
                        mapped.append((max(0, min(1, u)), max(0, min(1, v))))
                    norm = [min((p[0] for p in mapped)), min((p[1] for p in mapped)), max((p[0] for p in mapped)), max((p[1] for p in mapped))]
                    lines.append({'text': value, 'bbox': [round(v, 5) for v in norm]})
            quality = ocr_quality(text)
            current = {'text': text, 'lines': lines, 'quality': quality, 'rotation': angle, 'attempts': attempts_done}
            if best is None or (quality['readable_by_rule'], quality['usable_characters']) > (best['quality']['readable_by_rule'], best['quality']['usable_characters']):
                best = current
            if quality['readable_by_rule']:
                break
        except InterruptedError:
            raise
        except Exception as exc:
            attempt_errors.append(type(exc).__name__ + ': ' + str(exc)[:180])
    if best is None:
        raise RuntimeError('OCR所有尝试失败：' + '；'.join(attempt_errors))
    best['attempts'] = attempts_done
    best['attempt_errors'] = attempt_errors
    return best

def _ocr_page_metrics(page, number, fitz, settings, cancelled=lambda: False, log=lambda _: None):
    metrics = _native_page_metrics(page, number, fitz, settings)
    metrics.update(ocr_used=False, ocr_accepted=False, ocr_problem='', ocr_text='', ocr_lines=[], ocr_attempts=0)
    if metrics['blank'] or not settings.ocr_enabled:
        return metrics
    area = page.rect.width * page.rect.height
    try:
        image_area = sum((max(0, item['bbox'][2] - item['bbox'][0]) * max(0, item['bbox'][3] - item['bbox'][1]) for item in page.get_image_info()))
    except Exception:
        image_area = 0
    if not metrics['image_only'] and image_area / max(area, 1) < 0.2:
        return metrics
    log(f'    第{number}页：本地OCR识别中（不联网）')
    metrics['ocr_used'] = True
    try:
        recognized = extract_ocr(page, fitz, settings, cancelled)
        metrics['ocr_text'] = recognized['text']
        metrics['ocr_lines'] = recognized['lines']
        metrics['ocr_attempts'] = recognized['attempts']
        metrics['ocr_quality'] = recognized['quality']
        metrics['ocr_rotation'] = recognized['rotation']
        metrics['ocr_accepted'] = recognized['quality']['readable_by_rule']
        if metrics['ocr_accepted']:
            native_lines = set(metrics['text'].splitlines())
            extra = [line for line in recognized['text'].splitlines() if line.strip() and line not in native_lines]
            text = metrics['text'] + '\n' + '\n'.join(extra)
            metrics['text'] = text
            metrics['chars'] = len(re.sub('\\s+', '', text))
            metrics['image_only'] = False
            metrics['placeholders'] = len(PLACEHOLDER.findall(text))
            metrics['form_labels'] = len(FORM_LABELS.findall(text))
            metrics['standalone_labels'] = sum((bool(re.fullmatch('(?:姓名|性别|出生日期|身份证(?:号|号码)?|联系电话|申请人|被申请人|工作经历|教育经历|审批意见|签字|盖章|单位名称|地址|邮编|民族|文化程度|事实[与和]理由)[：:\\s]*', line.strip())) for line in text.splitlines()))
        else:
            metrics['ocr_problem'] = 'OCR识别有效文字不足或乱码较多，无法确认页面内容'
        for line in recognized['lines']:
            b = line['bbox']
            center = (b[1] + b[3]) / 2
            if PROMO.search(line['text']) and 0.15 < center < 0.85 and (b[3] - b[1] >= 0.035):
                metrics['suspects'].append(finding('疑似图片水印', number, 'OCR发现正文区域的大字推广/水印候选：“' + line['text'][:100] + '”；需结合原图确认是否装饰背景', bbox=b))
    except InterruptedError:
        raise
    except Exception as exc:
        metrics['ocr_problem'] = 'OCR执行失败：' + type(exc).__name__ + ': ' + str(exc)[:200]
    return metrics

def vector_watermark_evidence(page, number, fitz, settings):
    """检测文字转轮廓的中央覆盖，不使用品牌名、文件名、哈希黑名单。"""
    width, height = (page.rect.width, page.rect.height)
    candidates = []
    seen = set()
    for path in page.get_drawings():
        color = path.get('fill')
        rect = path['rect']
        area = rect.width * rect.height / (width * height)
        if not color or len(color) != 3 or len(path.get('items', [])) < 15:
            continue
        if not any((item[0] == 'c' for item in path['items'])):
            continue
        if not (0.45 <= min(color) < 0.95 and max(color) - min(color) < 0.12):
            continue
        if path.get('fill_opacity', 1) > 0.85 or not 0.008 < area < 0.25:
            continue
        cx, cy = ((rect.x0 + rect.x1) / 2 / width, (rect.y0 + rect.y1) / 2 / height)
        if not 0.08 < cx < 0.92 or not 0.15 < cy < 0.9:
            continue
        key = (tuple((round(v, 1) for v in rect)), len(path['items']))
        if key not in seen:
            seen.add(key)
            candidates.append(path)
    if len(candidates) < 2:
        return None
    centers = [((p['rect'].x0 + p['rect'].x1) / 2, (p['rect'].y0 + p['rect'].y1) / 2) for p in candidates]
    mx = sum((x for x, y in centers)) / len(centers)
    my = sum((y for x, y in centers)) / len(centers)
    vx = sum(((x - mx) ** 2 for x, y in centers))
    vy = sum(((y - my) ** 2 for x, y in centers))
    covariance = sum(((x - mx) * (y - my) for x, y in centers))
    if vx <= 0 or vy <= 0:
        return None
    correlation = abs(covariance / math.sqrt(vx * vy))
    angle = abs(math.degrees(math.atan2(covariance, vx)))
    if correlation < 0.85 or not 25 < angle < 70:
        return None
    union = fitz.Rect(candidates[0]['rect'])
    for p in candidates[1:]:
        union |= p['rect']
    if union.width * union.height / (width * height) < 0.1:
        return None
    overlap = 0
    for block in page.get_text('dict').get('blocks', []):
        if block.get('type') != 0:
            continue
        for line in block.get('lines', []):
            box = fitz.Rect(line['bbox'])
            if box.y0 > height * 0.12 and (not (box & union).is_empty):
                overlap += 1
    if overlap < 2:
        return None
    fingerprint = hashlib.sha256(repr([(tuple(p['rect']), p['items']) for p in candidates]).encode()).hexdigest()
    return {'page': number, 'bbox': [round(union.x0 / width, 4), round(union.y0 / height, 4), round(union.x1 / width, 4), round(union.y1 / height, 4)], 'glyph_shapes': len(candidates), 'angle': round(angle, 1), 'overlapped_text_lines': overlap, 'fingerprint': fingerprint, 'paths': candidates}

def recognize_vector_layer(page, evidence, fitz, settings):
    cache = getattr(settings, '_vector_ocr_cache', {})
    key = evidence['fingerprint']
    if key in cache:
        return cache[key]
    if not settings.ocr_enabled:
        return ''
    with fitz.open() as isolated:
        p = isolated.new_page(width=page.rect.width, height=page.rect.height)
        candidates = evidence['paths']
        union = fitz.Rect(candidates[0]['rect'])
        for path in candidates:
            union |= path['rect']
            shape = p.new_shape()
            for item in path['items']:
                if item[0] == 'l':
                    shape.draw_line(item[1], item[2])
                elif item[0] == 'c':
                    shape.draw_bezier(item[1], item[2], item[3], item[4])
                elif item[0] == 're':
                    shape.draw_rect(item[1])
                elif item[0] == 'qu':
                    shape.draw_quad(item[1])
            shape.finish(fill=(0, 0, 0), color=None, closePath=path.get('closePath', False), even_odd=path.get('even_odd', False))
            shape.commit()
        union += (-15, -15, 15, 15)
        texts = []
        for rotation in (45, -45, 0):
            pix = p.get_pixmap(matrix=fitz.Matrix(0.7, 0.7).prerotate(rotation), clip=union, alpha=False)
            with fitz.open() as doc:
                q = doc.new_page(width=pix.width, height=pix.height)
                q.insert_image(q.rect, stream=pix.tobytes('png'))
                tp = q.get_textpage_ocr(language='chi_sim+eng', dpi=72, full=True, tessdata=resolve_tessdata(settings))
                text = re.sub('\\s+', '', q.get_text(textpage=tp))
                texts.append(text)
                if len(re.findall('[\\u3400-\\u9fff]', text)) >= 2:
                    break
        best = max(texts, key=lambda t: (len(re.findall('[\\u3400-\\u9fff]', t)), len(t)), default='')
    cache[key] = best
    settings._vector_ocr_cache = cache
    return best
CORE_FORM_LABEL = re.compile('姓名|性别|民族|出生年月日|出生日期|籍贯|学历|身份证(?:号码|号)?|联系电话(?:.*)?|电子(?:信箱|邮箱)|政治面貌|高考生源地|英语水平|计算机水平|现住址|单位名称|地址|邮编|name|gender|dateofbirth|email|phone', re.I)

def _legacy_blank_form_evidence(page, number, metrics):
    empty = 0
    pairs = 0
    if metrics['form_labels'] >= 3 or metrics['standalone_labels'] >= 4:
        try:
            import contextlib, io
            with contextlib.redirect_stdout(io.StringIO()):
                tables = page.find_tables().tables
            for table in tables:
                for row in table.extract():
                    row = [re.sub('\\s+', '', str(c)) for c in row if c is not None]
                    for i, cell in enumerate(row[:-1]):
                        if CORE_FORM_LABEL.fullmatch(cell):
                            pairs += 1
                            if not row[i + 1]:
                                empty += 1
        except Exception:
            pass
    if pairs >= 4 and empty / pairs >= 0.8:
        return finding('空白模板', number, f'识别到{pairs}组核心字段和值格，其中{empty}组未填写；空值占比{empty / pairs:.0%}', level='明确字段证据')
    if pairs >= 4:
        return None
    if metrics['standalone_labels'] >= 6 and metrics['chars'] < 600:
        positioned = []
        for block in page.get_text('dict').get('blocks', []):
            for line in block.get('lines', []):
                text = ''.join((s.get('text', '') for s in line.get('spans', []))).strip()
                if text:
                    positioned.append((re.sub('\\s+', '', text), line['bbox']))
        filled = 0
        for text, box in positioned:
            if not CORE_FORM_LABEL.fullmatch(text):
                continue
            cy = (box[1] + box[3]) / 2
            if any((other and (not CORE_FORM_LABEL.fullmatch(other)) and (b[0] >= box[2]) and (abs((b[1] + b[3]) / 2 - cy) < max(box[3] - box[1], b[3] - b[1]) * 0.6) for other, b in positioned)):
                filled += 1
        if filled >= 2:
            return None
        return finding('空白模板', number, f"{metrics['standalone_labels']}个核心字段只有独立标签，无对应值，页面有效文字共{metrics['chars']}字", level='明确字段证据')
    return None

def audit_page_evidence(page, number, fitz, settings, metrics):
    vector = vector_watermark_evidence(page, number, fitz, settings)
    metrics['vector_watermark'] = None
    if vector:
        promotion = bool(re.search('关注|公众号|添加微信|扫码|更多.{0,12}资料|下载|trial|preview|watermark', metrics['text'], re.I))
        try:
            text = '' if promotion else recognize_vector_layer(page, vector, fitz, settings)
        except Exception:
            text = ''
        vector = {k: v for k, v in vector.items() if k != 'paths'}
        vector.update(ocr_text=text, promotion_context=promotion)
        metrics['vector_watermark'] = vector
        metrics['suspects'].append(finding('矢量轮廓水印候选', number, f"正文区域有{vector['glyph_shapes']}个半透明复杂字符轮廓，倾斜约{vector['angle']}度，覆盖{vector['overlapped_text_lines']}行正文；轮廓OCR：{text or '未可靠识读'}", bbox=vector['bbox']))
    metrics['blank_form'] = blank_form_evidence(page, number, metrics)
    metrics['suspects'].extend(metrics.get('template_candidates', []))
    return metrics
TEMPLATE_KEYS = '身份证号码|身份证号|联系电话|联系地址|签订日期|出生日期|入职日期|电子邮箱|电子信箱|工作岗位|工作单位|单位名称|合同金额|申请事项|甲方|乙方|姓名|性别|民族|地址|邮编|岗位|工资|薪资|金额|日期|部门|name|gender|email|phone|address|salary|amount|date'
TEMPLATE_KV = re.compile('(?P<label>' + TEMPLATE_KEYS + ')\\s*[:：]\\s*(?P<value>.*?)(?=(?:' + TEMPLATE_KEYS + ')\\s*[:：]|$)', re.I)

def empty_field_value(value):
    value = re.sub('[\\s_:：—─━﹍﹎▁‗\\-./\\\\年月日元整%人民币￥¥()（）\\[\\]【】]+', '', value)
    return not value or bool(re.fullmatch('(?:X{2,}|待填写|请填写|待填|空白|填写内容)', value, re.I))

def blank_form_evidence(page, number, metrics):
    """内容长度不能抵消关键字段空缺；仅在多项证据一致时自动拒绝。"""
    fields = {}
    positions = []
    strokes = []
    for line in metrics['text'].splitlines():
        for match in TEMPLATE_KV.finditer(line.strip()):
            label = match.group('label').lower()
            value = match.group('value').strip()
            fields[label] = empty_field_value(value)
    structured = page.get_text('dict')
    for block in structured.get('blocks', []):
        for line in block.get('lines', []):
            text = ''.join((s.get('text', '') for s in line.get('spans', []))).strip()
            if text:
                positions.append((text, line['bbox']))
    drawings = page.get_drawings()
    for path in drawings:
        for item in path.get('items', []):
            if item[0] == 'l' and abs(item[1].y - item[2].y) < 1 and (abs(item[1].x - item[2].x) >= 24):
                strokes.append((min(item[1].x, item[2].x), max(item[1].x, item[2].x), (item[1].y + item[2].y) / 2))
    for text, box in positions:
        label = re.sub('[\\s:：]+', '', text).lower()
        if not re.fullmatch(TEMPLATE_KEYS, label, re.I):
            continue
        candidates = [s for s in strokes if s[0] >= box[2] - 3 and abs(s[2] - box[3]) <= 14]
        if not candidates:
            continue
        stroke = min(candidates, key=lambda s: s[0])
        end = stroke[1]
        values = [other for other, b in positions if b[0] >= box[2] - 1 and b[0] < end and (abs((b[1] + b[3]) / 2 - (box[1] + box[3]) / 2) < max(box[3] - box[1], b[3] - b[1]) * 0.65)]
        fields[label] = not any((not empty_field_value(v) for v in values))
    blank = sum(fields.values())
    count = len(fields)
    metrics['template_details'] = {'identified_fields': count, 'empty_fields': blank, 'empty_field_ratio': round(blank / count, 3) if count else None, 'field_status': fields}
    if count >= 4 and blank / count >= 0.75:
        return finding('空白模板', number, f'识别{count}类关键字段，{blank}类为空值、下划线或未填写横线；空缺比例{blank / count:.0%}；完整正文不能抵消这些缺项', level='明确字段证据')
    if len(drawings) >= 12 or metrics['form_labels'] >= 3:
        try:
            import contextlib, io
            with contextlib.redirect_stdout(io.StringIO()):
                tables = page.find_tables().tables
            for table in tables:
                rows = table.extract()
                if len(rows) < 3:
                    continue
                cells = [str(c).strip() for row in rows[1:] for c in row if c is not None]
                if len(cells) < 8:
                    continue
                empty = sum((not c or bool(re.fullmatch('[_﹍﹎▁‗]{3,}|待填写|请填写|待填', c)) for c in cells))
                area = (table.bbox[2] - table.bbox[0]) * (table.bbox[3] - table.bbox[1]) / (page.rect.width * page.rect.height)
                outside = 0
                table_rect = type(page.rect)(table.bbox)
                for block in page.get_text('blocks'):
                    rect = type(page.rect)(block[:4])
                    intersection = rect & table_rect
                    if not rect.get_area() or intersection.get_area() / rect.get_area() < 0.5:
                        outside += len(re.sub('\\s+', '', str(block[4])))
                detail = {'body_cells': len(cells), 'empty_body_cells': empty, 'empty_ratio': round(empty / len(cells), 3), 'page_area_ratio': round(area, 3), 'outside_text_chars': outside}
                metrics['template_details'].setdefault('tables', []).append(detail)
                if empty >= 8 and empty / len(cells) >= 0.75 and (area >= 0.2) and (outside <= 400):
                    return finding('空白表格模板', number, f'表头以外{len(cells)}个数据格，{empty}格为空或占位，空格占比{empty / len(cells):.0%}；表格占页面{area:.0%}，表外正文{outside}字', level='明确表格证据')
                if empty >= 8 and empty / len(cells) >= 0.75:
                    metrics.setdefault('template_candidates', []).append(finding('疑似空白表格', number, f'数据区{len(cells)}格中{empty}格为空；因表格占比或正文较多，不直接认定整份为空白模板'))
        except Exception:
            pass
    return _legacy_blank_form_evidence(page, number, metrics)

def page_role(page, metrics):
    """先区分封面、正文、空白与模板。标题/封面不参加水印重复计数。"""
    blocks = page.get_text('dict').get('blocks', [])
    sizes = [s.get('size', 0) for b in blocks for line in b.get('lines', []) for s in line.get('spans', []) if s.get('text', '').strip()]
    line_count = sum((len(b.get('lines', [])) for b in blocks))
    image_area = sum(((i['bbox'][2] - i['bbox'][0]) * (i['bbox'][3] - i['bbox'][1]) for i in page.get_image_info())) / (page.rect.width * page.rect.height)
    chars = metrics['chars']
    if metrics['blank']:
        return 'blank'
    if metrics.get('template_page') and (metrics.get('blank_form') or {}).get('category')!='空白表格模板':
        return 'template'
    if metrics.get('template_page') and metrics.get('template_has_grid'):
        return 'template'
    if metrics['number'] == 1 and (chars <= 180 and max(sizes, default=0) >= 22 or (chars <= 120 and image_area >= 0.2)):
        return 'cover'
    if metrics.get('template_page'):
        return 'template'
    if chars >= 80 and (line_count >= 4 or len(metrics.get('ocr_lines', [])) >= 4):
        return 'body'
    return 'other'

def reliable_template_page(page, metrics):
    proof = metrics.get('blank_form')
    if proof and proof['category'] == '空白表格模板':
        table_stats=metrics.get('template_details',{}).get('tables',[])
        if any(t.get('outside_text_chars',0)>=120 for t in table_stats):
            return False
        image_area = sum(((i['bbox'][2] - i['bbox'][0]) * (i['bbox'][3] - i['bbox'][1]) for i in page.get_image_info())) / (page.rect.width * page.rect.height)
        if image_area >= 0.15:
            return False
        if re.search('图例|不重要|次重要|重要程度|legend', metrics['text'], re.I):
            return False
        horizontal=set();vertical=set()
        for path in page.get_drawings():
            color=path.get('color');fill=path.get('fill');rect=path['rect']
            if color and max(color)<.4 and path.get('stroke_opacity',1)>.8:
                for item in path.get('items',[]):
                    if item[0]=='re':
                        box=item[1];horizontal.update((round(box.y0,1),round(box.y1,1)));vertical.update((round(box.x0,1),round(box.x1,1)))
                    elif item[0]=='l':
                        a,b=item[1:3]
                        if abs(a.y-b.y)<1 and abs(a.x-b.x)>20:horizontal.add(round(a.y,1))
                        if abs(a.x-b.x)<1 and abs(a.y-b.y)>20:vertical.add(round(a.x,1))
            elif fill and max(fill)<.4:
                if rect.height<2 and rect.width>20:horizontal.add(round((rect.y0+rect.y1)/2,1))
                if rect.width<2 and rect.height>20:vertical.add(round((rect.x0+rect.x1)/2,1))
        metrics['template_has_grid']=len(horizontal)>=3 and len(vertical)>=3
        if not metrics['template_has_grid']:return False
    if proof:
        return True
    return metrics['placeholders'] >= 5 and metrics['form_labels'] >= 3

def background_candidates(page, metrics, fitz, settings):
    if metrics['page_role'] != 'body':
        return []
    traces = page.get_texttrace()
    regular = [t for t in traces if t.get('size', 0) < 24 and t.get('opacity', 1) > 0.8 and (t['bbox'][1] > page.rect.height * 0.1)]

    def behind(box, seq):
        return sum((t['seqno'] > seq and (not (fitz.Rect(t['bbox']) & fitz.Rect(box)).is_empty) for t in regular)) >= 2
    candidates = []
    for t in traces:
        angle = abs(math.degrees(math.atan2(t['dir'][1], t['dir'][0]))) % 180
        diagonal = 15 < angle < 75 or 105 < angle < 165
        color = t.get('color', (0, 0, 0))
        color = (color,) * 3 if isinstance(color, (int, float)) else color
        pale = len(color) == 3 and 0.45 < min(color) < 0.92 and (max(color) - min(color) < 0.12)
        if t.get('size', 0) < 24 or (not (pale or t.get('opacity', 1) < 0.8)):
            continue
        box = t['bbox']
        center = (box[1] + box[3]) / 2 / page.rect.height
        if not 0.15 < center < 0.85 or not behind(box, t['seqno']):
            continue
        text = ''.join((chr(c[0]) for c in t.get('chars', []) if 0 <= c[0] <= 1114111))
        text = re.sub('\\s+', '', text).lower()
        if len(text) < 2:
            continue
        norm = [round(box[0] / page.rect.width, 3), round(box[1] / page.rect.height, 3), round(box[2] / page.rect.width, 3), round(box[3] / page.rect.height, 3)]
        key = 'native:' + text + ':' + repr([round(v / 0.05) for v in norm])
        candidates.append({'key': key, 'page': metrics['number'], 'bbox': norm, 'type': '背景文字', 'description': f'正文背后的浅色/半透明大字：{text[:60]}；绘制顺序早于覆盖正文'})
    vector = vector_watermark_evidence(page, metrics['number'], fitz, settings)
    if vector:
        union = [vector['bbox'][0] * page.rect.width, vector['bbox'][1] * page.rect.height, vector['bbox'][2] * page.rect.width, vector['bbox'][3] * page.rect.height]
        seq = max((p.get('seqno', 10 ** 9) for p in vector['paths']))
        if behind(union, seq):
            candidates.append({'key': 'vector:' + vector['fingerprint'], 'page': metrics['number'], 'bbox': vector['bbox'], 'type': '背景矢量字符轮廓', 'description': f"正文背后{vector['glyph_shapes']}个斜向半透明复杂字符轮廓，覆盖{vector['overlapped_text_lines']}行文字，绘制顺序早于正文"})
    return candidates

def apply_document_policy(metrics, total, complete):
    notes = []
    proofs = []
    if not complete:
        return ('不通过', '检查未完成或文件完整性异常；这是技术失败，不是确认存在水印或模板', 'technical_failure', proofs, notes)
    groups = collections.defaultdict(list)
    for p in metrics:
        for candidate in p.get('background_candidates', []):
            groups[candidate['key']].append(candidate)
    for items in groups.values():
        pages = sorted({i['page'] for i in items})
        if len(pages) >= 3:
            for item in items:
                proofs.append(finding('重复正文背景水印', item['page'], item['description'] + f'；相同特征共见于正文页{pages}', level='跨页背景证据', bbox=item['bbox']))
    if proofs:
        pages = sorted({p['page'] for p in proofs})
        return ('不通过', f'相同背景水印特征出现在{len(pages)}个不同正文页：{pages}', 'watermark', proofs, notes)
    if groups:
        notes.append('发现少量正文背景候选，但未满足同一特征至少3个正文页，不据此拒绝。')
    inspected_all = len(metrics) == total
    relevant = [p for p in metrics if p['page_role'] not in ('cover', 'blank')]
    template_pages = [p for p in relevant if p['template_page']]
    normal = [p for p in relevant if not p['template_page']]
    if inspected_all and relevant and (len(template_pages) == len(relevant)):
        proofs = [p['blank_form'] or finding('整份空白模板', p['number'], '该页主要为未填字段及占位符', level='整体模板证据') for p in template_pages]
        return ('不通过', '已检查全文：除封面和空白页外，所有内容页均为未填写模板，没有实质正文', 'whole_template', proofs, notes)
    if template_pages:
        notes.append('部分页面含空表或模板，但存在其他正文，或尚未检查全文；不把局部模板当成整份空白模板。')
    if inspected_all and metrics and all((p['blank'] for p in metrics)):
        return ('不通过', '全文页面均为空白', 'blank', [], notes)
    if not inspected_all:
        notes.append('仅检查前10页，无法据此确认全文无问题，也无法确认整份都是空白模板。')
    low = [p['number'] for p in metrics if p.get('ocr_problem') or p.get('image_only')]
    if low:
        notes.append(f'OCR识读不足页：{low}；未形成明确违规证据，按优先避免误拒的策略放行，并非确认这些页合格。')
    if any(p.get('ocr_used') for p in metrics):
        notes.append('扁平扫描图的OCR可以读字，但不能可靠证明图片内部的底层绘制关系；未据此强行判定背景水印。')
    return ('通过', '已检查范围未达到明确拒绝条件；封面装饰、局部空表和单页疑点不作为拒绝依据', 'no_confirmed_violation', [], notes)

def page_metrics(page, number, fitz, settings, cancelled=lambda: False, log=lambda _: None):
    metrics = _ocr_page_metrics(page, number, fitz, settings, cancelled, log)
    metrics['blank_form'] = blank_form_evidence(page, number, metrics)
    metrics['template_page'] = reliable_template_page(page, metrics)
    metrics['page_role'] = page_role(page, metrics)
    if metrics['page_role'] == 'cover':
        metrics['template_page'] = False
    metrics['background_candidates'] = background_candidates(page, metrics, fitz, settings)
    return metrics

def inspect_file(source, evidence, settings, cancelled=lambda: False, log=lambda _: None):
    fitz = require_runtime()
    source = Path(source)
    evidence = Path(evidence)
    evidence.mkdir(parents=True, exist_ok=True)
    r = {'decision': '不通过', 'reason': '检查未完成', 'decision_basis': 'technical_failure', 'notes': [], 'total_pages': 0, 'checked_pages': 0, 'complete': False, 'full_document_checked': False, 'sampled': False, 'planned_pages': 0, 'uninspected_pages': 0, 'inspection_scope': '未完成', 'stages': [], 'findings': [], 'errors': [], 'page_images': [], 'rule_version': RULE_VERSION, 'inspection_type': '本地OCR及跨页文档规则，二分类', 'ocr_evidence_dir': str((evidence / 'ocr').resolve())}
    if source.suffix.lower() not in SUPPORTED:
        r.update(reason='不支持或不符合文档格式要求', decision_basis='unsupported_format', complete=True)
        save_json(evidence / 'inspection.json', r)
        return r
    metrics = []
    try:
        pdf = convert_to_pdf(source, evidence, settings)
        with fitz.open(pdf) as doc:
            if not doc.is_pdf:
                raise ValueError('真实格式不是PDF')
            if doc.needs_pass:
                raise ValueError('需要打开密码')
            total = len(doc)
            r['total_pages'] = total
            if not total:
                raise ValueError('没有页面')
            if type(settings.pdf_page_limit) is not int or settings.pdf_page_limit < 0:
                raise ValueError('页数上限不合法')
            limit = min(total, settings.pdf_page_limit) if settings.pdf_page_limit else total
            r.update(planned_pages=limit, sampled=limit < total, inspection_scope=f'前{limit}页抽检' if limit < total else '全文检查')
            log(f"    {r['inspection_scope']}：共{total}页，检查{limit}页")
            for index in range(limit):
                if cancelled():
                    raise InterruptedError('用户停止')
                try:
                    p = page_metrics(doc[index], index + 1, fitz, settings, cancelled, log)
                    metrics.append(p)
                    if p.get('ocr_used'):
                        folder = evidence / 'ocr'
                        folder.mkdir(exist_ok=True)
                        (folder / f'page_{index + 1:05d}.txt').write_text(p.get('ocr_text', ''), encoding='utf-8')
                        save_json(folder / f'page_{index + 1:05d}.json', {'page': index + 1, 'text': p.get('ocr_text', ''), 'lines': p.get('ocr_lines', []), 'quality': p.get('ocr_quality', {}), 'problem': p.get('ocr_problem', '')})
                except InterruptedError:
                    raise
                except Exception as exc:
                    r['errors'].append({'page': index + 1, 'error': type(exc).__name__ + ': ' + str(exc)[:180]})
            if doc.is_repaired:
                r['errors'].append({'error': '解析器修复了文件，完整性未确认'})
            r['checked_pages'] = len(metrics)
            r['complete'] = len(metrics) == limit and (not r['errors'])
            decision, reason, basis, proofs, notes = apply_document_policy(metrics, total, r['complete'])
            r.update(decision=decision, reason=reason, decision_basis=basis, findings=proofs, notes=notes)
            r['stages'] = [{'name': '指定范围扫描及页面角色识别', 'pages': len(metrics), 'planned': limit}, {'name': '正文背景跨页判定', 'minimum_body_pages': 3, 'confirmed_pages': sorted({f['page'] for f in proofs if f['category'] == '重复正文背景水印'})}, {'name': '整份模板判定', 'whole_document_scanned': len(metrics) == total, 'template_pages': [p['number'] for p in metrics if p['template_page']]}]
            numbers = list(dict.fromkeys((f['page'] for f in proofs))) or [1]
            r['evidence_pages_omitted'] = max(0, len(numbers) - settings.evidence_pages)
            for number in numbers[:settings.evidence_pages]:
                if cancelled():
                    raise InterruptedError('用户停止')
                try:
                    page = doc[number - 1]
                    scale = settings.image_long_edge / max(page.rect.width, page.rect.height)
                    target = evidence / f'page_{number:05d}.jpg'
                    page.get_pixmap(matrix=fitz.Matrix(scale, scale), colorspace=fitz.csRGB, alpha=False).save(str(target))
                    r['page_images'].append({'page': number, 'path': str(target.resolve())})
                except Exception as exc:
                    r['notes'].append('证据图导出失败：' + type(exc).__name__)
    except Exception as exc:
        r['errors'].append({'error': type(exc).__name__ + ': ' + str(exc)[:300]})
        r.update(decision='不通过', reason='技术检查未完成：' + str(exc)[:180], decision_basis='technical_failure', complete=False)
    r['checked_pages'] = len(metrics)
    r['uninspected_pages'] = max(0, r['total_pages'] - len(metrics))
    r['full_document_checked'] = r['complete'] and len(metrics) == r['total_pages']
    if r['sampled']:
        r['reason'] += f"；仅检查前{r['planned_pages']}页，其余{r['uninspected_pages']}页未检查"
    r['page_metrics'] = [{k: v for k, v in p.items() if k not in ('text', 'suspects', 'strong_watermarks', 'ocr_text', 'ocr_lines')} for p in metrics]
    save_json(evidence / 'inspection.json', r)
    return r
if __name__ == '__main__':
    main()
