"""环境自检：装好 skill 后先跑一次，缺什么直接告诉你怎么补。

用法：python3 doctor.py
"""
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

NAME = "comic-maker"
HOME_DIR = Path.home() / ".comic-maker"
LOCAL_DIR = Path.cwd() / ".comic-maker"


def pick_data():
    """和 skill 脚本同一套规则：环境变量 > 当前目录已有 > 家目录（可写）> 当前目录（家目录只读时先复制旧设置）。"""
    if os.environ.get("COMIC_MAKER_HOME"):
        return Path(os.environ["COMIC_MAKER_HOME"])
    if LOCAL_DIR.is_dir():
        return LOCAL_DIR
    try:
        HOME_DIR.mkdir(parents=True, exist_ok=True)
        (HOME_DIR / ".probe").write_text("x"); (HOME_DIR / ".probe").unlink()
        return HOME_DIR
    except OSError:
        pass
    if (HOME_DIR / "settings.json").exists():  # 家目录只读：复制一份旧设置到项目里
        try:
            for src in HOME_DIR.rglob("*"):  # 只复制内容，不带只读权限
                dst = LOCAL_DIR / src.relative_to(HOME_DIR)
                if src.is_dir():
                    dst.mkdir(parents=True, exist_ok=True)
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_bytes(src.read_bytes())
        except OSError:
            return HOME_DIR
    return LOCAL_DIR


DATA = pick_data()
SESSIONS = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "sessions"
ok = True


def line(good, what, fix=""):
    global ok
    ok &= good is not False
    mark = "✓" if good else ("!" if good is None else "✗")
    print(f" {mark} {what}" + (f"\n     → {fix}" if fix and not good else ""))


print(f"{NAME} 环境自检")
line(sys.version_info >= (3, 8), f"Python {sys.version.split()[0]}", "需要 Python 3.8 以上")
line(True if importlib.util.find_spec("PIL") else None, "Pillow（可选，用来校验图片）", "pip3 install pillow；不装也能用，只是校验粗一些")
codex = shutil.which("codex")
line(bool(codex), f"Codex CLI：{codex or '没找到'}", "安装：npm i -g @openai/codex，或见 https://github.com/openai/codex")
if codex:
    r = subprocess.run(["codex", "login", "status"], capture_output=True, text=True)
    line(r.returncode == 0, "Codex 已登录", "运行 codex login，用能出图的 ChatGPT 账号登录")
line(SESSIONS.is_dir() or None, f"Codex 会话日志目录 {SESSIONS}", "第一次跑过 Codex 后会自动生成；没有它就没法核对提示词是否逐字")
try:
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / ".w").write_text("x"); (DATA / ".w").unlink()
    line(True, f"用户数据目录可写：{DATA}")
    if DATA == LOCAL_DIR and not os.environ.get("COMIC_MAKER_HOME"):
        line(None, f"家目录 {HOME_DIR} 写不进（多半是 Codex 沙盒），设置存在当前项目的 {LOCAL_DIR}；以后在这个项目里用会自动读到")
except OSError as e:
    line(False, f"用户数据目录不可写：{DATA}", str(e))
print(" · 能不能真的出图，要第一次出图才知道：需要你的 ChatGPT 账号能用 Codex 的内置图像生成。")
print("结论：" + ("可以开始用" if ok else "先把 ✗ 的项补上"))
sys.exit(0 if ok else 1)
