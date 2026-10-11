"""出图对比页：「按图看」（同一张图的不同风格放一行）/「按风格看」两种视图，每张可点 ♡ 标记 + 备注，一键复制反馈。

用法：python3 make_page.py <任务目录> [--title 标题]   → <任务目录>/review.html
"""
import argparse
import html
from urllib.parse import quote
from pathlib import Path
from _lib import SKILL, prompt_files, split_code, style_card, valid_image

ap = argparse.ArgumentParser(); ap.add_argument("job"); ap.add_argument("--title", default="")
a = ap.parse_args()
job = Path(a.job).resolve()
title = a.title or job.name
prompts = prompt_files(job)
if not prompts:
    raise SystemExit(f"错误：{job / 'prompts'} 里没有提示词")
items = []
for p in prompts:
    img, sid = split_code(p.stem)
    sname = style_card(sid).stem.split("-", 1)[1]
    ok, size = valid_image(job / "out" / f"{p.stem}.png")
    items.append(dict(code=p.stem, img=img, sid=sid, sname=sname, ok=ok, size=size, prompt=p.read_text(encoding="utf-8")))


def fig(it, show_style=True):
    src = html.escape("out/" + quote(it["code"] + ".png"), quote=True)
    pic = f'<a href="{src}" target="_blank"><img src="{src}" loading="lazy"></a>' if it["ok"] else '<div class="miss">未生成</div>'
    label = f"{it['sid']} {it['sname']}" if show_style else f"图 {it['img']}"
    return (f'<figure>{pic}<figcaption><b>{html.escape(it["code"])}</b> · {html.escape(label)} <span class="px">{it["size"]}</span>'
            f'<details><summary>提示词</summary><pre>{html.escape(it["prompt"])}</pre></details></figcaption></figure>')


def group(key, head):
    out, seen = "", []
    for it in items:
        if it[key] not in seen:
            seen.append(it[key])
    for k in seen:
        g = [it for it in items if it[key] == k]
        out += f'<h2>{html.escape(head(g[0]))}</h2><div class="row">' + "".join(fig(it, key == "img") for it in g) + "</div>"
    return out


by_img = group("img", lambda it: f"图 {it['img']}")
by_style = group("sid", lambda it: f"{it['sid']} · {it['sname']}")
done = sum(it["ok"] for it in items)
mark = (SKILL / "scripts" / "mark.js").read_text(encoding="utf-8")
page = f'''<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · 出图对比</title><style>
:root{{--bg:#f5f3ee;--card:#fff;--fg:#222;--muted:#777;--line:#e2ded5;--acc:#2f6fb5}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#1b1b1b;--card:#262626;--fg:#eee;--muted:#aaa;--line:#3a3a3a;--acc:#7fb0ea}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 -apple-system,"PingFang SC",sans-serif}}
main{{max-width:1700px;margin:0 auto;padding:20px 16px 90px}} h1{{font-size:24px;margin:0}} .note{{color:var(--muted);font-size:13px}}
.tabs{{position:sticky;top:0;background:var(--bg);padding:10px 0;z-index:2;border-bottom:1px solid var(--line)}}
.tabs button{{font:inherit;padding:6px 14px;margin-right:8px;border:1px solid var(--line);border-radius:20px;background:var(--card);color:var(--fg);cursor:pointer}}
.tabs button.on{{background:var(--acc);color:#fff;border-color:var(--acc)}}
h2{{font-size:18px;margin:30px 0 10px}}
.row{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px;align-items:start}}
figure{{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}}
figure img{{width:100%;display:block}} figcaption{{padding:8px 12px;font-size:14px}} .px{{color:var(--muted);font-size:12px}}
.miss{{aspect-ratio:16/9;display:grid;place-items:center;color:var(--muted)}}
summary{{cursor:pointer;color:var(--acc);font-size:13px}} pre{{white-space:pre-wrap;font-size:12px;background:var(--bg);padding:10px;border-radius:6px;max-height:380px;overflow:auto}}
.view{{display:none}} .view.on{{display:block}}
</style></head><body><main>
<h1>{html.escape(title)}</h1>
<p class="note">已出 {done}/{len(items)} 张。编号 = 图号-风格编号。点图片右上角 ♡ 标记喜欢的，写一句喜欢哪里，右下角「复制反馈」。</p>
<div class="tabs"><button class="on" data-v="a">按图看</button><button data-v="b">按风格看</button></div>
<div class="view on" id="a">{by_img}</div><div class="view" id="b">{by_style}</div>
</main><script>
document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{{document.querySelectorAll('.tabs button,.view').forEach(x=>x.classList.remove('on'));b.classList.add('on');document.getElementById(b.dataset.v).classList.add('on');}});
</script><script data-page="{html.escape(job.name)}" data-seed="">{mark}</script></body></html>'''
(job / "review.html").write_text(page, encoding="utf-8")
print(f"{job / 'review.html'}（{done}/{len(items)} 张）")
