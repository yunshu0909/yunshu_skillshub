"""按风格卡重建 styles/README.md 索引，并检查档位和样张数是否对得上。写回样张、改档位后跑一次。

档位规则：待验证 = 1 张；特定 = 2 张；常用 = 3–4 张；主力 = ≥5 张且在 ≥2 类场景被选中（主力需人工判断，脚本只提醒）。
只管内置风格（skill 目录里的 styles/）；你自己新增的风格不需要跑这个。
用法：python3 update_index.py
"""
import argparse
import re
from _lib import STYLES

argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()

order = {"主力": 0, "常用": 1, "特定": 2, "待验证": 3}


def expect(n):
    return "待验证" if n <= 1 else "特定" if n == 2 else "常用" if n <= 4 else "主力"


rows, warns = [], []
for f in sorted(STYLES.glob("[SN][0-9][0-9]-*.md")):
    t = f.read_text(encoding="utf-8")
    sid, name = f.stem.split("-", 1)
    tier = re.search(r"档位：\*\*(.+?)\*\*", t).group(1)
    n = len(re.findall(r"`samples/[^`]+`", t))
    if "```style" not in t:
        warns.append(f"{f.name}: 缺 ```style 代码块")
    t2 = re.sub(r"（被作者选中 \d+ 张）", f"（被作者选中 {n} 张）", t)
    if t2 != t:
        f.write_text(t2, encoding="utf-8")
    if expect(n) != tier and not (tier == "常用" and n >= 5):
        warns.append(f"{sid} {name}: 档位写的是「{tier}」，按 {n} 张样张应为「{expect(n)}」")
    rows.append((order.get(tier, 9), -n, sid, name, re.search(r"类别：(\S+)", t).group(1), tier, n, re.search(r"- 适合：(.+)", t).group(1), f.name))
rows.sort()
tbl = "\n".join(f"| {sid} | [{name}]({fn}) | {cat} | {tier} | {n} | {fit} |" for _, _, sid, name, cat, tier, n, fit, fn in rows)
(STYLES / "README.md").write_text(f"""# 风格库索引

{len(rows)} 种风格，每种都有样张，样张来自作者实测时标过「喜欢」的图；你自己新增的风格放在 `~/.image-render/styles/`，不在这个索引里。

档位：**主力**（≥5 张、跨 ≥2 类场景都被选中）→ **常用**（3–4 张）→ **特定**（2 张，碰到合适内容才用）→ **待验证**（1 张）。

| 编号 | 风格 | 类别 | 档位 | 选中张数 | 适合 |
|---|---|---|---|---|---|
{tbl}

每张卡：风格块（```style 代码块，脚本按它提取，只写长什么样、不写版式）+ 叙事语法 + 文字放在哪 + 已知坑 + 样张。
新增风格：复制任意一张卡改写，编号接着往下排；样张放 `samples/`；改完跑 `scripts/update_index.py`。
""", encoding="utf-8")
for w in warns:
    print("提醒", w)
print(f"索引已重建：{len(rows)} 种风格，{len(warns)} 条提醒")
