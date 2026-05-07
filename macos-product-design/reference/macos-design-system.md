# macOS 产品设计系统（基于 Apple HIG + 顶级应用调研）

> 来源：Apple Human Interface Guidelines、WWDC 演讲、Evil Martians 设计文章、Raycast/Linear/Arc Browser 设计分析、ceorkm/macos-design-skill
> 用途：供 AI agent 读取后，按 macOS 原生标准输出高质量的前端设计稿（HTML/CSS）
> 提取日期：2026-04-07

---

## 一、设计理念

### Apple 对 macOS 的定位

> "People rely on the power, spaciousness, and flexibility of a Mac as they perform in-depth productivity tasks, view media or content, and play games, often using several apps at once."
> — Apple HIG: Designing for macOS

macOS 设计的三个关键词：**power（强大）、spaciousness（宽敞）、flexibility（灵活）**。与 iOS 的"直接、简洁"完全不同。

### HIG 三大核心原则

- **Clarity（清晰）**：界面清晰可读、精确、易于理解
- **Deference（谦逊）**：UI 帮助用户聚焦内容和任务，最小化不必要的视觉杂乱
- **Depth（深度）**：视觉层次和逼真的动效传达层级关系

### 顶级 macOS 应用的设计哲学

**Raycast** — "fast, simple, and delightful"
> 完全原生 macOS 应用，扩展用 React 声明但渲染为原生 UI。
> — Raycast Blog

**Linear** — "A calmer interface for a product in motion"
> "Don't compete for attention you haven't earned."
> "Structure should be felt not seen."
> — Linear Design Refresh

**Arc Browser**：
> "Arc was initially designed as a browser for macOS, so the creative team behind Arc sought to create a UI that perfectly aligns with the Apple environment, and they succeeded brilliantly."
> — Medium, Arc Browser Design Analysis

### 为什么原生感重要

> "Apps with native design appear more credible, seem more thoroughly considered, feel more stable in performance."
> — Evil Martians

原生设计不只是美观问题，它直接影响用户对应用**可信度、完成度和性能**的感知。

---

## 二、排版系统

### 字体

- 系统字体：**SF Pro**（San Francisco）
- SF Pro Display：**20pt 及以上**自动切换
- SF Pro Text：**19pt 及以下**自动切换
- 等宽字体：**SF Mono**
- 来源：Apple HIG Typography、Apple Fonts

**CSS Font Stack：**
```css
font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
font-family: "SF Mono", "Menlo", "Monaco", monospace; /* 等宽 */
```

### 字号体系

**关键事实：macOS 的 Body 字号是 13px，不是 Web 的 16px。这是区分桌面应用和网页最显著的特征。**

| 样式 | 字号 | 字重 | 行高 |
|------|------|------|------|
| Large Title | 26px | Bold (700) | 32px |
| Title 1 | 22px | Regular (400) | 28px |
| Title 2 | 17px | Regular (400) | 22px |
| Title 3 | 15px | Semibold (600) | 20px |
| **Body** | **13px** | Regular (400) | 18px |
| Callout | 12px | Regular (400) | 16px |
| Footnote | 12px | Regular (400) | 16px |
| Caption | 11px | Regular (400) | 14px |
| Mini | 9px | Medium (500) | 12px |

来源：Apple HIG Typography、NSFont gist (shaps80)

---

## 三、颜色系统

### 系统色

| 颜色 | Light Mode | Dark Mode |
|------|-----------|-----------|
| Blue | #007AFF | #0A84FF |
| Green | #34C759 | #30D158 |
| Red | #FF3B30 | #FF453A |
| Orange | #FF9500 | #FF9F0A |
| Yellow | #FFCC00 | #FFD60A |
| Purple | #AF52DE | #BF5AF2 |
| Pink | #FF2D55 | #FF375F |
| Teal | #5AC8FA | #64D2FF |

来源：GitHub gist (andrejilderda)

### 语义色

**Light Mode：**
- labelColor: rgba(0, 0, 0, 0.847)
- secondaryLabelColor: rgba(0, 0, 0, 0.498)
- tertiaryLabelColor: rgba(0, 0, 0, 0.259)
- placeholderTextColor: rgba(0, 0, 0, 0.247)
- separatorColor: rgba(0, 0, 0, 0.098)
- windowBackgroundColor: #ECECEC

**Dark Mode：**
- labelColor: rgba(255, 255, 255, 0.847)
- textBackgroundColor: rgb(30, 30, 30)
- windowBackgroundColor: #323232
- linkColor: rgb(65, 156, 255)

**关键原则：Dark Mode 不是简单反色。**
> "Do NOT directly invert colors between modes." Dark mode requires greater color differentiation.
> Apple 在 Dark Mode 中不使用纯黑 #000000，而是深灰 #1C1C1E。

### CSS 变量方案

**Light Mode：**
```
--bg-primary: #FFFFFF
--bg-secondary: #F5F5F7
--bg-tertiary: #E8E8ED
--text-primary: #1D1D1F
--text-secondary: #6E6E73
--text-tertiary: #AEAEB2
--border: rgba(0, 0, 0, 0.08)
--border-strong: rgba(0, 0, 0, 0.15)
--accent: #007AFF
--surface-hover: rgba(0, 0, 0, 0.04)
--surface-active: rgba(0, 0, 0, 0.08)
```

**Dark Mode：**
```
--bg-primary: #1C1C1E
--bg-secondary: #2C2C2E
--bg-tertiary: #3A3A3C
--text-primary: #F5F5F7
--text-secondary: #98989D
--text-tertiary: #636366
--border: rgba(255, 255, 255, 0.08)
--border-strong: rgba(255, 255, 255, 0.15)
--accent: #0A84FF
--surface-hover: rgba(255, 255, 255, 0.06)
--surface-active: rgba(255, 255, 255, 0.1)
```

来源：ceorkm/macos-design-skill

---

## 四、间距系统

macOS 使用 **8px 基础网格**。

| 场景 | 数值 |
|------|------|
| 窗口内边距 | 16-20px |
| 分区间距 | 24px |
| 卡片间距 | 12-16px |
| 元素间距（按钮等） | 8px |
| 卡片内边距 | 12px |
| 按钮内边距 | 6px 12px |
| 输入框内边距 | 8px 12px |
| 图标到文字间距 | 6px |
| 控件间距（Regular） | 12px |
| 控件间距（Small） | 10px |
| 标签到控件距离 | 8px |

来源：ceorkm/macos-design-skill、Apple HIG Controls

---

## 五、组件尺寸规范

### 交互元素高度

| 元素 | 高度 |
|------|------|
| 工具栏/标题栏 | 48-52px |
| 默认按钮 | 28px |
| 大按钮 | 34px |
| 输入框 | 28px |
| 侧边栏行 | 28-32px |
| 列表行 | 36-44px |
| 工具栏图标按钮 | 28x28px |

来源：ceorkm/macos-design-skill、Apple HIG Controls

### 圆角半径

| 元素 | 圆角 |
|------|------|
| 窗口 | 10px |
| 模态/面板 | 12px |
| 卡片 | 8px |
| 按钮 | 6px |
| 输入框 | 6px |
| Tag/Badge | 4px |
| Toggle 开关 | 14px（药丸形） |

来源：ceorkm/macos-design-skill

### Traffic Lights（窗口控制按钮）

- 直径：12px 圆形
- 间距：左上角 8px，按钮之间 8px
- 颜色：红 #FF5F57、黄 #FEBC2E、绿 #28C840
- Hover：显示 ×、−、+ 图标
- 非活跃窗口：全部变灰 #CDCDCD

来源：Apple HIG

### 侧边栏

- 宽度范围：200-260px
- 推荐最小宽度：225pt
- 推荐最大宽度：350-400pt
- 背景：使用 vibrancy/blur
- 可折叠，快捷键 Cmd+Ctrl+S
- 最大嵌套层级：2 级

来源：Sidebar Guidelines (Mario Aguzman)

---

## 六、阴影系统

macOS 的标志性视觉：**0.5px border-shadow + 分层阴影**。

> "The `0 0 0 0.5px` border-shadow is essential. It gives subtle definition to edges without using a visible border. **This is THE macOS look.**"
> — ceorkm/macos-design-skill

**精妙阴影（卡片、按钮）：**
```css
box-shadow: 0 0 0 0.5px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.06);
```

**中等阴影（下拉菜单、弹出框）：**
```css
box-shadow: 0 0 0 0.5px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.1);
```

**重阴影（浮动窗口、模态框）：**
```css
box-shadow: 0 0 0 0.5px rgba(0,0,0,0.1), 0 2px 8px rgba(0,0,0,0.08),
            0 8px 30px rgba(0,0,0,0.14), 0 24px 60px rgba(0,0,0,0.08);
```

Dark Mode 阴影透明度约 2 倍增加。

---

## 七、Vibrancy（毛玻璃效果）

### 该用 blur 的地方
- 侧边栏、顶部栏/工具栏
- 浮动面板和弹出框
- Spotlight 风格的快速访问窗口
- Toast 通知

### 不该用 blur 的地方
- 主内容区域（必须不透明，保证可读性）
- 模态背景（用半透明深色遮罩）

### CSS 实现
```css
.sidebar {
  background: rgba(246, 246, 246, 0.72);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
}
```

> Always include `saturate(180%)` to prevent colors from appearing washed out behind blur.
> — ceorkm/macos-design-skill

---

## 八、动画规范

**缓动函数：**
```css
--ease-out: cubic-bezier(0.25, 0.46, 0.45, 0.94);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);  /* 轻微过冲 */
--ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);
```

**时长：**
- Fast（hover、小变化）：150ms
- Normal（面板、展开）：250ms
- Slow（页面级过渡）：400ms

来源：ceorkm/macos-design-skill

---

## 九、做与不做（来自调研的硬规则）

### 光标——最容易暴露"不原生"的细节

```css
*, a, button { cursor: default; user-select: none; }
```

- 原生应用所有可点击元素用 **default cursor（箭头）**，不是 pointer（手型）
- pointer cursor **仅用于跳出应用的外部链接**
- 非内容文本默认不可选

来源：Evil Martians

### Hover 状态——跟 Web 规则相反

- 有样式的按钮（styled buttons）：**不响应 hover**
- 幽灵按钮（plain text / icon button）：**响应 hover**
- 菜单项和表格行：**无 hover 效果**
- 下拉菜单项：**有 hover 高亮**（键盘导航需要）

来源：Evil Martians

### 字号——杀手级差异

```css
html { font-size: 13px; }  /* 不是 Web 的 16px */
```

来源：Apple HIG Typography

### 边框——macOS 不用厚边框

macOS 使用极细（0.5px）、低透明度的 border-shadow，不是 1px solid border。

### 失焦状态

窗口失去焦点时，accent color 替换为灰色变体。这是原生应用的标志行为。

来源：Making Electron apps feel native (DEV Community)

### 窗口行为

- 先隐藏后显示（避免白屏闪烁）
- 记住窗口位置和尺寸
- Dark Mode 下设置 backgroundColor 防止 resize 闪烁
- 自定义标题栏空白区域可拖拽（`-webkit-app-region: drag`）

### 必须有键盘快捷键

- Cmd+, 打开偏好设置
- Cmd+K 命令面板
- Cmd+Z / Cmd+Shift+Z 撤销/重做
- 每个菜单操作都应有快捷键

### "视觉恐怖谷"

> "Users can instantly tell when something isn't native without necessarily understanding why."
> — Evil Martians

功能正常但缺少平台细节时，用户会本能感到"不对劲"。具体暴露点：
1. pointer cursor 代替 default cursor
2. 16px 基础字号
3. 所有按钮都有 hover 效果
4. 缺少窗口失焦颜色变化
5. 缺少 vibrancy
6. 使用厚边框
7. 使用单一重阴影（应该分层）
8. 缺少键盘快捷键

---

## 十、图标

遵循 SF Symbols 设计语言：
- 单线描边风格（1.5-2px 描边宽度）
- 简单几何形状
- 默认尺寸 16px，突出操作 20px，内联提示 12px
- 使用 `currentColor` 继承文本颜色
- 描边轻微圆角

来源：ceorkm/macos-design-skill

---

## 十一、顶级应用的具体设计决策

### Linear 的颜色策略

- 从 HSL 迁移到 **LCH 色彩空间**，保证感知均匀亮度
- 主题变量从 98 个减到仅 3 个：base color、accent color、contrast
- **侧边栏亮度降低数个档位**，让主内容区获得视觉优先级
- 从冷蓝灰转向暖灰
- 限制 chrome 蓝色使用，追求"neutral and timeless appearance"

来源：Linear UI Redesign Part II

### Raycast 的设计细节

- Search bar 增大以突出核心地位
- 搜索结果使用更大的前导图标加速视觉扫描
- 底部 Action bar 整合 actions、toasts、navigation
- Toast 移到应用窗口内部
- 图标 outline 风格，加粗描边使其更突出
- 支持 Compact Mode

来源：Raycast Blog

### Arc 的差异化

- 主工作区**没有任何界面元素**——全收进自动隐藏侧边栏
- 地址栏不在顶部
- muted, bright colors + serif 字体组合
- 大量负空间、柔和圆角、细腻动画

来源：LogRocket UX Analysis、Medium Design Analysis

---

## 来源索引

- [Apple HIG](https://developer.apple.com/design/human-interface-guidelines/)
- [Apple HIG - Designing for macOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-macos)
- [Apple HIG - Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Apple Fonts](https://developer.apple.com/fonts/)
- [WWDC20 - Adopt the new look of macOS](https://developer.apple.com/videos/play/wwdc2020/10104/)
- [ceorkm/macos-design-skill (GitHub)](https://github.com/ceorkm/macos-design-skill)
- [macOS System Colors (andrejilderda)](https://gist.github.com/andrejilderda/8677c565cddc969e6aae7df48622d47c)
- [NSFont Helpers (shaps80)](https://gist.github.com/shaps80/2d21b2ab92ea4fddd7b545d77a47024b)
- [Sidebar Guidelines (Mario Aguzman)](https://marioaguzman.github.io/design/sidebarguidelines/)
- [Evil Martians - How to make any app look like macOS](https://evilmartians.com/chronicles/how-to-make-absolutely-any-app-look-like-a-macos-app)
- [Making Electron feel native (DEV)](https://dev.to/vadimdemedes/making-electron-apps-feel-native-on-mac-52e8)
- [Raycast Blog - A Fresh Look and Feel](https://www.raycast.com/blog/a-fresh-look-and-feel)
- [Linear UI Redesign Part II](https://linear.app/now/how-we-redesigned-the-linear-ui)
- [Arc Browser UX Analysis (LogRocket)](https://blog.logrocket.com/ux-design/ux-analysis-arc-opera-edge/)
