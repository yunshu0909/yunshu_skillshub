# Peer Handoff Template

复制本模板，为当前 gate 填写自包含事实。删除空占位，不要把 primary 的结论当作原始事实。

## Gate

`intent | plan | implementation | final`

## 用户原话（逐字）

<raw_user_request>
按时间顺序逐字保留原始请求、纠正和验收反馈。长对话可附 transcript 路径，但这里仍必须摘出会改变目标的原话。
</raw_user_request>

## 真实业务结果

- 用户最终要看到或得到什么：
- 成功时可观察到什么：
- 失败时必须如何表现：

## 范围与权限

- In scope：
- Out of scope：
- 允许的外部写入/发布动作：
- 禁止或尚未授权的动作：

## 事实、推断、假设

### 已证实事实

- 事实 + 证据路径/命令：

### 当前推断

- 推断 + 依据：

### 未验证假设

- 假设 + 若错误会造成的影响：

## 项目上下文

`<artifact_manifest>` 内每行只能写一个真实路径；相对路径按 `--cwd` 解析，包含空格时无需额外引号。

<artifact_manifest>
- /absolute/project/root
- AGENTS.md
- path/to/plan.md
- path/to/diff.patch
</artifact_manifest>

## 当前阶段产物

<validation_evidence>
- Intent contract / plan / diff：
- 变更文件：
- 测试与结果：
- 真实数据、迁移、性能或视觉证据：
</validation_evidence>

## 已知限制与未完成项

<known_gaps>
- 尚未验证：
- 明确没做：
- 需要用户决策：
</known_gaps>

## 请独立挑战

1. 是否准确解决用户真实需求，而不是只满足字面合同？
2. 哪些假设可能让实现“技术正确、产品无效”？
3. 当前阶段有哪些 P0/P1/P2 finding？
4. 还缺哪些证据才能 ACK？

不要修改文件，不要调用另一个模型。直接读取上述原始材料并返回结构化 verdict。
