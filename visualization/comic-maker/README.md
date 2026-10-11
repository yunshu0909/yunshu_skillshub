# 漫画小课堂（comic-maker）

你的 IP 当老师，用一期 3:4 竖版漫画（6–9 页，固定「开课」封面和「下课」结尾）讲清一个概念。适合小红书。

## 需要什么

- [Claude Code](https://claude.com/claude-code) 或 [Codex CLI](https://github.com/openai/codex)（Claude 负责设计画面，出图交给 Codex）
- Codex CLI 已登录，账号能用 Codex 的内置图像生成（imagegen）
- Python 3.8+；Pillow 可选（`pip3 install pillow`）

## 安装

把整个 `comic-maker` 文件夹放进 skill 目录：

- Claude Code：`~/.claude/skills/comic-maker/`
- Codex：`~/.agents/skills/comic-maker/`

装完跑一次自检：`python3 ~/.claude/skills/comic-maker/scripts/doctor.py`

## 第一次用

对 Claude 说「画一期漫画讲 XX」。没有角色时先准备：有自己的 IP 就给一张图和名字；没有就回答三个问题（画什么、配饰、画风），从 3–4 个候选形象里挑一个。角色存成默认，之后每期直接用。漫画的画风跟着角色图走。第一次用会先出封面看角色像不像。

## 产出

按页序排好的 `发布/01.png…`（直接拖进小红书）+ 对比页 `review.html`。

## 你的数据存在哪

`~/.comic-maker/`（默认设置、角色等），不在 skill 文件夹里，升级 skill 不会被覆盖。在 Codex 里用、家目录写不进时，会自动存到当前项目的 `.comic-maker/`（有旧设置会先复制过来）。想换位置就设环境变量（见 `scripts/settings.py`）。
