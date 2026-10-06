---
name: dual-agent-collaboration
description: 让 Codex 与 Claude Code 通过本机 CLI 组成“主执行者 + 独立审查者”的对称协作闭环。用于用户要求两个模型一起完成、交叉校核、独立审查、修到 ACK，或任务涉及产品需求收敛、复杂方案、跨模块开发、迁移、安全、重要重构和高质量交付时；无论从 Codex 还是 Claude Code 启动，都由当前模型主持，并完整调用另一方完成需求挑战、方案门禁、实现冷审和最终验收。
metadata:
  status: active
  status_updated_at: "2026-10-06"
---

# Codex × Claude 双模型协作

把当前模型设为 primary，把另一个 CLI 模型设为 peer reviewer。Primary 对结果负责；peer 提供独立判断，不共同编辑同一工作树。

核心不变量：

> 先验证“做的是不是用户真正要的”，再验证“方案和代码是否正确”。两个模型对同一份错误合同达成一致，不算成功。

这里的“协作”默认指：primary 完成研究、实现与自测，peer 读取同一批原始证据做独立挑战和校核，primary 再按 finding 修正。Peer 不在共享工作树直接编码；这正是本 Skill 对既有“Codex 主做、Claude Code 独立校核”流程的通用化。若用户明确要双模型分工编码，必须使用独立 worktree，并把合并审查另列为任务，不能复用默认模式偷偷并行写。

## 0. 完整性与效率边界

“所有产品都能使用”指 Skill 可跨项目发现和运行，不表示每个琐碎任务都强制双模型。按比例触发：

- 用户明确要求两个模型协作、交叉校核或“修到 ACK”：完整使用本 Skill。
- 复杂方案、跨模块开发、迁移、安全、重要重构、发布前验收：主动使用本 Skill。
- 低风险、边界明确、容易回退的小修：默认由单模型完成；除非用户点名，不为形式感增加四轮模型调用。

一旦触发本 Skill，就完整走 Intent、Plan、Implementation、Final 四个 gate，不以“提速”为由省略。高效率来自：

- 自动识别 primary 并选择另一 CLI；
- 统一 handoff、schema 与命令，不让每个项目重新发明提示词；
- Intent/Plan 尽早阻止做错需求或走错方案；
- Plan 续接 Intent、修复轮续接 Implementation，只在需要去锚定时冷启动；
- 结构化 fail-closed，避免对半截输出反复人工判断；
- 用 state file 自动判断下一 gate，减少人工记 session 和漏审。

默认 `max` reasoning 是完整协作的质量基线；只有用户明确优先成本/时延时才用环境变量下调，并在最终结果中披露。30 分钟是失败上限，不是预期耗时。

## 1. 选择角色

| 当前启动者 | Peer | 调用参数 |
|---|---|---|
| Codex | Claude Code 最新 Opus | `--peer claude` |
| Claude Code | Codex 当前高质量配置 | `--peer codex` |
| 无法确定 | 让脚本检测；检测冲突则显式指定 | `--peer auto` |

使用本 Skill 的 `scripts/invoke_peer.py`。脚本使用 argv + stdin 调 CLI，不使用 shell 拼接；peer 运行在只读模式，并设置递归保护。

先做命令构造预检：

```bash
python3 <skill-dir>/scripts/invoke_peer.py \
  --peer auto \
  --phase intent \
  --cwd <project-root> \
  --task-id <stable-project-task-id> \
  --add-dir <external-evidence-dir> \
  --prompt-file <handoff.md> \
  --dry-run
```

若 CLI 不存在、未认证、超时或未返回结构化结论，视为 `BLOCKED`，禁止假装已经双模型审查。

`--dry-run` 只证明参数已组装，不能证明 CLI 能启动、权限正确或输出可解析。任何 gate 的完成证据必须来自真实调用。

推荐用 `--task-id`，由 wrapper 按“项目路径 hash + task id”把 state 放入持久的用户状态目录：macOS 使用 `~/Library/Application Support/CodePal/dual-agent-workflows/`，Linux 使用 `$XDG_STATE_HOME/codepal/dual-agent-workflows/` 或 `~/.local/state/...`。同一任务所有 gate 复用稳定 task id；不同任务不得复用。这样不污染仓库，也不会因系统清理 `/tmp` 或重启而丢掉 gate。只有集成方已有自己的状态存储时才显式用 `--state-file`。State 只存 verdict、session ID 和报告 hash，不存 handoff 正文。

## 2. 准备完整 handoff

读取 [references/handoff-template.md](references/handoff-template.md)，为每个门禁提供一份自包含 handoff。必须包含：

- 用户原话与后续纠正，放进 `<raw_user_request>` 标记，必须逐字引用，不能只给 primary 的总结。
- 期望业务结果、可观察行为、范围外事项。
- 当前事实和证据路径；区分事实、推断、假设。
- 项目协议、相关代码/文档、dirty worktree 和权限边界。
- 当前阶段的产物：方案、diff、测试结果、迁移演练或截图。
- 仍未验证的内容和需要 peer 挑战的问题。

把绝对路径或仓库内路径交给 peer，让它直接读原始材料。Artifact manifest 至少包含一个真实存在的绝对路径。不要只贴结论，也不要在 handoff 中暗示“预期 ACK”或泄露你怀疑的 bug。

发送证据前先检查项目根的 `AGENTS.md`、`CLAUDE.md`、安全/隐私文档和用户约束：

- 用户本次明确要求 Claude 与 Codex 协作，视为允许在当前任务范围内调用两端，但仍要排除 token、cookie、凭证和无关个人数据。
- 若是 primary 主动触发，发现禁止外部模型、单一供应商、保密或数据驻留要求时，必须先问用户；未获授权就不调用 peer。
- Handoff 保持“足以完整审查的最小数据集”，优先给受控路径，不复制无关仓库内容。

Claude 的读取边界默认是 `--cwd`。任何证据在 cwd 外时，必须显式传入其父目录：

```bash
--add-dir /absolute/read-only/evidence-directory
```

Claude 仍只开放 `Read/Grep/Glob`，所以 add-dir 不授予写能力。Peer 如果读不到 manifest 中的材料，必须 `BLOCKED`；不得忽略后继续 ACK。

Codex 的 read-only sandbox 限制写入但允许读取 manifest 中的绝对路径，因此没有 `--add-dir` 参数。首次安装或 Codex CLI 版本变化时，必须用 cwd 外临时证据做一次真实读取探针；读不到就 `BLOCKED`，不得假设行为不变。

Wrapper 会强制检查四段机器标记：

```text
<raw_user_request>...</raw_user_request>
<artifact_manifest>...</artifact_manifest>
<validation_evidence>...</validation_evidence>
<known_gaps>...</known_gaps>
```

标记只能防遗漏，不能判断内容是否诚实；primary 仍必须保证其中是原始事实。

以下任一缺失时不得获得最终 ACK：

- 用户原话；
- 可验收的产品结果；
- 关键产物路径；
- 实现阶段的 diff 与验证证据；
- 已知限制和未完成项。

## 3. 运行四个门禁

### Gate A：Intent

在设计或编码前，让 peer 独立回答：

1. 用户真正想得到什么，而不是字面要求了什么？
2. 哪些产品假设未经验证？
3. 当前边界是否会造成“技术正确、业务无效”？
4. 哪些验收必须使用真实数据或用户可见行为？

```bash
python3 <skill-dir>/scripts/invoke_peer.py \
  --peer auto --phase intent --cwd <project-root> \
  --task-id <stable-project-task-id> \
  --prompt-file <intent-handoff.md>
```

`NOT_ACK` 时先修正需求合同。不要开始实现。若 primary 不同意 finding，用原始证据反驳并续审，不要因 peer 权威而盲从。

### Gate B：Plan

Intent ACK 后，把已接受的需求合同、技术调研和完整计划交给同一 peer session 续审：

```bash
python3 <skill-dir>/scripts/invoke_peer.py \
  --peer <peer> --phase plan --cwd <project-root> \
  --task-id <stable-project-task-id> \
  --session-id <intent-session-id> \
  --prompt-file <plan-handoff.md>
```

Plan 必须覆盖正常路径、失败路径、迁移/回滚、隐私、安全、性能、真实数据验证和测试矩阵。Peer 必须重新对照用户原话，不能只检查计划内部自洽。

### Gate C：Implementation

Primary 独立编码、测试和记录证据。Peer 默认不修改文件，避免共享工作树冲突和责任模糊。Claude peer 只开放 `Read/Grep/Glob`；Codex peer 使用 `sandbox_mode=read-only + approval_policy=never`。需要 `git diff` 时由 primary 预先生成只读文件并加入 artifact manifest。

实现完成后开启一个**新的冷审 session**，不要续接 Plan session，降低锚定效应。Handoff 必须包含：

- 原始需求与已接受合同；
- 计划和变更文件；
- 完整 `git diff` 可读路径；
- 测试命令、通过数和失败输出；
- 真实数据/视觉/迁移证据；
- 没做什么及原因。

```bash
python3 <skill-dir>/scripts/invoke_peer.py \
  --peer auto --phase implementation --cwd <project-root> \
  --task-id <stable-project-task-id> \
  --add-dir <diff-or-evidence-dir> \
  --prompt-file <implementation-handoff.md>
```

Peer 按 P0/P1/P2/note 报告 finding。Primary 修复后，用该 implementation session ID 续审，逐项关闭旧 finding，同时要求 fresh scan，不能只确认补丁表面存在。

### Gate D：Final

只有以下条件全部满足才进入 final：

- Intent 与 Plan 已 ACK；
- Implementation 无未关闭 P0/P1；
- Primary 自己跑完必要验证；
- 用户可见结果与真实数据已验证；
- 没有把 out-of-scope 当成“用户不需要”；
- 未完成项已明确，不伪装完成。

高风险任务、需求中途变化或真实验收推翻过方案时，Final 使用新的冷审 session；否则可续接 implementation session。

Wrapper 用 `--task-id` 自动定位 state（或由集成方显式传 `--state-file`），机器执行 gate 顺序：

- `intent` 创建 workflow。
- `plan` 只接受已 ACK 的 intent，并必须续接 intent session。
- 首轮 `implementation` 必须是新冷审 session；修复轮必须续接该 implementation session。
- `final` 只接受 intent / plan / implementation 全部 ACK。
- 任一 gate 已 ACK 后不可覆盖；用户纠正需求时换一个新的 state file，从 intent 重开。

最终只接受三个 verdict：

- `ACK`：合同和当前阶段证据充分，无阻断 finding。
- `NOT_ACK`：存在需要修复或重新定需求的问题。
- `BLOCKED`：缺少证据、权限、CLI 或用户决策，无法诚实判断。

## 4. 处理审查循环

每轮遵循：

```text
peer finding
  → primary 用证据复核
  → 接受并修复，或有证据地拒绝
  → primary 自测
  → resume 同一审查 session 逐项关闭
  → 要求 fresh scan
  → ACK / NOT_ACK / BLOCKED
```

规则：

- Peer 不是投票器；结论必须带文件、行为或证据。
- Primary 不能把测试职责外包给 peer。
- 不并行修改同一工作树。需要 peer 编码时必须使用独立 worktree，并由 primary 审查后再合并；默认不这么做。
- 不因 token、时间或 CLI 卡住而把未完成写成 ACK。
- Peer 最后停在 tool request、plan 或无 verdict，属于未完成；不要人工把自然语言残片改写成 ACK，修复调用或续审后重新取得结构化报告。
- 需求被用户验收推翻时，回到 Gate A，旧 ACK 自动失效。

## 5. CLI 调用与续审

脚本参数：

```text
--peer auto|claude|codex
--phase intent|plan|implementation|final
--cwd PROJECT_ROOT
--add-dir DIR           # 可重复；Claude 读取 cwd 外证据时必传
--task-id ID            # 推荐；按项目与任务自动隔离持久 state
--state-file PATH       # 高级用法；与 --task-id 二选一
--prompt-file PATH      # 与 --prompt / stdin 三选一
--prompt TEXT
--session-id ID         # 续审
--timeout-seconds 1800
--save-raw DIR          # 仅在确需保存完整 CLI 事件时使用
--dry-run
```

输出是统一 JSON，至少包含：

```json
{
  "peer": "claude",
  "phase": "implementation",
  "sessionId": "...",
  "verdict": "NOT_ACK",
  "report": {
    "summary": "...",
    "findings": []
  }
}
```

默认不持久化原始 CLI 事件，因为其中可能包含项目内容。只有用户明确需要完整审查日志时才使用 `--save-raw`，并把目录放在安全位置。

模型选择：

- Claude 默认使用 `opus` alias + `max` effort，并启用 safe mode、禁用自定义 MCP、限制为 Read/Grep/Glob；macOS 上再用 `sandbox-exec` 禁止写 cwd/证据目录。用 `DUAL_AGENT_CLAUDE_MODEL`、`DUAL_AGENT_CLAUDE_EFFORT` 覆盖。
- Codex 默认沿用本机配置模型，并强制 `max` reasoning；用 `DUAL_AGENT_CODEX_MODEL`、`DUAL_AGENT_CODEX_REASONING` 覆盖。
- 不硬编码会过期的完整模型版本号。交付时报告 CLI 返回的实际模型或请求模型。

## 6. 完成条件

向用户汇报时说清：

- 谁是 primary、谁是 peer。
- 经过哪些 gate，各 gate 最终 verdict。
- Peer 发现了什么，primary 如何处理。
- Primary 自己跑了哪些验证。
- 仍未完成或需要用户验收的内容。

若 primary 按比例原则判定某个低风险任务不触发本 Skill，必须向用户明确说明“本任务未启用双模型审查”及理由，不能让用户误以为已经发生协作。

首次安装或修改本 Skill 时，Final 还必须有这些可观察证据：

- Codex primary → Claude peer 完成真实 fresh 与 resume，并拿到结构化 verdict 与 state 变化。
- Claude primary → Codex peer 完成真实 fresh 与 resume，并拿到结构化 verdict 与 state 变化。
- 中央仓、Codex、Claude Code 三份目录内容一致。
- Codex 和 Claude Code 各自的新 CLI 会话能发现并触发本 Skill。

任何一项只有 dry-run、mock 或“理论上支持”，都不能写成已经完成。

Final handoff 必须把中央源目录和两个实际安装目录的绝对路径全部放进 `<artifact_manifest>`。Claude peer 审查时，还要为 cwd 外的每个安装目录传 `--add-dir`，让 peer 自己逐文件比较；任何目录不可读就 `BLOCKED`。

“三份一致”的唯一口径是：排除 `__pycache__/`、`*.pyc`、`*.pyo`、`.DS_Store` 后，比较全部相对文件路径集合和每个文件的 SHA-256；不得用目录大小、mtime 或抽样代替。

安装或更新采用可回滚顺序：

1. 在每个目标目录的同一父目录复制到唯一 staging 目录，并先做内容比对。
2. 若旧版本存在，将它原子改名为唯一 backup；再把 staging 原子改名为正式目录。
3. 两个目标全部验证一致后才删除 backup。
4. 任一目标失败，恢复所有已替换目标的 backup，清理 staging，并重新做三方一致性检查。

不要直接覆盖一个正在使用的目标目录，也不要在半成功状态下交付。

本 Skill 自带原子分发脚本，先 dry-run 再执行：

```bash
python3 <skill-dir>/scripts/install_skill.py \
  --source <central-skill-dir> \
  --target <codex-skill-dir> \
  --target <claude-skill-dir> \
  --dry-run
```

移除 `--dry-run` 后才会 staging、比对、替换与回滚。脚本排除上述生成物，最终输出统一内容 manifest 的 SHA-256。

本 Skill 的官方结构检查命令是：

```bash
uv run --with pyyaml \
  <skill-creator-dir>/scripts/quick_validate.py \
  <dual-agent-collaboration-dir>
```

预期输出包含 `Skill is valid!`；它只验证 Skill 结构，不替代真实 CLI 与新会话发现测试。

不得说“两个模型都同意，所以一定正确”。只能说：两套独立推理在完整证据上完成了交叉审查，当前没有已知阻断项。
