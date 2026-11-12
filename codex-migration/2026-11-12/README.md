# Codex Windows → MacBook 迁移入口

备份日期：2026-11-12。

## 给新 Mac 上的 Codex 的指令

> 请按 https://github.com/haonanz295-dev/portfolio/tree/main/codex-migration/2026-11-12 的说明，为我的 MacBook 恢复 Codex skills 和插件。先检查本目录是否已有完整备份分卷；若尚未上传，请让我提供已经保存的“Codex迁移完整备份.zip”，不要把来源不明的项目当成已恢复。读取备份说明，先预演，再恢复所有可迁移 skill，跳过现有同名目录，按需要安装 Mac 依赖，提示我完成插件授权，最后列出已恢复和仍待处理的项目。

## 当前保存范围

此文档保存公开可用的名称、来源链接和迁移说明。完整本机备份已生成于原 Windows 电脑，但公开上传需要另行明确批准。**在本目录未出现完整备份分卷前，不能仅凭此链接完整重建所有本地 skill。请保留本地完整备份 ZIP。**

- 本机盘点：273 条本地 skill 定义（272 个顶层目录，其中有一条嵌套定义）、5 条系统定义。
- 25 条插件版本缓存记录、65 条插件附带 skill 定义记录；含旧版本，不等于已启用数量。
- Windows 电脑另存有可筛选 Excel、完整 skill 文件包、逐文件 SHA256、恢复脚本及软件环境清单。
- 无法从现状准确追溯哪些项目由过去的助手安装。以下清单按磁盘实际存在记录编制。

## Mac 恢复方式

1. 安装 Mac 版 Codex，以相同账号登录。
2. 将本地完整备份 ZIP 带到 Mac 并解压；阅读其中的迁移说明及 `restore-mac.py`。
3. 确认 Python 3 可用，先执行 `python3 restore-mac.py --bundle /解压目录` 预演。
4. 再执行 `python3 restore-mac.py --bundle /解压目录 --apply`。默认恢复到 `~/.agents/skills`，校验文件，不执行 skill 自带脚本，跳过已有顶层目录。
5. 重启 Codex，核对定义是否被识别，报告跳过或冲突项。系统 skill 随新版应用提供。
6. 按插件清单检查当前 Mac 版是否提供相应插件，按需重新安装和授权；不复制 Windows 插件运行缓存。
7. 根据使用需求安装 Mac 版 Python/Node 依赖。Windows exe、通知命令、管道、绝对路径和整份原始 config.toml 不直接移植。
8. 对账号登录、OAuth、系统权限及不兼容功能逐项报告。不要把文件复制成功等同于每项功能验证完成。

官方文档列出的用户级 skill 目录为 `~/.agents/skills`；未来恢复时先复核当时的应用版本：https://learn.chatgpt.com/docs/build-skills 。相同账号不等于本地文件、全部授权或系统权限自动同步。

## Skill 名称及来源

来源只在有本地证据时填写。来源仓库 SKILL.md 比对忽略 CRLF/LF 差异；HEAD 链接不固定版本。需要精确恢复时以完整备份及其逐文件校验为准。

| 名称 | 目录 | 类别 | 来源或恢复方式 |
| --- | --- | --- | --- |
| imagegen | `.system/imagegen` | 系统内置 | https://github.com/openai/skills |
| openai-docs | `.system/openai-docs` | 系统内置 | https://github.com/openai/skills |
| review-agent | `.system/review-agent` | 系统内置 | https://github.com/openai/skills |
| skill-creator | `.system/skill-creator` | 系统内置 | https://github.com/openai/skills |
| skill-installer | `.system/skill-installer` | 系统内置 | https://github.com/openai/skills |
| acquisition-channel-advisor | `acquisition-channel-advisor` | 本地 skill | 来源未确认；从完整备份恢复 |
| agent-orchestration-advisor | `agent-orchestration-advisor` | 本地 skill | 来源未确认；从完整备份恢复 |
| ai-behavior-trees-utility-ai | `ai-behavior-trees-utility-ai` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/disciplines/ai-behavior-trees-utility-ai |
| ai-shaped-readiness-advisor | `ai-shaped-readiness-advisor` | 本地 skill | 来源未确认；从完整备份恢复 |
| altitude-horizon-framework | `altitude-horizon-framework` | 本地 skill | 来源未确认；从完整备份恢复 |
| ansoff-matrix | `ansoff-matrix` | 本地 skill | 来源未确认；从完整备份恢复 |
| api-review | `api-review` | 本地 skill | 来源未确认；从完整备份恢复 |
| audio-design | `audio-design` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/disciplines/audio-design |
| autonomous-investigation | `autonomous-investigation` | 本地 skill | 来源未确认；从完整备份恢复 |
| battle-card-builder | `battle-card-builder` | 本地 skill | 来源未确认；从完整备份恢复 |
| bevy-ecs | `bevy-ecs` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/other-engines/bevy-ecs |
| brainstorming | `brainstorming` | 本地 skill | 来源未确认；从完整备份恢复 |
| business-health-diagnostic | `business-health-diagnostic` | 本地 skill | 来源未确认；从完整备份恢复 |
| camera-systems | `camera-systems` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/disciplines/camera-systems |
| card-game | `card-game` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/genres/card-game |
| cavecrew | `cavecrew` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/plugins/caveman/skills/cavecrew |
| caveman | `caveman` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/plugins/caveman/skills/caveman |
| caveman-commit | `caveman-commit` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/skills/caveman-commit |
| caveman-compress | `caveman-compress` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/plugins/caveman/skills/caveman-compress |
| caveman-discover | `caveman-discover` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/skills/caveman-discover |
| caveman-evidence-review | `caveman-evidence-review` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/skills/caveman-evidence-review |
| caveman-explore | `caveman-explore` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/skills/caveman-explore |
| caveman-help | `caveman-help` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/skills/caveman-help |
| caveman-learn | `caveman-learn` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/skills/caveman-learn |
| caveman-manage | `caveman-manage` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/skills/caveman-manage |
| caveman-optimize | `caveman-optimize` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/skills/caveman-optimize |
| caveman-review | `caveman-review` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/skills/caveman-review |
| caveman-setup | `caveman-setup` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/skills/caveman-setup |
| caveman-stats | `caveman-stats` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/skills/caveman-stats |
| company-intel | `company-intel` | 本地 skill | 来源未确认；从完整备份恢复 |
| company-research | `company-research` | 本地 skill | 来源未确认；从完整备份恢复 |
| competitive-analysis-process | `competitive-analysis-process` | 本地 skill | 来源未确认；从完整备份恢复 |
| competitive-intel-watch | `competitive-intel-watch` | 本地 skill | 来源未确认；从完整备份恢复 |
| competitive-research-snapshot | `competitive-research-snapshot` | 本地 skill | 来源未确认；从完整备份恢复 |
| context-engineering-advisor | `context-engineering-advisor` | 本地 skill | 来源未确认；从完整备份恢复 |
| create-game-assets | `create-game-assets` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/disciplines/create-game-assets |
| customer-journey-map | `customer-journey-map` | 本地 skill | 来源未确认；从完整备份恢复 |
| customer-journey-mapping-workshop | `customer-journey-mapping-workshop` | 本地 skill | 来源未确认；从完整备份恢复 |
| defold-core | `defold-core` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/other-engines/defold-core |
| derisk-measurement-advisor | `derisk-measurement-advisor` | 本地 skill | 来源未确认；从完整备份恢复 |
| diagnosing-superpowers | `diagnosing-superpowers` | 本地 skill | 来源未确认；从完整备份恢复 |
| dialogue-systems | `dialogue-systems` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/disciplines/dialogue-systems |
| director-readiness-advisor | `director-readiness-advisor` | 本地 skill | 来源未确认；从完整备份恢复 |
| discovery-interview-prep | `discovery-interview-prep` | 本地 skill | 来源未确认；从完整备份恢复 |
| discovery-process | `discovery-process` | 本地 skill | 来源未确认；从完整备份恢复 |
| dispatching-parallel-agents | `dispatching-parallel-agents` | 本地 skill | 来源未确认；从完整备份恢复 |
| draft-openspec-docs | `draft-openspec-docs` | 本地 skill | 来源未确认；从完整备份恢复 |
| ebitengine-game | `ebitengine-game` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/ebitengine/ebitengine-game |
| eol-checklist | `eol-checklist` | 本地 skill | 来源未确认；从完整备份恢复 |
| eol-internal-enablement | `eol-internal-enablement` | 本地 skill | 来源未确认；从完整备份恢复 |
| eol-message | `eol-message` | 本地 skill | 来源未确认；从完整备份恢复 |
| eol-process | `eol-process` | 本地 skill | 来源未确认；从完整备份恢复 |
| eol-readiness-advisor | `eol-readiness-advisor` | 本地 skill | 来源未确认；从完整备份恢复 |
| eol-stakeholder-sequence | `eol-stakeholder-sequence` | 本地 skill | 来源未确认；从完整备份恢复 |
| epic-breakdown-advisor | `epic-breakdown-advisor` | 本地 skill | 来源未确认；从完整备份恢复 |
| epic-hypothesis | `epic-hypothesis` | 本地 skill | 来源未确认；从完整备份恢复 |
| executing-plans | `executing-plans` | 本地 skill | 来源未确认；从完整备份恢复 |
| executive-onboarding-playbook | `executive-onboarding-playbook` | 本地 skill | 来源未确认；从完整备份恢复 |
| feature-investment-advisor | `feature-investment-advisor` | 本地 skill | 来源未确认；从完整备份恢复 |
| figma-designer | `figma-designer` | 本地 skill | https://github.com/elayadesign/ai-design-skills/tree/HEAD/skills/figma-designer |
| finance-based-pricing-advisor | `finance-based-pricing-advisor` | 本地 skill | 来源未确认；从完整备份恢复 |
| finance-metrics-quickref | `finance-metrics-quickref` | 本地 skill | 来源未确认；从完整备份恢复 |
| finishing-a-development-branch | `finishing-a-development-branch` | 本地 skill | 来源未确认；从完整备份恢复 |
| fps-shooter | `fps-shooter` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/genres/fps-shooter |
| frontend-slides | `frontend-slides/plugins/frontend-slides/skills/frontend-slides` | 本地 skill | https://github.com/zarazhangrui/frontend-slides/tree/HEAD/. |
| frontend-slides | `frontend-slides` | 本地 skill | https://github.com/zarazhangrui/frontend-slides/tree/HEAD/. |
| game-ai | `game-ai` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/disciplines/game-ai |
| game-feel | `game-feel` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/disciplines/game-feel |
| game-jam | `game-jam` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/workflows/game-jam |
| game-ui-asset-pipeline | `game-ui-asset-pipeline` | 本地 skill | 来源未确认；从完整备份恢复 |
| game-ui-component-breakdown | `game-ui-component-breakdown` | 本地 skill | 来源未确认；从完整备份恢复 |
| game-ui-extension | `game-ui-extension` | 本地 skill | 来源未确认；从完整备份恢复 |
| game-ui-page-generator | `game-ui-page-generator` | 本地 skill | 来源未确认；从完整备份恢复 |
| game-ui-product-design | `game-ui-product-design` | 本地 skill | 来源未确认；从完整备份恢复 |
| game-ui-specification | `game-ui-specification` | 本地 skill | 来源未确认；从完整备份恢复 |
| game-ui-sprite-sheet-splitter | `game-ui-sprite-sheet-splitter` | 本地 skill | 来源未确认；从完整备份恢复 |
| game-ui-ux | `game-ui-ux` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/disciplines/game-ui-ux |
| game-ui-workflow | `game-ui-workflow` | 本地 skill | 来源未确认；从完整备份恢复 |
| godot-2d-movement | `godot-2d-movement` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/godot/godot-2d-movement |
| godot-3d-essentials | `godot-3d-essentials` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/godot/godot-3d-essentials |
| godot-animation | `godot-animation` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/godot/godot-animation |
| godot-audio | `godot-audio` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/godot/godot-audio |
| godot-csharp | `godot-csharp` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/godot/godot-csharp |
| godot-export | `godot-export` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/godot/godot-export |
| godot-gdscript | `godot-gdscript` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/godot/godot-gdscript |
| godot-gdscript-headless-testing | `godot-gdscript-headless-testing` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/godot/godot-gdscript-headless-testing |
| godot-multiplayer | `godot-multiplayer` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/godot/godot-multiplayer |
| godot-nodes-scenes | `godot-nodes-scenes` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/godot/godot-nodes-scenes |
| godot-physics | `godot-physics` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/godot/godot-physics |
| godot-resources | `godot-resources` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/godot/godot-resources |
| godot-shaders | `godot-shaders` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/godot/godot-shaders |
| godot-signals-groups | `godot-signals-groups` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/godot/godot-signals-groups |
| godot-tilemap | `godot-tilemap` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/godot/godot-tilemap |
| godot-ui-control | `godot-ui-control` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/godot/godot-ui-control |
| gsap-core | `gsap-core` | 本地 skill | 来源未确认；从完整备份恢复 |
| gsap-frameworks | `gsap-frameworks` | 本地 skill | 来源未确认；从完整备份恢复 |
| gsap-performance | `gsap-performance` | 本地 skill | 来源未确认；从完整备份恢复 |
| gsap-plugins | `gsap-plugins` | 本地 skill | 来源未确认；从完整备份恢复 |
| gsap-react | `gsap-react` | 本地 skill | 来源未确认；从完整备份恢复 |
| gsap-scrolltrigger | `gsap-scrolltrigger` | 本地 skill | 来源未确认；从完整备份恢复 |
| gsap-timeline | `gsap-timeline` | 本地 skill | 来源未确认；从完整备份恢复 |
| gsap-utils | `gsap-utils` | 本地 skill | 来源未确认；从完整备份恢复 |
| guizang-ppt-skill | `guizang-ppt-skill` | 本地 skill | https://github.com/op7418/guizang-ppt-skill/tree/HEAD/. |
| huashu-design | `huashu-design` | 本地 skill | https://github.com/alchaincyf/huashu-design |
| hypit | `hypit` | 本地 skill | 来源未确认；从完整备份恢复 |
| react-admin-i18n | `i18n` | 本地 skill | 来源未确认；从完整备份恢复 |
| incoming-request-advisor | `incoming-request-advisor` | 本地 skill | 来源未确认；从完整备份恢复 |
| input-systems | `input-systems` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/disciplines/input-systems |
| intel-discipline-advisor | `intel-discipline-advisor` | 本地 skill | 来源未确认；从完整备份恢复 |
| intelligence-collection-disciplines | `intelligence-collection-disciplines` | 本地 skill | 来源未确认；从完整备份恢复 |
| investigate-first | `investigate-first` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/skills/investigate-first |
| itch-publish | `itch-publish` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/workflows/itch-publish |
| jobs-to-be-done | `jobs-to-be-done` | 本地 skill | 来源未确认；从完整备份恢复 |
| landing-page-design | `landing-page-design` | 本地 skill | https://github.com/elayadesign/ai-design-skills/tree/HEAD/skills/landing-page-design |
| lean-build | `lean-build` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/skills/lean-build |
| lean-ux-canvas | `lean-ux-canvas` | 本地 skill | 来源未确认；从完整备份恢复 |
| level-design | `level-design` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/disciplines/level-design |
| lifecycle-play-advisor | `lifecycle-play-advisor` | 本地 skill | 来源未确认；从完整备份恢复 |
| love2d-core | `love2d-core` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/other-engines/love2d-core |
| market-landscape-scan | `market-landscape-scan` | 本地 skill | 来源未确认；从完整备份恢复 |
| megacave | `megacave` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/plugins/caveman/skills/megacave |
| migration | `migration` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/skills/migration |
| mineru | `mineru` | 本地 skill | 来源未确认；从完整备份恢复 |
| nature-academic-search | `nature-academic-search` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-academic-search |
| nature-citation | `nature-citation` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-citation |
| nature-data | `nature-data` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-data |
| nature-downloader | `nature-downloader` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-downloader |
| nature-experiment-log | `nature-experiment-log` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-experiment-log |
| nature-figure | `nature-figure` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-figure |
| nature-image2ppt | `nature-image2ppt` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-image2ppt |
| nature-literature-pipeline | `nature-literature-pipeline` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-literature-pipeline |
| nature-paper-card | `nature-paper-card` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-paper-card |
| nature-paper-to-patent | `nature-paper-to-patent` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-paper-to-patent |
| nature-paper-trans | `nature-paper-trans` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-paper-trans |
| nature-paper-xray | `nature-paper-xray` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-paper-xray |
| nature-paper2ppt | `nature-paper2ppt` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-paper2ppt |
| nature-paper2word | `nature-paper2word` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-paper2word |
| nature-polishing | `nature-polishing` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-polishing |
| researchwrite | `nature-proposal-writer` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-proposal-writer |
| nature-reader | `nature-reader` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-reader |
| nature-ref-verifier | `nature-ref-verifier` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-ref-verifier |
| nature-response | `nature-response` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-response |
| nature-reviewer | `nature-reviewer` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-reviewer |
| nature-shared | `nature-shared` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-shared |
| nature-social-science | `nature-social-science` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-social-science |
| nature-statistics | `nature-statistics` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-statistics |
| nature-writing | `nature-writing` | 本地 skill | https://github.com/Yuan1z0825/nature-skills/tree/HEAD/skills/nature-writing |
| openspec-apply-change | `openspec-apply-change` | 本地 skill | 来源未确认；从完整备份恢复 |
| openspec-archive-change | `openspec-archive-change` | 本地 skill | 来源未确认；从完整备份恢复 |
| openspec-bulk-archive-change | `openspec-bulk-archive-change` | 本地 skill | 来源未确认；从完整备份恢复 |
| openspec-continue-change | `openspec-continue-change` | 本地 skill | 来源未确认；从完整备份恢复 |
| openspec-explore | `openspec-explore` | 本地 skill | 来源未确认；从完整备份恢复 |
| openspec-ff-change | `openspec-ff-change` | 本地 skill | 来源未确认；从完整备份恢复 |
| openspec-new-change | `openspec-new-change` | 本地 skill | 来源未确认；从完整备份恢复 |
| openspec-onboard | `openspec-onboard` | 本地 skill | 来源未确认；从完整备份恢复 |
| openspec-propose | `openspec-propose` | 本地 skill | 来源未确认；从完整备份恢复 |
| openspec-sync-specs | `openspec-sync-specs` | 本地 skill | 来源未确认；从完整备份恢复 |
| openspec-update-change | `openspec-update-change` | 本地 skill | 来源未确认；从完整备份恢复 |
| openspec-verify-change | `openspec-verify-change` | 本地 skill | 来源未确认；从完整备份恢复 |
| opportunity-solution-tree | `opportunity-solution-tree` | 本地 skill | 来源未确认；从完整备份恢复 |
| organic-growth-advisor | `organic-growth-advisor` | 本地 skill | 来源未确认；从完整备份恢复 |
| performance-optimization | `performance-optimization` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/disciplines/performance-optimization |
| pestel-analysis | `pestel-analysis` | 本地 skill | 来源未确认；从完整备份恢复 |
| pestel-delta-monitor | `pestel-delta-monitor` | 本地 skill | 来源未确认；从完整备份恢复 |
| phaser-arcade-physics | `phaser-arcade-physics` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/web-engines/phaser-arcade-physics |
| phaser-core | `phaser-core` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/web-engines/phaser-core |
| physics-tuning | `physics-tuning` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/disciplines/physics-tuning |
| pixijs-rendering | `pixijs-rendering` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/web-engines/pixijs-rendering |
| platformer | `platformer` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/genres/platformer |
| playwright-audit-deps | `playwright-audit-deps` | 本地 skill | 来源未确认；从完整备份恢复 |
| playwright-cherry-pick | `playwright-cherry-pick` | 本地 skill | 来源未确认；从完整备份恢复 |
| playwright-cli | `playwright-cli` | 本地 skill | 来源未确认；从完整备份恢复 |
| playwright-component-testing | `playwright-component-testing` | 本地 skill | 来源未确认；从完整备份恢复 |
| playwright-dev | `playwright-dev` | 本地 skill | 来源未确认；从完整备份恢复 |
| playwright-devops | `playwright-devops` | 本地 skill | 来源未确认；从完整备份恢复 |
| playwright-release-notes | `playwright-release-notes` | 本地 skill | 来源未确认；从完整备份恢复 |
| playwright-test-results | `playwright-test-results` | 本地 skill | 来源未确认；从完整备份恢复 |
| playwright-trace | `playwright-trace` | 本地 skill | 来源未确认；从完整备份恢复 |
| playwright-triage | `playwright-triage` | 本地 skill | 来源未确认；从完整备份恢复 |
| pm-skill-creator | `pm-skill-creator` | 本地 skill | 来源未确认；从完整备份恢复 |
| pol-probe | `pol-probe` | 本地 skill | 来源未确认；从完整备份恢复 |
| pol-probe-advisor | `pol-probe-advisor` | 本地 skill | 来源未确认；从完整备份恢复 |
| porters-five-forces | `porters-five-forces` | 本地 skill | 来源未确认；从完整备份恢复 |
| positioning-statement | `positioning-statement` | 本地 skill | 来源未确认；从完整备份恢复 |
| positioning-workshop | `positioning-workshop` | 本地 skill | 来源未确认；从完整备份恢复 |
| ppt-master | `ppt-master` | 本地 skill | https://github.com/hugohe3/ppt-master/tree/HEAD/skills/ppt-master |
| prd-development | `prd-development` | 本地 skill | 来源未确认；从完整备份恢复 |
| press-release | `press-release` | 本地 skill | 来源未确认；从完整备份恢复 |
| pricing-packaging-tracker | `pricing-packaging-tracker` | 本地 skill | 来源未确认；从完整备份恢复 |
| prioritization-advisor | `prioritization-advisor` | 本地 skill | 来源未确认；从完整备份恢复 |
| problem-framing-canvas | `problem-framing-canvas` | 本地 skill | 来源未确认；从完整备份恢复 |
| problem-statement | `problem-statement` | 本地 skill | 来源未确认；从完整备份恢复 |
| procedural-gen | `procedural-gen` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/disciplines/procedural-gen |
| product-lifecycle-plays | `product-lifecycle-plays` | 本地 skill | 来源未确认；从完整备份恢复 |
| product-sense-interview-answer | `product-sense-interview-answer` | 本地 skill | 来源未确认；从完整备份恢复 |
| product-strategy-session | `product-strategy-session` | 本地 skill | 来源未确认；从完整备份恢复 |
| proto-persona | `proto-persona` | 本地 skill | 来源未确认；从完整备份恢复 |
| prototype-fast | `prototype-fast` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/workflows/prototype-fast |
| puzzle | `puzzle` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/genres/puzzle |
| pydantic | `pydantic` | 本地 skill | 来源未确认；从完整备份恢复 |
| pygame-core | `pygame-core` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/other-engines/pygame-core |
| react-admin | `react-admin` | 本地 skill | 来源未确认；从完整备份恢复 |
| receiving-code-review | `receiving-code-review` | 本地 skill | 来源未确认；从完整备份恢复 |
| recommendation-canvas | `recommendation-canvas` | 本地 skill | 来源未确认；从完整备份恢复 |
| release-openspec | `release-openspec` | 本地 skill | 来源未确认；从完整备份恢复 |
| requesting-code-review | `requesting-code-review` | 本地 skill | 来源未确认；从完整备份恢复 |
| roadmap-planning | `roadmap-planning` | 本地 skill | 来源未确认；从完整备份恢复 |
| roblox-characters | `roblox-characters` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/other-engines/roblox-characters |
| roblox-datastores | `roblox-datastores` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/other-engines/roblox-datastores |
| roblox-luau | `roblox-luau` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/other-engines/roblox-luau |
| roblox-networking | `roblox-networking` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/other-engines/roblox-networking |
| roblox-physics | `roblox-physics` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/other-engines/roblox-physics |
| roblox-simulator-economy | `roblox-simulator-economy` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/other-engines/roblox-simulator-economy |
| roblox-studio-workflow | `roblox-studio-workflow` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/other-engines/roblox-studio-workflow |
| roblox-ui | `roblox-ui` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/other-engines/roblox-ui |
| roguelike | `roguelike` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/genres/roguelike |
| router | `router` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/router |
| rpg | `rpg` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/genres/rpg |
| saas-economics-efficiency-metrics | `saas-economics-efficiency-metrics` | 本地 skill | 来源未确认；从完整备份恢复 |
| saas-revenue-growth-metrics | `saas-revenue-growth-metrics` | 本地 skill | 来源未确认；从完整备份恢复 |
| safe-refactor | `safe-refactor` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/skills/safe-refactor |
| save-systems | `save-systems` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/disciplines/save-systems |
| shader-programming | `shader-programming` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/disciplines/shader-programming |
| skill-authoring-workflow | `skill-authoring-workflow` | 本地 skill | 来源未确认；从完整备份恢复 |
| stakeholder-engagement-advisor | `stakeholder-engagement-advisor` | 本地 skill | 来源未确认；从完整备份恢复 |
| stakeholder-identification | `stakeholder-identification` | 本地 skill | 来源未确认；从完整备份恢复 |
| stakeholder-mapping | `stakeholder-mapping` | 本地 skill | 来源未确认；从完整备份恢复 |
| steam-publish | `steam-publish` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/workflows/steam-publish |
| storyboard | `storyboard` | 本地 skill | 来源未确认；从完整备份恢复 |
| subagent-driven-development | `subagent-driven-development` | 本地 skill | 来源未确认；从完整备份恢复 |
| surgical-patch | `surgical-patch` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/skills/surgical-patch |
| survival-crafting | `survival-crafting` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/genres/survival-crafting |
| swot-analysis | `swot-analysis` | 本地 skill | 来源未确认；从完整备份恢复 |
| systematic-debugging | `systematic-debugging` | 本地 skill | 来源未确认；从完整备份恢复 |
| tam-sam-som-calculator | `tam-sam-som-calculator` | 本地 skill | 来源未确认；从完整备份恢复 |
| design-taste-frontend | `taste-skill` | 本地 skill | https://github.com/Leonxlnx/taste-skill/tree/HEAD/skills/taste-skill |
| test-driven-development | `test-driven-development` | 本地 skill | 来源未确认；从完整备份恢复 |
| threejs-gltf-loading | `threejs-gltf-loading` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/web-engines/threejs-gltf-loading |
| threejs-materials-lighting | `threejs-materials-lighting` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/web-engines/threejs-materials-lighting |
| threejs-scene-setup | `threejs-scene-setup` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/web-engines/threejs-scene-setup |
| tower-defense | `tower-defense` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/genres/tower-defense |
| ui-ux-pro-max | `ui-ux-pro-max` | 本地 skill | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/HEAD/.claude/skills/ui-ux-pro-max |
| ultracave | `ultracave` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/plugins/caveman/skills/ultracave |
| unity-animation | `unity-animation` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/unity/unity-animation |
| unity-build-pipeline | `unity-build-pipeline` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/unity/unity-build-pipeline |
| unity-csharp-scripting | `unity-csharp-scripting` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/unity/unity-csharp-scripting |
| unity-input-system | `unity-input-system` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/unity/unity-input-system |
| unity-navmesh | `unity-navmesh` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/unity/unity-navmesh |
| unity-physics | `unity-physics` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/unity/unity-physics |
| unity-scriptableobjects | `unity-scriptableobjects` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/unity/unity-scriptableobjects |
| unity-tilemap-2d | `unity-tilemap-2d` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/unity/unity-tilemap-2d |
| unreal-behavior-trees | `unreal-behavior-trees` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/unreal/unreal-behavior-trees |
| unreal-blueprints | `unreal-blueprints` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/unreal/unreal-blueprints |
| unreal-cpp-gameplay | `unreal-cpp-gameplay` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/unreal/unreal-cpp-gameplay |
| unreal-enhanced-input | `unreal-enhanced-input` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/unreal/unreal-enhanced-input |
| unreal-niagara | `unreal-niagara` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/unreal/unreal-niagara |
| unreal-packaging | `unreal-packaging` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/unreal/unreal-packaging |
| user-story | `user-story` | 本地 skill | 来源未确认；从完整备份恢复 |
| user-story-mapping | `user-story-mapping` | 本地 skill | 来源未确认；从完整备份恢复 |
| user-story-mapping-workshop | `user-story-mapping-workshop` | 本地 skill | 来源未确认；从完整备份恢复 |
| user-story-splitting | `user-story-splitting` | 本地 skill | 来源未确认；从完整备份恢复 |
| using-git-worktrees | `using-git-worktrees` | 本地 skill | 来源未确认；从完整备份恢复 |
| using-superpowers | `using-superpowers` | 本地 skill | 来源未确认；从完整备份恢复 |
| verification-before-completion | `verification-before-completion` | 本地 skill | 来源未确认；从完整备份恢复 |
| verify-and-stop | `verify-and-stop` | 本地 skill | https://github.com/JuliusBrussee/caveman/tree/HEAD/skills/verify-and-stop |
| verify-openspec-docs | `verify-openspec-docs` | 本地 skill | 来源未确认；从完整备份恢复 |
| visual-novel | `visual-novel` | 本地 skill | https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/HEAD/skills/genres/visual-novel |
| voice-of-customer-miner | `voice-of-customer-miner` | 本地 skill | 来源未确认；从完整备份恢复 |
| vp-cpo-readiness-advisor | `vp-cpo-readiness-advisor` | 本地 skill | 来源未确认；从完整备份恢复 |
| workshop-facilitation | `workshop-facilitation` | 本地 skill | 来源未确认；从完整备份恢复 |
| write-openspec-docs | `write-openspec-docs` | 本地 skill | 来源未确认；从完整备份恢复 |
| writing-plans | `writing-plans` | 本地 skill | 来源未确认；从完整备份恢复 |
| writing-skills | `writing-skills` | 本地 skill | 来源未确认；从完整备份恢复 |

## 插件版本缓存记录

缓存存在不证明插件当前已启用或账号已授权。

| 插件 | ID | 市场 | 缓存版本 | 官网/元数据链接 |
| --- | --- | --- | --- | --- |
| Browser | browser | openai-bundled | 26.1103.32239 | https://github.com/openai/openai/tree/master/lib/oai_browser_use/plugin |
| codex-app-tools | codex-app-tools | openai-bundled | 26.1103.32239 |  |
| Computer Use | computer-use | openai-bundled | 26.1103.32239 | https://github.com/openai/openai/tree/master/project/cua/sky_js/plugin |
| unified-computer-use | unified-computer-use | openai-bundled | 26.1103.32239 |  |
| Visualize | visualize | openai-bundled | 1.0.84 | https://openai.com/ |
| Adobe | app-69312da8e4dc81919370cb86fd172b6c | openai-curated-remote | 10.0.0 | https://www.adobe.com |
| Lovart | app-6aad62677cd481918e0f05dd0e13863c | openai-curated-remote | 1.0.5 | https://www.lovart.ai |
| Canva | canva | openai-curated-remote | 17.0.1 | https://www.canva.com |
| Cloud Environment | cloud-environment | openai-curated-remote | 0.2.0 |  |
| Figma | figma | openai-curated-remote | 18.0.0 | https://www.figma.com |
| GitHub | github | openai-curated-remote | 0.1.13-77c10e110b37 | https://github.com/ |
| Gmail | gmail | openai-curated-remote | 0.1.10 | https://workspace.google.com/products/gmail/ |
| Google Calendar | google-calendar | openai-curated-remote | 1.2.7 | https://workspace.google.com/products/calendar/ |
| Google Contacts | google-contacts | openai-curated-remote | 1.0.0 | https://contacts.google.com |
| Google Drive | google-drive | openai-curated-remote | 0.1.23 | https://workspace.google.com/products/drive/ |
| Default templates | openai-templates | openai-curated-remote | 0.1.1 | https://github.com/openai/oai-maintained-plugins/tree/main/plugins/openai-templates |
| Plugin Management | plugin-management | openai-curated-remote | 0.1.0 | https://openai.com/ |
| Sites | sites | openai-curated-remote | 1.1.6 | https://openai.com/ |
| Visualize | visualize | openai-curated-remote | 1.0.89 | https://openai.com/ |
| Pets | work-pets | openai-curated-remote | 0.1.6 | https://openai.com/ |
| Documents | documents | openai-primary-runtime | 26.1111.10930 | https://openai.com/ |
| PDF | pdf | openai-primary-runtime | 26.1111.10930 | https://openai.com/ |
| Presentations | presentations | openai-primary-runtime | 26.1111.10930 | https://openai.com/ |
| Spreadsheets | spreadsheets | openai-primary-runtime | 26.1111.10930 | https://openai.com/ |
| Template Creator | template-creator | openai-primary-runtime | 26.1111.10930 | https://openai.com/ |

不公开保存账号凭据、原始私人配置、聊天记录或 OAuth token。完整备份未做 Mac 真机功能验证。
