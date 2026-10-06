# Recon Heuristics · 真物栖息地图谱

> Case Radar 的核心 IP 在这里。**别把这个文件读成 checklist——读成 patterns 集合**。某个新对象的真物可能在这 7 种之外的第 8 种位置，遇到了就把它加进来。

---

## 7 种已知的真物栖息地

### #1 · README 里的 screenshots/ examples/ assets/ 目录

**长什么样**：仓库根目录下有 `screenshots/`、`examples/`、`docs/`、`assets/`、`demos/` 等目录，里面是 PNG/WEBP/GIF。

**为什么是真物**：作者主动放的"我这个项目能做出什么"的视觉证据。

**抓法**：
```bash
# 先列目录看里面有什么
gh api repos/<owner>/<repo>/contents/screenshots --jq '.[] | .name + " (" + (.size|tostring) + " bytes)"'

# curl 直接拉
curl -sLo screenshots/cases/<name>.<ext> "https://github.com/<owner>/<repo>/raw/main/screenshots/<file>"
```

**实战案例**：
- `JimLiu/baoyu-skills` 的 `screenshots/xhs-images-styles/cute.webp`、`screenshots/infographic-layouts/bridge.webp`、`screenshots/slide-deck-styles/blueprint.webp`——直接拿到 Skill 生成的产物
- `Leonxlnx/taste-skill` 的 `examples/floria-top.webp`、`floria-bottom.webp`——用 Skill 真建出来的 Botanic Architecture 落地页

**信号**：作者愿意把 demo 资源 commit 进 git，说明对效果有信心；越用心维护 screenshots/ 目录的 repo，真物越值得抓。

---

### #2 · 官方商店/Marketplace 的产品页

**长什么样**：Anthropic Plugin Store、VSCode Marketplace、Chrome Web Store、Vercel Marketplace、HuggingFace Spaces 等。

**为什么是真物**：第三方平台背书的"安装数 + 官方排版 + 真实评价"——比 GitHub repo 页可信。

**抓法**：用 agent-browser 截全页。

```bash
agent-browser open https://claude.com/plugins/<name>
agent-browser wait 2000
agent-browser screenshot --full <name>-store-page.png
```

**实战案例**：
- `obra/superpowers` → `https://claude.com/plugins/superpowers` 显示 64.5 万次安装、Jesse Vincent 作者署名、Anthropic 排版背书——比任何 GitHub README 截图都有说服力

**信号**：能上官方 store 的工具自带过滤——质量门槛先过了一道。

---

### #3 · SKILL.md / SPEC.md / 配置文件的原文段落

**长什么样**：repo 里的 `SKILL.md`、`spec.md`、`CONFIG.md`、`.cursorrules` 等定义文件。

**为什么是真物**：作者**自己写的工作哲学/约束**。比所有二手解读都准。

**抓法**：
```bash
gh api repos/<owner>/<repo>/contents/<path>/SKILL.md --jq '.content' | base64 -d > screenshots/cases/<name>-skillmd.txt
```

挑 10-30 行最锋利的段落（frontmatter + 一个核心 heading 下面的金句）放进 HTML 的 code block。

**实战案例**：
- `obra/superpowers/skills/test-driven-development/SKILL.md` 的 "Iron Law: NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST"
- `bokan/claude-skill-self-improvement/SKILL.md` 的 Phase 1 / Phase 2 流程
- `NeoLabHQ/.../reflexion/skills/reflect/SKILL.md` 的 "You are a ruthless quality gatekeeper... You will be killed"——气质极端的人格设定

**信号**：原文段落是否锋利，**直接取决于作者的笔力**。锋利的 SKILL.md 往往配合好的真物截图——两者一起出现是金矿。

---

### #4 · before/after 对比图 / 数据可视化

**长什么样**：作者放在 `docs/images/` 里的对比图、贡献图、性能 benchmark 曲线、用户反馈截图等。

**为什么是真物**：用**自己的成果**做证明——胜过任何"我做了 X 然后 Y"的文字描述。

**抓法**：curl 直接拉两张图。

**实战案例**：
- `garrytan/gstack/docs/images/github-2013.png`（772 commits 整年）vs `github-2026.png`（1,237 commits 仅 Feb-Mar）——Garry 自己放的"用 gstack 前后我的产量对比"

**信号**：作者放对比图说明"项目有量化效果"。**这种栖息地最稀缺也最值钱**，找到一个抵 10 个普通案例。

---

### #5 · 独立产品落地页（Next.js / Vercel / GitHub Pages）

**长什么样**：项目有自己的 `*.dev`、`*.io`、`*.app` 域名落地页，通常 Next.js 或类似 SPA。

**为什么是真物**：作者愿意为项目做独立站，说明它**已经超出 repo 范畴成了产品**。落地页本身就是"这个 Skill 能做出什么级别的东西"的证明。

**抓法**：agent-browser 整页截图。

```bash
agent-browser open https://<domain>
agent-browser wait 2500   # SPA 等久一点
agent-browser screenshot --full <name>-landing.png
```

**实战案例**：
- `tasteskill.dev`——Taste Skill 的官网，本身就用 Taste Skill 做的，展示"Floria"、"Botanic Architectures"等真实建站案例
- `agent-browser.dev`、`chrome-relay.kushalsm.com` 等

**信号**：有独立站 + 站点本身有审美 = 这个项目对效果有自信。

---

### #6 · 第三方深度玩家的实战博客

**长什么样**：Simon Willison、Pieter Levels、Anthropic 工程师博客、独立 substack 写手用这个工具做了**具体的事**并写出过程。

**为什么是真物**：第三方独立验证，比作者自述更可信；过程描述里通常自带截图。

**抓法**：agent-browser 整页截博客原文。

```bash
agent-browser open <blog-url>
agent-browser wait 1500
agent-browser screenshot --full <name>-blog.png
```

**实战案例**：
- Fred Benenson 用 Claude Code 重做 Spotify 推荐的博客文章
- Simon Willison 用 Skills 解决 Starlette 1.0 breaking changes 的文章

**信号**：找博客时优先：① 写作者本身有声誉 ② 过程有截图/代码 ③ 不是"What is X" 而是 "I did X with Y" 的实战记录。

---

### #7 · README 里的 ASCII workflow / 命令示例 / Demo Block

**长什么样**：README 里有一段以 ` ``` ` 围起来的命令交互流程、ASCII 流程图、典型 session 录屏文字版。

**为什么是真物**：作者**自己演练过的真实工作流**，不是想象的使用场景。

**抓法**：用 WebFetch 抓 README，提取那段 code block，放进 HTML 的 `<pre>` 块。

**实战案例**：
- `garrytan/gstack` README 里的 `/office-hours` → `/plan-ceo-review` → `/ship` 完整流程
- agent-browser 自己的 README 里的 `open → snapshot -i → click @e3 → screenshot` core loop

**信号**：作者写的 demo block 越具体、越有变量值（而不是占位符），真实度越高。

---

## 如何选 1 个最值得抓的真物

对每个候选案例，按这个顺序问：

1. **它有 #4 数据对比图吗？** → 有 → 优先抓，最稀缺
2. **它有 #5 独立产品落地页吗？** → 有 → 抓首屏 + 滚到 bottom 整页截
3. **它有 #1 screenshots/ 目录吗？** → 有 → 挑 1-3 张最有代表性的
4. **它在 #2 官方商店有页吗？** → 有 → 抓商店页（含安装数）
5. **它的 SKILL.md（#3）里有金句吗？** → 有 → 抓段落
6. **作者类型决定 #6 #7**：如果作者是知名工程师/博主，找 ta 写的 ↑ 实战博客；如果作者是无名小卒，去 README 找 #7 demo block

**一个案例最多抓 3 件真物**——再多就不是精读了，是堆砌。

---

## 反向信号：什么时候真物难找

- repo star 数 < 50 + 没有 screenshots 目录 → 可能根本没做出过像样的效果，**不要进精读单**
- README 里全是文字、没有任何 image / code block / link → 同上
- repo 描述模糊（如 "An experimental agent project"）→ 作者自己也没定型，跳过

---

## 加新栖息地的流程

发现一种本文未列出的真物形态时（比如 YouTube demo / Discord 群聊截图 / Notion 工作模板）：

1. 给它起名（一句话标题）
2. 写 4 个字段：长什么样 / 为什么是真物 / 抓法 / 实战案例
3. 加到本文档末尾，编号 #8、#9...
4. 在 SKILL.md 主流程里**不需要**改任何代码——recon 阶段是开放的 pattern matching，新增 pattern 自动可用

---

## 元规则（这一条最重要）

> **真物的判别标准不是"是不是漂亮"，是"能不能让人 3 秒内 grok 这个工具能做出什么"。**
>
> baoyu 的 cute.webp 萌系卡片不"专业"，但 3 秒看懂"哦，能做这种小红书图"——它是真物。
>
> Anthropic plugin store 上 superpowers 的页面"很官方"但只是排版好——如果不显示 64.5 万安装数，它就不算真物。
>
> 永远问："这一张图/这段文字，能不能替代 500 字描述？" 不能就不是真物。
