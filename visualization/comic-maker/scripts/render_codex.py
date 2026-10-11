"""小课堂漫画出图：prompts/*.txt → Codex 内置 imagegen（带角色参考图）→ out/*.png → 核对提示词逐字 → review.html + 发布/。

用法：
  python3 render_codex.py <任务目录> [--only 04] [--ref 图片] [--title 标题] [--batch 3] [--parallel 3] [--retries 1] [--timeout 40]
  python3 render_codex.py <任务目录> --no-ref        # 不垫图（生成角色候选时用）
参考图优先级：--ref > 任务目录 ref.png > 默认角色的 ref.png（settings.py）；都没有就报错。
--model / --effort 不填就用你 Codex 自己的默认配置。提示词或参考图改过的页，旧图自动移到 _v1/ 再重出。
  python3 render_codex.py <任务目录> --check          # 只检查提示词
  python3 render_codex.py <任务目录> --page-only      # 只重做对比页
退出码：0 全部成功且本次新出的都核到逐字；1 有失败或没核到；2 输入错误。
"""
import argparse
import atexit
import hashlib
import html
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _data import default_character  # noqa: E402

TASK = """你是执行者，只负责干活，不参与创作。
任务：用内置图像生成工具（imagegen）画 {n} 张图。

文件：prompts/ 目录下这 {n} 个提示词文件：{files}
{refline}

硬性规则：
1. 每个文件对应一张图，把文件全文一字不改作为 prompt 传给 imagegen。不要翻译、润色、增删、合并或改写。
2. {rule2}
3. 每个文件只调用一次，不重试。可以并行，同一时间最多 3 个；失败就记下错误继续。
4. **每张一生成就立刻**原样保存到 out/，不要等其他张都出完再统一保存；文件名与提示词同名（如 prompts/03.txt → out/03.png），不做后处理。某次调用超过 10 分钟没返回，就放弃它、记下来，继续其他张。
5. 只读写当前目录里 prompts/ 和 out/，不要读其他文件。
6. 最后简短汇报每张是否成功和像素尺寸，失败的原样贴错误。不要评价图片。
"""


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def valid_image(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size == 0:
        return False, ""
    try:
        from PIL import Image
        with Image.open(path) as im:
            im.load()
            return True, "%d×%d" % im.size
    except ImportError:
        data = path.read_bytes()
        ok = data[:8] == b"\x89PNG\r\n\x1a\n" and b"IEND" in data[-16:]
        return ok, "?" if ok else ""
    except Exception:
        return False, ""


def _walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("revisedPrompt", "revised_prompt") and isinstance(v, str):
                yield v
            else:
                yield from _walk(v)
    elif isinstance(o, list):
        for x in o:
            yield from _walk(x)


def verify_verbatim(prompts, since):
    """在 Codex 会话日志里找 imagegen 实际收到的 prompt，去首尾空白后完整相等才算逐字。"""
    root = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "sessions"
    if not root.is_dir():
        return set(), f"会话日志目录不存在：{root}"
    want = {v.strip(): k for k, v in prompts.items()}
    since_utc = since.astimezone(timezone.utc)
    hit, n_calls = set(), 0
    d = since.date() - timedelta(days=1)
    while d <= date.today():
        for f in (root / f"{d:%Y/%m/%d}").glob("*.jsonl"):
            if f.stat().st_mtime < since.timestamp() - 60:
                continue
            for line in open(f, encoding="utf-8", errors="ignore"):
                if "revised" not in line:
                    continue
                try:
                    obj = json.loads(line)
                    ts = datetime.fromisoformat(obj.get("timestamp", "").replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    continue
                if ts < since_utc:
                    continue
                for v in set(_walk(obj)):
                    n_calls += 1
                    if v.strip() in want:
                        hit.add(want[v.strip()])
        d += timedelta(days=1)
    # 会话日志是全局的，会扫到别的任务的出图记录，那些不算问题，不报
    return hit, ("Codex 会话日志里没找到任何出图记录" if n_calls == 0 else "已在 Codex 会话日志里逐张比对")


def make_page(job, title, report):
    mark = (SKILL / "scripts" / "mark.js").read_text(encoding="utf-8")
    figs = ""
    for i, r in enumerate(report, 1):
        src = f"out/{r['name']}.png"
        tag = "✅ 提示词逐字" if r["verbatim"] else ("之前已出" if r["ok"] and r.get("old") else "⚠️ 未核到")
        pic = f'<a href="{src}" target="_blank"><img src="{src}" loading="lazy"></a>' if r["ok"] else '<div class="miss">未生成</div>'
        prompt = (job / "prompts" / f"{r['name']}.txt").read_text(encoding="utf-8")
        figs += (f'<figure>{pic}<figcaption><b>第 {i} 页</b> <span class="px">{html.escape(r["name"])}.png</span> <span class="px">{r["size"]} · {tag}</span>'
                 f'<details><summary>提示词</summary><pre>{html.escape(prompt)}</pre></details></figcaption></figure>')
    page = f'''<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>
:root{{--bg:#f5f3ee;--card:#fff;--fg:#222;--muted:#777;--line:#e2ded5;--acc:#2f6fb5}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#1b1b1b;--card:#262626;--fg:#eee;--muted:#aaa;--line:#3a3a3a;--acc:#7fb0ea}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 -apple-system,"PingFang SC",sans-serif}}
main{{max-width:1600px;margin:0 auto;padding:20px 16px 90px}} h1{{font-size:24px}}
.row{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;align-items:start}}
figure{{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}}
figure img{{width:100%;display:block}} figcaption{{padding:8px 12px;font-size:14px}} .px{{color:var(--muted);font-size:12px}}
.miss{{aspect-ratio:3/4;display:grid;place-items:center;color:var(--muted)}}
summary{{cursor:pointer;color:var(--acc);font-size:13px}} pre{{white-space:pre-wrap;font-size:12px;background:var(--bg);padding:10px;border-radius:6px;max-height:380px;overflow:auto}}
</style></head><body><main><h1>{html.escape(title)}</h1><div class="row">{figs}</div></main>
<script data-page="{html.escape(job.name)}" data-seed="">{mark}</script></body></html>'''
    (job / "review.html").write_text(page, encoding="utf-8")


COLOR_RE = re.compile(r"(colou?r theme|background colou?r|warm colou?rs|cool colou?rs|pastel \w+ background|\b\w+ tones\b)", re.I)
MUST = ["Use the same style and character design as the reference image.", "Follow the exact same art style",
        "All Chinese text clearly readable"]


def lint(prompts, no_ref=False):
    """出图前检查提示词（铁律）。返回 (错误列表, 提醒列表)。不垫图（角色候选）时只查 URL 和引号。"""
    errs, warns = [], []
    for p in prompts:
        t = p.read_text(encoding="utf-8")
        if no_ref:
            if "http://" in t or "https://" in t:
                errs.append(f"{p.name}：提示词里有 URL")
            if t.count('"') % 2:
                errs.append(f"{p.name}：英文双引号不成对")
            continue
        for m in MUST:
            if m not in t:
                errs.append(f"{p.name}：缺「{m}」")
        if not t.lstrip().startswith(MUST[0]):
            errs.append(f"{p.name}：第一句应是「{MUST[0]}」（用 Codex 时不写 URL）")
        if "http://" in t or "https://" in t:
            errs.append(f"{p.name}：提示词里有 URL；用 Codex 出图时参考图走 referenced_image_paths")
        for m in COLOR_RE.findall(t):
            errs.append(f"{p.name}：指定了配色「{m}」（铁律：配色交给垫图）")
        if t.count('"') % 2:
            errs.append(f"{p.name}：英文双引号不成对，中文文字可能被截断")
        if "No brand logos anywhere" not in t:
            warns.append(f"{p.name}：没写「No brand logos anywhere.」")
    return errs, warns


def run_batch(job, batch, ref, timeout, tag, model="", effort=""):
    if ref:
        refline, rule2 = f"参考图：{ref}", "每次调用 referenced_image_paths 只传上面这一张参考图的绝对路径；不要传 num_last_images_to_include；不设 transparent_background。"
    else:
        refline, rule2 = "不用参考图。", "只传 prompt 一个参数：不传 referenced_image_paths，也不传 num_last_images_to_include，不设 transparent_background。"
    task = TASK.format(n=len(batch), files=" ".join(p.name for p in batch), refline=refline, rule2=rule2)
    log = job / "logs" / f"codex-{datetime.now():%H%M%S}-{tag}.log"
    cmd = ["codex", "exec"] + (["-m", model] if model else []) + (["-c", f"model_reasoning_effort={effort}"] if effort else []) + \
          ["-s", "workspace-write", "--skip-git-repo-check", "-C", str(job), task]
    f = open(log, "w")
    return subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=f, stderr=subprocess.STDOUT), log, f


def take_lock(job):
    lock = job / "logs" / ".lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        pid = lock.read_text().strip()
        try:
            os.kill(int(pid), 0)
            die(f"错误：这个任务目录正在出图（pid {pid}），等它跑完再来")
        except (ValueError, ProcessLookupError):
            lock.unlink()  # 上次异常退出留下的锁
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)
    atexit.register(lambda: lock.unlink(missing_ok=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job")
    ap.add_argument("--only", default="", help="只出文件名以此开头的页，如 04")
    ap.add_argument("--ref", default="")
    ap.add_argument("--no-ref", action="store_true", help="不垫图（生成角色候选用）")
    ap.add_argument("--model", default="", help="不填 = Codex 默认模型")
    ap.add_argument("--effort", default="", help="不填 = Codex 默认推理强度")
    ap.add_argument("--title", default="")
    ap.add_argument("--batch", type=int, default=3, help="每批几页（一个 Codex 进程）")
    ap.add_argument("--parallel", type=int, default=3, help="同时跑几批")
    ap.add_argument("--retries", type=int, default=1)
    ap.add_argument("--timeout", type=int, default=40, help="每轮最长分钟数")
    ap.add_argument("--page-only", action="store_true", help="不出图，只重做对比页和发布文件夹")
    ap.add_argument("--check", action="store_true", help="只检查提示词")
    ap.add_argument("--since", default="", help="配合 --page-only：核对这个时间（YYYY-MM-DD HH:MM）之后出的页，Codex 自己出图后用")
    a = ap.parse_args()
    if a.batch < 1 or a.parallel < 1 or a.retries < 0 or a.timeout < 1:
        die("错误：--batch / --parallel / --timeout 至少为 1，--retries 不能为负")
    job = Path(a.job).resolve()
    if not (job / "prompts").is_dir():
        die(f"错误：{job}/prompts 不存在")
    pages = sorted((job / "prompts").glob("*.txt"))          # 整期所有页（对比页、发布按这个排）
    prefixes = tuple(x.strip() for x in a.only.split(",") if x.strip()) or ("",)  # --only 支持逗号：00,02
    targets = [p for p in pages if p.stem.startswith(prefixes)]  # 这次要出的页
    if not targets:
        die("错误：没有匹配的提示词文件")
    errs, warns = lint(targets, a.no_ref)
    for w in warns:
        print("提醒：" + w)
    for e in errs:
        print("错误：" + e, file=sys.stderr)
    if errs:
        sys.exit(2)
    if a.check:
        print(f"检查 {len(targets)} 页：0 个错误，{len(warns)} 个提醒")
        return
    if a.no_ref:
        ref = None
    elif a.ref:
        ref = Path(a.ref).resolve()
    elif (job / "ref.png").exists():
        ref = job / "ref.png"
    else:
        cid, info, ref = default_character()
        if not ref:
            die("错误：没有角色参考图。先准备角色（SKILL.md「第 0 步」：导入你的 IP，或生成候选形象），"
                "或用 --ref 指定一张图")
    if ref is not None and (not ref.is_file() or not valid_image(ref)[0]):
        die(f"错误：参考图不存在或打不开：{ref}")
    (job / "out").mkdir(exist_ok=True)
    (job / "logs").mkdir(exist_ok=True)
    take_lock(job)
    title = a.title or job.name

    # 提示词或参考图变了：旧图移到 _v1/，这次重出
    fp_file = job / "logs" / "fingerprints.json"
    try:
        fps = json.loads(fp_file.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        fps = {}
    refbytes = ref.read_bytes() if ref else b""
    cur_fp = {p.stem: hashlib.sha1(p.read_text(encoding="utf-8").strip().encode() + refbytes).hexdigest()[:16] for p in pages}
    stale = [p.stem for p in targets if p.stem in fps and fps[p.stem] != cur_fp[p.stem] and valid_image(job / "out" / f"{p.stem}.png")[0]]
    if stale and not (a.page_only or a.since):
        (job / "_v1").mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%H%M%S")
        for n in stale:
            (job / "out" / f"{n}.png").rename(job / "_v1" / f"{n}-{stamp}.png")
        print(f"提示词或参考图改过，旧图移到 _v1/ 后重出：{' '.join(stale)}", flush=True)

    since = datetime.now().astimezone()
    rendered = set()
    if a.since:
        try:
            since = datetime.strptime(a.since, "%Y-%m-%d %H:%M").astimezone()
        except ValueError:
            die("错误：--since 格式应为 YYYY-MM-DD HH:MM")
        rendered = {p.stem for p in targets if valid_image(job / "out" / f"{p.stem}.png")[0]}
    if not a.page_only:
        for attempt in range(a.retries + 1):
            pending = [p for p in targets if not valid_image(job / "out" / f"{p.stem}.png")[0]]
            if not pending:
                break
            rendered |= {p.stem for p in pending}
            batches = [pending[i:i + a.batch] for i in range(0, len(pending), a.batch)]
            print(f"第 {attempt + 1} 轮：待出图 {len(pending)} 页，分 {len(batches)} 批（参考图 {ref if ref else '无'}）", flush=True)
            for i in range(0, len(batches), a.parallel):
                running = [run_batch(job, b, ref, a.timeout, f"b{i + k + 1}", a.model, a.effort) for k, b in enumerate(batches[i:i + a.parallel])]
                deadline = datetime.now() + timedelta(minutes=a.timeout)
                for proc, log, f in running:
                    try:
                        proc.wait(timeout=max(1, (deadline - datetime.now()).total_seconds()))
                    except subprocess.TimeoutExpired:
                        proc.terminate()
                        print(f"  {log.name} 超时，已结束", flush=True)
                    f.close()
                    if "at capacity" in log.read_text(errors="ignore"):
                        print(f"  {log.name}：Codex 满载，下一轮重跑", flush=True)

    # 报告覆盖整期；本次没出的页沿用上次的核对结果
    prev = {}
    rp = job / "logs" / "report.json"
    if rp.exists():
        try:
            prev = {r["name"]: r for r in json.loads(rp.read_text(encoding="utf-8"))}
        except (ValueError, KeyError, TypeError):
            prev = {}
    hit, note = verify_verbatim({p.stem: p.read_text(encoding="utf-8") for p in pages if p.stem in rendered}, since) if rendered else (set(), "本次没有新出图")
    report, bad = [], 0
    for p in pages:
        ok, size = valid_image(job / "out" / f"{p.stem}.png")
        if p.stem in rendered:
            verbatim = p.stem in hit
            if not ok or not verbatim:
                bad += 1
            tag = "提示词逐字" if verbatim else "提示词未核到"
        else:
            verbatim = bool(prev.get(p.stem, {}).get("verbatim"))
            if p in targets and not ok:
                bad += 1
            tag = "之前已核到提示词逐字" if verbatim else "之前已出"
        if ok:
            fps[p.stem] = cur_fp[p.stem]
        report.append(dict(name=p.stem, ok=ok, size=size, verbatim=verbatim, old=p.stem not in rendered, text_on_image="未核验"))
        state = "成功" if ok else ("失败" if p in targets else "未出（本次没选这页）")
        print(f"{p.stem:6} {state}  {size:10} {tag if ok else ''}")
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    fp_file.write_text(json.dumps(fps, ensure_ascii=False, indent=1), encoding="utf-8")
    make_page(job, title, report)
    pub = job / "发布"
    pub.mkdir(exist_ok=True)
    for old_png in pub.glob("*.png"):
        old_png.unlink()
    for i, r in enumerate(report, 1):
        if r["ok"]:
            (pub / f"{i:02d}.png").write_bytes((job / "out" / f"{r['name']}.png").read_bytes())
    print(f"{note}；对比页 {job / 'review.html'}；发布文件夹 {pub}（{sum(r['ok'] for r in report)} 页）")
    print("注意：脚本只核对 imagegen 收到的提示词，图上实际画出的字没有检查，交付前要逐页看图。")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
