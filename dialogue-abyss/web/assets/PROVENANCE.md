# 设计资产来源与复用

- art/ocean-keyart.png：2026-11-07 通过本会话内置图像生成工具生成的原创新主视觉；无参考图片输入。用于启动界面，不作为实时游戏截图。模型版本由工具管理，未指定或声称使用某个 image2.0 版本。
- concepts/worlds.png、diver-turnaround.png、creatures-turnaround.png：沿用此前已交付的项目概念图。用于世界与角色风格参考，不是精确的工程建模尺寸图。
- models/*.gltf：从本项目 Three.js 程序几何导出，包含当前简化的真实几何与材质；未使用商业游戏模型。
- ui/*.svg：本轮编写的标记、菜单、罗盘和相机矢量图形。
- audio：见 audio/PROVENANCE.md；原创程序合成，非商业游戏原曲。
- vendor/three.min.js：Third-party Three.js，遵循同目录 LICENSE-three.txt。
- 其余界面使用操作系统字体，没有打包商业字体。

## 新主视觉提示词存档（创作要点）
Original stylized 3D underwater adventure game key art, matte sculpted shapes, soft painterly gradients, atmospheric volumetric underwater sun rays. Original small diver explorer: cream round helmet with dark oval face window and two warm eyes, teal suit, orange buoyancy vest. Mint manta companion, lilac jellyfish, small gold seahorse and peach octopus. Broad coral forms and ancient rounded stone arches in a welcoming ocean. Teal, ivory, lilac, peach and honey light. Diver on the right, quiet dark teal negative space on left 40% for UI. No text, no logos, no photorealism. Wide landscape composition.

## 改用建议
启动图可替换为同类横幅；模型与图像应分别管理版本。人物关节姿势、NPC 行为和碰撞仍需要代码或引擎动画连接；替换图片不会自动改变 3D 角色。





## v0.6 模型修订
2026-11-12：七种动物由 sculpted-models.js 原创生成，潜水员新增装备细节；所有 models/*.gltf 已重新导出。模型使用层级关节，尚不含蒙皮骨骼动画、LOD或完整精修UV。模型工作室使用本地实时三点布光，不是离线渲染短片。
