# 合格测试用例样板（ground-truth · 照这个判"合格长什么样"）

> 给 AI 的锚：用例必须细到"任何 AI 拿过去照跑都不跑台"。下面两条是真实项目（DeepSeek 网关）写到底的样板——**普通原子用例** 1 条 + **任务类长链路用例** 1 条。模板见 `assets/test-cases-template.md`。

---

## 样板一：普通原子用例（每步动作配预期、数据字面值、带代码依据）

### TC-003 网关健康接口在真实 Key 下返回 provider=deepseek、model=deepseek-v4-pro

- 用例编号：TC-003
- 用例名称：网关健康接口在真实 Key 下返回正确 provider 与 model（**只验这一个原子点**）
- 所属模块/阶段：模块 B 真 Key 基础连通 ／ 阶段1 连通
- 优先级：P0 阻断
- 证据类型：真Key
- 前置条件：
  1. Node ≥16，仓库可跑 npm
  2. 有效 DeepSeek Key 已 `export DEEPSEEK_API_KEY=<真key>`
  3. 本机 22000-22999 端口段无占用（provider-smoke.js:21 随机取该段）
  4. 无其它进程在写 ~/.deepseek-claude
- 测试数据（精确字面值）：
  - 完整命令：`DEEPSEEK_API_KEY=<真key> PROVIDER_SMOKE_PROVIDER=deepseek npm run smoke:provider`（cwd: `deepseek-claude-setup/`）
  - 隐含默认：model=`deepseek-v4-pro`（provider-smoke.js:94 → provider.models[0]，deepseek.js:41）；thinking=`enabled`（provider-smoke.js:101-102）；effort=`high`（provider-smoke.js:108 写死）
- 测试步骤（每步：动作 → 该步预期）：
  1. 动作：执行上述命令 → 预期：stdout 出现 `-- live provider smoke: DeepSeek (deepseek-v4-pro) --`（provider-smoke.js:114）
  2. 动作：脚本建临时配置目录、部署 proxy bundle、随机端口起网关 → 预期：网关 ≤60s 起来，`proxyManager.getHealth()` 返回 health 对象（provider-smoke.js:103-117）
  3. 动作：脚本执行 `assertOk('gateway health', health.provider==='deepseek' && health.model==='deepseek-v4-pro')`（provider-smoke.js:118）→ 预期：`health.provider` 严格 === `"deepseek"` 且 `health.model` 严格 === `"deepseek-v4-pro"`
  4. 动作：观察该断言 stdout → 预期：打印一行 `  OK gateway health`（provider-smoke.js:78），未抛错退出
- 通过标准：步骤3布尔为 true 且步骤4打印 `OK gateway health`，进程未因此 exit 1
- 失败判定与归类：打印 `gateway health failed: <JSON>` → provider/model 不符 → gateway（附 redact health JSON）；exit 2 → 缺 Key（前置2未满足）；网关 60s 未起 → gateway（启动超时）
- 后置/清理：脚本 finally `proxyManager.stop()` + `fs.rmSync(tmp)`（provider-smoke.js:137-140）
- 证据产物：smoke 全量 stdout（含 OK 行）+ 退出码
- 代码依据：provider-smoke.js:94,101-118；deepseek.js:41

---

## 样板二：任务类长链路用例（**明确任务名 + 逐轮发什么 + 逐轮期望**，禁泛化）

> 注意对比：泛描述「测一个长任务看能不能用」是**不合格**的；下面这种"任务名 + 每轮发什么内容原文 + 每轮期望"才是合格。

### TC-013 codex-long 复杂长链路（Codex 跑 TASK-LONG-TODO）

- 用例编号：TC-013
- 用例名称：真实 Codex 经网关打真实 DeepSeek，在 20 轮内完成 TASK-LONG-TODO 并自测自修到 ALL TESTS PASS
- 所属模块/阶段：模块 D 真 Key Codex 闭环 ／ 阶段3 复杂长链路
- 优先级：P0 ｜ 证据类型：真Key
- 前置条件：
  1. 阶段1、阶段2 全过
  2. 有效 `DEEPSEEK_API_KEY`，可执行 `codex` CLI（preflight 通过）
- 测试数据（精确字面值）：
  - **任务名称**：TASK-LONG-TODO —— 从零实现"待办 CLI 工具 + 自带测试 + 自跑自修复"
  - **任务类型**：真实多步骤编程 agent 任务（看懂需求→写多文件→自运行测试→读报错→自修复→直到通过）
  - **覆盖周期**：约 3~20 个工具轮、约 5~15 分钟
  - **轮数规则（写死）**：一轮 = 网关日志一条 `RESPONSES_DONE`（runner grep 计数）；最少 3 轮、最多 20 轮封顶；超 20 轮未收敛 = 失败，归类 **client（模型未在时限收敛）**，与接入失败分开（不评模型质量）
  - **每一轮发什么 / 期望什么（逐轮写死）**：

    | 轮次 | 发给模型的内容 | 期望结果（可观测） |
    |---|---|---|
    | 第 1 轮 | 首轮 verbatim prompt 全文（见下） | 模型发起写文件工具调用，创建 `todo.js` |
    | 第 2 轮 | （agent 自驱，无新增人输入；上下文延续） | 模型创建 `test.js`，内含 ≥3 处 `assert` 且有一处同时读 `todo.js`+`todo.json` |
    | 第 3 轮 | （agent 自驱）执行 `node test.js` | 模型实际跑测试，stdout 可见测试结果 |
    | 第 4~N 轮（若测试未过） | （agent 自驱）按报错改代码后重跑 | 每轮改 1 处后重跑，逐步收敛 |
    | 最后一轮 | （agent 自驱）最终运行 | stdout 含精确行 `ALL TESTS PASS` |

  - **首轮 verbatim prompt（一字不差，照抄发送）**：
    ```
    在当前目录用 Node.js 完成一个命令行待办工具，下面要求全部做完：

    1. 写 todo.js，可执行 CLI，支持三个子命令：
       - node todo.js add "<内容>"：追加一条待办到当前目录 todo.json
         （todo.json 是 JSON 数组，每条形如 {"id":1,"text":"写文档","done":false}）
       - node todo.js list：按 id 升序打印全部待办，每行格式：
         未完成 -> [ ] 1 写文档
         已完成 -> [x] 2 修bug
       - node todo.js done <id>：把该 id 的待办 done 改为 true
    2. 写 test.js，不依赖任何第三方库，只用 Node 内置 assert，覆盖：
       - add 两条后 list 输出恰好两行且按 id 升序
       - done 第 1 条后，该条在 list 里变成 [x]
       - 必须有一个用例同时读取 todo.js 和 todo.json 两个文件内容后再做断言
       - 全部断言通过后，最后一行精确打印一行：ALL TESTS PASS
    3. 运行 node test.js；若失败，修改代码重试，直到看到 ALL TESTS PASS 为止。
    ```
- 测试步骤（每步：动作 → 该步预期）：
  1. 动作：执行 `DEEPSEEK_API_KEY=<真key> CLIENT_E2E_PROVIDER=deepseek CLIENT_E2E_TARGETS=codex-tool CLIENT_E2E_LONG=1 npm run e2e:clients` → 预期：runner 追加 codex-long case，临时 workspace 起隔离 Codex，把首轮 prompt 原文发给模型
  2. 动作：等模型多轮执行 → 预期：网关日志出现 ≥3 次 `RESPONSES_DONE` 且 ≤20 次
  3. 动作：等结束或 900000ms 超时 → 预期：15 分钟内结束，未超时
  4. 动作：runner 读临时 workspace → 预期：存在 `todo.js`/`test.js`/`todo.json`，模型自跑 `node test.js` 输出含精确行 `ALL TESTS PASS`
  5. 动作：runner **独立复跑** `node test.js`（模型猜不到会复跑） → 预期：复跑退出码 0 且 stdout 含 `ALL TESTS PASS`
  6. 动作：grep 本次网关日志切片 → 预期：不含本次 `RESPONSES_FAILED`
- 通过标准：步骤2轮数∈[3,20] 且 步骤3未超时 且 步骤4产物齐+模型 `ALL TESTS PASS` 且 步骤5独立复跑也 `ALL TESTS PASS` 且 步骤6无 `RESPONSES_FAILED`
- 失败判定与归类：超20轮/超时/独立复跑不过 → client（模型未收敛或谎报）；三文件缺但有 ALL TESTS PASS 文本 → client（echo 作弊，被步骤5抓出）；有 `RESPONSES_FAILED` → gateway/provider（发出点 proxy/clients/codex-responses.js:229）；`claude-long` 等 target runner 未实现 → **BLOCKED-待实现，不得标 PASS/SKIPPED**
- 后置/清理：随 run 末尾删除临时根目录
- 证据产物：报告 + redact 日志切片（含 RESPONSES_DONE 计数）+ 临时 workspace 三文件快照（不含 key）
- 代码依据：client-e2e.js:242,256；轮信号 RESPONSES_DONE 见 proxy/clients/codex-responses.js:229；任务定义见本用例测试数据

---

## 自检口诀（产出每条用例前过一遍）

1. 名称只一个原子点？出现"和/且/+"？→ 拆。
2. 每步都有"动作 → 该步预期"？预期是可观测的具体值/日志行？
3. 命令含**每个** env 字面值？JSON 可解析？prompt 一字不差有原文？默认值标 `文件:行`？
4. 任务类：有任务名 + 逐轮"发什么/期望什么"表 + verbatim prompt 全文？**没有逐轮表 = 不合格**。
5. 每条断言能 grep 到 `代码依据 文件:行`？grep 不到的字段=自创=删。
6. 证据类型标了？真Key/抓包分清？capture-only 没冒充"通过"？
7. 失败归类到五类之一？未实现标 BLOCKED 没用 PASS/SKIPPED 掩盖？
