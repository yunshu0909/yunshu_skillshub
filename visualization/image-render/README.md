# 配图出图（image-render）

给文章配图：定好每张图讲什么、图上逐字写什么，用你的默认风格设计画面，交给 Codex 原样出图，图上的中文逐字核对。风格库 28 种，每种都有样张。

## 需要什么

- [Claude Code](https://claude.com/claude-code) 或 [Codex CLI](https://github.com/openai/codex)（Claude 负责设计画面，出图交给 Codex）
- Codex CLI 已登录，账号能用 Codex 的内置图像生成（imagegen）
- Python 3.8+；Pillow 可选（`pip3 install pillow`）

## 安装

把整个 `image-render` 文件夹放进 skill 目录：

- Claude Code：`~/.claude/skills/image-render/`
- Codex：`~/.agents/skills/image-render/`

装完跑一次自检：`python3 ~/.claude/skills/image-render/scripts/doctor.py`

## 第一次用

对 Claude 说「给这篇文章配图」。没有默认风格时会先打开风格选择页，你看样张挑一种存成默认，之后每次直接用。想换说「换默认风格」，只这次换说「这次用 N42」，想比一比说「给我几个风格看看」，想要库里没有的风格说「加个新风格」。第一次用会先出 1 张给你看，满意再出整套。

## 产出

每张一个 PNG（`out/`）+ 可以点 ♡ 标记喜欢的对比页 `review.html`。

## 你的数据存在哪

`~/.image-render/`（默认设置、角色等），不在 skill 文件夹里，升级 skill 不会被覆盖。在 Codex 里用、家目录写不进时，会自动存到当前项目的 `.image-render/`（有旧设置会先复制过来）。想换位置就设环境变量（见 `scripts/settings.py`）。
