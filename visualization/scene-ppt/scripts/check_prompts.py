"""出图前检查 adapt/ 里的画面文件。有错误就退出码 1。

检查：两段标题完整；第一句是实测过的画幅；画面描述里的「」都在文字清单里；
清单每条形如「- 角色：「文字」」且引号成对；文件名合法、风格卡存在；写了主体占比（提醒）；字数（标题 ≤ 20、其他 ≤ 22、最多 10 处，提醒）。
无字图：清单里写一行「- 无」。
用法：python3 check_prompts.py <任务目录>
"""
import re
import sys
from pathlib import Path
from _lib import RATIOS, parse_adapt, quoted, split_code, style_card

if len(sys.argv) != 2:
    raise SystemExit(__doc__)
job = Path(sys.argv[1]).resolve()
files = sorted((job / "adapt").glob("*.txt"))
if not files:
    raise SystemExit(f"错误：{job / 'adapt'} 不存在或没有画面文件")
errors, warns = [], []
for f in files:
    name = f.name
    try:
        _, sid = split_code(f.stem)
        style_card(sid)
    except ValueError as e:
        errors.append(f"{name}: {e}"); continue
    text = f.read_text(encoding="utf-8")
    body, texts = parse_adapt(text)
    if body is None:
        errors.append(f"{name}: 缺【画面与版式】或【必须逐字放入的文字（唯一真值）】（标题要写全）"); continue
    if re.search(r"[「」]", re.sub(r"「[^「」]+」", "", text)):
        errors.append(f"{name}: 「」不成对或顺序反了")
    ratio = re.match(r"(\d+:\d+)", body)
    if not ratio:
        errors.append(f"{name}: 【画面与版式】第一句要先写画幅，如「16:9 横版。」")
    elif ratio.group(1) not in RATIOS:
        errors.append(f"{name}: 画幅 {ratio.group(1)} 没实测过，只用：{'、'.join(RATIOS)}")
    stray = set(quoted(body)) - set(quoted(texts))
    if stray:
        errors.append(f"{name}: 画面描述里的「」内容不在文字清单里，会被画出来：{'、'.join(stray)}")
    head_rest, *rest = texts.splitlines() or [""]
    if head_rest.strip():
        errors.append(f"{name}: 文字清单标题后面要换行再写条目")
    lines = [l.strip() for l in rest if l.strip()]
    if lines != ["- 无"]:
        if not lines:
            errors.append(f"{name}: 文字清单为空（无字图请写一行「- 无」）")
        for l in lines:
            if not re.fullmatch(r"- [^「」]*「[^「」]+」", l):
                errors.append(f"{name}: 清单格式应为「- 角色：「文字」」，这行不对：{l}")
    items = [(re.match(r"- ([^「」：:]*)", l).group(1), quoted(l)[0]) for l in lines if lines != ["- 无"] and quoted(l) and re.match(r"- ", l)]
    if len(items) > 10:
        warns.append(f"{name}: 文字 {len(items)} 处，超过「1 个标题 + 2–9 处」")
    for role, s in items:
        limit = 20 if "标题" in role and "副" not in role else 22
        if len(s) > limit:
            warns.append(f"{name}: 「{s}」{len(s)} 个字，超过 {limit} 字（标题 ≤ 20，其他每条 ≤ 22，按字符数算）")
    if not re.search(r"[一二三四五六七八九两半]成|分之|占|两行|两列|竖排|并排", body):
        warns.append(f"{name}: 没写主体占画面多大（容易画得很空）")
for w in warns:
    print("提醒", w)
for e in errors:
    print("错误", e)
print(f"检查 {len(files)} 个画面：{len(errors)} 个错误，{len(warns)} 个提醒")
sys.exit(1 if errors else 0)
