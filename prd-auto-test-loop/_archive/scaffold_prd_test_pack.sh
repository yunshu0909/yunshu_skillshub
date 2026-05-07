#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "用法: $0 <project_root> <version>"
  exit 1
fi

project_root="$1"
version="$2"
base_dir="$project_root/自动化测试/$version"

mkdir -p "$base_dir/tests/unit" "$base_dir/tests/integration" "$base_dir/tests/e2e"

plan_file="$base_dir/TEST_PLAN.md"
report_file="$base_dir/TEST_REPORT.md"

if [ ! -f "$plan_file" ]; then
  cat > "$plan_file" <<TPL
# TEST_PLAN（$version）

## 测试范围
- PRD：
- 范围内：
- 非范围：

## 用例分层
- Unit：
- Integration：
- E2E：

## 完成门槛
1. 计划内用例全部通过
2. P0 用例通过率为 100%
3. 连续两轮稳定通过
4. 无阻断/严重缺陷遗留
TPL
fi

if [ ! -f "$report_file" ]; then
  cat > "$report_file" <<TPL
# TEST_REPORT（$version）

## 结果摘要
- 日期：
- 结论：

## 执行命令与结果
-

## 分层覆盖
- Unit：
- Integration：
- E2E：

## 剩余风险
-
TPL
fi

echo "已初始化: $base_dir"
echo "测试计划: $plan_file"
echo "测试报告: $report_file"
