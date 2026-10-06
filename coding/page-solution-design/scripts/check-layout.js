/**
 * 视觉件自查：横向溢出 + 数字列共线 + 槽位单行 + 类名有无样式定义 + 原生控件默认外观。
 *
 * 用法：起本地 http server（playwright 不允许 file://），打开视觉件，读返回的 problems。
 * 不需要安装任何依赖，也不需要 node 环境。两种跑法：
 *
 *   推荐：browser_run_code 里注入本文件，不用手贴整段函数
 *     async (page) => { const p = await page.context().newPage(); await p.goto('<视觉件 URL>');
 *       await p.addScriptTag({ path: '<本文件绝对路径>' });
 *       const r = await p.evaluate(() => checkLayout({ win: '#catalog .win', card: '.card' })); await p.close(); return r; }
 *   备选：把本文件整段贴进 evaluate
 *     () => { <本文件内容> ; return checkLayout({ win: '#catalog .win', card: '.card', num: '.kv td:last-child' }); }
 *
 * 跑之前先确认 location.href 是你要查的页面：浏览器可能被别的任务共用、已经切走。
 * 并行跑时用 browser_run_code 新开一个 page（page.context().newPage()）再 goto，互不干扰。
 *
 * 参数（全部可选，按被测页面的类名改）：
 *   win     窗口/画布容器选择器，默认 '.win'。
 *           定稿 HTML 上方是交互流程（缩略图里也有 .win），只查下方状态目录：传 '#catalog .win'。
 *   scroll  内容滚动区，默认 '.scroll'
 *   card    卡片/行容器，默认 '.card'
 *   num     数字单元格，逗号分隔多个，默认 ''（不查共线）
 *   slot    一次只能显示一行的槽位，默认 ''（不查）。按 offsetHeight 判断，窗口被 transform 缩放也有效。
 *   classes 查窗口里用到、但任何样式表都没出现过的类名，默认 true。
 *           只能查「完全没定义」：样式包主规则漏了、只剩零星几条（如 .btn:disabled）时查不出，靠下面的 native。
 *           类名只出现在 :not() / :has() 里或只作祖先出现，也算「有定义」；只靠 [class*=x] 定样式的类会误报。
 *   ignore  不查的类名（数组），只当 JS 钩子、确实不需要样式的类放这里，例如 ['js-hook']。
 *   native  查窗口里可见的 button / input / select / textarea 是否还是浏览器默认外观，默认 true。
 *           判据是边框为立体的 outset / inset：作者写过边框的控件都不是这样，漏搬主规则、退回浏览器默认时才会是。
 *           不看 appearance：没写 appearance:none 的正常按钮也是 auto，会误报。checkbox / radio / range / color / file 不查。
 *   nativeAllow 故意保留原生外观的控件选择器（逗号分隔），例如 '.keep-native'，默认 ''。
 *
 * 返回 { windows, skippedSheets, problems: [...] }，problems 为空即通过。
 * skippedSheets > 0 说明有跨域样式表读不到，其中定义的类会被当成「没定义」。
 */
function checkLayout(opt = {}) {
  const sel = {
    win: '.win', scroll: '.scroll', card: '.card', num: '', slot: '', classes: true, ignore: [], native: true, nativeAllow: '', ...opt,
  };
  const ignore = [].concat(sel.ignore);
  const problems = [];
  const wins = [...document.querySelectorAll(sel.win)];
  const scopes = wins.length ? wins : [document.body];

  scopes.forEach((scope, wi) => {
    const tag = wins.length ? `窗口 ${wi + 1}` : '页面';
    const scroll = scope.querySelector(sel.scroll) || scope;
    const sr = scroll.getBoundingClientRect();

    // 1) 横向溢出：任何后代的右边缘超出滚动区，或自身产生横向滚动
    if (scroll.scrollWidth > scroll.clientWidth + 1) {
      problems.push(`${tag}：滚动区横向溢出 ${scroll.scrollWidth - scroll.clientWidth}px`);
    }
    scope.querySelectorAll(`${sel.card}, ${sel.card} *`).forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.width && r.right > sr.right + 1) {
        problems.push(`${tag}：${describe(el)} 右边缘超出滚动区 ${Math.round(r.right - sr.right)}px`);
      }
    });

    // 2) 数字列共线：同一卡内所有数字单元格右边缘对齐到同一条竖线
    if (sel.num) {
      scope.querySelectorAll(sel.card).forEach((card, ci) => {
        const rights = [...card.querySelectorAll(sel.num)]
          .map((e) => Math.round(e.getBoundingClientRect().right))
          .filter((x) => x > 0);
        if (rights.length < 2) return;
        const min = Math.min(...rights); const max = Math.max(...rights);
        if (max - min > 1) {
          problems.push(`${tag} 卡 ${ci + 1}：数字列右边缘未共线，差 ${max - min}px（${[...new Set(rights)].join(' / ')}）`);
        }
      });
    }

    // 3) 槽位单行：一个槽位任何状态下只能有一行。offsetHeight 不受 transform 缩放影响
    if (sel.slot) {
      scope.querySelectorAll(sel.slot).forEach((el) => {
        const cs = getComputedStyle(el);
        const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.4;
        if (el.offsetHeight > lh * 1.6) {
          problems.push(`${tag}：槽位「${el.textContent.trim().slice(0, 20)}」换行了`);
        }
      });
    }

    // 5) 原生控件默认外观：边框是立体的 outset / inset = 没吃到作者样式
    if (sel.native) {
      const skip = /^(checkbox|radio|range|color|file|hidden)$/;
      scope.querySelectorAll('button, input, select, textarea').forEach((el) => {
        if (el.tagName === 'INPUT' && skip.test(el.type)) return;
        if (sel.nativeAllow && el.matches(sel.nativeAllow)) return;
        const cs = getComputedStyle(el);
        if (!el.offsetWidth || !el.offsetHeight || cs.visibility === 'hidden' || cs.opacity === '0') return;
        if (/outset|inset/.test(cs.borderStyle)) {
          problems.push(`${tag}：${describe(el)}「${(el.textContent || el.value || '').trim().slice(0, 12)}」还是浏览器默认外观（边框 ${cs.borderStyle}）`);
        }
      });
    }
  });

  // 4) 类名有无样式定义：收集同源样式表（含 @import、@media 内）的所有选择器，逐个类名比对
  let skippedSheets = 0;
  if (sel.classes) {
    const selectors = [];
    const walk = (rules) => [...rules].forEach((r) => {
      if (r.selectorText) selectors.push(r.selectorText);
      if (r.cssRules) walk(r.cssRules);
      if (r.styleSheet) { try { walk(r.styleSheet.cssRules); } catch (e) { skippedSheets += 1; } }
    });
    [...document.styleSheets].forEach((sh) => { try { walk(sh.cssRules); } catch (e) { skippedSheets += 1; } });
    const all = selectors.join(' ');
    const used = new Set();
    scopes.forEach((scope) => scope.querySelectorAll('[class]').forEach((el) => el.classList.forEach((c) => used.add(c))));
    const esc = (c) => c.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    [...used].filter((c) => !ignore.includes(c) && !new RegExp('\\.' + esc(CSS.escape(c)) + '(?![\\w-])').test(all))
      .forEach((c) => problems.push(`类名 .${c} 在样式表里没有定义`));
  }

  function describe(el) {
    const cls = (el.className || '').toString().split(/\s+/).filter(Boolean).slice(0, 2).join('.');
    return cls ? `${el.tagName.toLowerCase()}.${cls}` : el.tagName.toLowerCase();
  }

  return { windows: scopes.length, skippedSheets, problems };
}
