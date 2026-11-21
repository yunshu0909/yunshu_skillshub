---
name: skill-loader-audit
description: 盘点本机 Claude Code 与 Codex 的 Skill，按最近一段时间的实际使用证据排序。用于找低频技能、按客户端或精确来源启停、预览批量清理，以及恢复本批加载设置。
---

# Skill 使用盘点与加载管理

用户只问“最近用了哪些”时，执行只读盘点。用户要求改动时，按其指定的客户端、时间窗和名称确定范围。两端的同名 Skill 可以独立开关。按名称关闭整个插件、移动文件或断开账号属于不同操作，本工具管理的是 Skill 加载设置。

## 盘点

需要 Python 3.11 或更新版本。找到本 Skill 目录，用下方命令中的 TOOL 表示其中 scripts/skills.py 的绝对路径。通用参数放在子命令之前。

~~~sh
python3 "$TOOL" audit --days 30 --html skills-30d.html --json skills-30d.json
python3 "$TOOL" --client claude audit --days 60
~~~

默认按机器的本地自然日统计，包含当天。用 --days 指定窗口，对照两种窗口时分别运行。HTML 按证据数降序，JSON 含可供选择的来源路径，均写到新文件。对外只分发技能包，盘点输出、计划和恢复凭据留在本机。

- **客户端列出**表示当前客户端在所选工作目录提供了该技能。**目录中存在**可能是文件发现或已安装插件包推断。用 --cwd 指定需要核实的项目。
- **证据数**是能归属的调用、成功读取或支持的脚本执行。一个任务可以留下多条证据。另列去重会话数和最近日期。某些版本不保留直接输入 /skill 或在界面点选技能的记录。Claude 原生末次使用可补一条下界；累积总数不能直接当作窗口用量。
- 0 表示所读记录没有命中。null 或 — 表示缺乏可归属的数据。同名副本、清理过的日志、旧客户端和远程插件可能造成漏计。展示每端的活跃日数和覆盖状态。可重复传入 --exclude-session ID 排除审计会话。
- 工具尊重 CLAUDE_CONFIG_DIR、CODEX_HOME；也可在子命令前传 --claude-home、--codex-home、--agents-root。共享技能目录默认是 ~/.agents/skills/，模拟环境请显式指定测试目录。默认用已安装 CLI 做无模型对话的目录查询，客户端自身可能访问其插件服务。--files-only 跳过这些查询。

## 关闭、开启、恢复

先生成计划，查看实际客户端和目标，再执行用户已授权的那一批。询问使用频率只触发读取。如果用户已明确指定要关闭哪些，核对范围后直接执行。空计划不会修改配置。示例中的名称是占位符。

~~~sh
python3 "$TOOL" plan --action disable --pick 'claude:example' --pick 'codex:example' --out close-plan.json
python3 "$TOOL" apply --plan close-plan.json --receipt close-receipt.json
python3 "$TOOL" restore --receipt close-receipt.json
~~~

- --action enable 显式开启。restore 还原改动前的设置，可还原为“从未设置覆盖”。保留回执。
- 只处理一端时，把 --client claude 或 --client codex 放在子命令之前。Codex 重名时用 --pick 'codex:/absolute/path/to/SKILL.md'。Claude 的覆盖按名称匹配，多来源重名要先厘清影响范围。单个 Skill 的配置可以与其父插件状态不同。
- 要预览近 30 天未见证据的候选，运行下面的命令。自动筛选仅看当下客户端列出、能唯一归属的技能。历史覆盖不完整，或存在客户端点选、斜杠调用等取证盲区时，默认跳过该端。向用户说明覆盖天数与缺口；接受按“现有记录未检出”生成候选时，在下方命令中加 --include-partial。没有活动记录的客户端始终跳过。逐个点名可处理候选清单以外的已发现技能。

~~~sh
python3 "$TOOL" --client codex plan --action disable --unused --days 30 --out unused-plan.json
~~~

- apply 核对配置指纹和目标。遇到过期计划，重新读取当前状态并重新生成。父插件开关、项目覆盖或远程同步都可能影响结果。写入后在**同一目录的新客户端进程**重新运行 audit，分别报告已写入、实际列出及无法验证的条目。
- 常规关闭只改本机用户设置，保留技能文件。计划和回执使用新的本机文件名。恢复时如果目标设置已被另行修改，先核实当前值。

## 分发与安装

压缩包内有一层 skill-loader-audit/，里面直接含 SKILL.md 和 scripts/。解压后把该文件夹放入需要调用此技能的客户端目录。Codex 用 $CODEX_HOME/skills/（默认 ~/.codex/skills/），Claude Code 用 $CLAUDE_CONFIG_DIR/skills/（默认 ~/.claude/skills/）。重开会话后可说“统计我最近 30 天用了哪些 Skill”或“只关掉 Codex 里我选的这两个”。只装一端也可以从该端盘点两端的本机记录。示例使用 POSIX shell；Windows 可用 py -3.11 或更高版本并传入实际脚本路径。
