"""风格选择页：所有带样张的风格（内置 + 你自己新增的），点 ♡ 选风格，一键复制反馈。没有样张的风格不显示。

用法：python3 style_picker.py [输出路径] [--only S01,N24,...]   默认输出到当前目录 风格选择.html
"""
import argparse
import html
import re
from urllib.parse import quote
from pathlib import Path
from _lib import SKILL, all_cards, card_samples, load_settings

ap = argparse.ArgumentParser(); ap.add_argument("out", nargs="?", default="风格选择.html"); ap.add_argument("--only", default="")
a = ap.parse_args()
only = [x.strip() for x in a.only.split(",") if x.strip()]
default = load_settings().get("style", "")
order = {"主力": 0, "常用": 1, "特定": 2, "待验证": 3, "我的": 4}
cards = []
for f in all_cards():
    sid = f.stem.split("-")[0]
    if only and sid not in only:
        continue
    sams = card_samples(f)
    if not sams:
        continue
    t = f.read_text(encoding="utf-8")
    m = re.search(r"档位：\*\*(.+?)\*\*", t); tier = m.group(1) if m else "我的"
    m = re.search(r"- 适合：(.+)", t); fit = m.group(1) if m else "—"
    m = re.search(r"类别：(\S+)", t); cat = m.group(1) if m else "自建"
    cards.append((0 if sid == default else 1, order.get(tier, 9), -len(sams), sid, f.stem.split("-", 1)[1], cat, tier, fit, sams))
cards.sort()
body = ""
for first, _, _, sid, name, cat, tier, fit, sams in cards:
    urls = [html.escape("file://" + quote(str(s)), quote=True) for s in sams[:4]]
    pics = "".join(f'<a href="{u}" target="_blank"><img src="{u}" loading="lazy"></a>' for u in urls)
    cur = ' <span class="tier cur">当前默认</span>' if first == 0 else ""
    body += (f'<figure><div class="pics">{pics}</div><figcaption><b>{sid}</b> · {html.escape(name)} <span class="tier t{order.get(tier, 9)}">作者{tier}</span>{cur}'
             f'<span class="cat">{cat} · 样张 {len(sams)}</span><div class="fit">适合：{html.escape(fit)}</div></figcaption></figure>')
mark = (SKILL / "scripts" / "mark.js").read_text(encoding="utf-8")
page = f'''<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>选配图风格</title><style>
:root{{--bg:#f5f3ee;--card:#fff;--fg:#222;--muted:#777;--line:#e2ded5}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#1b1b1b;--card:#262626;--fg:#eee;--muted:#aaa;--line:#3a3a3a}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 -apple-system,"PingFang SC",sans-serif}}
main{{max-width:1500px;margin:0 auto;padding:20px 16px 90px}} h1{{font-size:24px;margin:0}} .note{{color:var(--muted);font-size:13px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:16px;align-items:start}} @media (max-width:480px){{.grid{{grid-template-columns:1fr}}}}
figure{{margin:0;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden}}
.pics{{display:grid;grid-template-columns:repeat(2,1fr);gap:2px;background:var(--line)}} .pics img{{width:100%;height:150px;object-fit:cover;display:block}}
figcaption{{padding:10px 12px}} .tier{{font-size:12px;border-radius:10px;padding:1px 8px;margin-left:6px;color:#fff}}
.t0{{background:#e0475b}} .t1{{background:#e08a2e}} .t2{{background:#3f8f6b}} .t3{{background:#888}} .t4,.cur{{background:#5b5bd6}}
.cat{{display:block;color:var(--muted);font-size:12px}} .fit{{font-size:13px;margin-top:4px}}
</style></head><body><main><h1>选配图风格</h1>
<p class="note">挑一种当<b>默认风格</b>：以后每次出图都用它，随时可以换。点图片右上角 ♡ 标记，右下角「复制反馈」；也可以直接说编号。想先比一比，就选 3–4 种，用你自己的一张图各出一版。档位是作者按自己用的次数排的，仅供参考。</p>
<div class="grid">{body}</div></main><script data-page="风格选择" data-seed="">{mark}</script></body></html>'''
Path(a.out).write_text(page, encoding="utf-8")
print(f"{Path(a.out).resolve()}（{len(cards)} 种风格）")
