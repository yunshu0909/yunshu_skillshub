"""风格块 × 适配后的画面 × 通用约束 → prompts/。只拼接，不改任何一段原文。

用法：python3 build_prompts.py <任务目录>
- adapt/<图号>-<风格编号>.txt 必需；任务目录 common.txt 可覆盖默认约束。
- adapt/ 里已经删掉的画面，对应的旧提示词会一并删除，避免继续出图。
- 拼好后再查一遍：整份提示词里的「」必须都在文字清单里（风格块、约束也算）。
"""
import sys
from pathlib import Path
from _lib import TEMPLATES, parse_adapt, quoted, split_code, style_block

if len(sys.argv) != 2:
    raise SystemExit(__doc__)
job = Path(sys.argv[1]).resolve()
adapts = sorted((job / "adapt").glob("*.txt"))
if not adapts:
    raise SystemExit(f"错误：{job / 'adapt'} 不存在或没有画面文件")
common_file = job / "common.txt" if (job / "common.txt").exists() else TEMPLATES / "common.txt"
common = common_file.read_text(encoding="utf-8").strip()
(job / "prompts").mkdir(exist_ok=True)
errors, built = [], {}
for f in adapts:
    try:
        _, sid = split_code(f.stem)
        block = style_block(sid)
    except ValueError as e:
        errors.append(str(e)); continue
    text = f.read_text(encoding="utf-8").strip()
    prompt = "\n\n".join(["【风格基准（唯一允许）】\n" + block + "\n整张图只用这一种风格，不得混入其他风格。", text, common]) + "\n"
    _, texts = parse_adapt(text)
    stray = set(quoted(prompt)) - set(quoted(texts or ""))
    if stray:
        errors.append(f"{f.name}: 拼好的提示词里有清单外的「」内容，会被画出来：{'、'.join(stray)}"); continue
    built[f.stem] = prompt
if errors:  # 有任何错误就一份都不写，避免半新半旧
    for e in errors:
        print("错误", e)
    sys.exit(1)
for stem, prompt in built.items():
    (job / "prompts" / f"{stem}.txt").write_text(prompt, encoding="utf-8")
stale = [p for p in (job / "prompts").glob("*.txt") if p.stem not in {f.stem for f in adapts}]
for p in stale:
    p.unlink()
print(f"{len(built)} 份提示词 → {job / 'prompts'}（约束：{common_file.name}）" + (f"；清掉 {len(stale)} 份已删除画面的旧提示词" if stale else ""))
