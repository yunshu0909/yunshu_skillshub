<p align="right">
  <strong>简体中文</strong> · <a href="./README.en.md">English</a>
</p>

<p align="center">
  <img src="./assets/readme/hero.png" width="100%" alt="云舒的 Skills 搭子们：狗子 IP 与 33 个面向产品、开发、研究、写作和效率场景的 Agent Skills" />
</p>

# Yunshu SkillsHub

把模糊任务交给一组可复用、可执行、可验收的 AI 工作流。

<p align="center">
  <a href="https://github.com/yunshu0909/yunshu_skillshub/stargazers"><img alt="GitHub Stars" src="https://img.shields.io/github/stars/yunshu0909/yunshu_skillshub?style=flat-square&color=4E63D9" /></a>
  <a href="https://github.com/yunshu0909/yunshu_skillshub/network/members"><img alt="GitHub Forks" src="https://img.shields.io/github/forks/yunshu0909/yunshu_skillshub?style=flat-square&color=1FA884" /></a>
  <a href="./LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-172033?style=flat-square" /></a>
  <img alt="33 installable skills" src="https://img.shields.io/badge/skills-33_installable-F6F3EA?style=flat-square&labelColor=172033" />
</p>

这里不是一叠孤立的提示词。每个 Skill 都用 `SKILL.md` 固化触发条件、工作阶段、确认门槛和交付物，让 Codex、Claude Code 等 Agent 在产品、开发、研究、写作和日常效率任务中按同一套方法工作。

> 当前仓库可被 `skills` CLI 识别出 **33 个 Skill**：其中 **32 个推荐使用**，`plan-report` 已并入 `issue-pool`，作为历史兼容目录保留。

## 一条真实的交付链路

多个 Skills 可以组合成一条从想法到反馈的闭环：

```text
想法 / 痛点 / 外部反馈
        ↓  issue-pool
需求收敛与可开工 task
        ↓  design-exploration
设计方向与全状态约束
        ↓  prd-test-writer
PRD + 可执行测试用例
        ↓  AI 实现与验证
代码、测试结果与审阅材料
        ↓  git-push
Branch → PR → 合并 / 发版
        ↓  issue-triage
新反馈回到 Issue 池
```

这条链路已有可浏览的公开样板：[CodePal 托管 Coding 项目案例](https://github.com/yunshu0909/codepal-managed-project-example)。它展示了 Issue、设计、PRD、测试用例、代码与 PR 如何围绕同一个 task 组织，而不只是描述一个理想流程。

## 30 秒开始

先查看仓库里有哪些 Skills，不做安装：

```bash
npx skills add yunshu0909/yunshu_skillshub --list
```

把全部 Skills 安装到当前项目检测到的 Agent：

```bash
npx skills add yunshu0909/yunshu_skillshub --all
```

也可以只安装需要的 Skill：

```bash
npx skills add yunshu0909/yunshu_skillshub --skill issue-pool
```

安装后直接描述需求即可，相关 Skill 会按触发条件工作：

```text
记个 issue：用户晚上使用时觉得页面太亮
帮我把这个模糊需求收敛成 Codex 能自主执行的 goal
扫一下 Agent Memory 生态，给我看真实案例
把这些零散观点整理成一篇文章
```

也可以直接点名：`/issue-pool`、`/goal-setter`、`/case-radar`、`/writing-assistant`。

## 按你的问题选择 Skill

如果你还不知道名字，从现在遇到的问题开始找。

### 产品与需求 · 9

| Skill | 什么时候用 | 主要产物 |
| --- | --- | --- |
| [`vision-exploration`](./vision-exploration) | 想法还很早，先看最远可能性 | 多种终局愿景 |
| [`product-naming`](./product-naming) | 产品、项目或模块需要命名 | 命名方向、候选与验证 |
| [`backlog-manager`](./backlog-manager) | 日常收集、合并和筛选需求 | 可维护的需求池 |
| [`issue-pool`](./issue-pool) | 把想法或反馈收敛成可开工 task | Issue、task、滚动计划 |
| [`version-planner`](./version-planner) | 把需求拆成 MVP 到 V1.0 | 渐进式版本路线 |
| [`design-exploration`](./design-exploration) | 新功能需要先探索交互与状态 | ASCII 方案、HTML 设计稿、实现契约 |
| [`prd-doc-writer`](./prd-doc-writer) | 需要故事驱动的 PRD | 用户故事、验收标准、图表 |
| [`prd-test-writer`](./prd-test-writer) · Beta | PRD 与测试用例必须对齐 | PRD、测试用例、双 review HTML |
| [`req-change-workflow`](./req-change-workflow) | 在现有代码上安全改需求 | 变更简报、影响评估、回归证据 |

### 工程与交付 · 6

| Skill | 什么时候用 | 主要产物 |
| --- | --- | --- |
| [`ui-design`](./ui-design) | 基于现有页面调整样式与布局 | UI 方案与最小代码修改 |
| [`macos-product-design`](./macos-product-design) · Beta | 设计 macOS 原生风格界面 | 可预览的 HTML/CSS 设计稿 |
| [`prd-auto-test-loop`](./prd-auto-test-loop) · Beta | 用 PRD 编排自动化测试闭环 | 测试计划、自测修复、测试报告 |
| [`issue-triage`](./issue-triage) | 收到 GitHub Issue 后需要诊断和回复 | 根因判断、决策与用户回复 |
| [`project-map-builder`](./project-map-builder) | 需要快速理解或维护目录说明 | `PROJECT_MAP.md` |
| [`git-push`](./git-push) | 首次推送、日常更新或版本发布 | 安全检查、提交、推送与 Release |

### 调研与决策 · 6

| Skill | 什么时候用 | 主要产物 |
| --- | --- | --- |
| [`case-radar`](./case-radar) | 想看一个新生态里真实做出了什么 | 带截图、源码或演示的 HTML 案例集 |
| [`github-repo-search`](./github-repo-search) | 需要搜索和筛选开源项目 | 可比较的 Top N 推荐报告 |
| [`system-study`](./system-study) | 想系统吃透一个领域 | 有体系、有案例的 HTML 学习材料 |
| [`multi-perspective-analysis`](./multi-perspective-analysis) | 一个问题需要多个独立视角 | 共识、分歧与盲区报告 |
| [`thinking-partner`](./thinking-partner) | 局面混乱，不知道核心卡点 | 问题诊断、共创解法、行动计划 |
| [`priority-judge`](./priority-judge) | 待办太多，不知道先做什么 | 优先级判断与当前行动 |

### 内容与表达 · 7

| Skill | 什么时候用 | 主要产物 |
| --- | --- | --- |
| [`thought-mining`](./thought-mining) | 脑中有零散想法但还没成形 | 洞察记录、选题与文章素材 |
| [`writing-assistant`](./writing-assistant) | 从选题、框架一路写到成稿 | 结构清晰的文章 |
| [`readable-output`](./readable-output) | 要把复杂内容整理给人阅读 | 高可读 HTML 长文 |
| [`image-assistant`](./image-assistant) | 文章、PPT 或社媒内容需要配图 | Copy Spec 与生图提示词 |
| [`lesson-builder`](./lesson-builder) | 需要快速备课或制作培训材料 | 课程大纲与课件 |
| [`weekly-report`](./weekly-report) | 要把一周工作讲清价值与边界 | 结构化周报 |
| [`hermes-persona-builder`](./hermes-persona-builder) | 为 Hermes 或陪伴型 Agent 创建人设 | 可直接使用的 `SOUL.md` |

### Agent 与个人效率 · 4

| Skill | 什么时候用 | 主要产物 |
| --- | --- | --- |
| [`auto-task`](./auto-task) · Beta | 复杂任务希望 AI 长时间自主推进 | 任务队列、阶段证据与最终结果 |
| [`goal-setter`](./goal-setter) | 要把模糊诉求交给另一个 Agent 执行 | 有范围、验收与停止条件的 goal |
| [`memory-init`](./memory-init) | 新项目需要稳定的长期记忆协议 | `CLAUDE.md`、`MEMORY.md`、`memory/` |
| [`organize`](./organize) | 文件夹混乱、重复或难以归档 | 经确认的整理方案与目录结果 |

### 历史兼容 · 1

| Skill | 状态 | 推荐替代 |
| --- | --- | --- |
| [`plan-report`](./plan-report) | 已合并并退役，目录暂时保留 | 使用 [`issue-pool`](./issue-pool) 的滚动计划流程 |

## 真实产物与示例

- [CodePal 托管 Coding 项目案例](https://github.com/yunshu0909/codepal-managed-project-example)：Issue → 设计 → PRD → 测试 → PR → 反馈的完整公开链路。
- [PRD review 示例](./prd-test-writer/samples/PRD-SAMPLE-review.html)：面向人审阅的 PRD HTML。
- [测试用例 review 示例](./prd-test-writer/samples/PRD-SAMPLE-测试用例-review.html)：与 PRD 对齐的可执行测试用例。
- [10 个精选使用示例](./EXAMPLES.md)：展示触发方式、对话过程和预期输出。
- [更新日志](./CHANGELOG.md)：查看 Skill 的新增、调整与 Beta 状态。

## 设计原则

这些 Skills 共享几条底层原则：

- **先摸现实，再给方案**：能从代码、文件和外部事实确认的信息，不反问用户。
- **用户决定方向，Agent 负责推进**：关键分歧确认后，执行、检查与整理尽量自主完成。
- **交付物必须可检查**：PRD 有验收标准，测试有证据，调研有来源，计划有完成条件。
- **小步确认，避免大返工**：高影响选择先收敛，细节在已确认的框架内推进。
- **不虚构能力与结果**：依赖缺失、无法验证或需要人工判断时明确标注。

## 兼容性与仓库结构

仓库采用标准的 `SKILL.md` 目录约定，已验证 `skills` CLI 可以发现全部 33 个 Skill。不同 Agent 的工具能力并不完全相同；涉及浏览器、联网、图像生成或多 Agent 的 Skill，会以各自 `SKILL.md` 中的依赖和降级规则为准。

```text
<skill-name>/
├── SKILL.md          # 触发条件、流程、约束与交付
├── references/       # 按需读取的规范与参考材料
├── assets/           # 模板或可复用资源
└── scripts/          # 可选的确定性工具

assets/readme/        # README 视觉资产
EXAMPLES.md           # 精选使用示例
CHANGELOG.md          # 更新记录
```

## 贡献与许可

欢迎通过 [Issues](https://github.com/yunshu0909/yunshu_skillshub/issues) 提交问题、真实使用反馈或新的 Skill 建议，也欢迎发起 Pull Request。

本项目采用 [MIT License](./LICENSE)。

---

Made with care by Yunshu.
