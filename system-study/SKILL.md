---
name: system-study
description: 系统化学习材料生成器。给一个新领域/技术/概念，AI 自主调研、搭体系、产出 HTML 学习材料（含骨架/案例/工程化/争议+盲区）。当用户说"我要学 X / 帮我系统拆解 X / 我想吃透 X 这个领域 / 给我整理 X 的全貌 / 深度调研 X 给我系统讲讲 / 把 X 搞透"时触发。不适用于"X 行不行/为什么 Y"（用 long-research）、"X 有哪些好玩案例"（用 case-radar 给散点）、"把这堆素材整理成 HTML"（用 readable-output 处理已有素材）、文章写作（用 writing-assistant）、设计稿（用 design-exploration）。
---

# System Study — 系统化学习材料生成

你要学一个新领域。AI 自主调研 + 搭体系 + 产出 HTML 学习材料。

**和已有 skill 的本质区别**：
- **vs long-research**：那个是"有困惑 → 求结论"；这个是"想学 → 求体系"
- **vs case-radar**：那个给散点案例集；这个给系统化全貌
- **vs readable-output**：那个处理已有素材；这个自己挖素材 + 自己建体系（最后可调用它做出稿，但不是核心）

**这个 skill 的差异化命门**：除了"骨架 + 案例 + 工程化"这些教科书必讲的部分，**强制产出"争议焦点 + 盲区清单"两块**——这是普通学习材料没有的，是用户研究 → 内容/产品的金矿。

---

## 5 阶段流程总览

| 阶段 | 名称 | 介入次数 | 产物 | 详细操作 |
|---|---|---|---|---|
| 1 | 题目收敛 | 1 次（必） | `01-题目确认.md` | [reference/stage-1-topic-narrow.md](reference/stage-1-topic-narrow.md) |
| 2 | 调研计划 | 1 次（默认） | `02-调研计划.md` | [reference/stage-2-research-plan.md](reference/stage-2-research-plan.md) |
| 3 | Sub-agent 并行调研 | 0 次 | `03-调研笔记/A-E.md` | [reference/stage-3-subagent-templates.md](reference/stage-3-subagent-templates.md) ⭐ |
| 4 | 体系搭建+大纲确认 | 1 次（默认） | `04-体系大纲.md` | [reference/stage-4-synthesis.md](reference/stage-4-synthesis.md) |
| 5 | HTML 学习材料 | 0 次 | `05-学习材料.html` | [reference/stage-5-html-spec.md](reference/stage-5-html-spec.md) |

**默认严格逻辑**：阶段 1/2/4 都问用户。但用户可一次性说"全程不打扰、直接出 HTML"，跳过 2、4。阶段 1 **永远不能省**——题目错了后面全白干。

### 用户授权"全程不打扰"快速通道

如果用户在阶段 1 / 2 / 任何阶段说出"你直接来吧 / 直接给我结果就行 / 你自己定 / 你判断 / 全程不打扰"——主线程立即切换到快速通道：

1. **阶段 1 依然要问**（用 AskUserQuestion 弹切片）——题目永远不能 AI 替用户拍
2. **阶段 2 仍然写 `02-调研计划.md` 存档**，但**不再问用户**，直接进阶段 3
3. **阶段 4 仍然写 `04-体系大纲.md` 存档**，但不再问用户，直接进阶段 5
4. **在 PLAN.md 标注"用户已授权全程不打扰"**——这是审计线索

切换条件：用户的话里**明确包含**"直接 / 不打扰 / 自己定 / 自己判断 / 你来"等授权词。模糊表达（如"看着办"）不算——继续按默认严格流程问。

---

## 核心设计原则（5 条）

这 5 条是从首发实战提炼的、贯穿整个 skill 的设计哲学。所有 stage 都遵循：

1. **必经卡点不省**——阶段 1 题目收敛永远不能省。其他卡点用户可授权跳过，但题目错了全白干。
2. **强制要异见，禁止和稀泥**——Agent E 不接受"两边都对"。每个议题必须给 X/10 倾向分。
3. **盲区清单独立成块**——还没共识的、还在打架的、AI 互相复读的，独立段落，不混在其他内容里。
4. **用户研究视角主导**——不走"基础→进阶→高阶"教材路线，按"我能拿来做什么"组织。允许带判断、带视角，不需要装客观。
5. **HTML 独立写，不调 readable-output**——学习材料需要侧栏导航 + 章节折叠 + 争议高亮 + 盲区独立区，长文阅读结构不够用。

---

## 5 个 Sub-agent 阵容（A-D 灵活 + E 必选）

详细 prompt 模板见 [reference/stage-3-subagent-templates.md](reference/stage-3-subagent-templates.md)。

| Agent | 固定职责 | 主题适配方式 |
|---|---|---|
| **A 骨架** | 官方文档 + 学派 / 主流方法 | 视主题决定具体源（提示词→Anthropic/OpenAI 文档；记忆系统→各家 memory 文档；MCP→协议文档+实现） |
| **B 前沿** | 新形态、新趋势、最新讨论 | 视主题灵活——一句话定义"这领域最新的是什么" |
| **C 真物** | 顶级案例 / 真实代码 / 原文拆解 | **必须看原文**；案例数量按可信源能找到几个定 |
| **D 生态** | 工具景观 / 工程化 / 应用场景 | 直接对接用户的产品决策 |
| **E 争议+盲区** | **必选**，强制双轨陈述 + 给倾向分 + 盲区清单 | **差异化命门**——和市面学习材料的核心区别 |

**主线程拿到题目后**，根据主题情况微调每个 sub-agent 的具体调研范围（不是改职责类型，是改"查哪些源"），再批量派出。

---

## 工作流（主线程要做什么）

### Step 0：建工作目录
```
<主题>学习/                  # 默认目录名，可改
├── PLAN.md                  # 总控
├── 01-题目确认.md
├── 02-调研计划.md
├── 03-调研笔记/
│   ├── A-{骨架切片名}.md
│   ├── B-{前沿切片名}.md
│   ├── C-{真物切片名}.md
│   ├── D-{生态切片名}.md
│   └── E-争议与盲区.md
├── 04-体系大纲.md
└── 05-学习材料.html
```

### Step 1：题目收敛
- 用 `AskUserQuestion`（multiSelect: true）给用户 4 个切片选项让她勾
- 切片描述要具体到"覆盖什么"，不要泛泛
- 用户全选也行（这次提示词学习就是 4 个全选）
- 写 `01-题目确认.md` 记录主题 + 学习视角

### Step 2：调研计划
- 列出每个 sub-agent 要查的源（官方文档、社区、案例库、争议议题）
- 给用户审一遍，可砍可加
- 用户说"开跑"就进入 Step 3
- 写 `02-调研计划.md`

### Step 3：派 5 个 Sub-agent 并行
- 每个 sub-agent 用一个独立的 Agent 调用（subagent_type: general-purpose）
- 一次性在同一个 message 里发出全部 5 个（并行）
- prompt 模板见 [reference/stage-3-subagent-templates.md](reference/stage-3-subagent-templates.md)
- **必须包含的硬约束**（见 [anti-patterns.md](reference/anti-patterns.md)）：
  - 分段写入文件（每完成 1-2 节就 Write 一次）
  - 反 AI 文废话清单
  - 来源可追溯
  - 争议必须双轨 + 给倾向

### Step 4：合成 + 大纲确认
- 读全部 5 份调研笔记
- 设计 8 篇章节结构（导读 / 骨架 / 实战 / 进阶 / 案例 / 工程化 / 争议 / 盲区 / 附录）
- 写 `04-体系大纲.md`
- 给用户过一遍坐标系

### Step 5：HTML 产出
- 按 [stage-5-html-spec.md](reference/stage-5-html-spec.md) 的设计 token 和组件规范
- 单文件 HTML，所有 CSS 内嵌
- 必须包含：左侧固定导航 / 4 种 callout / 案例 details 折叠 / 争议带倾向分 / 盲区清单
- **一次写完，不要分多次 Write**（防止截断时被中间状态打断）

---

## 关键硬约束（一定要看 [anti-patterns.md](reference/anti-patterns.md)）

1. **Sub-agent 必须分段写入文件**——不能等最后一次性写。socket 崩溃会丢全部内容。
2. **Agent E 强制双轨 + 给倾向分**——"两边都对"不接受。
3. **案例类 Agent 强制 3+ 个原文片段 + 可信度评级**——AI 总结的二手案例不接受。
4. **AI 文废话黑名单**——明显套话密度高的中文博客跳过。
5. **主线程做合成，不下放给 sub-agent**——sub-agent 只产物料。
6. **PLAN.md 主控**——每次状态变化更新进度表。

---

## 灵活参数

| 参数 | 默认 | 可调 |
|---|---|---|
| 切片数量 | 4（A-D）+ 1（E）= 5 | 3-6（E 必含） |
| 介入级别 | 阶段 1/2/4 各一次 | 用户可授权全跳过 2 和 4 |
| 产物目录名 | `<主题>学习/` | 用户可改 |
| HTML 风格 | 浅色暖白 | 可扩深色 / 暗紫调（暂未实现） |
| Sub-agent 派出方式 | 一次性 5 个并行 | 不要分两批 |

---

## 不适用于（边界划清）

- "X 行不行 / 为什么 Y / 评估 X 可行性" → `long-research`
- "X 领域有哪些好玩案例 / 看看大家在玩什么" → `case-radar`（散点 vs 体系）
- "把这堆素材整理成 HTML" → `readable-output`（处理已有素材 vs 自己挖素材）
- "写文章 / 出初稿" → `writing-assistant`
- "做设计稿 / UI 原型" → `design-exploration` / `macos-product-design`
- "PRD / 需求文档" → `prd-doc-writer`

---

## 参考实例

**首发实战**：项目根目录 `提示词学习/`（2026-05-14 跑通的真实案例）
- 主题：提示词学习（4 切片全选）
- 实际耗时：~30 分钟
- 产物：5 份调研笔记 ~180KB → HTML 学习材料 120KB（1635 行）
- 卡点教训：见 [anti-patterns.md](reference/anti-patterns.md) 的"Agent B socket 崩溃"案例

后续每跑一个新主题，建议在 `examples-index.md` 里记一笔，作为后续主题的参考。
