# 办公文档本地质检

2026-11-12 整理的最新界面版，代码与当前 Windows PyCharm 项目一致。
完全本地运行，无需 API Key，不调用外部 AI。内置中英文 OCR 模型。

## 快速开始（Windows，已验证）

1. 安装 Python 3.10 或更新版本，勾选加入 PATH。
2. 在此目录打开终端，运行 `python -m pip install -r requirements.txt`。
3. 运行 `python document_qc_offline_ocr.py`，或双击 `start_windows.bat`。
4. 选择原始文件夹和独立的结果文件夹，点击开始。高级路径通常留空。
5. Word/PPT 需要另行安装 LibreOffice；PDF 不需要。保留旁边的 tessdata 目录。

完整包包含源码、模型、依赖清单、说明和校验脚本；不包含 Python 解释器、PyMuPDF 安装包或 LibreOffice 安装程序。首次安装依赖需要网络，质检本身不需要网络。

## 换到 MacBook

Python 源码和模型可以保留。需要安装带 Tk 支持的 Python、requirements.txt 依赖，以及处理 Word/PPT 所需的 LibreOffice。当前版本在 Windows 验证，尚未在 macOS 实机测试。

Mac 中 LibreOffice 通常需在高级设置指定 `/Applications/LibreOffice.app/Contents/MacOS/soffice`。当前“打开结果文件夹”按钮使用 Windows 接口，Mac 请手动在 Finder 打开输出目录。此仓库备份保留当前版本，没有擅自改变质检逻辑。

## 规则及实际边界

- 默认仅检查每份文档前 10 页，不足 10 页则全部检查。
- 同一背景水印特征需要至少出现在 3 个正文页，并有底层绘制与正文覆盖证据；封面和单页装饰不计入。
- 只有已检查全文且内容页整体为空模板时，按空模板拒绝；局部空表不直接拒绝。
- 输出“通过”和“不通过”，附 HTML、CSV、JSON 报告。
- “通过”表示抽检范围没有达到拒绝条件。OCR 识读不足等情况会备注并放行，不能视为全文质量证明。
- 扁平图片中的水印缺少图层信息，存在漏检；不承诺 90% 准确率。三个阶段是本地规则，不是三轮 AI。

更多规则见 `二分类版使用说明.txt`。模型来源和 Apache 2.0 许可证见 `THIRD_PARTY_NOTICES.md` 与 `tessdata/LICENSE`。

## 校验完整性

运行 `python verify_package.py`，核对 SHA-256 校验清单。

本项目不包含真实办公文档、输入数据、运行结果、账号密钥或聊天记录。
