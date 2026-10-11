// 给对比页里每张图加「喜欢」标记 + 备注；存在本机浏览器里，可一键复制反馈。
(function () {
  const me = document.currentScript;
  const page = me.dataset.page || document.title;
  const KEY = "likes:" + page;
  const seed = (me.dataset.seed || "").split(",").filter(Boolean);
  let data = {};
  try { const raw = localStorage.getItem(KEY); data = raw ? JSON.parse(raw) : Object.fromEntries(seed.map(c => [c, "（之前在聊天里选过）"])); } catch (e) {}
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(data)); } catch (e) {} render(); };

  const css = document.createElement("style");
  css.textContent = `
  figure{position:relative} figure.liked{outline:3px solid #e0475b;outline-offset:-3px}
  .mk-btn{position:absolute;top:8px;right:8px;z-index:3;border:0;border-radius:20px;padding:4px 12px;font:14px -apple-system,sans-serif;cursor:pointer;background:rgba(255,255,255,.92);color:#e0475b;box-shadow:0 1px 4px rgba(0,0,0,.2)}
  figure.liked .mk-btn{background:#e0475b;color:#fff}
  .mk-note{display:none;width:100%;box-sizing:border-box;margin-top:6px;padding:6px 8px;border:1px solid #e0475b;border-radius:6px;font:13px -apple-system,"PingFang SC",sans-serif;background:transparent;color:inherit}
  figure.liked .mk-note{display:block}
  .mk-bar{position:fixed;right:16px;bottom:16px;z-index:9;background:#e0475b;color:#fff;border-radius:12px;padding:10px 14px;font:14px -apple-system,"PingFang SC",sans-serif;box-shadow:0 4px 16px rgba(0,0,0,.25);max-width:min(420px,calc(100vw - 32px))}
  .mk-bar button{margin:6px 6px 0 0;border:0;border-radius:6px;padding:4px 10px;cursor:pointer;font:inherit}
  .mk-list{font-size:12px;opacity:.9;margin-top:4px;word-break:break-all}`;
  document.head.appendChild(css);

  const figs = [...document.querySelectorAll("figure")].filter(f => f.querySelector("figcaption b"));
  figs.forEach(f => {
    const code = f.querySelector("figcaption b").textContent.trim();
    const btn = document.createElement("button"); btn.className = "mk-btn";
    const note = document.createElement("input"); note.className = "mk-note"; note.placeholder = "喜欢哪里？（可不填）";
    btn.onclick = e => { e.preventDefault(); if (code in data) delete data[code]; else data[code] = ""; save(); if (code in data) note.focus(); };
    note.oninput = () => { data[code] = note.value; save(); };
    f.appendChild(btn); f.querySelector("figcaption").appendChild(note);
    f._mk = { code, btn, note };
  });

  const bar = document.createElement("div"); bar.className = "mk-bar"; document.body.appendChild(bar);
  const text = () => `【${page}】我喜欢的：\n` + Object.entries(data).map(([c, n]) => `- ${c}${n ? "：" + n : ""}`).join("\n");
  function render() {
    figs.forEach(f => { const on = f._mk.code in data; f.classList.toggle("liked", on); f._mk.btn.textContent = on ? "♥ 喜欢" : "♡"; if (document.activeElement !== f._mk.note) f._mk.note.value = data[f._mk.code] || ""; });
    const n = Object.keys(data).length;
    bar.innerHTML = `♥ 已标记 ${n} 张<div class="mk-list">${Object.keys(data).join("、") || "点图片右上角 ♡ 标记"}</div>`;
    if (n) {
      const cp = document.createElement("button"); cp.textContent = "复制反馈";
      cp.onclick = () => navigator.clipboard.writeText(text()).then(() => { cp.textContent = "已复制 ✓"; setTimeout(render, 1500); });
      const dl = document.createElement("button"); dl.textContent = "下载存档";
      dl.onclick = () => { const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([JSON.stringify({ page, likes: data }, null, 2)], { type: "application/json" })); a.download = `likes-${page}.json`; a.click(); };
      bar.append(cp, dl);
    }
  }
  render();
})();
