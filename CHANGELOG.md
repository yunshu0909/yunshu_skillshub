# 更新日志 / Changelog

记录影响使用的变化。日期按 Asia/Shanghai（北京时间）；`Unreleased` 是尚未正式发布的内容。正式版本以 GitHub Tag / Release 为准。

Changes that affect use are recorded here. Dates use Asia/Shanghai time. `Unreleased` contains unpublished work; GitHub tags and Releases identify published versions.

## [Unreleased]

### 调整 / Changed

- 当前整理版保留 **25 个在用 skill，7 个分类**：Coding 9、产品品牌 2、思考 3、学习 2、可视化 3、写作 2、Agent 4。分类路径改变，安装继续使用 skill 名称。
- 文件夹整理 `organize` 并入 Agent 助手，取消单独的小工具分类；`system-study` 属于学习，`github-repo-search` 属于 Coding。
- 开发暂以独立 skills 组合使用：引入或更新 Issue 池、页面方案、后端逻辑设计、PRD 与测试用例、已有需求变更。保留 `dual-agent-collaboration`，不加入 `cross-model-review`；本轮不发布 dev-workflow 插件。
- 中英文 README 按场景解释方法，通过各场景表格介绍全部 25 个 skill 的用途与交付物。
- 重做 README：头图改为七间小屋的“Skills 小岛”地图，“这是什么”和七个场景各配一张同一像素世界的场景图；开发排在最前，正文按场景用表格介绍，结尾加入微信二维码。画面单、提示词和生成记录保存在 `assets/readme/source/readme-20261006/`。
- 移除 EXAMPLES 案例页和产物截图，这一版 README 不放案例。
- 更新日志对齐现有 Release，修正占位链接；旧文档中的 `1.0.0` 保留为历史记录，不再当作可下载的正式版本。

- 优化 README 图片加载：头图与场景图保留原尺寸，轻微有损压缩后，含二维码的图片合计从约 7.06 MB 减至 2.31 MB；保存参数与逐图记录。

### 退役 / Removed

- 本轮移出在用目录：`auto-task`、`project-map-builder`、`backlog-manager`、`prd-auto-test-loop`、`prd-doc-writer`、`lesson-builder`、`plan-report`、`design-exploration`、`macos-product-design`、`ui-design`、`version-planner`、`vision-exploration`、`priority-judge`、`weekly-report`。
- 临时退役目录 `pending/` 已移除。旧版本中的目录可从对应版本或 Git 历史查阅。

## [0.1.0] - 2026-05-19

此节以 [v0.1.0 Release](https://github.com/yunshu0909/yunshu_skillshub/releases/tag/v0.1.0) 的实际发布记录为依据。发布时的技能清单属于该版本，与当前 Unreleased 整理版不同。

### 调整 / Changed

- 重排 PRD 与测试用例 review HTML：树形目录、标题层级、故事字段分组，以及测试用例 13 个字段的三段组织。
- 强化 Markdown 与 HTML 的逐项对应和审阅结构。
- `readable-output` 调整长文组织；`system-study` 更新到其材料版本 v0.3.1。

### 新增 / Added since v0.0.1

- 发布记录列出累计新增：`prd-test-writer`、`case-radar`、`readable-output`、`auto-task`、`macos-product-design`、`prd-auto-test-loop`、`organize`、`system-study`。其中部分已在当前整理版退役，保留名称用于准确描述历史。

## [0.0.1] - 2026-04-09

此节以 [v0.0.1 Release](https://github.com/yunshu0909/yunshu_skillshub/releases/tag/v0.0.1) 的实际发布记录为依据。

### 调整 / Changed

- 多视角深度分析从 5 种视角扩展到 10 种。
- 新增芒格、彼得·蒂尔、乔布斯、贝索斯、张一鸣、任正非视角，移除纳瓦尔视角。
- 补充参考材料编写指南，统一编号与路径，并同步 README。

## 历史文档记录 - 2026-01-19

旧更新日志曾以 `1.0.0` 记录首批内容。目前未找到对应的 GitHub Tag / Release，此处保留文档历史，不把它映射到后来的 v0.1.0。

- 记录了 `thought-mining`、`prd-doc-writer`、`req-change-workflow` 三个核心 skill 及相关模板、参考和脚本。
- 记录了中英文 README、MIT License、项目结构与安装指南。

## 维护方式

每次先把用户可见变化写进 Unreleased，描述新行为、目录或依赖变化，以及旧用法如何迁移。需要发版时，再按确定的版本创建 Tag / Release，把本节归档并填写实际发布日期。

[Unreleased]: https://github.com/yunshu0909/yunshu_skillshub/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yunshu0909/yunshu_skillshub/releases/tag/v0.1.0
[0.0.1]: https://github.com/yunshu0909/yunshu_skillshub/releases/tag/v0.0.1
