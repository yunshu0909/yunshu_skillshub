---
name: case-radar
description: 案例雷达。给一个新东西（新工具/新概念/新生态），扫一遍生态找好玩的真实案例，重点是抓"真物"（截图/源码/演示）而不是 GitHub 主页，输出可浏览的 HTML 案例集。当用户说"看看大家用 X 做了什么"、"扫一下 X 生态"、"市面上 X 有什么新玩法"、"给我看 X 的真物案例"、"/case-radar"时触发。不适合：① 已有明确目标的深度调研（用 long-research）② 写文章/出 PRD（用 writing-assistant / prd-doc-writer）③ 单纯求知不需要 HTML（直接问就好）。
---

# Case Radar · 案例雷达

把"想了解新东西"这件事从"读三手 SEO 文" → "拿到一手真物（截图/源码/演示）"。

输入：一个新东西的名字 + 一句话上下文（"我想用来做 X"）。
输出：一份可浏览的 HTML 案例集，每张卡都配真实物料（不是文字描述）。

**核心信念**：菜单一文不值，菜才是真东西。GitHub repo 主页是文件列表（菜单），README 里的截图、商店页的安装数、SKILL.md 的原文段落、产品落地页的真实建站效果——才是真东西（菜）。

---

## 流程概览

| 阶段 | 名称 | 目标 | 主要工具 |
|---|---|---|---|
| 0 | 环境自检 | 确认 agent-browser 装了 + 主题清晰 | Bash + 对话 |
| 1 | scan | 多渠道扫信源，列出候选案例 | WebSearch / Agent（不重新发明，直接调用） |
| 2 | recon | 给每个候选侦察"真物位置"——核心增值 | 读 `reference/recon-heuristics.md` |
| 3 | capture | 拉真物（curl 直接资源 + agent-browser 截图） | curl + agent-browser |
| 4 | embed | 套 HTML 模板输出 | 参考 `reference/html-template-spec.md` |

**每一步都可中断**。用户随时可以说"停"、"跳过这一步"、"回到上一步"。

---

## 阶段 0：环境自检 + 主题对齐

### 0.1 检查 agent-browser 是否装好

```bash
command -v agent-browser
```

- ❌ 未装 → 告诉用户："这个 Skill 依赖 vercel-labs/agent-browser 抓截图。一行命令装：`brew install agent-browser && agent-browser install`。装完回来。" 终止。
- ✅ 已装 → 继续

> 注意：`agent-browser install` 会下 Chrome 二进制（~169 MB）。如果在中国大陆，可能下载失败。但实测即使 install 卡住，agent-browser 也能复用机器上已有的 Playwright Chromium（`~/Library/Caches/ms-playwright/`）。所以即使 install 报错，先试一下 `agent-browser open https://example.com`，能跑就跳过 install。

### 0.2 检查 gh CLI 已登录（recon 阶段要用）

```bash
gh auth status
```

- ❌ 未登录 → 提示 `gh auth login`，终止
- ✅ → 继续

### 0.3 主题对齐——3 个问题，最多问一次

用 AskUserQuestion 一次性问完，不要反复 ping-pong：

1. **新东西的名字和上下文**（"Claude Skills 生态" / "MCP 最新玩法" / "AI Agent 框架对比" 等）
2. **用途**：① 为研究/产品开发服务（深度优先）② 为内容创作服务（兼顾"我能记住"和"未来能引用"）③ 纯求知/拓展视野（广度优先）④ 三种都要，按事走（边做边定）
3. **范围圈**：① 锚定一个生态（如 Claude Skills）② 一个工具/产品（如 cline、cursor）③ 一个概念（如 MCP、Subagent）④ 不设限，临时定

> ⚠️ 这一步**不要扩展成讨论会**。3 个问题问完就动手。如果用户答不上某条，给一个合理默认值（用途默认"三种都要"，范围默认"锚定一个生态"），继续。

---

## 阶段 1：scan · 多渠道扫信源

**不重新发明**——直接调 WebSearch 或起一个 Agent 跑扫描。

### 1.1 起一个 scan agent（推荐）

如果案例可能 >20 个，用 `Agent` 工具起一个 general-purpose subagent 并行跑扫描，避免污染主上下文。Prompt 关键点：

- 信源分级要求：**一手源**（官方文档/作者博客/原推文/changelog）/ **二手优质**（HN 高分贴 / Reddit / Simon Willison 这类深度玩家 / 知名工程师博客）/ **三手中文**（公众号/知乎/CSDN，只要有"独立观察"的，纯翻译稿不要）
- 严格砍掉：基础教程、awesome-list（meta 仓库，除非 list 里被点名的好案例）、纯 SaaS API 包装、官方文档操作类示范
- 输出格式：每条 `[标题](URL) — 1 句话简介 + 为什么值得深挖`
- 数量：目标 25-40 个合格案例
- 末尾要求 100-200 字"扫描印象"（生态全景：3 大热门 / 3 大空白 / 1 个最强信号）

### 1.2 用户拍板候选范围

scan agent 跑完后，**不要立刻全部进 recon**。先把信源清单给用户，让她：
- 砍掉明显不感兴趣的几个
- 标出"特别想看"的 5-8 个作为**精读单**（这部分进入 recon + capture 深加工）
- 剩下的进入"普通卡片"层（只显示标题 + 链接，不抓真物）

> ⚠️ 如果用户说"全部都要"，提醒她：v2 实测 35 案例 grid 是"断崖式注意力低谷"——读者读到 35 时已经累了。建议精读 5-7 个，其余作为索引保留。最终决定权在用户。

---

## 阶段 2：recon · 真物侦察（核心增值）

> **这是 Case Radar 的独家增值**。其他阶段都被现有 Skill 覆盖，唯独"判断每个案例的真物在哪种栖息地"这一步是新的。

**读 `reference/recon-heuristics.md` 获得 7 种"真物栖息地"的判别模式。**

对精读单里每个候选案例，问自己：
1. 这个对象的真物最可能在哪个栖息地？（参考 heuristics 的 7 种模式）
2. 用什么工具抓最合适？（curl 直接资源 / gh API 拉源码 / agent-browser 截图全页）

把每个案例的"真物位置"写下来——这是 capture 阶段的施工图。

**反 checklist 化提醒**：recon-heuristics 是 patterns 集合，不是 checklist。某个案例的真物可能在 7 种栖息地之外的第 8 种位置。**保留发现新栖息地的可能**，发现了就更新 heuristics 文件。

---

## 阶段 3：capture · 抓真物

按 recon 阶段的施工图，对每个精读案例抓真物。

### 3.1 优先 curl 直接资源（最快、最干净）

```bash
curl -sLo screenshots/cases/<name>.<ext> "<url>"
```

适合：README 里已有的 `screenshots/` `examples/` `assets/` 目录里的图、GIF、demo 视频。无浏览器渲染开销，不会有边框/黑条。

### 3.2 gh API 拉源码片段

适合：SKILL.md 原文、配置文件、changelog 关键段落。

```bash
gh api repos/<owner>/<repo>/contents/<path>/SKILL.md --jq '.content' | base64 -d
```

把关键段落（10-30 行）保留到 `screenshots/cases/<name>-skillmd.txt`，HTML 里用 `<pre>` 块呈现。

### 3.3 agent-browser 截网页

适合：产品落地页（Next.js SPA）、官方商店页（如 Anthropic plugin store）、长博客全页。

```bash
agent-browser open <url>
agent-browser wait 2000             # 等 JS 渲染
agent-browser screenshot --full screenshots/cases/<name>-fullpage.png
```

> ⚠️ agent-browser 默认把截图存到调用时的当前目录，不是参数路径——要么 cd 进 screenshots/cases，要么截完用 mv。

### 3.4 截不到/找不到真物的案例

不要硬凑。这种案例**不进精读单**，降级回普通卡片层（只显示文字描述 + 链接）。**装饰图比无图更糟**——v2 复盘已经验证（NeoLab 那张纯封面图被 4 个视角里 2 个点名说是"装饰层"）。

---

## 阶段 4：embed · 输出 HTML

参考 `reference/html-template-spec.md` 的视觉规范和层级标签系统。

### 4.1 文件命名

```
<工作目录>/<主题简称>-案例集-YYYY-MM-DD.html
```

例：`skills-生态创意案例集-2026-05-14.html`

图片路径用相对路径：`screenshots/cases/<file>` —— HTML 在原位置打开就能加载。

### 4.2 HTML 结构（4 块）

```
[Header]           标题 + 一句话 lede + 层级标签图例 + 升级说明（如有 v2）
[工具 Spotlight]   如果 capture 阶段重度使用了某个工具（如 agent-browser），单独 spotlight
[精读卡]           5-7 张富卡片，每张有真物 hero + 妙在 + 为什么是你 + 大 CTA
[Next Step]        3-5 个可选下一步（不下结论，给用户选）
```

> ⚠️ 不要加"生态全景 3 大热门"、"6 大分组 grid"这种结构层——v2 复盘已经验证这些是"AI 让自己显得完成度高"的装饰层。如果用户特别要全景图，作为可选附加层。

### 4.3 层级标签（最多 3 层，不要 4 层）

参考 `reference/html-template-spec.md`。**默认轻量 3 层**：事实层 / AI 推测层 / 你的判断区。复杂版（加 共识层、真物层）作为可选，不强加。

---

## 阶段 5：完成输出

```
✅ 案例雷达扫描完成！

- 扫描案例：[N] 个，精读 [M] 个
- 真物物料：[K] 件（X 张截图 + Y 段源码 + Z 个对比图）
- HTML：[相对路径]
- agent-browser 用量：[A] 次截图 + [B] 次 navigate

Next：
  - 在浏览器中打开 HTML 查看效果
  - 如发现某张精读卡的真物没抓到位，告诉我哪张，单独重抓
  - 如想把某个案例拆成短文/图文，告诉我
```

---

## 核心原则

### 1. 真物优先，描述其次

文字描述能讲什么、图能讲什么，永远先要图。**菜单一文不值，菜才是真东西。** 截不到真物的案例，降级到普通卡片层，不要硬塞装饰图。

### 2. 信源分级，砍掉 SEO 垃圾

一手源（官方/作者）/ 二手优质（深度玩家）/ 三手中文（有独立观察的），三层之外的 SEO 文、awesome 集市、纯翻译稿一律砍掉。

### 3. 精读 5-7 个，其他索引化

35 个全做精读会让读者"断崖式注意力低谷"。**精读单是用户拍的板，不是 AI 全包**——把候选清单给用户选，不要自作主张全部深加工。

### 4. recon 不 checklist 化

`reference/recon-heuristics.md` 是 patterns 集合，给 Claude 灵活选取。如果某案例的真物在 patterns 之外，**记下来更新 heuristics**——这个 Skill 应该越用越锋利。

### 5. 每一步可中断

用户随时可以说"停"、"跳过"、"换主题"。不要一口气从 scan 跑到 embed 不给反应机会——v2 实测每一步都需要用户拍板。

### 6. 反过度工程化

读 `reference/workflow-anti-patterns.md`。这个 Skill 容易落入"建工具不做事"陷阱——它的真正价值取决于用户能不能把案例集变成行动（写文章、做实验、定方向），不取决于 HTML 多精美。

---

## 什么时候不该用这个 Skill（重要）

> 这一段是 4 视角诊断后留下的自我提醒。**Skill 跑得动 ≠ Skill 该被点开**。

读 `reference/workflow-anti-patterns.md` 末尾的"4 个反向信号"判断。简版：

- ✗ **如果你只是好奇但没想拿去做点什么** → 直接读原文/翻 X 列表更轻，不需要跑全套
- ✗ **如果你已经在写一篇相关文章了** → 先把那篇写完，案例当素材手抓即可
- ✗ **如果你这周已经在另一件具体的事上有进展了** → 不要用这个 Skill 制造新的"建工具的忙碌感"
- ✗ **如果新东西的"真物"很难界定**（如某种抽象概念/非工具类） → recon 阶段会失锚，应该用 long-research 而非这个

---

## 使用示例

### 场景 1：扫一个新生态

```
用户：扫一下 MCP 生态最新玩法

Skill：
→ 0.1 ✅ agent-browser 装好
→ 0.2 ✅ gh 已登录
→ 0.3 问 3 个对齐问题（用途 / 范围 / 1 个其他）
→ 1.1 起 scan agent，跑 5-8 分钟拉回 32 个候选 + 扫描印象
→ 1.2 用户从 32 个里挑 6 个精读
→ 2 对 6 个跑 recon，判别每个的真物位置
→ 3 拉真物（curl 5 个直接图 + gh 拉 3 段 SKILL.md + agent-browser 截 2 个落地页）
→ 4 出 HTML
→ 5 ✅ 完成
```

### 场景 2：恢复中断的 scan

```
用户：之前那个 Skills 生态扫得怎么样了

Skill：
→ 找最近的 case-radar 输出文件
→ 报告当前状态：scan 已完成（35 个）/ recon 完成 7 个 / capture 完成 4 个
→ 问用户从哪一步继续
```

### 场景 3：用户说"我已经在写文章了"

```
用户：我准备写一篇关于 Cursor 0.50 的文章，先扫一下生态

Skill：
→ ⚠️ 触发"反向信号 #2"：用户已在写文章
→ 反问："你需要的是案例集 HTML 还是几张关键截图直接放进文章？"
   - 案例集 → 继续走全流程
   - 几张截图 → 跳过 scan + embed，直接进 capture，用 agent-browser 抓你指定的 URL
```

### 场景 4：临时发现真物在 heuristics 之外

```
recon 阶段发现某 Skill 的真物是一段 YouTube demo 视频字幕。
heuristics 文件没列这种栖息地。

Skill：
→ 用 agent-browser 抓字幕（snapshot -i 拿 YouTube 字幕面板）
→ 完成 capture 后，提示用户："本次发现新栖息地：YouTube 字幕。
   是否更新 recon-heuristics.md 加入第 8 种栖息地？"
→ 用户确认 → 更新 reference 文件
```

---

## 维护与扩展

- 加新的 recon pattern → 编辑 `reference/recon-heuristics.md`
- 加新的 HTML 视觉模板 → 编辑 `reference/html-template-spec.md`
- 修改反 anti-pattern 列表 → 编辑 `reference/workflow-anti-patterns.md`
- 新增整个新维度（如新增多语言案例支持） → 参考 `reference/_how-to-extend.md`
