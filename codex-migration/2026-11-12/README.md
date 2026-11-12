# Windows → MacBook：Codex 恢复入口

备份日期：2026-11-12。固定入口：

https://github.com/haonanz295-dev/portfolio/tree/main/codex-migration/2026-11-12

## 新电脑直接复制这段话给 Codex

> 请打开 https://github.com/haonanz295-dev/portfolio/tree/main/codex-migration/2026-11-12 ，先阅读 README.md，再按其中的恢复步骤为我的 MacBook 恢复全部可迁移的 Codex skills。使用备份中的文件，不依赖无法确认的上游来源。先检查本机情况，下载并校验所有备份分卷，运行 restore-mac.py 的预演，再执行恢复；跳过已有的同名目录并报告冲突，不要覆盖我的现有配置。根据 manifest-public.json 核对插件，在当前版本支持的范围内安装；需要账号登录、OAuth 或 macOS 权限时明确提示我。按 skill 的实际需要安装 macOS 依赖，最后核对 skill 数量、代表性功能与未完成项目。不要承诺 Windows 程序可直接在 Mac 运行。

## 保存了什么

- 273 条本地 skill 定义，位于 272 个顶层目录；frontend-slides 内还带一个嵌套 skill。
- 5 条系统 skill 记录。系统 skill 随新版应用提供，不覆盖系统目录。
- 25 条插件版本缓存记录和 65 条插件附带 skill 定义记录，含旧版本；它们不是已启用或已授权插件的精确数量。
- Excel 清单、可复制来源链接 CSV、完整 JSON 清单、逐文件 SHA256 和跨平台恢复脚本。
- 4 个 PATH 工具、当前 Python 环境的包清单，以及 85 条 Windows 应用注册表记录。
- 本地 skill 备份包含 16,993 个文件，保留脚本、引用和素材。GitHub 使用分卷保存，脚本自动合并。

无法从当前电脑状态准确判断每项是否由过去的助手安装，因此清单按实际存在的文件和记录编制，不伪造安装历史。来源未确认的项目已保留文件备份。已确认的上游链接可能指向 HEAD，不代表与本机快照完全相同；精确恢复以备份及逐文件校验为准。

## 恢复步骤（给新 Mac 上的 Codex）

1. 安装 Mac 版 Codex，用相同账号登录。不要把 Windows 应用、整个 `.codex` 文件夹、插件缓存或原始 `config.toml` 覆盖过去。
2. 确认 Mac 上有 Python 3。把本目录的 `restore-mac.py` 下载到本地并阅读代码。
3. 先运行 `python3 restore-mac.py`。默认只下载、校验和列出计划，不复制到 skill 目录。
4. 运行 `python3 restore-mac.py --apply`。它默认复制到 `~/.agents/skills`，不执行 skill 内的脚本，不覆盖已有顶层目录。若当前 Codex 版本使用其他目录，先查当前官方文档，再显式传入 `--target`；不要重复装到两个目录。
5. 若使用本地完整备份包，解压后运行 `python3 restore-mac.py --bundle /解压目录 --apply`。该目录需要 `skills-backup.zip` 和 `files-sha256.json`。
6. 重启 Codex，检查 273 条本地 skill 定义能否被发现。嵌套 skill、已有目录冲突和系统内置差异要单独报告。不要把复制成功当成每个 skill 的功能均已验证。
7. 按清单逐项核对插件。内置插件和运行库由 Mac 版应用供应；第三方插件从当前插件目录安装。Windows Computer Use、通知 exe、node_repl 管道和绝对路径须由 Mac 版本重新生成，不移植旧配置。
8. GitHub、Google Drive、Gmail、Calendar、Contacts、Figma、Adobe、Canva、Sites 等连接按新电脑显示的状态处理；需重新授权时由用户完成。相同账号不保证本地文件、全部授权和系统权限自动恢复。
9. 按实际需求恢复 Python/Node 依赖。`python-packages.json` 是环境快照，不是应无条件全部安装的兼容性锁文件。Windows 应用清单仅供手动核对，不自动安装所有整机软件。
10. 输出已恢复、已跳过、需要授权、Mac 不兼容和来源/依赖仍待确认的列表，并抽查几项常用 skill。

## 文件

- `Codex迁移清单.xlsx`：可筛选 Excel；链接是可直接复制的文本。
- `manifest-public.json`：移除本地绝对路径的 skill、插件和运行环境清单。
- `skills-links.csv`：带 UTF-8 BOM，可直接用 Excel 打开。
- `skills-backup.zip.part-*` + `bundle-index.json`：完整 skill 备份分卷及分卷校验。
- `files-sha256.json`：解压后每个文件的 SHA256。
- `restore-mac.py`：预演/恢复脚本，使用 Python 标准库，不依赖 pip 包。
- `backup-report.json`：数量、排除项和扫描范围。
- `python-packages.json`、`windows-apps.json`：辅助核对清单。

## 未纳入备份

账号凭据、API 密钥、OAuth token、`auth.json`、聊天/日志数据库、会话、浏览器个人数据、原始全量配置、Codex 内置系统 skill、插件运行缓存、依赖安装目录及 Windows 可执行文件。备份前已扫描常见密钥特征，未发现匹配；特征扫描不能证明任何文件中绝无敏感内容。

本仓库为公开仓库。上传的是 skill 文件和恢复资料，不含原始私人配置；保留第三方文件中原有的许可证与声明。软件许可证、服务订阅、付费功能及登录授权不能靠备份迁移。

## 官方依据

本次查阅的官方文档将用户级本地 skill 目录列为 `~/.agents/skills`，系统 skill 由应用内置，重名 skill 不合并。未来恢复时应复核当时的版本：

https://learn.chatgpt.com/docs/build-skills

本备份不是 Windows 整机镜像，也不是已在 Mac 上完成验证的一键系统安装器；它提供完整本地 skill 文件恢复，以及插件、依赖和授权的逐项重建依据。

## 公开上传授权

用户于 2026-11-12 明确同意将完整 skill 文件备份（含脚本、参考资料和素材）及软件清单上传至此公开仓库。
