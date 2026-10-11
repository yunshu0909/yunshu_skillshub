"""把用户喜欢的一张图写回风格库，当作这个风格的样张（有样张的风格才会出现在风格选择页、才能设为默认）。

做三件事：缩略成长边 1000 像素的 jpg → 放进这张卡所在目录的 samples/ → 在卡的「样张」一节加一行。
内置风格（S/N 开头）写回 skill 目录并重建索引；自建风格（U 开头）写回 ~/.image-render/styles/。

用法：
  python3 add_sample.py <风格编号> <图片> [--note "一句说明"] [--default]
例：
  python3 add_sample.py U01 images/01-xx/out/1-U01.png --note "封面" --default
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from _lib import SETTINGS, die, load_settings, save_settings, style_card

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("sid"); ap.add_argument("image"); ap.add_argument("--note", default="")
ap.add_argument("--default", action="store_true", help="同时设为默认风格")
a = ap.parse_args()
src = Path(a.image)
if not src.is_file():
    die(f"错误：图片不存在 {src}")
try:
    card = style_card(a.sid)
except ValueError as e:
    die(f"错误：{e}")
sdir = card.parent / "samples"
sdir.mkdir(parents=True, exist_ok=True)
n = 1
while (sdir / f"{a.sid}-{n}.jpg").exists():
    n += 1
dst = sdir / f"{a.sid}-{n}.jpg"
try:
    from PIL import Image
    with Image.open(src) as im:
        im = im.convert("RGB"); im.thumbnail((1000, 1000)); im.save(dst, "JPEG", quality=82)
except ImportError:
    if shutil.which("sips"):
        subprocess.run(["sips", "-s", "format", "jpeg", "-Z", "1000", str(src), "--out", str(dst)], check=True, capture_output=True)
    else:
        die("错误：需要 Pillow 来缩略图片：pip3 install pillow")
t = card.read_text(encoding="utf-8")
line = f"- `samples/{dst.name}`" + (f"（{a.note}）" if a.note else "")
if re.search(r"^## 样张", t, re.M):
    head, tail = re.split(r"^## 样张.*\n", t, maxsplit=1, flags=re.M)
    sec, *rest = re.split(r"^(?=## )", tail, maxsplit=1, flags=re.M)  # 样张一节之后如果还有别的节，原样保留
    body = "\n".join(l for l in sec.splitlines() if l.strip().startswith("- `samples/"))  # 只保留已有样张行，去掉占位说明
    t = head + "## 样张\n\n" + (body + "\n" if body else "") + line + "\n" + ("\n" + rest[0] if rest else "")
else:
    t = t.rstrip() + "\n\n## 样张\n\n" + line + "\n"
card.write_text(t, encoding="utf-8")
print(f"样张已写回：{dst}")
if a.sid[0] in "SN":
    subprocess.run([sys.executable, str(Path(__file__).with_name("update_index.py"))])
if a.default:
    s = load_settings(); s["style"] = a.sid; save_settings(s)
    print(f"默认风格已设为 {card.stem}（{SETTINGS}）")
