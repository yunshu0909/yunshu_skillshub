# Prompt 结构模板

## ⚠️ Prompt 编写铁律

### 1. 垫图怎么给

| 出图方式 | 怎么给垫图 |
|---|---|
| **Codex 内置 imagegen（默认）** | 提示词里不写 URL；`render_codex.py` 用 `referenced_image_paths` 传默认角色的 `ref.png` 绝对路径 |
| 按 URL 垫图的 API（旧方式） | 图片 URL 放在提示词最前面，空格后接正文 |

无论哪种，正文第一句都是：

```
Use the same style and character design as the reference image.
```

### 2. 绝不指定配色

禁止 "Green color theme"、"Warm colors"、"Pastel blue background" 这类**整体配色 / 色调**的词。垫图决定配色，指定配色会覆盖垫图、导致风格不一致。

**不算违规**：角色档里角色本身的颜色（如 red knitted scarf，照原样带上）、具体道具的固有颜色（green chalkboard、red tomato timer）。脚本只拦整体配色词。

### 3. 详细描述画面元素

每格的元素要具体列出，不能空泛；结尾写元素丰富度（"Rich visual details: …"）。

### 4. 强调中文可读、不要品牌标志

结尾段固定包含：`No brand logos anywhere. All Chinese text clearly readable.`
（实测：不写时 AI 小机器人胸口冒出过疑似真实品牌标志。）

---

## 标准 Prompt 结构

```
Use the same style and character design as the reference image.

A vertical 3:4 manga comic page with X panels. Follow the exact same art style, color palette, character design, and border style as the reference image.

Main character: <name_en> the <species_en> (same design as reference - <desc_en>).
Second character: AI Helper, a small round friendly robot with a screen face and two dot eyes (same art style as the reference).

Panel 1 (位置, 占比%): Scene "场景名". [谁在做什么]. [画面元素]. Speech bubble from <name_en>: "对话". Caption: "旁白"

Panel 2 (位置, 占比%): ...

Rich visual details: [元素]. No brand logos anywhere. All Chinese text clearly readable. [情绪氛围].
```

`Second character` 那一行**只在讲 AI / 软件 / 工具时加**，别的主题删掉。

- 位置：top / middle / bottom / left / right / header / full page；占比写百分比。
- `Scene "名字"` 带引号会被画成格子角标（MCP 实测）；不想要角标就不加引号。
- 情绪氛围示例：`Funny and relatable mood` / `Chaotic, exhausted but comedic mood` / `Bright, relieved, triumphant mood` / `Warm, celebratory finale mood`。

---

## 系列固定页模板

### 封面「开课」（每期第一页，00.txt）

```
Use the same style and character design as the reference image.

A vertical 3:4 manga comic page with 1 large panel. Follow the exact same art style, color palette, character design, and border style as the reference image.

Main character: ...
Second character: ...

Panel 1 (full page, cover): Scene "开课". At the very top, a string of small colorful triangle bunting flags, one Chinese character on each flag, spelling: "<series>". Below it, a big decorative title with sparkles: "<series>开课啦！". In the middle, a cozy classroom: <name_en> stands in front of a green chalkboard, waving one <hand> happily like a teacher, a pointer stick in the other <hand>. On the chalkboard, written large in chalk: "[本期主题]", with a small chalk doodle of [和主题相关的小图]. [配角在做什么]. Wooden student desks in the foreground, a few books, a globe, a potted plant. Speech bubble from <name_en>: "同学们好！今天我们来聊聊 [主题]～".

Rich visual details: chalk dust, sparkles, bunting flags, warm sunlight through the classroom window. No brand logos anywhere. All Chinese text clearly readable. Warm, welcoming opening mood.
```

### 结尾「下课」（每期最后一页）

```
Panel 1 (full page, ending): Scene "下课". At the top of the green chalkboard, written large in chalk: "下课啦！". <name_en> stands in the center of the classroom making a heart shape with both <hands>, big happy smile, sparkles around. [配角拿着本期的标志道具]. Below the title, the chalkboard shows a simple chalk drawing of [本期核心比喻]. Colorful triangle bunting flags across the top. Speech bubble from <name_en>: "记住：[一句话总结]！". At the bottom, ending text in a decorative banner: "这就是 [主题] 的奥秘，你学会了吗？".

Rich visual details: confetti, sparkles, little hearts floating, classroom desks and books. No brand logos anywhere. All Chinese text clearly readable. Warm, celebratory finale mood.
```

完整原文见 `examples/mcp/00.txt`、`examples/mcp/07.txt`（示例角色橘子）。

`<name_en>`、`<species_en>`、`<desc_en>`、`<series>` 都从角色档 `character.json` 原样填入（`python3 scripts/settings.py get default`）。

**写法提醒**：
- 结尾页黑板上的「下课啦！」要写成明确要画的字（实测只写 `Scene "下课"` 有时不画出来）。
- `<hand>` / `<hands>` 按角色换：四足动物 paw / front paws，人 hand / hands，鸟 wing / wings，企鹅 flipper / flippers。
- 指代角色用名字或 they / it，别猜性别写 him / her。
- **配角**：讲 AI、软件、工具时加 `Second character: AI Helper…`；别的主题（做饭、健康、生活常识）删掉这一行即可（实测效果好），想热闹点也可以按主题现编一个（比如一个毛绒玩偶），写细外貌、跨页照抄。
- **页数**：用户说了几页就做几页。文件名按顺序编 `00`（封面）、`01`…，最后一页就是结尾，不用凑到 `07`。3 页 = 封面 + 1 页正文 + 结尾。

---

## ✅ 正文页示例（MCP 第 2 页，用户认可）

```
Use the same style and character design as the reference image.

A vertical 3:4 manga comic page with 3 panels. Follow the exact same art style, color palette, character design, and border style as the reference image.

Main character: <name_en> the <species_en> (same design as reference - <desc_en>).
Second character: AI Helper, a small round friendly robot with a screen face and two dot eyes (same art style as the reference).

Panel 1 (top, full width, 45%): Scene "以前的做法". A wall behind <name_en> covered with a chaotic tangle of cables. Each tool (a calendar, a mailbox, a database cabinet, a file folder) has its own oddly shaped plug: square, star-shaped, triangle, zigzag, all different. Adapters stacked on adapters. <name_en> stands in the middle holding a bundle of cables, overwhelmed, sweat drops. Caption: "以前：每个工具都要单独写一套对接".

Panel 2 (bottom left, 27%): <name_en> wearing safety goggles, soldering yet another weird adapter, a pile of finished adapters beside. Speech bubble: "又一个转接头……".

Panel 3 (bottom right, 28%): One of the tools gets a shiny update badge and its plug changes shape; the old cable pops out with a little spark. <name_en> falls back in shock. Speech bubble: "工具一更新，对接就断了".

Rich visual details: cables, plugs, sockets, toolbox, scattered screws. All Chinese text clearly readable. Chaotic, exhausted but comedic mood.
```

（当时还没有 `No brand logos anywhere.`，新写的都要加上。）

---

## ❌ 错误示例

```
3:4 educational manga style, 4 panels.

Panel 1: Blue color theme. Title "Subagent..."  ❌ 指定了颜色
Panel 2: Orange theme. Claude looking confused... ❌ 指定了颜色

Modern minimalist style. ❌ 没有强调用垫图风格，还用别的风格词覆盖
```

---

## Prompt 自检表

- [ ] 第一句是 "Use the same style and character design as the reference image." 吗？（用 URL API 时 URL 在它前面）
- [ ] 有 "Follow the exact same art style, color palette…" 吗？
- [ ] 指定颜色了吗？（有就删）
- [ ] 每格位置、占比、画面元素都具体吗？
- [ ] 要画的中文都在英文双引号里吗？事实、数字来自原文吗？
- [ ] 结尾有 Rich visual details + No brand logos anywhere + All Chinese text clearly readable + 情绪氛围吗？
- [ ] 封面是「开课」、最后一页是「下课」吗？
