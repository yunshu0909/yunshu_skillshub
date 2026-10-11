"""默认风格的读写。数据在 ~/.image-render/settings.json（可用环境变量 IMAGE_RENDER_HOME 改位置），升级 skill 不会覆盖。

用法：
  python3 settings.py show              # 看当前默认
  python3 settings.py set style N24     # 设默认风格（必须是有样张的风格）
  python3 settings.py get style         # 只打印值，没有就打印空行
  python3 settings.py unset style       # 清掉默认，下次重新选
"""
import sys
from _lib import SETTINGS, USER_STYLES, card_samples, die, load_settings, save_settings, style_card

KEYS = {"style": "默认风格编号（如 N24）"}
args = sys.argv[1:]
if not args or args[0] not in ("show", "get", "set", "unset"):
    die(__doc__)
s = load_settings()
cmd = args[0]
if cmd == "show":
    print(f"设置文件：{SETTINGS}")
    print(f"自建风格目录：{USER_STYLES}")
    for k, desc in KEYS.items():
        v = s.get(k, "")
        name = ""
        if v:
            try:
                name = " · " + style_card(v).stem.split("-", 1)[1]
            except ValueError:
                name = "（找不到这张风格卡，重新选一个）"
        print(f"{k}：{v or '未设置（第一次用时打开风格选择页让用户选）'}{name}")
elif len(args) < 2 or args[1] not in KEYS:
    die(f"错误：只能设置 {', '.join(KEYS)}")
elif cmd == "get":
    print(s.get(args[1], ""))
elif cmd == "unset":
    s.pop(args[1], None); save_settings(s); print(f"已清除 {args[1]}")
else:
    if len(args) < 3:
        die("错误：缺少值，例：python3 settings.py set style N24")
    try:
        card = style_card(args[2])
    except ValueError as e:
        die(f"错误：{e}")
    if not card_samples(card):
        die(f"错误：{card.stem} 还没有样张，不能当默认风格（先出一张你喜欢的图写回样张）")
    s[args[1]] = args[2]; save_settings(s)
    print(f"默认风格已设为 {card.stem}（{SETTINGS}）")
