# Stage 5：HTML 学习材料规范

> 单文件 HTML，所有 CSS 内嵌，离线可用。这一篇是设计规范——拿首发"提示词学习"作为参考实例。

---

## 文件位置
`<工作目录>/05-学习材料.html`

## 关键约束

1. **一次性 Write 写完**——不要分多次写避免被中间状态打断
2. **单文件**——CSS、JS 都内嵌；不依赖外部 CDN
3. **离线可用**——所有内容自包含
4. **中文字体优先**——PingFang SC / Hiragino Sans GB / 系统字体

---

## 设计 Token（直接复制用）

```css
:root{
  --bg:#FAFAF7; --bg-soft:#F2F2EC; --bg-card:#FFFFFF;
  --text:#1F1F1F; --text-soft:#4A4A48; --text-dim:#6B6B68;
  --border:#E5E5E0; --border-soft:#EFEFE9;
  --accent:#2563EB; --accent-soft:#DBEAFE;
  --warn:#B45309; --warn-bg:#FEF3C7; --warn-border:#FCD34D;
  --gold:#92400E; --gold-bg:#FEF3C7; --gold-border:#F59E0B;
  --emerald:#065F46; --emerald-bg:#D1FAE5; --emerald-border:#34D399;
  --rose:#9F1239; --rose-bg:#FFE4E6; --rose-border:#FB7185;
  --code-bg:#1E1E2E; --code-text:#E4E4E4;
  --mono:"SF Mono","JetBrains Mono","Menlo",monospace;
  --sans:-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
}
```

## 布局结构

```
.layout (grid 280px + 1fr)
├── .sidebar (sticky, 100vh, 左侧)
│   ├── .sidebar-header (标题 / 副标题 / 日期)
│   └── nav.toc (分组：起步 / 基础 / 进阶 / 差异化 / 附录)
└── main (max-width: 920px, padding: 48px 56px)
    └── section[id] × 8-9
```

主内容区：
- `max-width: 920px`（保证中文行长可读）
- `padding: 48px 56px 80px`
- `scroll-behavior: smooth`

侧栏导航：
- `width: 280px`
- `position: sticky; top: 0; height: 100vh; overflow-y: auto`
- IntersectionObserver 高亮 active 章节

---

## 4 种 Callout（必含）

### `.warn`（琥珀色）— 用于"主流观点的强调" / "Anthropic 砍掉了 X"这种警告
```html
<div class="warn">
<span class="label">Anthropic 4.6+ 的重要变化</span>
<p>... </p>
</div>
```

### `.gold`（金色）— 用于盲区
```html
<div class="gold">
<p><strong>现象</strong>：...</p>
<p><strong>我的怀疑</strong>：...</p>
<p><strong>真实证据</strong>：...</p>
<p><strong>选题机会</strong>：...</p>
</div>
```

### `.yunshu`（绿色，emerald）— 用于"对用户的启示"
```html
<div class="yunshu">
<span class="label">对用户的启示</span>
<p>...</p>
</div>
```
**注意**：CSS class 名叫 `.yunshu` 是因为这是云舒专属的"启示"块。其他用户可以改名，但语义不变（"对用户的具体启示"）。

### `.rose`（玫红）— 用于安全警告 / 致命反模式
```html
<div class="rose">
<span class="label">致命三件套</span>
<p>...</p>
</div>
```

---

## 案例篇必备：details 折叠

```html
<details>
<summary>① Aider — prompt 工程的"祖坟" <span class="stars">★★★★★</span></summary>
<div>
<p><strong>来源</strong>：...</p>
<h5>原文片段 ①</h5>
<div class="snippet">原文保留英文</div>
<p><strong>点评</strong>：中文点评</p>
</div>
</details>
```

每个案例必含：来源 / 骨架 / 3+ 原文片段 / 独特技巧 / 与其他差异。

---

## 争议篇必备：双轨 + 倾向分

```html
<h3>议题 N：标题<span class="judgment">X/10 倾向 Y</span></h3>

<div class="dual-view">
<div class="mainstream"><span class="label">主流</span>
<p>...</p>
</div>
<div class="alternative"><span class="label">非主流</span>
<p>...</p>
</div>
</div>

<h5>我的初判</h5>
<p>...</p>

<div class="yunshu">
<span class="label">对用户启示</span>
<p>...</p>
</div>
```

---

## 顶部 hero 模板

```html
<div class="hero">
  <span class="section-eyebrow">导读</span>
  <h1>{主题}系统学习</h1>
  <p class="lead">这是 {用户} "全维度学习 {主题}" 调研的最终学习材料...</p>
  <div class="meta">
    <span>📅 日期</span>
    <span>📚 N 个 Sub-agent 调研</span>
    <span>📎 N 个顶级案例原文</span>
    <span>⚖️ N 个争议议题</span>
  </div>
</div>
```

---

## 内嵌 JS（高亮当前章节）

```javascript
const sections = document.querySelectorAll('section[id]');
const tocLinks = document.querySelectorAll('.toc a');
const linkMap = {};
tocLinks.forEach(a => { const id = a.getAttribute('href').slice(1); linkMap[id] = a; });

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const id = entry.target.id;
      tocLinks.forEach(a => a.classList.remove('active'));
      if (linkMap[id]) linkMap[id].classList.add('active');
    }
  });
}, { rootMargin: '-20% 0px -75% 0px' });

sections.forEach(s => observer.observe(s));
```

---

## 实例参考

**首发实战**：项目根目录 `提示词学习/05-学习材料.html`
- 文件大小 ~120KB
- 1635 行
- 8 篇结构全包含
- 11 个案例 details 折叠
- 10 个争议议题 + 6 个盲区

直接打开看效果，照着改即可。

---

## 反模式

### ❌ 分多次 Write
HTML 必须一次性产出。如果担心截断，先在草稿里组织好结构，再 Write。

### ❌ 用外部 CDN
所有资源内嵌——离线可用是硬要求。

### ❌ 字体不指定中文
必须 `--sans:-apple-system,"PingFang SC","Hiragino Sans GB",...`

### ❌ 没有 details 折叠
案例多时一定要 details 折叠，否则一页十几屏滚动疲劳。

### ❌ 配色太花
4 种 callout 已经足够区分语义。不要加第 5 种颜色。
