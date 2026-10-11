"""单独核对：out/ 里的图是否完整可解码，imagegen 收到的 prompt 是否与 prompts/ 逐字一致。
Codex 自己执行本 skill（直接用内置 imagegen、不调 render_codex.py）时，出完图跑这个。

用法：python3 verify_log.py <任务目录> [--since "2026-10-02 15:00"] [--only 前缀]
默认核对最近 6 小时的会话日志。退出码：0 全部成功且逐字，1 有问题。结果写 logs/report.json。
"""
import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from _lib import die, prompt_files, valid_image, verify_verbatim

ap = argparse.ArgumentParser(); ap.add_argument("job"); ap.add_argument("--since", default=""); ap.add_argument("--only", default="")
a = ap.parse_args()
job = Path(a.job).resolve()
since = datetime.strptime(a.since, "%Y-%m-%d %H:%M") if a.since else datetime.now() - timedelta(hours=6)
prompts = prompt_files(job, a.only)
if not prompts:
    die(f"错误：{job / 'prompts'} 里没有提示词")
hit, note = verify_verbatim({p.stem: p.read_text(encoding="utf-8") for p in prompts}, since)
rows = []
for p in prompts:
    ok, size = valid_image(job / "out" / f"{p.stem}.png")
    rows.append({"name": p.stem, "ok": ok, "size": size, "prompt_verbatim": p.stem in hit, "text_on_image": "未核验"})
    print(f"{p.stem:<16} {'成功' if ok else '缺图/损坏'}  {size:<10} {'提示词逐字' if p.stem in hit else '提示词未核到逐字'}")
(job / "logs").mkdir(exist_ok=True)
(job / "logs" / "report.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
bad = [r for r in rows if not (r["ok"] and r["prompt_verbatim"])]
print(f"图 {sum(r['ok'] for r in rows)}/{len(rows)}，提示词逐字 {len(hit)}/{len(rows)}（{note}，自 {since:%m-%d %H:%M}）")
print("注意：图上实际画出的字没有检查，交付前要逐张看图。")
sys.exit(1 if bad else 0)
