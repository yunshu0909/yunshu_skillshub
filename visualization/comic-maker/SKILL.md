---
name: comic-maker
description: 教程漫画「小课堂」：你的 IP 当老师（没有就先生成一个），3:4 竖版，一期默认 6–9 页（用户要几页就几页），固定有「开课」封面和「下课」结尾，交给 Codex 内置 imagegen 出图并核对。当用户说"画漫画"、"做一套漫画讲XXX"、"用漫画解释"、"小课堂"、"换个老师 / 换角色"时触发。
metadata:
  status: active
  status_updated_at: "2026-10-11"
---

# 漫画小课堂（comic-maker）

一个固定的老师角色，用一期漫画讲清一个概念。当前助手（Claude 或 Codex）写故事和每页提示词、交付前逐页看图；出图交给 Codex 内置 imagegen 原样执行；脚本负责检查和核对。

下文 `S` 指本 skill 的脚本目录：

```bash
S=<本 SKILL.md 所在目录>/scripts
```

## 默认配置

```
风格：小课堂（styles/classroom.md）；画风跟着角色参考图走
比例：3:4（提示词第二句写 A vertical 3:4 manga comic page…，见「提示词铁律」；实测 1086×1448）
主角：默认角色（~/.comic-maker/characters/<角色ID>/，settings.py 管理）；讲 AI 时配角用 AI Helper 小机器人
每期：封面「开课」+ 正文 4–7 页 + 结尾「下课」
出图：Codex 内置 imagegen（scripts/render_codex.py），默认用你 Codex 自己配置的模型
```

## 第 0 步：角色（每次开工先看）

`python3 $S/settings.py get default`（打印出角色档 JSON = 有默认角色；报「没有默认角色」= 还没有）：

- **有默认角色**：告诉用户「本期老师是 X（系列名），要换说一声」，直接往下做。
- **没有**（第一次用）：先跑 `python3 $S/doctor.py` 自检，再按 `templates/character.md` 准备角色——
  - 有自己的 IP：给一张图 + 名字，写角色档（字段表在 `templates/character.md`），给用户确认后保存。
  - 没有：问三件事（画什么、配饰、画风，默认彩铅水彩）→ 出 3–4 个候选 → 用户挑 → 保存。
- **「这期用团团」**：`settings.py get <角色ID>` 读那个角色，只这期用；**「以后都用团团」**：`settings.py use <角色ID>`。

## 启动：先定协作模式

- **快速模式**（用户说「直接做」「你定」「随便选个主题」）：不逐项问，直接给故事线表格 + 每页布局，一次展示后出图；只在出图后请用户看。
- **确认模式**（默认）：在这几处停下来等用户：① 新建角色时，角色档（名字、外貌、系列名）；② 故事线和布局；③ 第一次用 / 刚换角色时的封面试图。其余不打断。

## 工作流程

### 步骤 1：物料理解

- 用户给了文章 / 文件：先读完，提炼核心定义和 3–5 个关键点；数字、事实只用原文的。
- 只给了主题：基于常识讲，事实拿不准的不写进对白。
- 原文里的真人（作者朋友、名人）不画成角色；产品名可以写成字，但不要画品牌标志。

### 步骤 2：故事线 + 布局（用户拍板一次）

1. 按 `templates/story-structure.md` 选结构（问题-方案 / 教程 / 故事），默认 6–9 页（用户指定页数就照用户的，3–5 页用「压缩版」），**第一页固定封面「开课」、最后一页固定结尾「下课」**（见 `styles/classroom.md`「系列固定页」）。
2. 每页按 `templates/layout-patterns.md` 选布局，ASCII 示意。
3. 每格写：画面（谁在做什么、具体道具）、对话气泡、旁白 / 标注。
4. 原则：每格是一个**场景**不是信息点；有连贯故事线（问题 → 解决 → 结果）；元素丰富；字不多不少（每页 2–5 处指定文字）。

### 步骤 3：写提示词

- 按 `templates/prompt-template.md` 写，每页一个文件：`<任务目录>/prompts/00.txt、01.txt …`（00 = 封面）。角色英文名、外貌、系列名从角色档原样填入；`<hand>` 按角色换成 paw / hand / wing；**不讲 AI 的主题删掉 AI 小机器人那一行**。
- 好例子：`examples/mcp/`（MCP 一期 8 页，示例角色橘子，3 张缩略图），写新一期前先看一份。
- 每份写完对照模板末尾的自检表。

### 步骤 4：出图 + 核对

```bash
python3 $S/render_codex.py <任务目录> --check                       # 只检查提示词（出图前也会自动查）
python3 $S/render_codex.py <任务目录> --only 00 --title "系列名 · 主题"  # 第一次用 / 刚换角色：先出封面看角色像不像（确认模式等用户说像再继续；快速模式自己看像就继续）
python3 $S/render_codex.py <任务目录> --title "系列名 · 主题"          # 出 prompts/ 里还没出的页
```

- 参考图：默认角色的 `ref.png`；任务目录放 `ref.png` 或 `--ref` 可临时换。都没有会报错，提示先准备角色。
- 自动检查（有错误直接停，退出码 2）：第一句、Follow the exact same…、All Chinese text clearly readable 是否都在；有没有 URL；有没有指定配色；英文双引号是否成对。
- 出图：每 3 页一个 Codex 进程，3 个同时跑，9 页约 4–6 分钟；满载或失败的页下一轮自动重跑。
- 改了某页提示词，直接重跑：脚本发现提示词变了，会把旧图移到 `_v1/` 再重出。
- `--only` 按文件名开头匹配：`--only 00` 只出封面，`--only 0` 出 00–09。
- 产物：`review.html`（按第 1…N 页排，可点 ♡ 复制回来）、`发布/01.png…`（按顺序，直接拖进小红书）。

**交付前逐页看（必须做，当前助手自己看图）**：脚本报的「提示词逐字」只说明 imagegen 收到的提示词没被改写，**不代表图上的字画对了**。

- 指定文字有没有错字；角色像不像；有没有品牌标志。
- 模型自己加的小字（黑板、便签、书脊）有没有**说过头或和原文矛盾**的。生活化标语可以留；说错事实的要提给用户。
- 汇报时分两项：提示词逐字 N/N；图上文字看过、问题逐条列出。

### Codex 自己跑本 skill 时

不要调用 `render_codex.py` 出图（它会再起一个 Codex）。按步骤 1–3 写好 `prompts/`，跑 `render_codex.py <任务目录> --check`，然后对每个文件调用内置 imagegen：prompt = 文件全文原样，`referenced_image_paths` = 默认角色 `ref.png` 的绝对路径（`settings.py get default` 里的 `ref`），不传 `num_last_images_to_include`；保存为 `out/<同名>.png`；出图前记下开始时间，最后跑 `render_codex.py <任务目录> --page-only --since "YYYY-MM-DD HH:MM"` 核对并生成对比页和发布文件夹。

### 步骤 5：迭代

- 用户满意的页先把提示词复制到 `baselines/`，再改。
- **一次只改一处**（加一句或改一句），其他原样不动。
- 不要整段重写提示词。

## 提示词铁律

1. 第一句：`Use the same style and character design as the reference image.`；第二句写 `A vertical 3:4 manga comic page with N panels. Follow the exact same art style, color palette, character design, and border style as the reference image.`
2. **绝不指定颜色**（配色交给参考图）。
3. 每格写位置和占比、具体画面元素、对话和旁白（中文放英文双引号里）。
4. 结尾段：`Rich visual details: …` + `No brand logos anywhere.` + `All Chinese text clearly readable.` + 情绪氛围。想要干净（不让模型加小字）再加 `No other words besides the quoted text.`
5. 提示词里**不写 URL**，参考图走 `referenced_image_paths`；不传 `num_last_images_to_include`（只能 1–5，传 0 报错）。

## 相关文件

- 风格：`styles/classroom.md`
- 角色：`templates/character.md`（导入 IP / 生成候选）；数据在 `~/.comic-maker/`，升级 skill 不会覆盖；家目录写不进时（Codex 沙盒）自动存到当前项目的 `.comic-maker/`；也可以用环境变量 `COMIC_MAKER_HOME` 指定
- 模板：`templates/story-structure.md`、`templates/layout-patterns.md`、`templates/prompt-template.md`
- 例子：`examples/mcp/`（8 份提示词 + 3 张缩略图）、`examples/character/`（示例角色橘子和它的生成提示词）
- 脚本：`scripts/doctor.py` 自检、`scripts/settings.py` 角色、`scripts/render_codex.py` 出图、`scripts/mark.js`
