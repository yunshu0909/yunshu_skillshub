# 场景讲解 PPT（scene-ppt）

把一篇文章放进一个「世界」里讲完（小课堂、后厨、RPG、像素小岛、复古广告…），一页一张 16:9 图。自带出图脚本，单独装就能用。

## 需要什么

- [Claude Code](https://claude.com/claude-code) 或 [Codex CLI](https://github.com/openai/codex)（Claude 负责设计画面，出图交给 Codex）
- Codex CLI 已登录，账号能用 Codex 的内置图像生成（imagegen）
- Python 3.8+；Pillow 可选（`pip3 install pillow`）

## 安装

把整个 `scene-ppt` 文件夹放进 skill 目录：

- Claude Code：`~/.claude/skills/scene-ppt/`
- Codex：`~/.agents/skills/scene-ppt/`

装完跑一次自检：`python3 ~/.claude/skills/scene-ppt/scripts/doctor.py`

## 第一次用

对 Claude 说「把这篇文章做成 PPT」。没有默认世界时会先打开世界选择页（11 个世界，都有样张），挑一个存成默认。选「小课堂」要用你的角色（可以从漫画小课堂导入）。之后每次直接用默认世界，想换说「换默认世界」或「这次用 RPG」。第一次用先出封面和一页内容给你看。

## 产出

一页一张 PNG，按页序排好的 `发布/01.png…` + 对比页 `review.html`。是图片，不是可编辑的 .pptx。

## 你的数据存在哪

`~/.scene-ppt/`（默认设置、角色等），不在 skill 文件夹里，升级 skill 不会被覆盖。在 Codex 里用、家目录写不进时，会自动存到当前项目的 `.scene-ppt/`（有旧设置会先复制过来）。想换位置就设环境变量（见 `scripts/settings.py`）。
