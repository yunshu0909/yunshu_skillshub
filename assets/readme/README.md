# README 视觉资产

- [`hero.png`](./hero.png)：1916 × 821 头图，中英文 README 共用。一座漂浮小岛，七间小屋对应七个场景；狗子是云舒，两个小机器人是 AI 搭子。
- [`scenes/`](./scenes/)：七个场景各一张 21:9 场景图，是头图里各间小屋的室内特写；`about.jpg` 配「这是什么」一节，讲“做完一件事 → 写下怎么做的 → 下次照着做”。
- [`hero.svg`](./hero.svg)：引用同目录 PNG 的 SVG 包装，保留原有入口。
- [`yunshu-ip.jpg`](./yunshu-ip.jpg)：蓝帽狗子的参考图，出图时用来垫图。
- [`source/readme-20261006/`](./source/readme-20261006/scenes.md)：画面单、逐张适配稿、实际提示词和逐字核对报告。

风格是 `image-render` 的 N42 等距像素，调用 Codex 内置图像生成。图上只写场景名和一句话，skill 数量与版本放在正文维护。

- [`wechat-qr.jpg`](./wechat-qr.jpg)：用户提供的微信二维码，原图直接改名并移动，中英文 README 共用。

## 更新顺序

1. 更新 skill 与分类，核对数量。
2. 更新中英文 README 的场景表格和安装说明。
3. 更新 CHANGELOG 的 Unreleased；正式发布时再填写 Tag / Release。
4. 场景名、顺序或品牌表达变了才重画图：改 `source/` 里的适配稿，重新出图并核对图上的字。
