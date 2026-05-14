# Stage 1：题目收敛（必经卡点，禁止 AI 拍）

> **这一步如果错了，后面所有调研都白干**。所以必须用 AskUserQuestion 让用户勾选，不要让 AI 替用户做决定。

---

## 操作流程

### Step 1.1：判断主题是否需要收敛

用户说"我要学 X"时，X 几乎总是太大。判断标准：

- 如果 X 是"一个具体技术 / 一个具体工具 / 一个具体产品"（如"learn how to use Aider"）→ 可能不需要收敛，确认一次即可
- 如果 X 是"一个领域 / 一类技术 / 一个概念"（如"提示词" / "记忆系统" / "MCP"）→ **必须收敛**

### Step 1.2：拆切片

根据主题领域，给出 4 个核心切片（覆盖完整领域）。每个切片要：
- **互斥**（不重叠）
- **完备**（覆盖该领域大部分内容）
- **具体**（不是抽象类别，是用户能 get 到的方向）

#### 拆切片的方法论

按"4 个不同维度"切：

1. **基础维度**：基础概念 / 主流方法 / 学派
2. **新形态维度**：当下最新的形态 / 趋势 / 新概念
3. **真物维度**：可看到的真实代码 / 顶级案例 / 大厂实现
4. **应用维度**：工具生态 / 工程化 / 产品落地

具体落地时切片名要贴主题：

| 主题 | 切片 | 具体覆盖（用作 AskUserQuestion description） |
|---|---|---|
| **提示词** | 实战写作 + Claude 实践 | 怎么写出能用的 prompt，含 Claude 特定技巧（XML 标签、prefill、role、思考块、example placement） |
| 同上 | Agent 时代 | system prompt 设计、tool description 写法、subagent 协调、context 工程、记忆与状态管理 |
| 同上 | 顶级公开案例 | Cursor / Claude Code / Devin / v0 / Bolt / Lovable / Replit / Aider / Cline 等被泄露或公开的真实 system prompt |
| 同上 | 工程化管理 | 提示词模板/变量/版本控制/A/B 测试/评估指标，与提示词管理产品相关 |
| **记忆系统** | Memory tool 基础 | 各家 memory tool API（Anthropic / OpenAI）、自动注入机制、view/create/str_replace 接口 |
| 同上 | Agent 长程记忆 | 跨 session 持久化、ASSUME INTERRUPTION 范式、状态文件分层（CLAUDE.md / NOTES.md / TodoWrite） |
| 同上 | CLAUDE.md 模式 | 项目级记忆文件、自学习上下文设计、记忆 protocol 的 prompt 注入 |
| 同上 | 记忆系统产品对比 | Letta / Mem0 / Zep / Cognee / MemGPT 的设计哲学、商业模式、技术路线 |
| **MCP** | MCP 协议规范 | Protocol spec、transport 层（stdio / SSE / streamable HTTP）、capabilities 协商 |
| 同上 | Server 开发 | SDK 使用、tool/resource/prompt 三件套、错误处理、安全模型 |
| 同上 | 顶级 MCP server | 官方 reference servers + 热门第三方 servers 源码拆解 |
| 同上 | 生态与 Skills 关系 | Marketplace 生态、各 client 集成、Skills 和 MCP 的边界与互补 |
| **Claude Skills** | 基础概念 | Skills 是什么、frontmatter 规范、reference/ 目录用法、和 subagent 的关系 |
| 同上 | 编排模式 | Skills 内部如何调用 sub-agent、AskUserQuestion 协议、阶段化流程 |
| 同上 | 顶级 Skills 案例 | 公开仓库里的 Skills 拆解（云舒自己的 + 社区精选） |
| 同上 | Plugin Store 生态 | Anthropic Plugin Store 商业模式、分发机制、各家 fork 的 Skills 集合 |

### Step 1.3：用 AskUserQuestion 问

```
{
  question: "你最关心 <主题> 的哪些切片？（可多选）",
  header: "主题切片",
  multiSelect: true,
  options: [
    { label: "切片 1 名字", description: "具体覆盖什么的解释" },
    { label: "切片 2 名字", description: "..." },
    { label: "切片 3 名字", description: "..." },
    { label: "切片 4 名字", description: "..." }
  ]
}
```

注意 AskUserQuestion 最多 4 个选项。**不要再加第 5 个**——"争议+盲区"是 Agent E 必含，不需要让用户选。

### Step 1.4：处理用户回答

- **全选**：4 个切片都做，调研规模大，预计 30-60 分钟
- **选 1-2 个**：聚焦深入，调研规模中，预计 20-40 分钟
- **选 3 个**：和全选差不多

不管选几个，Agent E（争议+盲区）必选。

### Step 1.5：写 `01-题目确认.md`

```markdown
# 阶段 1 产物：题目确认

## 确认时间
{YYYY-MM-DD}

## 主题
{主题描述} — {勾选切片数量} 个切片

## 切片详情

### 切片 1：{名字}
{具体覆盖什么}

### 切片 2：{名字}
...

## 学习视角

**用户研究视角**为主：
- 不走教材路线，按"我能拿来做什么"组织
- 允许带判断、带视角
- 重点输出：争议焦点 + 盲区清单

## 副作用预期
- 直接用：{用户的产品 / 工作}
- 间接用：选题素材
- 可发布：可整理出文章
```

---

## 反模式（一定要避免）

### ❌ AI 替用户拍主题
"我猜你应该是想学 X 的 Y 方面"——禁止。让用户自己勾。

### ❌ 切片太抽象
"基础 / 进阶 / 高级"——这是教材式切片，不是研究视角。不要用。

### ❌ 切片太碎
切到 8 个、10 个——AskUserQuestion 最多 4 个选项，物理限制。

### ❌ 跳过题目确认直接调研
即使用户说"你直接来吧"——也必须先弹 AskUserQuestion 让她勾切片。题目错了全白干。

---

## 例外

只有这种情况可以省略 AskUserQuestion：

**用户在初始消息里已经明确给出切片**——比如"我要学提示词，从实战写作、Agent 时代、案例和工程化四个角度"——这种情况直接写 `01-题目确认.md` 记录即可。

但**99% 的情况都不是这样**——大部分用户说"我要学 X"就完了。
