"""image-render 脚本共用：路径、风格卡、用户设置、画面文件解析、图片校验、提示词指纹、Codex 会话日志逐字核对。"""
import hashlib
import json
import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
STYLES = SKILL / "styles"
TEMPLATES = SKILL / "templates"

def _data_dir(name, env):
    """用户数据目录。优先级：环境变量 > 当前目录已有 .{name}/ > ~/.{name}/（可写）> 当前目录 .{name}/（家目录只读时先把旧设置复制过来）。
    最后一种给 Codex 这类只能写工作目录的沙盒用：设置存在项目里，以后在这个项目里用会自动读到。"""
    if os.environ.get(env):
        return Path(os.environ[env])
    local, home = Path.cwd() / f".{name}", Path.home() / f".{name}"
    if local.is_dir():
        return local
    try:
        home.mkdir(parents=True, exist_ok=True)
        (home / ".probe").write_text("x"); (home / ".probe").unlink()
        return home
    except OSError:
        pass
    # 家目录只能读不能写（沙盒）：有旧设置就复制一份到项目里，之后读写都用项目这份
    if (home / "settings.json").exists():
        try:
            for src in home.rglob("*"):  # 只复制内容，不带只读权限
                dst = local / src.relative_to(home)
                if src.is_dir():
                    dst.mkdir(parents=True, exist_ok=True)
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_bytes(src.read_bytes())
        except OSError:
            return home
    return local

# 用户数据放在 skill 目录外，升级 skill 不会覆盖：默认风格、自己新增的风格卡和样张
DATA = _data_dir("image-render", "IMAGE_RENDER_HOME")
USER_STYLES = DATA / "styles"
SETTINGS = DATA / "settings.json"
# 实测过的画幅（Codex 内置 imagegen，只靠提示词第一句控制）
RATIOS = {"21:9": "1916×821", "16:9": "1672×941", "2:1": "1774×887", "1:1": "1254×1254", "3:4": "1086×1448", "9:16": "941×1672"}
TEXT_HEAD = "【必须逐字放入的文字（唯一真值）】"
BODY_HEAD = "【画面与版式】"
SID_RE = re.compile(r"[SNU]\d{2}")  # S/N = 内置风格，U = 用户新增


def style_dirs():
    return [d for d in (STYLES, USER_STYLES) if d.is_dir()]


def all_cards():
    """内置 + 用户新增的风格卡（按编号排）。"""
    return sorted((f for d in style_dirs() for f in d.glob("[SNU][0-9][0-9]-*.md")), key=lambda f: f.name)


def card_samples(card):
    """卡片「样张」一节列出的、实际存在的样张路径。没有样张的风格不给用户选。"""
    names = re.findall(r"`samples/([^`]+)`", card.read_text(encoding="utf-8"))
    return [card.parent / "samples" / n for n in names if (card.parent / "samples" / n).is_file()]


def style_card(sid):
    hits = sorted(f for d in style_dirs() for f in d.glob(f"{sid}-*.md"))
    if not hits:
        hint = "" if USER_STYLES.is_dir() else f"；自建风格目录 {USER_STYLES} 还不存在，先 mkdir -p 再放卡片"
        raise ValueError(f"找不到风格卡 {sid}（styles/{sid}-*.md 或 {USER_STYLES}/{sid}-*.md）{hint}")
    return hits[0]


def load_settings():
    try:
        return json.loads(SETTINGS.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return {}


def save_settings(s):
    try:
        DATA.mkdir(parents=True, exist_ok=True)
        SETTINGS.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    except OSError as e:
        print(f"错误：设置写不进 {DATA}（{e}）。多半是沙盒只允许写工作目录："
              f"在工作目录里运行，或设环境变量 IMAGE_RENDER_HOME 指到一个能写的目录", file=sys.stderr)
        sys.exit(2)


def fingerprint(text, ref=None):
    """提示词全文 + 参考图内容的指纹：任一变了就说明旧图过期。"""
    h = hashlib.sha1(text.strip().encode("utf-8"))
    if ref:
        h.update(Path(ref).read_bytes())
    return h.hexdigest()[:16]


def style_block(sid):
    card = style_card(sid)
    m = re.search(r"```style\n(.*?)\n```", card.read_text(encoding="utf-8"), re.S)
    if not m:
        raise ValueError(f"{card.name} 里没有 ```style 代码块")
    return m.group(1).strip()


def split_code(stem):
    """文件名 = <图号>-<风格编号>[-<后缀>]，必须恰好一个风格编号、图号不能为空。
    例：2-S07 → (2, S07)；R-N42-W → (R-W, N42)。"""
    parts = stem.split("-")
    idx = [i for i, p in enumerate(parts) if SID_RE.fullmatch(p)]
    if len(idx) != 1:
        raise ValueError(f"文件名 {stem} 要恰好包含一个风格编号（S01、N24 这种），现在有 {len(idx)} 个")
    img = "-".join(parts[:idx[0]] + parts[idx[0] + 1:])
    if not img:
        raise ValueError(f"文件名 {stem} 缺图号（应为 <图号>-<风格编号>，如 2-S07）")
    return img, parts[idx[0]]


def parse_adapt(text):
    """拆出【画面与版式】正文和文字清单（清单标题必须完整）。缺任一段返回 (None, None)。"""
    if BODY_HEAD not in text or TEXT_HEAD not in text:
        return None, None
    body, texts = text.split(TEXT_HEAD, 1)
    return body.split(BODY_HEAD, 1)[1].strip(), texts


def quoted(text):
    return re.findall(r"「([^「」]+)」", text)


def valid_image(path):
    """能完整解码才算出图成功；返回 (ok, 尺寸字符串)。"""
    path = Path(path)
    if not path.is_file() or path.stat().st_size == 0:
        return False, ""
    try:
        from PIL import Image
        with Image.open(path) as im:
            im.load()
            return True, "%d×%d" % im.size
    except ImportError:  # 没装 Pillow：至少确认是完整 PNG（有文件头和结束块）
        data = path.read_bytes()
        ok = data[:8] == b"\x89PNG\r\n\x1a\n" and b"IEND" in data[-16:]
        return ok, "?" if ok else ""
    except Exception:
        return False, ""


def prompt_files(job, only=""):
    """只认 prompts/ 下文件名合法的 .txt（基线、备份放别处或改名都不会混进来）。"""
    out = []
    prefixes = [x.strip() for x in only.split(",") if x.strip()] or [""]  # --only 支持逗号：01-,03-
    for p in sorted({q for pre in prefixes for q in (Path(job) / "prompts").glob(f"{pre}*.txt")}):
        try:
            split_code(p.stem)
            out.append(p)
        except ValueError:
            pass
    return out


def codex_sessions_root():
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "sessions"


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
    """在 Codex 会话日志里找 imagegen 实际收到的 prompt：解析 JSON、按事件时间（≥ since）筛选、
    去掉首尾空白后完整相等才算逐字。prompts: {名字: 全文}。返回 (命中名字集合, 说明)。
    局限：同一份全文的两个任务无法区分；只核对「收到的 prompt」，不核对它最终存成了哪张图。"""
    from datetime import timezone
    root = codex_sessions_root()
    if not root.is_dir():
        return set(), f"会话日志目录不存在：{root}，无法核对"
    want = {v.strip(): k for k, v in prompts.items()}
    since_utc = since.astimezone(timezone.utc) if since.tzinfo else since.astimezone().astimezone(timezone.utc)
    hit, n_files, n_calls, n_other = set(), 0, 0, 0
    d = since.date() - timedelta(days=1)
    while d <= date.today():
        for f in (root / f"{d:%Y/%m/%d}").glob("*.jsonl"):
            if f.stat().st_mtime < since.timestamp() - 60:
                continue
            n_files += 1
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
                    else:
                        n_other += 1
        d += timedelta(days=1)
    # 会话日志是全局的，会扫到别的任务的出图记录，那些不算问题，不报
    note = "Codex 会话日志里没找到任何出图记录" if n_calls == 0 else "已在 Codex 会话日志里逐张比对"
    return hit, note


def die(msg):
    """输入错误：打印并以退出码 2 结束。"""
    print(msg, file=sys.stderr)
    sys.exit(2)
