---
name: image-render
description: 配图出图 - 给文章配图：定好每张图讲什么、图上逐字写什么，用你的默认风格（第一次从带样张的风格库里看图选）为每张图设计画面，交给 Codex 内置 imagegen 原样出图，生成可标记喜欢的对比页。支持探索（一张图试几种风格）、量产（默认风格出整套）和新增自己的风格。当用户说「给这篇文章配图」「出几张图」「用 XX 风格出图」「换默认风格」「加个新风格」时触发。
metadata:
  status: active
  status_updated_at: "2026-10-11"
---

# 配图出图（image-render）

把文章变成一套风格统一的配图。Claude 负责想清楚画什么、图上写哪些字；Codex 只负责把提示词原样交给 imagegen 出图；脚本负责检查和核对。

下文 `S` 指本 skill 的脚本目录（本文件所在目录下的 `scripts/`）：

```bash
S=<本 SKILL.md 所在目录>/scripts
```

## 第一次用

1. `python3 $S/doctor.py`：环境自检（Codex 装没装、登没登录、Python）。有 ✗ 先按提示补。
2. 没有默认风格时，开风格选择页让用户看图选（见下面「默认风格」）。

## 默认风格

风格 = 有样张的风格，用户看图选。选一次存成默认，之后每次直接用，不再每次问。

| 用户说 | 怎么做 |
|---|---|
| （开工时） | `python3 $S/settings.py get style`。打印出编号 → 告诉用户「本次用默认风格 X（编号 · 名字），要换说一声」，直接往下做。**什么都没打印 = 还没设**，走「第一次选」 |
| 第一次选 / 「换默认风格」 | 先把画面单给用户确认，再 `python3 $S/style_picker.py <任务目录>/风格选择.html` 并打开；用户报编号（或贴回 ♡ 复制的内容）就视为选定默认 → `python3 $S/settings.py set style <编号>` |
| 「这次用 N42」 | 只这一次用，**不改设置**：adapt 文件名里写这个编号（如 `1-N42.txt`）。**真正决定用哪张风格卡的是文件名里的编号**；`scenes.md` 顶部写一行「本次风格：N42」只是备忘 |
| 「给我几个风格看看」 | 探索：选 3–4 种（`reference/recommend.md` 按内容类型推荐），用用户自己的同一张图各出一版对比；用户选中的可以设成新默认 |
| 「你推荐」 | 才参考 `reference/recommend.md` 和 `reference/taste.md`（作者口味） |

设置存在 `~/.image-render/settings.json`，升级 skill 不会被覆盖；家目录写不进时（Codex 沙盒）自动存到当前项目的 `.image-render/`，以后在这个项目里用会自动读到；也可以用环境变量 `IMAGE_RENDER_HOME` 指定。

## 流程

| 步 | 做什么 | 谁 | 详细 |
|---|---|---|---|
| 1 画面单 | 每张图：画幅 / 用途、讲什么、内容类型、必含文字（「」包住）。写完给用户确认（用户说「直接做」可跳过） | Claude → 用户 | `stages/01-scenes.md` |
| 2 定风格 | 默认风格；没有就看图选；探索时选 3–4 种 | 用户 | `stages/02-pick-style.md` |
| 3 风格适配 | **核心**：按风格卡的叙事语法为每张图重新设计场景、比喻、文字载体 | Claude | `stages/03-adapt.md` |
| 4 出图 | 检查 → 拼提示词 → Codex 原样出图 → 核对提示词逐字。**第一次用或刚换默认风格：先只出第 1 张给用户看，满意再出剩下的** | 脚本 + Codex | `stages/04-render.md` |
| 5 挑图与迭代 | Claude 先逐张看图上的字；对比页给用户标 ♡；不满意一次只改一处；选中的图写回样张 | Claude → 用户 | `stages/05-review.md` |

## 新增风格

用户想要库里没有的风格（给一句描述或一张参考图）：

1. 找到自建风格目录（`python3 $S/settings.py show` 第二行，一般是 `~/.image-render/styles/`；第一次加风格时可能还不存在，先 `mkdir -p`），复制 `templates/style-card.md` 进去，命名为 `U01-<风格名>.md`（编号 `U01`、`U02`… 接着排，文件名 = 编号-名字），填好。风格块只写「长什么样」——材质、线条、配色、文字长相、不要什么，**不写版式**。
2. 用用户手头的一张图按新卡出一张试图（adapt 文件名写 `1-U01.txt`）。
3. **用户说喜欢** → `python3 $S/add_sample.py U01 <试图路径>`（要设成默认就加 `--default`）。这一条命令会缩略图片、放进样张目录、写进卡片。**有样张才算进库**，风格选择页才会显示它。
4. 用户不喜欢：在风格块里只改一处再出一版；放弃就删掉这张卡，不留空卡。

## 关键原则（都有实测证据，见 `reference/lessons.md`）

1. **风格卡固定，画面每张定制。** 机械套同一个画面换风格，一张都没被选中。
2. **风格块逐字粘贴**，不改写；版式写进画面，不写进风格块。
3. **「」只留给要画出来的字。** 出图前必须过 `check_prompts.py`。
4. **提示词落盘、原样传入、事后核对**：Codex 只执行，不改写。
5. **画幅只靠第一句**：只写实测过的（21:9 / 16:9 / 2:1 / 1:1 / 3:4 / 9:16）。
6. **写明主体占画面多大**（「约六成宽」），否则画面很空。
7. 现编角色写细就能跨图一致；**真实角色（你的宠物、IP）必须垫图**（`--ref`）。
8. **脚本只核对 imagegen 收到的提示词，不检查图上画出的字。** 交付前当前助手（Claude 或 Codex）必须逐张看图，错字、多字要说出来。

## 目录

- `styles/`：风格库（每张卡都有样张，`README.md` 是索引，`samples/` 是样张）
- `templates/`：`scene.md` 画面单模板、`style-card.md` 新风格卡模板、`adapt-example.txt` 适配样例、`common.txt` 通用约束、`codex-task.md` 给 Codex 的任务模板
- `scripts/`：`doctor.py` 自检、`settings.py` 默认风格、`style_picker.py` 风格选择页、`add_sample.py` 写回样张、`render_codex.py`（检查 + 拼接 + 出图 + 核对，一条命令）、`check_prompts.py`、`build_prompts.py`、`verify_log.py`（Codex 自己出图后核对）、`make_page.py` 对比页、`update_index.py` 重建风格索引
- `reference/`：`formats.md` 画幅、`recommend.md` 内容类型 → 风格、`taste.md` 作者口味、`lessons.md` 实测规则与证据

## 任务目录（每篇文章 / 每批图一个）

```
<项目>/images/<NN-简述>/
  scenes.md               画面单（阶段 1）
  adapt/<图号>-<风格>.txt  适配后的画面（阶段 3），如 2-S07.txt
  prompts/  out/  logs/    脚本生成
  review.html             对比页
  ref.png                 （可选）参考图
  _v1/                    改过提示词后被替换下来的旧图
  baselines/              （可选）用户认可后冻结的版本
```

## 执行者是谁

- **Claude 主导**：阶段 1–3、5 由 Claude 做；阶段 4 用 `render_codex.py` 调 `codex exec`，Codex 只负责原样出图。
- **Codex 自己跑本 skill**：阶段 4 不调 `render_codex.py`（否则会再起一个 Codex），按 `stages/04-render.md`「Codex 自己跑」一节做。
