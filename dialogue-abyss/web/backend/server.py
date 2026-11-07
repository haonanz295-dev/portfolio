"""Local publisher service. Python standard library; private SQLite outside static routes."""
import argparse, base64, hashlib, hmac, json, mimetypes, os, secrets, sqlite3, time
from collections import defaultdict, deque
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get('ABYSS_DATA_DIR', str(ROOT / 'backend' / 'data'))).resolve()
DATA.mkdir(parents=True, exist_ok=True)
UPLOADS = DATA / 'uploads'
UPLOADS.mkdir(exist_ok=True)
DB = DATA / 'ocean.sqlite3'
TOKENS = {}
LIMITS = defaultdict(deque)

def conn():
    c = sqlite3.connect(DB, timeout=10)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    return c

def init():
    with conn() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY, token_hash TEXT NOT NULL, created REAL NOT NULL, updated REAL NOT NULL, age TEXT, context TEXT, intent TEXT, mbti TEXT, preferences TEXT, seconds INTEGER DEFAULT 0, events TEXT DEFAULT '{}');
        CREATE TABLE IF NOT EXISTS feedback(id TEXT PRIMARY KEY, created REAL, rating INTEGER, text TEXT);
        CREATE TABLE IF NOT EXISTS content(id TEXT PRIMARY KEY, kind TEXT, title TEXT, description TEXT, region INTEGER, status TEXT DEFAULT 'draft', created REAL);
        CREATE TABLE IF NOT EXISTS assets(id TEXT PRIMARY KEY, name TEXT, kind TEXT, filename TEXT, size INTEGER, created REAL);
        ''')
    auth = DATA / 'owner.json'
    if not auth.exists():
        password = os.environ.get('ABYSS_ADMIN_PASSWORD')
        if password:
            if len(password) < 12:raise SystemExit('Password must have at least 12 characters.')
            salt = secrets.token_bytes(32)
            digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 310000)
            auth.write_text(json.dumps({'salt':salt.hex(), 'hash':digest.hex()}), encoding='utf-8')
        else:return None
    return json.loads(auth.read_text(encoding='utf-8'))

def clean(value, size=120):
    return str(value or '').strip()[:size]

def rows(c, sql, args=()):
    return [dict(r) for r in c.execute(sql,args)]

class Handler(BaseHTTPRequestHandler):
    server_version = 'AbyssLocal/0.4'
    def log_message(self, fmt, *args):
        # No request body or authorization values in logs.
        pass

    def reply(self, status, data):
        raw = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers()
        self.wfile.write(raw)

    def authorized(self):
        token = self.headers.get('Authorization','').removeprefix('Bearer ')
        now=time.time()
        for k,v in list(TOKENS.items()):
            if v<now:TOKENS.pop(k,None)
        return token in TOKENS

    def limited(self, kind, cap, period=60):
        key=(self.client_address[0],kind); q=LIMITS[key]; now=time.time()
        while q and q[0]<now-period:q.popleft()
        if len(q)>=cap:return True
        q.append(now);return False

    def valid_origin(self):
        origin=self.headers.get('Origin')
        return not origin or origin in ('http://'+self.headers.get('Host',''), 'https://'+self.headers.get('Host',''))

    def do_GET(self):
        path=unquote(urlparse(self.path).path)
        if path=='/api/health':return self.reply(200,{'ok':True,'version':'0.4','setup':AUTH is None})
        if path.startswith('/api/admin/'):
            if not self.authorized():return self.reply(401,{'error':'请先登录发布者后台'})
            with conn() as c:
                if path=='/api/admin/overview':
                    sessions=rows(c,'SELECT id,created,updated,age,context,intent,mbti,preferences,seconds,events FROM sessions ORDER BY created DESC LIMIT 300')
                    for s in sessions:
                        s['preferences']=json.loads(s['preferences']);s['events']=json.loads(s['events'])
                    totals=dict(c.execute('SELECT COUNT(*) visits,COALESCE(SUM(seconds),0) seconds FROM sessions').fetchone())
                    return self.reply(200,{'totals':totals,'sessions':sessions,'feedback':rows(c,'SELECT * FROM feedback ORDER BY created DESC LIMIT 300'),'content':rows(c,'SELECT * FROM content ORDER BY created DESC'),'assets':rows(c,'SELECT * FROM assets ORDER BY created DESC')})
                if path.startswith('/api/admin/assets/'):
                    a=c.execute('SELECT * FROM assets WHERE id=?',(path.rsplit('/',1)[1],)).fetchone()
                    if not a:return self.reply(404,{'error':'素材不存在'})
                    return self.file(UPLOADS / a['filename'], download=a['filename'])
            return self.reply(404,{'error':'接口不存在'})
        if path.startswith('/api/'):return self.reply(404,{'error':'接口不存在'})
        if path in ('/admin','/admin/'):return self.file(ROOT/'backend'/'admin.html')
        if path in ('/admin.js','/admin.css'):return self.file(ROOT/'backend'/path[1:])
        # Explicit allowlist. Never expose database, credentials, tools or backups.
        if path=='/':path='/index.html'
        allowed={'index.html','开始探索.html','style.css','art.css','ocean-art.js','reflection.js','forms.css','experience.css','profile.js','ui-additions.js','audio.js','game.js','experience.js'}
        rel=path.lstrip('/')
        target=(ROOT/rel).resolve()
        if not target.is_relative_to(ROOT) or '..' in Path(rel).parts:return self.reply(403,{'error':'禁止访问'})
        if rel not in allowed and not rel.startswith(('vendor/','assets/')):return self.reply(404,{'error':'页面不存在'})
        return self.file(target)

    def file(self, target, download=None):
        if not target.is_file():return self.reply(404,{'error':'文件不存在'})
        self.send_response(200)
        self.send_header('Content-Type',mimetypes.guess_type(str(target))[0] or 'application/octet-stream')
        self.send_header('Content-Length',str(target.stat().st_size))
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','same-origin')
        if download:self.send_header('Content-Disposition','attachment; filename="'+download+'"')
        self.end_headers()
        try:
            with target.open('rb') as f:
                while chunk:=f.read(65536):self.wfile.write(chunk)
        except (ConnectionError, BrokenPipeError):
            pass  # Scene switching can cancel in-flight audio/image requests.

    def do_POST(self):
        try:
            if not self.valid_origin():return self.reply(403,{'error':'不接受跨站请求'})
            path=urlparse(self.path).path
            if path.startswith('/api/admin/') and path not in ('/api/admin/login','/api/admin/setup') and not self.authorized():return self.reply(401,{'error':'请先登录发布者后台'})
            if self.limited('all',180):return self.reply(429,{'error':'请求较多，请稍后再试'})
            n=int(self.headers.get('Content-Length','0'))
            limit=7*1024*1024 if path=='/api/admin/assets' else 16384
            if n<1 or n>limit:return self.reply(413,{'error':'内容过大或为空'})
            d=json.loads(self.rfile.read(n))
            if not isinstance(d,dict):raise ValueError('需要 JSON 对象')
            now=time.time()
            if path=='/api/admin/setup':
                global AUTH
                if AUTH is not None:return self.reply(409,{'error':'发布者密码已经创建'})
                if self.client_address[0] not in ('127.0.0.1','::1'):return self.reply(403,{'error':'首次设置仅允许在本机进行'})
                password=str(d.get('password',''))
                if len(password)<12:return self.reply(400,{'error':'密码至少需要 12 个字符'})
                salt=secrets.token_bytes(32);digest=hashlib.pbkdf2_hmac('sha256',password.encode(),salt,310000)
                authfile=DATA/'owner.json'
                try:
                    with authfile.open('x',encoding='utf-8') as f:json.dump({'salt':salt.hex(),'hash':digest.hex()},f)
                except FileExistsError:return self.reply(409,{'error':'密码已经创建，请刷新页面登录'})
                AUTH={'salt':salt.hex(),'hash':digest.hex()}
                token=secrets.token_urlsafe(36);TOKENS[token]=now+8*3600
                return self.reply(201,{'token':token})
            if path=='/api/admin/login':
                if AUTH is None:return self.reply(409,{'error':'请先设置发布者密码'})
                if self.limited('login',8,300):return self.reply(429,{'error':'登录尝试较多，请五分钟后再试'})
                digest=hashlib.pbkdf2_hmac('sha256',str(d.get('password',''))[:1024].encode(),bytes.fromhex(AUTH['salt']),310000).hex()
                if not hmac.compare_digest(digest,AUTH['hash']):return self.reply(401,{'error':'密码不正确'})
                token=secrets.token_urlsafe(36);TOKENS[token]=now+8*3600
                return self.reply(200,{'token':token})
            if path=='/api/admin/logout':
                TOKENS.pop(self.headers.get('Authorization','').removeprefix('Bearer '),None)
                return self.reply(200,{'ok':True})
            with conn() as c:
                if path=='/api/experience':
                    if d.get('consent') is not True:return self.reply(400,{'error':'需要单独同意'})
                    if self.limited('create',20):return self.reply(429,{'error':'创建次数较多，请稍后再试'})
                    if d.get('age') not in ('18-24','25-30','31+'):raise ValueError('当前仅提供成年体验')
                    p=d.get('preferences') or {}; values=p.get('values')
                    if not isinstance(values,list) or len(values)!=5 or any(type(v) not in (int,float) or not 1<=v<=5 for v in values):raise ValueError('偏好数据不完整')
                    # Recompute adaptation tier; never trust client tier or psychological labels.
                    tier=max(1,min(5,6-int((values[0]+values[1])/2+.5)))
                    pref={'version':1,'values':values,'tier':tier}
                    sid=secrets.token_hex(16);token=secrets.token_urlsafe(32)
                    c.execute('INSERT INTO sessions(id,token_hash,created,updated,age,context,intent,mbti,preferences) VALUES(?,?,?,?,?,?,?,?,?)',(sid,hashlib.sha256(token.encode()).hexdigest(),now,now,d['age'],clean(d.get('context')),clean(d.get('intent')),clean(d.get('mbti'),4),json.dumps(pref)))
                    return self.reply(201,{'id':sid,'token':token})
                if path in ('/api/experience/update','/api/experience/delete'):
                    sid=clean(d.get('id'),64);record=c.execute('SELECT * FROM sessions WHERE id=?',(sid,)).fetchone()
                    token_hash=hashlib.sha256(clean(d.get('token'),200).encode()).hexdigest()
                    if not record or not hmac.compare_digest(record['token_hash'],token_hash):return self.reply(403,{'error':'记录凭据无效'})
                    if path.endswith('/delete'):
                        c.execute('DELETE FROM sessions WHERE id=?',(sid,));return self.reply(200,{'ok':True})
                    ev=d.get('events') or {}
                    if not isinstance(ev,dict) or len(ev)>50:raise ValueError('活动数据不正确')
                    allowed={'resonance_start','resonance_complete','resonance_try','resonance_stop','garden_start','garden_complete','garden_try','garden_stop','companion_change','journey_end','journey_restart','wave','raise','spin','bubbles','bow','stretch','follow','bye','rest','listen','talk','invite_shown','invite_accept','invite_decline','invite_quiet','race_start','race_complete','race_try','race_stop','hide_start','hide_complete','hide_try','hide_stop','guide_start','guide_arrive','guide_stop','photo_open','photo_save','region_visit'}
                    ev={k:min(10000,max(0,int(v))) for k,v in ev.items() if k in allowed}
                    sec=min(86400,max(0,int(d.get('seconds',0))))
                    c.execute('UPDATE sessions SET seconds=?,events=?,updated=? WHERE id=?',(sec,json.dumps(ev),now,sid));return self.reply(200,{'ok':True})
                if path=='/api/feedback':
                    if d.get('consent') is not True:return self.reply(400,{'error':'请单独同意发送反馈'})
                    if self.limited('feedback',6):return self.reply(429,{'error':'请稍后再发送'})
                    rating=d.get('rating');txt=clean(d.get('text'),1200)
                    if rating is not None and (type(rating) is not int or not 1<=rating<=5):raise ValueError('评价范围不正确')
                    if not txt and rating is None:raise ValueError('请填写评价或建议')
                    c.execute('INSERT INTO feedback VALUES(?,?,?,?)',(secrets.token_hex(16),now,rating,txt));return self.reply(201,{'ok':True})
                if path=='/api/admin/content':
                    kind=d.get('kind');title=clean(d.get('title'),80)
                    if kind not in ('level','character','animal') or not title:raise ValueError('请选择内容类型并填写名称')
                    region=int(d.get('region',0))
                    if not 0<=region<=5:raise ValueError('海域不正确')
                    cid=clean(d.get('id'),64) or secrets.token_hex(16)
                    c.execute('INSERT INTO content VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET kind=excluded.kind,title=excluded.title,description=excluded.description,region=excluded.region,status=excluded.status',(cid,kind,title,clean(d.get('description'),2000),region,'draft',now));return self.reply(200,{'ok':True,'id':cid})
                if path=='/api/admin/assets':
                    raw=base64.b64decode(d.get('data',''),validate=True)
                    if not raw or len(raw)>5*1024*1024:raise ValueError('素材需要小于 5 MB')
                    if raw.startswith(b'\x89PNG\r\n\x1a\n'):ext='png'
                    elif raw.startswith(b'\xff\xd8\xff'):ext='jpg'
                    elif raw[:4]==b'glTF' and len(raw)>=12 and int.from_bytes(raw[4:8],'little')==2 and int.from_bytes(raw[8:12],'little')==len(raw):ext='glb'
                    elif raw.lstrip().startswith(b'{'):
                        model=json.loads(raw)
                        if model.get('asset',{}).get('version')!='2.0' or not model.get('meshes'):
                            raise ValueError('需要包含网格的 glTF 2.0 模型')
                        for resource in model.get('buffers',[])+model.get('images',[]):
                            if 'uri' in resource and not str(resource['uri']).startswith('data:'):
                                raise ValueError('glTF 需内嵌资源，不能引用外部文件或链接')
                        ext='gltf'
                    else:raise ValueError('仅接收 PNG、JPEG、GLB 或内嵌 glTF 2.0 文件')
                    aid=secrets.token_hex(16);filename=aid+'.'+ext
                    (UPLOADS/filename).write_bytes(raw)
                    c.execute('INSERT INTO assets VALUES(?,?,?,?,?,?)',(aid,clean(d.get('name'),100) or filename,clean(d.get('kind'),30),filename,len(raw),now));return self.reply(201,{'ok':True,'id':aid})
                if path=='/api/admin/delete':
                    table=d.get('table');rid=clean(d.get('id'),64)
                    if table not in ('sessions','feedback','content','assets'):raise ValueError('类型不正确')
                    if table=='assets':
                        a=c.execute('SELECT filename FROM assets WHERE id=?',(rid,)).fetchone()
                        if a:(UPLOADS/a['filename']).unlink(missing_ok=True)
                    c.execute('DELETE FROM '+table+' WHERE id=?',(rid,));return self.reply(200,{'ok':True})
            self.reply(404,{'error':'接口不存在'})
        except (ValueError,TypeError,KeyError,OverflowError) as e:self.reply(400,{'error':'数据格式不正确：'+str(e)[:100]})
        except (ConnectionError,BrokenPipeError):pass
        except Exception:self.reply(500,{'error':'保存失败，请查看本机服务与磁盘状态'})

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=4196);parser.add_argument('--host',default='127.0.0.1');args=parser.parse_args()
    AUTH=init()
    print(f'Game: http://{args.host}:{args.port}/\nPublisher: http://{args.host}:{args.port}/admin\nKeep this window open. Ctrl+C stops the service.',flush=True)
    ThreadingHTTPServer((args.host,args.port),Handler).serve_forever()
