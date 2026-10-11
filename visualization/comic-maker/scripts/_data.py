"""用户数据：默认角色、角色档。放在 skill 目录外（~/.comic-maker，可用环境变量 COMIC_MAKER_HOME 改），升级 skill 不会覆盖。

角色档：<DATA>/characters/<角色ID>/ref.png + character.json
character.json 字段：name（中文名，如 橘子）、name_en（英文名，提示词里用，如 Juzi）、species_en（如 Orange Cat）、
desc_en（英文外貌，提示词里括号那段）、desc_cn（中文外貌）、series（系列名，如 橘子小课堂）
"""
import json
import os
import sys
from pathlib import Path


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

DATA = _data_dir("comic-maker", "COMIC_MAKER_HOME")
SETTINGS = DATA / "settings.json"
CHARS = DATA / "characters"
FIELDS = ["name", "name_en", "species_en", "desc_en", "desc_cn", "series"]


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
              f"在工作目录里运行，或设环境变量 COMIC_MAKER_HOME 指到一个能写的目录", file=sys.stderr)
        sys.exit(2)


def character(cid):
    """返回 (角色档 dict, 参考图路径)；不存在返回 (None, None)。"""
    d = CHARS / cid
    try:
        info = json.loads((d / "character.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return None, None
    return info, (d / "ref.png" if (d / "ref.png").is_file() else None)


def default_character():
    cid = load_settings().get("character", "")
    if not cid:
        return "", None, None
    info, ref = character(cid)
    return cid, info, ref
