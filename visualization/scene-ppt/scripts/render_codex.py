"""（scene-ppt 自带的出图核心，来自 image-render）先检查、拼提示词，再把还没出图的交给 Codex（内置 imagegen）原样出图；失败 / 超时批次自动重跑；最后逐字核对。

用法：python3 render_codex.py <任务目录> [--only 前缀] [--batch 8] [--parallel 3] [--retries 2] [--timeout 40]
                              [--model 模型] [--effort 推理强度] [--ref 参考图] [--no-build] [--dry-run]
- 每次运行先跑 check_prompts + build_prompts（改了 adapt/ 直接重跑本命令即可；--no-build 跳过）。
- 已有且能正常解码的 out/<名>.png 跳过；提示词或参考图改过的（指纹变了）自动把旧图移到 _v1/ 再重画。损坏 / 空文件会重画。
- --model / --effort 不填就用你 Codex 自己的默认配置。
- 参考图：--ref 或任务目录 ref.png，对本次所有图生效；启动前检查能否打开。
- 同一任务目录同时只能跑一个（logs/.lock）。
- 退出码：0 全部成功且逐字；1 有失败 / 没核到逐字；2 输入错误。结果写 logs/report.json。
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from _lib import die, TEMPLATES, fingerprint, prompt_files, valid_image, verify_verbatim

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("job"); ap.add_argument("--only", default="", help="只出文件名以它开头的图，如 --only 02 或 --only 02- 只出第 02 张")
ap.add_argument("--batch", type=int, default=8); ap.add_argument("--parallel", type=int, default=3)
ap.add_argument("--retries", type=int, default=2); ap.add_argument("--timeout", type=int, default=40, help="每批最长分钟数")
ap.add_argument("--model", default="", help="不填 = Codex 默认模型"); ap.add_argument("--effort", default="", help="不填 = Codex 默认推理强度")
ap.add_argument("--ref", default=""); ap.add_argument("--no-build", action="store_true"); ap.add_argument("--dry-run", action="store_true")
a = ap.parse_args()
if a.batch < 1 or a.parallel < 1 or a.retries < 0 or a.timeout < 1:
    die("错误：--batch、--parallel、--timeout 要 ≥ 1，--retries 要 ≥ 0")
job = Path(a.job).resolve()
if not job.is_dir():
    die(f"错误：任务目录不存在 {job}")

(job / "logs").mkdir(exist_ok=True)
lock = job / "logs" / ".lock"
for _ in range(2):
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode()); os.close(fd)
        break
    except FileExistsError:
        try:
            os.kill(int(lock.read_text().strip()), 0)
            die(f"错误：这个任务目录已有一个出图进程在跑（pid {lock.read_text().strip()}），等它结束或删掉 {lock}")
        except (ProcessLookupError, ValueError):
            lock.unlink()  # 上次异常退出留下的锁
else:
    die(f"错误：拿不到锁 {lock}")


def release():
    if lock.exists() and lock.read_text() == str(os.getpid()):
        lock.unlink()


import atexit
atexit.register(release)

if not a.no_build:
    for script in ("check_prompts.py", "build_prompts.py"):
        r = subprocess.run([sys.executable, str(HERE / script), str(job)])
        if r.returncode != 0:
            sys.exit(2)

ref = Path(a.ref).resolve() if a.ref else (job / "ref.png" if (job / "ref.png").exists() else None)
if ref is None and any("-N49" in p.name for p in prompt_files(job, a.only)):
    # 小课堂世界（N49）必须有角色：没给参考图就用默认角色
    from _lib import load_character, load_settings
    _, ref = load_character(load_settings().get("character", "") or "_none_")
    if ref is None:
        die("错误：小课堂世界需要角色参考图。先 settings.py add-character / import-character，或用 --ref 指定")
    print(f"用默认角色参考图：{ref}", flush=True)
if ref is not None and not valid_image(ref)[0]:
    die(f"错误：参考图打不开 {ref}")
rule2 = (f"referenced_image_paths 只传这一张参考图的绝对路径：{ref}；不传 num_last_images_to_include；不设 transparent_background。"
         if ref else "只传 prompt 一个参数：不传 referenced_image_paths，也不传 num_last_images_to_include，不设 transparent_background。")
template = (TEMPLATES / "codex-task.md").read_text(encoding="utf-8")
all_prompts = prompt_files(job, a.only)
if not all_prompts:
    die(f"错误：{job / 'prompts'} 里没有可出图的提示词（前缀：{a.only or '全部'}）")
(job / "out").mkdir(exist_ok=True)

run_id = datetime.now().strftime("%H%M%S")
fp_file = job / "logs" / "fingerprints.json"
try:
    fps = json.loads(fp_file.read_text(encoding="utf-8"))
except (FileNotFoundError, ValueError):
    fps = {}
cur_fp = {p.stem: fingerprint(p.read_text(encoding="utf-8"), ref) for p in all_prompts}
stale = [n for n, f in cur_fp.items() if n in fps and fps[n] != f and valid_image(job / "out" / f"{n}.png")[0]]
if stale and not a.dry_run:
    (job / "_v1").mkdir(exist_ok=True)
    for n in stale:
        (job / "out" / f"{n}.png").rename(job / "_v1" / f"{n}-{run_id}.png")
    print(f"提示词或参考图改过，旧图移到 _v1/ 后重画：{' '.join(stale)}", flush=True)


def pending():
    return [p.stem for p in all_prompts if not valid_image(job / "out" / f"{p.stem}.png")[0]]


def run_round(names, round_no):
    batches = [names[i:i + a.batch] for i in range(0, len(names), a.batch)]
    procs, queue = [], list(enumerate(batches, 1))
    while queue or procs:
        while queue and len(procs) < a.parallel:
            i, b = queue.pop(0)
            task = template.format(n=len(b), files=" ".join(f"{x}.txt" for x in b), example=b[0], rule2=rule2)
            tag = f"{run_id}-r{round_no}-b{i}"
            (job / "logs" / f"task-{tag}.md").write_text(task, encoding="utf-8")
            if a.dry_run:
                print(f"[dry-run] {tag}：{len(b)} 张 → logs/task-{tag}.md"); continue
            log = open(job / "logs" / f"run-{tag}.log", "w")
            cmd = ["codex", "exec"] + (["-m", a.model] if a.model else []) + \
                  (["-c", f"model_reasoning_effort={a.effort}"] if a.effort else []) + \
                  ["-s", "workspace-write", "--skip-git-repo-check", "-C", str(job), task]
            procs.append((tag, subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT), log, time.time()))
            print(f"开跑 {tag}：{len(b)} 张", flush=True)
        for item in list(procs):
            tag, p, log, t0 = item
            if p.poll() is None and time.time() - t0 > a.timeout * 60:
                p.terminate()
                try:
                    p.wait(30)
                except subprocess.TimeoutExpired:
                    p.kill(); p.wait()
                print(f"超时 {tag}（>{a.timeout} 分钟），已终止，没出的留给下一轮", flush=True)
            if p.poll() is not None:
                log.close(); procs.remove(item)
                txt = (job / "logs" / f"run-{tag}.log").read_text(errors="ignore")
                print(f"结束 {tag}，退出码 {p.returncode}{'（模型满载）' if 'at capacity' in txt else ''}", flush=True)
        if procs:
            time.sleep(5)


try:
    start = datetime.now()
    todo = pending()
    existed = {p.stem for p in all_prompts} - set(todo)
    print(f"待出图 {len(todo)} / {len(all_prompts)} 张" + (f"（参考图：{ref}）" if ref else ""), flush=True)
    for r in range(1, a.retries + 2):
        if not todo:
            break
        if r > 1:
            print(f"第 {r} 轮：重跑 {len(todo)} 张没出来的", flush=True)
        run_round(todo, r)
        if a.dry_run:
            sys.exit(0)
        todo = pending()
    if existed >= {p.stem for p in all_prompts}:
        hit, note = set(), "本次没有新出的图，不用核对"
    else:
        hit, note = verify_verbatim({p.stem: p.read_text(encoding="utf-8") for p in all_prompts}, start)
    rows = []
    for p in all_prompts:
        ok, size = valid_image(job / "out" / f"{p.stem}.png")
        if ok:
            fps[p.stem] = cur_fp[p.stem]
        rows.append({"name": p.stem, "ok": ok, "size": size, "prompt_verbatim": p.stem in hit, "text_on_image": "未核验"})
    fp_file.write_text(json.dumps(fps, ensure_ascii=False, indent=1), encoding="utf-8")
    (job / "logs" / "report.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in rows:
        v = "提示词逐字" if r["prompt_verbatim"] else ("之前已出好，本次不核" if r["name"] in existed else "提示词未核到逐字！")
        print(f"{r['name']:<16} {'成功' if r['ok'] else '失败'}  {r['size']:<10} {v}")
    n_ok = sum(r["ok"] for r in rows)
    print(f"成功 {n_ok}/{len(rows)}；本次核到提示词逐字 {len(hit)} 张（{note}）；用时 {int((datetime.now() - start).total_seconds() // 60)} 分钟")
    # 顺手重建对比页（review.html）和发布文件夹，不用再单独跑 make_page.py
    r = subprocess.run([sys.executable, str(HERE / "make_page.py"), str(job)], capture_output=True, text=True)
    print(r.stdout.strip())
    print("注意：脚本只核对 imagegen 收到的提示词，图上实际画出的字没有检查，交付前要逐张看图。")
    new = {r["name"] for r in rows if r["ok"]} - existed
    sys.exit(0 if n_ok == len(rows) and new <= hit else 1)
finally:
    release()
