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

# 使用需求变更工作流
/req-change-workflow

# 使用课程构建器
/lesson-builder
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
├── req-change-workflow/        # 需求变更工作流
│   ├── SKILL.md               # Skill 定义文件
│   ├── references/            # 模板和清单
│   └── scripts/               # 辅助脚本
└── lesson-builder/             # 课程构建器
    └── skill.md               # Skill 定义文件
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

# Use Requirement Change Workflow
/req-change-workflow

# Use Lesson Builder
/lesson-builder
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
├── req-change-workflow/        # Requirement Change Workflow
│   ├── SKILL.md               # Skill definition file
│   ├── references/            # Templates and checklists
│   └── scripts/               # Helper scripts
└── lesson-builder/             # Lesson Builder
    └── skill.md               # Skill definition file
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
