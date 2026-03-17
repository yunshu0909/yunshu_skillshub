# 更新日志 / Changelog

所有重要的项目变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### 新增 / Added
- 📦 **需求池管理** (Backlog Manager)
  - 6 步结构化流程：收集 → 归类 → 写入 → 整理 → 筛选 → 归档
  - 痛点驱动，不做假设性规划
  - AI 整理，用户决策
  - 支持需求合并和状态升档
  - 基于频率/可绕过性/ROI 的筛选分析

- 🎨 **新功能设计探索** (Design Exploration)
  - 7 步结构化流程：需求收敛 → 技术调研 → ASCII 批量探索 → HTML 设计稿 → 全状态覆盖 → 需求总结
  - 一次出 5-8 个 ASCII 方案供选择
  - 全状态覆盖（正常/加载/空态/错误/边界）
  - 交互行为规则表，前端开发直接对照实现
  - 产出 3 个文件：需求总结.md、设计稿.html、全状态设计参考.html

- 🤝 **思考拍档** (Thinking Partner)
  - 5 步结构化流程：信息获取 → 锁定核心问题 → 拆解卡点 → 共创解法 → 落地计划
  - 基于"主次矛盾"思维模型，帮用户找到核心问题
  - 严格的阶段里程碑确认机制
  - 共创式解法讨论，不是单向给答案
  - 落地计划包含"做什么"和"不做什么"

- 🎨 **UI 样式修改助手** (UI Design)
  - 结构化 UI 修改协作流程
  - ASCII 布局图辅助沟通
  - 方案选择机制（2-3 个可视化方案）
  - 最小改动原则，避免过度修改
  - 微调迭代流程

- 🎨 **配图助手** (Image Assistant)
  - 5 个完整的工作阶段：需求澄清、配图规划、文案定稿、提示词封装、迭代润色
  - 统一风格的 16:9 信息图提示词生成
  - 多种配图模板（封面、对比图、洞察卡片、漫画等）
  - 批量生图脚本支持
  - 完整的风格块和 API 配置模板

- 🧠 **记忆系统初始化** (Memory Init)
  - 一键部署记忆系统：CLAUDE.md + MEMORY.md + memory/ 目录
  - 交互式模式：引导式收集角色、用途、风格偏好
  - Quick 模式：用默认模板快速生成，之后自行修改
  - 自动检测已有文件，避免覆盖
  - 固定记忆协议模板，保持跨项目一致性
  - 支持长期记忆 + 每日记忆分层管理

- 🔍 **GitHub 开源项目搜索助手** (GitHub Repo Search)
  - 四环节九步结构化流程：需求收敛 → 检索执行 → 质量精炼 → 交付迭代
  - 5-10 组检索词拆解，平衡召回率与相关性
  - 仓库归属类型分类（框架层/应用层/记忆层/MCP层/目录清单层等）
  - 综合权重排序（相关性/场景适用性/活跃度/工程成熟度）
  - 结构化推荐报告，可理解、可比较、可决策、可直接行动

### 计划中 / Planned
- 更多示例和最佳实践文档
- 视频教程
- 社区贡献的 Skills

---

## [1.0.0] - 2026-01-19

### 新增 / Added
- 🧠 **思维挖掘助手** (Thought Mining)
  - 5 个完整的工作阶段：思维挖掘、选题确定、观点验证、写作辅助、最终审核
  - 洞察记录模板和写作记录模板
  - 完整案例参考

- 📋 **PRD 文档撰写助手** (PRD Doc Writer)
  - 以用户故事为核心的需求文档撰写流程
  - ASCII 线框图支持
  - Mermaid 图表集成（流程图、状态图、时序图）
  - 阶段性确认机制
  - PRD 版本管理（总集/台账）

- 🔄 **需求变更工作流** (Requirement Change Workflow)
  - 7 步标准化变更流程
  - 需求澄清模板
  - 回归测试清单
  - 决策日志模板
  - 影响扫描脚本

### 文档 / Documentation
- 中英双语 README
- MIT 开源许可证
- 项目结构说明
- 快速开始指南
- 支持 Codex 和 Claude Code CLI 安装

---

## 版本说明 / Version Notes

### [Unreleased]
- 尚未发布的变更

### [1.0.0] - 2026-01-19
- 首次发布
- 包含 3 个核心 Skills

---

[Unreleased]: https://github.com/你的用户名/云舒的Skills搭子们/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/你的用户名/云舒的Skills搭子们/releases/tag/v1.0.0
