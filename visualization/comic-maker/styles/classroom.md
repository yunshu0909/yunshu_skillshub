# 小课堂 风格配置

一个固定的老师角色（用户的 IP），用一期漫画讲清一个概念。2026-10 实测：换成橘猫、小熊猫等不同角色，效果和原版一致。

## 角色从哪来

默认角色存在 `~/.comic-maker/characters/<角色ID>/`（`ref.png` + `character.json`），用 `python3 scripts/settings.py get default` 读出来。写提示词时用到这几个字段：

| 字段 | 例子 | 用在哪 |
|---|---|---|
| `name_en` | Juzi | 提示词里角色的英文名（对白归属、动作描述） |
| `species_en` | Orange Cat | 主角那一句 |
| `desc_en` | chubby round orange tabby cat, fluffy fur, round thin-rimmed glasses, red knitted scarf, rosy cheeks, cheerful expression | 主角那一句的括号里 |
| `series` | 橘子小课堂 | 封面彩旗、封面大标题 |

```
Main character: <name_en> the <species_en> (same design as reference - <desc_en>).
```

配角（**只在讲 AI / 软件 / 工具时加**；别的主题删掉，或按主题现编一个，写细即可跨页一致）：

```
Second character: AI Helper, a small round friendly robot with a screen face and two dot eyes (same art style as the reference).
```

## 画风

- **画风跟着角色参考图走**：彩铅水彩的角色出来就是彩铅漫画，Q 版卡通的角色出来就偏卡通。想要哪种画风，生成角色时就定好（见 `templates/character.md`）。
- **提示词里不指定整体配色**（color theme、warm tones 这类），配色交给参考图；角色本身的颜色和道具的固有颜色（红围巾、绿黑板）照写。

## 系列固定页（每期必有）

| 页 | 内容 | 模板 |
|---|---|---|
| 封面「开课」 | 顶部一串三角彩旗，每面一个字拼出系列名；大标题「<系列名>开课啦！」；主角在绿黑板前挥手、拿教鞭，黑板写本期主题；对话「同学们好！今天我们来聊聊 X～」 | `templates/prompt-template.md` 封面 |
| 结尾「下课」 | 黑板顶部写大字「下课啦！」；主角比心；对话一句总结；底部横幅「这就是 X 的奥秘，你学会了吗？」；彩旗、彩纸、小爱心 | `templates/prompt-template.md` 结尾 |

系列名建议 4–6 个字（彩旗一面一个字，太长会挤）。

## 文字

| 元素 | 样式 |
|---|---|
| 标题 | 彩色艺术字 + 装饰（彩旗、星星） |
| 对话气泡 | 白底黑字圆角气泡 |
| 旁白 / 标注 | 格子边缘或独立横条 |

## 常用元素

- 情绪：开心（闪光眼、sparkles）、疲惫（冒烟、汗滴）、惊喜（张嘴、感叹号）、骄傲（竖大拇指、比心）
- 装饰：⭐ 星星、✨ 闪光、三角彩旗、💡 灯泡、❤️ 爱心

## 已知现象（实测）

- 模型会在便利贴、书脊、黑板、海报上自己加小字（每页 5–15 处），整体观感是加分的，**默认不禁止**；某期要干净，在结尾段加 `No other words besides the quoted text.`（「干净模式」）
- 会冒出疑似真实品牌标志 → 结尾段固定写 `No brand logos anywhere.`
- `Scene "求助"` 这种带引号的场景名**有时**会被画成格子角标，有时不画。想让某个字一定出现，就写成明确的文字要求（如结尾页 `written large in chalk: "下课啦！"`），别靠场景名。
- 自加的小字偶尔**说过头**（例：黑板自加「一个MCP连接无限可能！」）。交付前逐页看，和原文矛盾的提给用户；要避免就在那一格写 `The chalkboard shows only these words: "…"`。
