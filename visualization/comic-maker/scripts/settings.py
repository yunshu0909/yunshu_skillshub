"""角色和默认设置。

用法：
  python3 settings.py show                         # 当前默认角色 + 所有角色
  python3 settings.py add <角色ID> --ref 图片 --name 橘子 --name-en Juzi --species-en "Orange Cat" \
          --desc-en "chubby orange tabby cat, round glasses, red scarf" --desc-cn "戴圆框眼镜、系红围巾的胖橘猫" --series 橘子小课堂
  python3 settings.py use <角色ID>                  # 设为默认角色
  python3 settings.py get <角色ID|default>          # 打印角色档 JSON（含参考图路径），写提示词时用

参考图可以是 png / jpg / webp，会统一存成 ~/.comic-maker/characters/<角色ID>/ref.png。字段怎么写见 templates/character.md。
"""
import argparse
import json
import shutil
import sys
from _data import CHARS, FIELDS, SETTINGS, character, default_character, load_settings, save_settings


def die(m):
    print(m, file=sys.stderr); sys.exit(2)


def save_png(src, dst):
    """参考图统一存成真正的 PNG（用户给 jpg / webp 也行）。"""
    try:
        from PIL import Image
        with Image.open(src) as im:
            im.save(dst, "PNG")
        return
    except ImportError:
        pass
    except Exception as e:
        die(f"错误：打不开这张图 {src}（{e}）")
    if src.lower().endswith(".png"):
        shutil.copyfile(src, dst)
    elif shutil.which("sips"):
        import subprocess
        subprocess.run(["sips", "-s", "format", "png", src, "--out", str(dst)], check=True, capture_output=True)
    else:
        die("错误：参考图不是 PNG，需要 Pillow 转换：pip3 install pillow")


ap = argparse.ArgumentParser(usage=__doc__)
ap.add_argument("cmd", choices=["show", "add", "use", "get"]); ap.add_argument("cid", nargs="?", default="")
ap.add_argument("--ref", default="")
for f in FIELDS:
    ap.add_argument("--" + f.replace("_", "-"), default="")
a = ap.parse_args()

if a.cmd == "show":
    cid, info, ref = default_character()
    print(f"设置文件：{SETTINGS}")
    print(f"默认角色：{cid + ' · ' + info['name'] if info else '未设置（第一次用时先准备角色）'}")
    for d in sorted(CHARS.glob("*/")) if CHARS.is_dir() else []:
        i, r = character(d.name)
        if i:
            print(f"  - {d.name}：{i['name']}（{i['series']}）{'' if r else '  ⚠ 缺 ref.png'}")
elif a.cmd == "add":
    if not a.cid or not a.ref:
        die("错误：add 需要角色ID 和 --ref 参考图")
    miss = [f for f in FIELDS if not getattr(a, f)]
    if miss:
        die(f"错误：缺少 {', '.join('--' + m.replace('_', '-') for m in miss)}")
    d = CHARS / a.cid
    d.mkdir(parents=True, exist_ok=True)
    save_png(a.ref, d / "ref.png")
    (d / "character.json").write_text(json.dumps({f: getattr(a, f) for f in FIELDS}, ensure_ascii=False, indent=1), encoding="utf-8")
    s = load_settings()
    if not s.get("character"):
        s["character"] = a.cid; save_settings(s)
        print("（这是第一个角色，已设为默认）")
    print(f"角色已保存：{d}")
elif a.cmd == "use":
    if not character(a.cid)[0]:
        die(f"错误：没有角色 {a.cid}，先 add")
    s = load_settings(); s["character"] = a.cid; save_settings(s)
    print(f"默认角色已设为 {a.cid}")
else:
    cid = default_character()[0] if a.cid in ("", "default") else a.cid
    info, ref = character(cid) if cid else (None, None)
    if not info:
        die("错误：没有默认角色" if a.cid in ("", "default") else f"错误：没有角色 {cid}")
    print(json.dumps({"id": cid, **info, "ref": str(ref or "")}, ensure_ascii=False, indent=1))
