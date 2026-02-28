# 云舒的 Skills 搭子们 / Yunshu's Claude Code Skills

[English](#english) | [中文](#中文)

---

## 中文

### 📖 简介

这是一个精心打造的 Claude Code Skills 集合，旨在提升软件开发和产品管理的效率。每个 Skill 都经过实战验证，帮助你在日常工作中更加高效。

### ✨ 包含的 Skills

#### 🎨 [配图助手](./image-assistant) (Image Assistant)
**描述**: 把文章/模块内容转成统一风格、少字高可读的 16:9 信息图提示词

**适用场景**:
- 文章需要配图但不知道怎么设计
- PPT、海报、社媒图需要统一风格
- 内容太多字，想要更趣味、更好读的视觉呈现
- 需要批量生成配图提示词

**核心功能**:
- 📋 需求澄清：挖掘内容、场景、受众和字数偏好
- 🗂️ 配图规划：拆分内容，定义图清单（几张图/每张讲什么）
- ✍️ 文案定稿：逐字定稿"图上写什么"（Copy Spec）
- 🎯 提示词封装：生成可复制的生图提示词，支持批量出图
- 🔄 迭代润色：根据反馈减字、换隐喻、提升可读性

**触发方式**:
```
这段内容做个图/配几张图
给我两张出图提示词
字太多不好看，帮我更趣味、更好读
/image /配图 /出图
```

---

#### 🧠 [思维挖掘助手](./thought-mining) (Thought Mining)
**描述**: 通过对话帮助你把脑子里的零散想法倒出来、记录下来、整理成文章

**适用场景**:
- 想写文章但思路不清晰
- 有很多零散想法需要整理
- 需要从混乱的思考中提炼核心观点

**核心功能**:
- 📝 思维挖掘：引导式对话，帮你说出并记录想法
- 🎯 选题确定：从洞察中找到核心观点
- ✅ 观点验证：联网搜索验证理解是否正确
- ✍️ 写作辅助：逻辑检查、文字润色、金句提炼
- 🔍 最终审核：发布前的全面检查

**触发方式**:
```
我想写一篇关于 XX 的文章
帮我整理一下我的想法
/thought-mining
```

---

#### 📋 [PRD 文档撰写助手](./prd-doc-writer) (PRD Doc Writer)
**描述**: 以故事驱动的方式，帮助你撰写和迭代完善 PRD/需求文档

**适用场景**:
- 需要撰写产品需求文档
- 想用用户故事的方式梳理需求
- 需要用图表减少需求歧义

**核心功能**:
- 🗺️ 用户旅程地图：构建宏观业务流程
- 📖 故事化需求：每个功能点都是一个完整的用户故事
- 🎨 ASCII 线框图：可视化页面布局
- 📊 Mermaid 图表：流程图/状态图/时序图
- ✅ 阶段性确认：确保每一步都与你达成共识

**触发方式**:
```
帮我写 PRD
梳理需求文档
/prd-doc-writer
```

---

#### 🎨 [新功能设计探索](./design-exploration) (Design Exploration)
**描述**: 新功能设计探索流程。从模糊想法产出可交付的设计参考文档，作为 PRD 阶段的输入

**适用场景**:
- 有模糊想法要做新功能/新模块
- 需要批量探索多种设计方案
- 需要完整覆盖页面状态（正常/异常/边界）
- 需要产出设计稿作为开发参考

**核心功能**:
- 📝 需求收敛：明确做什么、不做什么、边界在哪
- 🔍 技术调研：了解外部数据约束和技术可行性
- 🎨 ASCII 批量探索：一次出 5-8 个方案供选择
- 📐 HTML 设计稿：基于选定方案产出 mockup
- 📊 全状态覆盖：正常态/加载态/空态/错误态/边界情况
- 📋 交互规则表：前端开发直接对照实现

**触发方式**:
```
我想做个新功能
帮我设计一下这个模块
出个设计方案
/design-exploration
```

---

#### 🔄 [需求变更工作流](./req-change-workflow) (Requirement Change Workflow)
**描述**: 标准化需求变更流程，避免改需求时的混乱和代码崩溃

**适用场景**:
- 需要修改现有功能的需求
- 改需求时经常出现意外 bug
- 需要一个可靠的变更验证流程
- 特别适合 Chrome 扩展等复杂项目

**核心功能**:
- 📝 需求澄清：锁定变更范围和验收标准
- 🔍 现状基线：从代码中确认当前行为
- ⚠️ 影响评估：评估风险和变更范围
- 🎯 设计方案：提出新设计并获得批准
- 🛠️ 最小化实现：小范围、局部化的代码修改
- ✅ 回归测试：固定的验证清单
- 📚 文档维护：决策日志和文档更新

**触发方式**:
```
改需求/需求变更
调整交互/改功能
/req-change-workflow
```

---

#### 📚 [课程构建器](./lesson-builder) (Lesson Builder)
**描述**: 通过讨论驱动的方式，帮助你快速完成课程大纲和课件

**适用场景**:
- 需要快速备好一节课
- 已有清晰想法，需要整理成文档
- 需要迭代现有课程大纲
- 准备培训或教学内容

**核心功能**:
- 💭 共创大纲：通过讨论挖掘想法，形成清晰课程框架
- 📖 课件撰写：基于大纲写出完整课件内容
- 🎯 框架优先：先确认框架再写细节，避免返工
- ⚡ 快速迭代：支持快速共创和严格确认两种模式
- 📋 最少文档：只产出需要的内容（大纲/课件/补充材料）

**触发方式**:
```
备课
做课件/准备课程
/lesson-builder
```

---

#### 📦 [需求池管理](./backlog-manager) (Backlog Manager)
**描述**: 需求池管理。随时抛出想法/痛点，AI 负责追问、整理、合并、归档。准备开新版本时协助筛选。痛点驱动，不做提前排期

**适用场景**:
- 随时记录产品想法和功能需求
- 管理零散的需求，避免遗忘
- 准备新版本时挑选要做什么
- 整理和清理过时的需求

**核心功能**:
- 📝 收集：追问痛点、频率、绕过方式，确认理解
- 📂 归类：检查合并可能，判断状态（可以做了/需要想想/先放着）
- 🧹 整理：定期清理过时条目，升档想清楚的条目
- 🎯 筛选：基于频率/可绕过性/ROI 分析候选需求
- ✅ 归档：标记已完成，更新依赖关系

**触发方式**:
```
我想做个功能
记个需求
整理一下需求池
下一个版本做什么
/backlog-manager
```

---

#### 🗺️ [项目目录地图构建器](./project-map-builder) (Project Map Builder)
**描述**: 为指定目录范围生成或增量更新高信噪比的目录说明文档

**适用场景**:
- 需要生成项目目录概览
- 需要代码仓结构说明文档
- 想要更新已有的 PROJECT_MAP.md
- 需要理解项目文件夹结构

**核心功能**:
- 📋 智能范围确认：必须先询问要扫描的文件夹，不默认全仓扫描
- 🔍 关键文件识别：自动识别入口、配置、服务线程等关键文件
- 📝 增量更新：已有 PROJECT_MAP.md 时仅做增量更新，不全量重写
- 🎯 多目录支持：支持单目录或多目录（可合并或分别生成）
- ⚠️ 明确标注：不确定的地方显式标注"假设"或"未确认"

**触发方式**:
```
生成项目地图
更新 PROJECT_MAP
给我生成目录说明
/project-map-builder
```

---

#### 📅 [版本规划助手](./version-planner) (Version Planner)
**描述**: 将产品需求拆解成可执行的渐进式版本规划（V0.1 MVP → V1.0）

**适用场景**:
- 需要拆解产品版本
- 想要规划 MVP 最小可行产品
- 需要分阶段实现功能
- 不确定优先级和开发顺序

**核心功能**:
- 🎯 价值优先：优先解决用户最痛的点，而非技术最难的点
- 🚀 快速验证：MVP 设计为 2-3 天能跑通，避免过度设计
- 📋 明确边界：每个版本明确"做什么"和"不做什么"
- 🔄 渐进式交付：每个版本都能独立使用，不依赖后续版本
- ✅ 可测量：每个版本有清晰的验证点和完成标准

**触发方式**:
```
拆版本
版本规划
MVP怎么做
分阶段实现
/version-planner
```

---

#### ✍️ [写作助手](./writing-assistant) (Writing Assistant)
**描述**: 根据观点清晰度自动选择最优写作路线，覆盖从思维挖掘到成稿的完整流程

**适用场景**:
- 想写文章但思路不清晰
- 需要梳理选题和核心观点
- 需要组织文章框架和逻辑
- 从零散想法到完整文章

**核心功能**:
- 🔍 智能诊断：快速判断观点清晰度，选择最优路线
- 💭 思维挖掘：观点模糊时，通过引导式对话倒出零散想法
- 🎯 选题确定：从洞察中提炼核心选题和灵魂句
- 📐 框架打磨：组织文章逻辑结构，确保表达清晰
- ✍️ 内容产出：根据框架写成完整文章，保持用户风格

**触发方式**:
```
我想写XX
帮我梳理选题
怎么形成框架
给我组织思路
/writing-assistant
```

---

#### 📝 [周报写作助手](./weekly-report) (Weekly Report)
**描述**: 帮助用户梳理周报，按照完整逻辑展示工作价值和边界

**适用场景**:
- 需要整理一周的工作内容
- 想要清晰展示工作价值和成果
- 需要说明遇到的问题和挑战
- 梳理下周工作重点

**核心功能**:
- 📋 素材收集：引导式对话，收集本周工作内容
- 🗂️ 分类整理：根据角色灵活选择合适的模块分类
- 🔍 信息补充：追问背景、结果、价值、状态和下一步
- ✅ 讨论调整：确认表述习惯和逻辑完整性
- 📄 文档输出：生成结构清晰的周报文档

**触发方式**:
```
写周报
周报
梳理周报
整理工作
/weekly-report
```

---

#### 🎯 [优先级判断助手](./priority-judge) (Priority Judge)
**描述**: 从混沌的待办事项中判断优先级，确定现在该做什么

**适用场景**:
- 有很多事要做，不知道从哪开始
- 想快速理清楚今天/本周该做什么
- 需要基于客观标准判断优先级
- 避免在没想清楚的事情上浪费时间

**核心功能**:
- 📝 收集待办：记录所有要做的事情
- 🔍 状态询问：了解每件事的清晰度和deadline
- ⚖️ 优先级判断：基于清晰度和deadline做决策
- 🎯 聚焦行动：每次只聚焦1-2件最重要的事
- 📋 文档化：生成优先级清单文档

**触发方式**:
```
我有很多事要做
帮我理一下
排个优先级
今天该做什么
我要盘一下
/priority-judge
```

---

#### 🤝 [思考拍档](./thinking-partner) (Thinking Partner)
**描述**: 陪你从混沌中理清局面，锁定核心问题，拆解卡点，共创解法，落地行动

**适用场景**:
- 面对复杂问题不知道从哪入手
- 想法很多但理不清主次
- 需要有人陪你一起想清楚
- 避免陷入细节迷失方向

**核心功能**:
- 📝 信息获取：引导式提问，看清全局
- 🎯 锁定核心问题：从一堆问题中找到最关键的那个
- 🔍 拆解卡点：层层追问，找到真正的根因
- 💡 共创解法：基于你的想法补充和修正
- ✅ 落地计划：把讨论结论变成可执行的行动

**触发方式**:
```
我现在很乱，帮我理一下
这事我不知道怎么办
陪我想想这个问题
/thinking-partner
```

---

#### 🎨 [UI 样式修改助手](./ui-design) (UI Design)
**描述**: UI 样式修改协作流程。通过结构化流程减少沟通偏差，避免浪费 token

**适用场景**:
- 需要修改页面样式、布局
- 调整间距、颜色、组件搭配
- UI 细节优化和微调
- 避免猜测式改代码

**核心功能**:
- 📸 截图定位：用截图确认当前状态
- 📐 现状描述：ASCII 画出当前布局
- 🎯 方案选择：提供 2-3 个可视化方案
- 🛠️ 最小改动：只改选定方案涉及的部分
- 🔄 微调迭代：执行具体的小修改

**触发方式**:
```
改一下这个页面的布局
调整这里的样式
这个间距不太对
/ui-design
```

---

#### 🔍 [GitHub 开源项目搜索助手](./github-repo-search) (GitHub Repo Search)
**描述**: 帮助用户搜索和筛选 GitHub 开源项目，输出结构化推荐报告

**适用场景**:
- 想找某个方向的开源项目
- 需要对比多个同类项目
- 想了解技术栈选型方案
- 寻找可直接使用或二次开发的工具

**核心功能**:
- 📝 需求收敛：确认主题、数量、排序模式、目标形态
- 🔍 检索词拆解：5-10 组 query，覆盖同义词、场景词、技术词
- 🏷️ 仓库分类：框架层/应用层/记忆层/MCP层/目录清单层/垂直场景层/方法论层
- 📊 质量精炼：综合权重排序（相关性/场景适用性/活跃度/工程成熟度）
- 📋 结构化报告：可理解、可比较、可决策、可直接行动的候选仓库列表

**触发方式**:
```
帮我找开源项目
搜一下GitHub上有什么
找找XX方向的仓库
开源项目推荐
/github-search
```

---

### 🚀 快速开始

#### 安装方式

**使用 Codex 或 Claude Code CLI 安装**

如果你使用 Codex 或 Claude Code CLI，直接跟 AI 说：

```
安装这个 GitHub 库：https://github.com/yunshu0909/yunshu_skillshub
```

AI 会自动帮你完成安装！

**手动安装**

将本仓库克隆到你的本地 Skills 目录：

```bash
# Claude Code 默认 Skills 目录通常是 ~/.claude/skills/
cd ~/.claude/skills/

# 克隆本仓库
git clone https://github.com/yunshu0909/yunshu_skillshub.git
```

或者，你也可以单独复制需要的 Skill 到你的 Skills 目录。

#### 使用 Skills

在 Claude Code CLI 中，你可以通过以下方式使用：

```bash
# 使用配图助手
/image-assistant

# 使用思维挖掘助手
/thought-mining

# 使用 PRD 文档撰写助手
/prd-doc-writer

# 使用新功能设计探索
/design-exploration

# 使用需求变更工作流
/req-change-workflow

# 使用课程构建器
/lesson-builder

# 使用需求池管理
/backlog-manager

# 使用项目目录地图构建器
/project-map-builder

# 使用版本规划助手
/version-planner

# 使用写作助手
/writing-assistant

# 使用周报写作助手
/weekly-report

# 使用优先级判断助手
/priority-judge

# 使用思考拍档
/thinking-partner

# 使用 UI 样式修改助手
/ui-design

# 使用 GitHub 开源项目搜索助手
/github-search
```

或者直接在对话中描述你的需求，相关 Skill 会自动触发。

**📚 查看使用示例**

想了解每个 Skill 的具体使用方法？查看 [使用示例文档](./EXAMPLES.md)，里面包含了详细的使用场景和预期输出。

---

### 📂 项目结构

```
.
├── README.md                    # 项目说明文档
├── LICENSE                      # MIT 许可证
├── CHANGELOG.md                 # 更新日志
├── EXAMPLES.md                  # 使用示例
├── image-assistant/             # 配图助手
│   ├── SKILL.md                # Skill 定义文件
│   ├── stages/                 # 各阶段详细说明
│   ├── templates/              # 风格模板和配图模板
│   ├── examples/               # 使用示例
│   └── scripts/                # 批量生图脚本
├── thought-mining/              # 思维挖掘助手
│   ├── SKILL.md                # Skill 定义文件
│   ├── stages/                 # 各阶段详细说明
│   ├── templates/              # 模板文件
│   └── examples/               # 使用示例
├── prd-doc-writer/             # PRD 文档撰写助手
│   ├── SKILL.md               # Skill 定义文件
│   ├── assets/                # 模板资源
│   └── references/            # 参考文档和示例
├── design-exploration/         # 新功能设计探索
│   ├── SKILL.md               # Skill 定义文件
│   └── templates/             # 需求总结模板
├── req-change-workflow/        # 需求变更工作流
│   ├── SKILL.md               # Skill 定义文件
│   ├── references/            # 模板和清单
│   └── scripts/               # 辅助脚本
├── lesson-builder/             # 课程构建器
│   └── SKILL.md               # Skill 定义文件
├── backlog-manager/            # 需求池管理
│   └── SKILL.md               # Skill 定义文件
├── project-map-builder/        # 项目目录地图构建器
│   └── SKILL.md               # Skill 定义文件
├── version-planner/            # 版本规划助手
│   └── SKILL.md               # Skill 定义文件
├── writing-assistant/          # 写作助手
    ├── SKILL.md               # Skill 定义文件
    ├── stages/                # 各阶段详细说明
    └── templates/             # 模板文件
├── weekly-report/             # 周报写作助手
│   └── SKILL.md              # Skill 定义文件
├── priority-judge/            # 优先级判断助手
│   └── SKILL.md              # Skill 定义文件
├── thinking-partner/          # 思考拍档
│   └── SKILL.md              # Skill 定义文件
├── ui-design/                 # UI 样式修改助手
│   └── SKILL.md              # Skill 定义文件
└── github-repo-search/        # GitHub 开源项目搜索助手
    └── SKILL.md              # Skill 定义文件
```

---

### 🤝 贡献

欢迎提交 Issue 和 Pull Request！如果你有任何建议或发现了 bug，请随时告诉我。

---

### 📄 许可证

本项目采用 [MIT License](./LICENSE) 开源。

---

### 📧 联系方式

如有问题或建议，欢迎通过 GitHub Issues 联系。

---

## English

### 📖 Introduction

A carefully crafted collection of Claude Code Skills designed to boost efficiency in software development and product management. Each skill has been battle-tested to help you work more effectively in your daily tasks.

### ✨ Included Skills

#### 🎨 [Image Assistant](./image-assistant)
**Description**: Convert article/module content into unified-style, text-minimal, highly readable 16:9 infographic prompts

**Use Cases**:
- Need illustrations for articles but don't know how to design
- PPT, posters, or social media graphics need a unified style
- Too much text, want more engaging and readable visual presentation
- Need to batch generate illustration prompts

**Core Features**:
- 📋 Requirement Clarification: Extract content, scenario, audience, and text density preferences
- 🗂️ Illustration Planning: Split content, define image list (how many/what each explains)
- ✍️ Copy Finalization: Word-by-word finalization of "what text goes on the image" (Copy Spec)
- 🎯 Prompt Packaging: Generate copy-ready image generation prompts, support batch generation
- 🔄 Iterative Refinement: Reduce text, change metaphors, improve readability based on feedback

**Trigger**:
```
Make an image for this content / how many images?
Give me two image generation prompts
Too much text, make it more engaging and readable
/image
```

---

#### 🧠 [Thought Mining](./thought-mining)
**Description**: Helps you extract scattered thoughts from your mind, record them, and organize them into articles through conversational guidance

**Use Cases**:
- Want to write an article but thoughts are unclear
- Have many scattered ideas that need organizing
- Need to extract core insights from chaotic thinking

**Core Features**:
- 📝 Thought Mining: Guided conversation to help you articulate and record ideas
- 🎯 Topic Selection: Find core viewpoints from insights
- ✅ Validation: Verify understanding through web search
- ✍️ Writing Assistance: Logic checking, text polishing, extracting key phrases
- 🔍 Final Review: Comprehensive check before publishing

**Trigger**:
```
I want to write an article about XX
Help me organize my thoughts
/thought-mining
```

---

#### 📋 [PRD Doc Writer](./prd-doc-writer)
**Description**: A story-driven approach to writing and iteratively refining PRD/requirement documents

**Use Cases**:
- Need to write product requirement documents
- Want to organize requirements using user stories
- Need to reduce requirement ambiguity with diagrams

**Core Features**:
- 🗺️ User Journey Map: Build macro business processes
- 📖 Story-based Requirements: Each feature is a complete user story
- 🎨 ASCII Wireframes: Visualize page layouts
- 📊 Mermaid Diagrams: Flow charts/state diagrams/sequence diagrams
- ✅ Staged Confirmation: Ensure consensus at every step

**Trigger**:
```
Help me write a PRD
Organize requirement document
/prd-doc-writer
```

---

#### 🎨 [Design Exploration](./design-exploration)
**Description**: New feature design exploration workflow. From fuzzy ideas to deliverable design reference documents as input for the PRD phase

**Use Cases**:
- Have a fuzzy idea for a new feature/module
- Need to batch explore multiple design options
- Need complete coverage of page states (normal/exception/boundary)
- Need to produce design mockups as development reference

**Core Features**:
- 📝 Requirement Convergence: Define what to do, what not to do, and boundaries
- 🔍 Technical Research: Understand external data constraints and technical feasibility
- 🎨 ASCII Batch Exploration: Generate 5-8 options at once for selection
- 📐 HTML Mockups: Produce mockups based on selected option
- 📊 Full State Coverage: Normal/loading/empty/error/boundary states
- 📋 Interaction Rule Table: Frontend development reference

**Trigger**:
```
I want to build a new feature
Help me design this module
Create a design proposal
/design-exploration
```

---

#### 🔄 [Requirement Change Workflow](./req-change-workflow)
**Description**: Standardize the requirement change process to avoid chaos and code breakage when modifying requirements

**Use Cases**:
- Need to modify existing feature requirements
- Frequently encounter unexpected bugs when changing requirements
- Need a reliable change validation process
- Especially suitable for complex projects like Chrome extensions

**Core Features**:
- 📝 Requirement Clarification: Lock change scope and acceptance criteria
- 🔍 Current Baseline: Confirm current behavior from code
- ⚠️ Impact Assessment: Assess risks and change scope
- 🎯 Design Proposal: Propose new design and get approval
- 🛠️ Minimal Implementation: Small-scale, localized code changes
- ✅ Regression Testing: Fixed validation checklist
- 📚 Documentation Maintenance: Decision log and documentation updates

**Trigger**:
```
Change requirement/requirement modification
Adjust interaction/change feature
/req-change-workflow
```

---

#### 📚 [Lesson Builder](./lesson-builder)
**Description**: A discussion-driven approach to quickly complete course outlines and teaching materials

**Use Cases**:
- Need to quickly prepare a lesson
- Have clear ideas that need to be organized into documents
- Need to iterate on existing course outlines
- Preparing training or teaching content

**Core Features**:
- 💭 Co-create Outline: Extract ideas through discussion, form clear course framework
- 📖 Write Materials: Create complete teaching materials based on outline
- 🎯 Framework First: Confirm framework before details to avoid rework
- ⚡ Rapid Iteration: Supports both quick co-creation and strict confirmation modes
- 📋 Minimal Documentation: Only produce what you need (outline/materials/supplements)

**Trigger**:
```
Prepare lesson
Make teaching materials/prepare course
/lesson-builder
```

---

#### 📦 [Backlog Manager](./backlog-manager)
**Description**: Backlog management. Throw in ideas/pain points anytime, AI handles追问, organizing, merging, and archiving. Assists with selection when starting a new version. Pain-driven, no premature scheduling

**Use Cases**:
- Record product ideas and feature needs anytime
- Manage scattered requirements to avoid forgetting
- Select what to do when preparing a new version
- Organize and clean up outdated requirements

**Core Features**:
- 📝 Collection: Ask about pain points, frequency, workarounds to confirm understanding
- 📂 Categorization: Check merge possibilities, judge status (ready to do/needs thinking/on hold)
- 🧹 Organization: Regularly clean outdated items, upgrade well-thought-out items
- 🎯 Selection: Analyze candidates based on frequency/workaround feasibility/ROI
- ✅ Archiving: Mark completed, update dependencies

**Trigger**:
```
I want to build a feature
Record a requirement
Organize the backlog
What to do in next version
/backlog-manager
```

---

#### 🗺️ [Project Map Builder](./project-map-builder)
**Description**: Generate or incrementally update high signal-to-noise directory documentation for specified directories

**Use Cases**:
- Need to generate project directory overview
- Need codebase structure documentation
- Want to update existing PROJECT_MAP.md
- Need to understand project folder structure

**Core Features**:
- 📋 Smart Scope Confirmation: Must ask for folders to scan, never defaults to full repository
- 🔍 Key File Recognition: Automatically identifies entry points, configs, service threads, and other critical files
- 📝 Incremental Updates: Only does incremental updates when PROJECT_MAP.md exists, never full rewrites
- 🎯 Multi-directory Support: Supports single or multiple directories (merge or generate separately)
- ⚠️ Explicit Annotation: Clearly marks uncertain areas as "assumption" or "unconfirmed"

**Trigger**:
```
Generate project map
Update PROJECT_MAP
Generate directory documentation
/project-map-builder
```

---

#### 📅 [Version Planner](./version-planner)
**Description**: Decompose product requirements into executable progressive version roadmap (V0.1 MVP → V1.0)

**Use Cases**:
- Need to break down product versions
- Want to plan MVP (Minimum Viable Product)
- Need to implement features in stages
- Uncertain about priorities and development order

**Core Features**:
- 🎯 Value First: Prioritize solving users' biggest pain points, not the hardest technical challenges
- 🚀 Quick Validation: MVP designed to work in 2-3 days, avoiding over-engineering
- 📋 Clear Boundaries: Each version clearly defines "what to do" and "what not to do"
- 🔄 Progressive Delivery: Each version can be used independently, not dependent on future versions
- ✅ Measurable: Each version has clear validation points and completion criteria

**Trigger**:
```
Break down versions
Version planning
How to do MVP
Implement in stages
/version-planner
```

---

#### ✍️ [Writing Assistant](./writing-assistant)
**Description**: Automatically selects optimal writing route based on viewpoint clarity, covering complete flow from thought mining to final draft

**Use Cases**:
- Want to write an article but thoughts are unclear
- Need to organize topic and core viewpoint
- Need to organize article framework and logic
- From scattered ideas to complete article

**Core Features**:
- 🔍 Smart Diagnosis: Quickly assess viewpoint clarity and choose optimal route
- 💭 Thought Mining: When viewpoint is fuzzy, use guided dialogue to extract scattered ideas
- 🎯 Topic Selection: Extract core topic and key message from insights
- 📐 Framework Polishing: Organize article logic structure, ensure clear expression
- ✍️ Content Production: Write complete article based on framework, maintain user's style

**Trigger**:
```
I want to write XX
Help me organize my topic
How to form a framework
Help me organize my thoughts
/writing-assistant
```

---

#### 📝 [Weekly Report](./weekly-report)
**Description**: Helps users organize weekly reports with complete logic to showcase work value and boundaries

**Use Cases**:
- Need to organize a week's work content
- Want to clearly demonstrate work value and achievements
- Need to explain problems and challenges encountered
- Organize next week's priorities

**Core Features**:
- 📋 Material Collection: Guided dialogue to collect weekly work content
- 🗂️ Categorization: Flexibly choose appropriate module classification based on role
- 🔍 Information Supplement: Ask about background, results, value, status, and next steps
- ✅ Discussion & Adjustment: Confirm expression habits and logical completeness
- 📄 Document Output: Generate well-structured weekly report document

**Trigger**:
```
Write weekly report
Weekly report
Organize weekly report
Organize work
/weekly-report
```

---

#### 🎯 [Priority Judge](./priority-judge)
**Description**: Determine priorities from chaotic to-do items and decide what to do now

**Use Cases**:
- Have many things to do, don't know where to start
- Want to quickly figure out what to do today/this week
- Need to judge priorities based on objective criteria
- Avoid wasting time on things not thought through

**Core Features**:
- 📝 Collect To-dos: Record all things to do
- 🔍 Status Inquiry: Understand clarity and deadline of each item
- ⚖️ Priority Judgment: Make decisions based on clarity and deadline
- 🎯 Focus Action: Focus on only 1-2 most important things each time
- 📋 Documentation: Generate priority list document

**Trigger**:
```
I have many things to do
Help me sort it out
Prioritize
What should I do today
Let me review
/priority-judge
```

---

#### 🤝 [Thinking Partner](./thinking-partner)
**Description**: Accompany you to clarify the situation from chaos, lock core problems, break down bottlenecks, co-create solutions, and land actions

**Use Cases**:
- Facing complex problems and don't know where to start
- Have many ideas but can't sort out priorities
- Need someone to think through things with you
- Avoid getting lost in details and losing direction

**Core Features**:
- 📝 Information Gathering: Guided questioning to see the big picture
- 🎯 Lock Core Problem: Find the most critical one from a bunch of problems
- 🔍 Break Down Bottlenecks: Layer-by-layer questioning to find the real root cause
- 💡 Co-create Solutions: Supplement and refine based on your ideas
- ✅ Action Plan: Turn discussion conclusions into executable actions

**Trigger**:
```
I'm confused now, help me sort it out
I don't know what to do about this
Think through this problem with me
/thinking-partner
```

---

#### 🎨 [UI Design Assistant](./ui-design)
**Description**: UI style modification collaboration workflow. Reduce communication deviation and avoid wasting tokens through structured process

**Use Cases**:
- Need to modify page styles and layouts
- Adjust spacing, colors, component combinations
- UI detail optimization and fine-tuning
- Avoid guessing when changing code

**Core Features**:
- 📸 Screenshot Positioning: Confirm current state with screenshots
- 📐 Status Description: Draw current layout with ASCII
- 🎯 Solution Selection: Provide 2-3 visualized solutions
- 🛠️ Minimal Changes: Only change parts involved in selected solution
- 🔄 Iterative Refinement: Execute specific small modifications

**Trigger**:
```
Modify the layout of this page
Adjust the style here
The spacing is not quite right
/ui-design
```

---

#### 🔍 [GitHub Repo Search](./github-repo-search)
**Description**: Help users search and filter GitHub open source projects, output structured recommendation reports

**Use Cases**:
- Looking for open source projects in a specific direction
- Need to compare multiple similar projects
- Want to understand technology stack selection options
- Looking for tools ready to use or for secondary development

**Core Features**:
- 📝 Requirement Convergence: Confirm topic, quantity, sorting mode, target form
- 🔍 Query Breakdown: 5-10 query groups covering synonyms, scenario words, technical terms
- 🏷️ Repository Classification: Framework/Application/Memory/MCP/Catalog/Vertical/Methodology layers
- 📊 Quality Refinement: Comprehensive weighted ranking (relevance/applicability/activity/maturity)
- 📋 Structured Report: Understandable, comparable, decision-ready, actionable candidate repository list

**Trigger**:
```
Help me find open source projects
Search GitHub for XX
Looking for repositories in XX direction
Open source project recommendations
/github-search
```

---

### 🚀 Quick Start

#### Installation

**Using Codex or Claude Code CLI**

If you're using Codex or Claude Code CLI, simply tell the AI:

```
Install this GitHub repository: https://github.com/yourusername/云舒的Skills搭子们
```

The AI will automatically install it for you!

**Manual Installation**

Clone this repository to your local Skills directory:

```bash
# Claude Code default Skills directory is usually ~/.claude/skills/
cd ~/.claude/skills/

# Clone this repository
git clone https://github.com/yourusername/云舒的Skills搭子们.git
```

Alternatively, you can copy individual Skills you need to your Skills directory.

#### Usage

In Claude Code CLI, you can use them by:

```bash
# Use Image Assistant
/image-assistant

# Use Thought Mining
/thought-mining

# Use PRD Doc Writer
/prd-doc-writer

# Use Design Exploration
/design-exploration

# Use Requirement Change Workflow
/req-change-workflow

# Use Lesson Builder
/lesson-builder

# Use Backlog Manager
/backlog-manager

# Use Project Map Builder
/project-map-builder

# Use Version Planner
/version-planner

# Use Writing Assistant
/writing-assistant

# Use Weekly Report
/weekly-report

# Use Priority Judge
/priority-judge

# Use Thinking Partner
/thinking-partner

# Use UI Design Assistant
/ui-design

# Use GitHub Repo Search
/github-search
```

Or simply describe your needs in conversation, and the relevant Skill will trigger automatically.

**📚 Check Usage Examples**

Want to learn how to use each Skill? Check out the [Usage Examples](./EXAMPLES.md) for detailed scenarios and expected outputs.

---

### 📂 Project Structure

```
.
├── README.md                    # Project documentation
├── LICENSE                      # MIT License
├── CHANGELOG.md                 # Changelog
├── EXAMPLES.md                  # Usage examples
├── image-assistant/             # Image Assistant
│   ├── SKILL.md                # Skill definition file
│   ├── stages/                 # Detailed stage descriptions
│   ├── templates/              # Style templates and layout templates
│   ├── examples/               # Usage examples
│   └── scripts/                # Batch image generation scripts
├── thought-mining/              # Thought Mining Assistant
│   ├── SKILL.md                # Skill definition file
│   ├── stages/                 # Detailed stage descriptions
│   ├── templates/              # Template files
│   └── examples/               # Usage examples
├── prd-doc-writer/             # PRD Doc Writer
│   ├── SKILL.md               # Skill definition file
│   ├── assets/                # Template resources
│   └── references/            # Reference docs and examples
├── design-exploration/         # Design Exploration
│   ├── SKILL.md               # Skill definition file
│   └── templates/             # Requirements summary template
├── req-change-workflow/        # Requirement Change Workflow
│   ├── SKILL.md               # Skill definition file
│   ├── references/            # Templates and checklists
│   └── scripts/               # Helper scripts
├── lesson-builder/             # Lesson Builder
│   └── skill.md               # Skill definition file
├── backlog-manager/            # Backlog Manager
│   └── SKILL.md               # Skill definition file
├── project-map-builder/        # Project Map Builder
│   └── SKILL.md               # Skill definition file
├── version-planner/            # Version Planner
│   └── SKILL.md               # Skill definition file
├── writing-assistant/          # Writing Assistant
│   ├── SKILL.md               # Skill definition file
│   ├── stages/                # Detailed stage descriptions
│   └── templates/             # Template files
├── weekly-report/             # Weekly Report
│   └── SKILL.md              # Skill definition file
├── priority-judge/            # Priority Judge
│   └── skill.md              # Skill definition file
├── thinking-partner/          # Thinking Partner
│   └── SKILL.md              # Skill definition file
├── ui-design/                 # UI Design Assistant
│   └── SKILL.md              # Skill definition file
└── github-repo-search/        # GitHub Repo Search
    └── SKILL.md              # Skill definition file
```

---

### 🤝 Contributing

Issues and Pull Requests are welcome! If you have any suggestions or find bugs, please feel free to let me know.

---

### 📄 License

This project is open source under the [MIT License](./LICENSE).

---

### 📧 Contact

For questions or suggestions, please contact via GitHub Issues.

---

Made with ❤️ by Yunshu
