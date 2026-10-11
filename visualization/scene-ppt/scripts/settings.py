"""默认世界和角色。数据在 ~/.scene-ppt/（环境变量 SCENE_PPT_HOME 可改），升级 skill 不会覆盖。

用法：
  python3 settings.py show                          # 当前默认世界、默认角色、所有角色
  python3 settings.py set world <世界ID>             # 设默认世界（必须是选择页里有样张的世界）
  python3 settings.py get world                     # 只打印世界ID，没有就打印空行
  python3 settings.py add-character <角色ID> --ref 图片 --name 橘子 --name-en Juzi --species-en "Orange Cat" \
          --desc-en "..." --desc-cn "戴圆框眼镜、系红围巾的胖橘猫" --series 橘子小课堂
  python3 settings.py import-character <角色文件夹>   # 从别处拷一个角色（如 ~/.comic-maker/characters/juzi）
  python3 settings.py use-character <角色ID>         # 设为默认角色（小课堂世界用）
  python3 settings.py get-character [角色ID]         # 打印角色档 JSON（含参考图路径），写提示词时用

get world 没设置时打印空行。角色字段怎么写见 SKILL.md「角色档字段」。参考图 png / jpg / webp 都行，会转成 ref.png。
"""
import argparse
import json
import shutil
import sys
from pathlib import Path
from _lib import CHARS, SETTINGS, die, load_character, load_settings, save_settings, worlds

FIELDS = ["name", "name_en", "species_en", "desc_en", "desc_cn", "series"]
ap = argparse.ArgumentParser(usage=__doc__)
ap.add_argument("cmd", choices=["show", "set", "get", "add-character", "import-character", "use-character", "get-character"])
ap.add_argument("args", nargs="*"); ap.add_argument("--ref", default="")
for f in FIELDS:
    ap.add_argument("--" + f.replace("_", "-"), default="")
a = ap.parse_args()
s = load_settings()


def set_default_char(cid):
    if not s.get("character"):
        s["character"] = cid; save_settings(s); print("（这是第一个角色，已设为默认）")


if a.cmd == "show":
    ws = {w["id"]: w for w in worlds()}
    w = s.get("world", "")
    print(f"设置文件：{SETTINGS}")
    print(f"默认世界：{(w + ' · ' + ws[w]['name']) if w in ws else (w + '（找不到了，重新选）' if w else '未设置（第一次用时打开世界选择页让用户选）')}")
    c = s.get("character", "")
    info, _ = load_character(c) if c else (None, None)
    print(f"默认角色：{c + ' · ' + info['name'] if info else '未设置（只有小课堂世界需要）'}")
    for d in sorted(CHARS.glob("*/")) if CHARS.is_dir() else []:
        i, r = load_character(d.name)
        if i:
            print(f"  - {d.name}：{i['name']}{'' if r else '  ⚠ 缺 ref.png'}")
elif a.cmd in ("set", "get"):
    if not a.args or a.args[0] != "world":
        die("错误：只能 set / get world")
    if a.cmd == "get":
        print(s.get("world", ""))
    else:
        if len(a.args) < 2:
            die("错误：例 python3 settings.py set world kitchen")
        ws = {w["id"]: w for w in worlds()}
        if a.args[1] not in ws:
            die(f"错误：没有世界 {a.args[1]}。可选：{', '.join(ws)}")
        if not ws[a.args[1]]["samples"]:
            die(f"错误：{a.args[1]} 还没有样张，不能当默认")
        s["world"] = a.args[1]; save_settings(s)
        print(f"默认世界已设为 {a.args[1]} · {ws[a.args[1]]['name']}" + ("（这个世界需要角色，没有就先 add-character）" if a.args[1] == "classroom" else ""))
elif a.cmd == "add-character":
    if not a.args or not a.ref:
        die("错误：需要角色ID 和 --ref 参考图")
    miss = [f for f in FIELDS if not getattr(a, f)]
    if miss:
        die(f"错误：缺少 {', '.join('--' + m.replace('_', '-') for m in miss)}")
    d = CHARS / a.args[0]; d.mkdir(parents=True, exist_ok=True)
    try:  # 参考图统一存成真正的 PNG（用户给 jpg / webp 也行）
        from PIL import Image
        with Image.open(a.ref) as im:
            im.save(d / "ref.png", "PNG")
    except ImportError:
        if not a.ref.lower().endswith(".png"):
            die("错误：参考图不是 PNG，需要 Pillow 转换：pip3 install pillow")
        shutil.copyfile(a.ref, d / "ref.png")
    (d / "character.json").write_text(json.dumps({f: getattr(a, f) for f in FIELDS}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"角色已保存：{d}"); set_default_char(a.args[0])
elif a.cmd == "import-character":
    if not a.args:
        die("错误：给一个角色文件夹（里面有 ref.png 和 character.json）")
    src = Path(a.args[0]).expanduser()
    if not (src / "ref.png").is_file() or not (src / "character.json").is_file():
        die(f"错误：{src} 里要有 ref.png 和 character.json")
    d = CHARS / src.name; d.mkdir(parents=True, exist_ok=True)
    for f in ("ref.png", "character.json"):
        shutil.copyfile(src / f, d / f)
    print(f"角色已导入：{d}"); set_default_char(src.name)
elif a.cmd == "use-character":
    if not a.args or not load_character(a.args[0])[0]:
        die("错误：没有这个角色，先 add-character 或 import-character")
    s["character"] = a.args[0]; save_settings(s); print(f"默认角色已设为 {a.args[0]}")
else:
    cid = a.args[0] if a.args else s.get("character", "")
    info, ref = load_character(cid) if cid else (None, None)
    if not info:
        die("错误：没有角色。小课堂世界需要先 add-character 或 import-character")
    print(json.dumps({"id": cid, **info, "ref": str(ref or "")}, ensure_ascii=False, indent=1))
