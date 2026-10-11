"""世界选择页：每个世界的样张、画风、映射、作者评价，点 ♡ 选世界，一键复制反馈。没有样张的世界不显示。

用法：python3 world_picker.py [输出路径]   默认输出到当前目录 世界选择.html
"""
import argparse
import html
from urllib.parse import quote
from pathlib import Path
from _lib import SKILL, load_settings, worlds

ap = argparse.ArgumentParser(); ap.add_argument("out", nargs="?", default="世界选择.html")
a = ap.parse_args()
default = load_settings().get("world", "")
order = {"全选": 0, "可用": 1, "我的": 2}
ws = sorted((w for w in worlds() if w["samples"]), key=lambda w: (w["id"] != default, order.get(w["tier"], 9)))
body = ""
for w in ws:
    urls = [html.escape("file://" + quote(str(s)), quote=True) for s in w["samples"][:4]]
    pics = "".join(f'<a href="{u}" target="_blank"><img src="{u}" loading="lazy"></a>' for u in urls)
    cur = ' <span class="tag cur">当前默认</span>' if w["id"] == default else ""
    need = ' <span class="tag need">需要你的角色</span>' if w["id"] == "classroom" else ""
    body += (f'<figure><div class="pics">{pics}</div><figcaption><b>{html.escape(w["name"])}</b> <code>{w["id"]}</code>'
             f' <span class="tag t{order.get(w["tier"], 9)}">作者评价：{html.escape(w["tier"])}</span>{cur}{need}'
             f'<div class="meta">画风：{html.escape(w["style"])}</div><div class="meta">{html.escape(w["note"])}</div></figcaption></figure>')
mark = (SKILL / "scripts" / "mark.js").read_text(encoding="utf-8")
page = f'''<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>选 PPT 世界</title><style>
:root{{--bg:#f4f5f2;--card:#fff;--fg:#222;--muted:#6b7377;--line:#dfe3df}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#1b1d1e;--card:#25292b;--fg:#eee;--muted:#a3abae;--line:#3a3f42}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 -apple-system,"PingFang SC",sans-serif}}
main{{max-width:1500px;margin:0 auto;padding:20px 16px 90px}} h1{{font-size:24px;margin:0}} .note{{color:var(--muted);font-size:14px;max-width:70ch}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(440px,1fr));gap:16px;align-items:start}} @media (max-width:500px){{.grid{{grid-template-columns:1fr}}}}
figure{{margin:0;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden}}
.pics{{display:grid;grid-template-columns:repeat(2,1fr);gap:2px;background:var(--line)}} .pics img{{width:100%;aspect-ratio:16/9;object-fit:cover;display:block}}
figcaption{{padding:10px 12px}} code{{color:var(--muted);font-size:12px}} .meta{{font-size:13px;color:var(--muted)}}
.tag{{font-size:12px;border-radius:10px;padding:1px 8px;margin-left:6px;color:#fff}} .t0{{background:#3f8f6b}} .t1{{background:#b08a2e}} .t2,.cur{{background:#5b5bd6}} .need{{background:#c0603a}}
</style></head><body><main><h1>选 PPT 世界</h1>
<p class="note">整套 PPT 放进一个世界里讲（后厨、RPG、小课堂…），世界决定场景和画风。挑一个当<b>默认世界</b>，以后每次都用它，随时可以换。点图片右上角 ♡，右下角「复制反馈」；也可以直接说世界 ID。样张内容都是讲 AI / Skill 的，换主题时 助手会按你的内容重新想比喻。</p>
<div class="grid">{body}</div></main><script data-page="世界选择" data-seed="">{mark}</script></body></html>'''
Path(a.out).write_text(page, encoding="utf-8")
print(f"{Path(a.out).resolve()}（{len(ws)} 个世界）")
