# HTML Template Spec · 输出 HTML 的视觉规范

> 这个文件**不是 HTML 模板代码**，是规范——告诉 Claude embed 阶段该遵循的"视觉骨架 + 层级语义 + 反 anti-pattern"。具体 HTML 代码由 Claude 现写，不要从这里复制粘贴。
>
> 参考实例：`公众号文章` 同级目录下的 `skills-生态创意案例集-2026-05-v2.html` 是按本规范的 v2 实物（含 v1 → v2 对比和 fix 记录）。

---

## 1. 整体框架（4 块结构）

```
┌────────────────────────────────────────────────┐
│ Header                                          │
│ - meta (日期 + 版本号)                          │
│ - h1 主标题                                     │
│ - lede (一句话总览，限 80 字内)                │
│ - 层级标签图例                                  │
├────────────────────────────────────────────────┤
│ Sticky Nav (TOC，跳转锚点)                      │
├────────────────────────────────────────────────┤
│ 工具 Spotlight (条件性，capture 阶段重度用过的工具) │
├────────────────────────────────────────────────┤
│ 精读卡 (5-7 张富卡片，本页主体)                 │
│   每张：badge → h3 标题 → tagline →           │
│   pick-hero (图/对比图/code 块) →             │
│   pick-skills-list (可选 monospace 灰底块) → │
│   pick-insight (绿色"妙在")                   │
│   pick-why-you (橙色"为什么是你")             │
│   pick-footer (stats + 大 CTA 按钮)           │
├────────────────────────────────────────────────┤
│ Next Step (深色背景，3-5 个可选下一步)          │
└────────────────────────────────────────────────┘
```

**不要加的层**（v2 复盘验证为装饰）：
- 6 大分组的 grid（35 卡片全列）
- "生态全景"3 大热门 + 3 大空白 + 1 个最强信号的结构化总结块
- 4 层内容标签（事实 / 共识 / AI推测 / 真物 / 你的判断 → 砍到 3 层）

用户特别要求全景图时，作为可选附加层放在精读卡之后。**默认不放**。

---

## 2. 字体与颜色

### 字体栈

```css
font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", 
             "Helvetica Neue", "Microsoft YaHei", sans-serif;
```

中文优先，无外部 webfont 依赖。

### 颜色 token

```css
--bg: #fafaf7;              /* 主背景 · 暖白 */
--card: #ffffff;            /* 卡片白 */
--ink: #1a1a1a;             /* 主文字 */
--ink-soft: #555;           /* 次级文字 */
--ink-faint: #888;          /* 标注/出处 */
--line: #e8e6e0;            /* 分隔线 */
--accent: #c5530e;          /* 强调色 · 焦糖橙（云舒喜欢的暖色） */
--accent-soft: #fff1e6;     /* 强调浅底 */
--insight: #0f6f48;         /* "妙在"绿 */
--insight-soft: #e8f5ee;    /* "妙在"浅底 */
--ai-tag: #7c4dff;          /* AI 推测紫 */
--ai-tag-soft: #f3edff;
--tool: #0a6e9d;            /* 工具 spotlight 蓝 */
--tool-soft: #e0f2fb;
```

不要用 Inter / Roboto / Space Grotesk（避免 AI-aesthetic 字体堆叠）。

---

## 3. 层级标签系统（最多 3 层）

### 默认 3 层（推荐）

```html
<span class="layer-tag fact">事实层（出处+原文）</span>
<span class="layer-tag ai">🤖 AI 推测层（待你判）</span>
<span class="layer-tag app">👤 你的判断区（留白）</span>
```

| 层 | 颜色 | 含义 |
|---|---|---|
| 事实层 | 灰 | 引用原文、出处、数据 |
| AI 推测 | 紫 | AI 整合后下的判断 |
| 你的判断区 | 橙 | 留白让用户填 |

### 完整 5 层（用户特别要求时）

加上：
- **共识层**（蓝）：多源印证
- **真实物料层**（绿）：截图/源码

⚠️ **5 层是 v2 那版的设计，4 视角诊断认为"装饰"**。默认不要使用。

---

## 4. 精读卡（主菜）的内部结构

每张精读卡 4 块：

### 4.1 Header（卡顶）

```
[BADGE: 精读 #N · 类型] ← 颜色：默认橙 / 旗舰红 / 中文棕 / 元方法蓝
# 仓库名 / 工具名
副标题（一句话，限 25 字）
```

### 4.2 Hero 区（真物）

**3 种 hero 模式：**

| 模式 | 何时用 | 示例 |
|---|---|---|
| `pick-hero-img` 单张大图 | 有 1 张代表性图（landing page / 截图） | tasteskill Floria 站 |
| `pick-hero-strip` 多图横排（2-3 张） | 有 2-3 件并列真物 | baoyu 三件套（小红书卡 + 信息图 + 幻灯片） |
| `pick-hero-compare` 对比图（2 张） | before/after 对比 | gstack 2013 vs 2026 贡献图 |
| `pick-hero-code` 深色代码块 | SKILL.md 原文 / 配置片段 | superpowers TDD Iron Law、recursive-research 6 大原则 |

**关键 CSS 规则**：

```css
/* 多图横排：避免横版图被裁 */
.pick-hero-strip-item img {
  width: 100%;
  height: 240px;
  object-fit: contain;      /* 不是 cover! */
  background: #f5f4ef;      /* 空白部分用浅灰填充 */
  border-radius: 6px;
}

/* 单张大图 */
.pick-hero-img {
  max-width: 100%;
  width: 100%;
  height: auto;
  border-radius: 6px;
}

/* 代码块 */
.pick-hero-code {
  background: #1a1a1a;
  color: #e8e6e0;
  padding: 16px 18px;
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 12.5px;
  line-height: 1.65;
}
```

**反 anti-pattern**：
- ❌ 装饰性品牌封面图（v2 复盘 #7 NeoLab 被指认）—— **要么有信息，要么没有 hero 图**
- ❌ `object-fit: cover` 裁横版图（v2 复盘 baoyu 被指认）
- ❌ 多图风格分裂感（如三张图风格完全不同时，至少加视觉容器统一）

### 4.3 Body（卡心）

可选 3 个块（按需放）：

1. **pick-skills-list** —— 灰底 monospace 块，列 Skill 子列表 / 命令清单等
2. **pick-insight** —— 绿色左边线 "💡 妙在 · ..."（必须有）
3. **pick-why-you** —— 橙色左边线 "🤖 AI 推测 · 为什么是你"（精读单专用）

### 4.4 Footer（卡底）

```
[stats: 📦 安装数 · ⭐ Star · 👤 作者]    [大按钮: GitHub →]  [大按钮: 官网 →]
                                          padding: 8px 16px
                                          background: #1a1a1a (主)
                                          background: white + 边框 (次)
```

⚠️ CTA 必须够大可点。`font-size: 13px; padding: 8px 16px;`。

---

## 5. Sticky Nav 模式

```css
nav.toc {
  position: sticky;
  top: 0;
  background: rgba(250, 250, 247, 0.92);
  backdrop-filter: blur(8px);
  padding: 14px 28px;
  z-index: 100;
}
nav.toc ul {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  font-size: 13px;
}
```

锚点跳转到主要 section。**最多 8 个锚点**，再多就拥挤。

---

## 6. Next Step (深色块)

```css
.next-step {
  background: #1a1a1a;
  color: #fafaf7;
  padding: 28px 32px;
  border-radius: 12px;
}
```

3-5 条**可执行**的下一步选项。不要堆 10 条让用户分析瘫痪。每条带 `<strong>` 强调主动作 + 简短解释。

---

## 7. 输出文件命名

```
<工作目录>/<主题简称>-案例集-YYYY-MM-DD.html
```

如果之后有 v2、v3 迭代：

```
<主题简称>-案例集-YYYY-MM-DD-v2.html
```

**保留 v1**，不要覆盖——用户可能想对比。

---

## 8. 图片资源相对路径

所有 `<img src>` 用相对路径：

```html
<img src="screenshots/cases/<filename>" alt="...">
```

工作目录结构：

```
<工作目录>/
├── <主题>-案例集-YYYY-MM-DD.html
└── screenshots/
    └── cases/
        ├── <case-1>-<artifact-type>.<ext>
        ├── <case-2>-<artifact-type>.<ext>
        └── ...
```

文件命名规则：`<案例名>-<物料类型>.<ext>`，例：`baoyu-xhs-cute.webp`、`gstack-contributions-2026.png`、`superpowers-anthropic-plugin.png`、`recursive-skillmd.txt`。

---

## 9. v2-note 补丁说明块（迭代时用）

如果是 v2 或更后版本，在 header 下加一块说明：

```html
<div class="v2-note">
  <strong>v2 升级了什么：</strong>这里写一段 80-150 字的"和 v1 的区别"。
</div>
```

样式：浅绿底 + 绿色左边线，跟 insight 块同色系。

---

## 10. 质量自检清单（embed 完跑一遍）

在告诉用户"完成"之前自检：

- [ ] 所有 `<img src>` 路径都是相对路径，且文件确实存在
- [ ] 精读卡 5-7 张（不是 35 张全 grid）
- [ ] 每张精读卡都有 hero（图 / 对比图 / code 块），**没有 hero 的不进精读单**
- [ ] 没有 "纯装饰" hero（如品牌封面只有 logo + 名字）
- [ ] 多图 strip 用 `object-fit: contain`（不裁原图）
- [ ] 西语/法语/其他非中英文 SKILL.md 段落有中文注释
- [ ] CTA 按钮大小合适（不要 11px 小链接）
- [ ] Sticky nav 锚点 ≤ 8 个
- [ ] Next Step 3-5 条不要 10 条
- [ ] 没有 "生态全景 3 热门 3 空白" 这种装饰结构块（除非用户特别要求）
- [ ] 默认 3 层标签，不是 4-5 层
