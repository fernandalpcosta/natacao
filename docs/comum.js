const NADOS = { freestyle: "Crawl", backstroke: "Costas", breaststroke: "Peito", butterfly: "Borboleta", drill: "Educativo", mixed: "Misto", im: "Medley" };
const MESES = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"];
const tip = document.getElementById("tip") || document.body.appendChild(Object.assign(document.createElement("div"), { className: "tip", id: "tip" }));

const mmss = s => s == null ? "–" : `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, "0")}`;
const mesLabel = k => { const [y, m] = k.split("-"); return `${MESES[+m - 1]}/${y.slice(2)}`; };
const median = xs => { const a = xs.filter(x => x != null).sort((a, b) => a - b); if (!a.length) return null; const h = a.length >> 1; return a.length % 2 ? a[h] : (a[h - 1] + a[h]) / 2; };
const el = (tag, attrs = {}, parent) => { const n = document.createElementNS("http://www.w3.org/2000/svg", tag); for (const k in attrs) n.setAttribute(k, attrs[k]); if (parent) parent.appendChild(n); return n; };
const dt = r => new Date(r.data.slice(0, 10) + "T12:00");
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();

function showTip(container, x, y, title, rows) {
  tip.replaceChildren();
  const t = document.createElement("div"); t.className = "t"; t.textContent = title; tip.appendChild(t);
  for (const r of rows) {
    const d = document.createElement("div"); d.className = "r";
    if (r.color) { const i = document.createElement("i"); i.style.background = r.color; d.appendChild(i); }
    const b = document.createElement("b"); b.textContent = r.value; d.appendChild(b);
    if (r.label) { const s = document.createElement("span"); s.textContent = r.label; d.appendChild(s); }
    tip.appendChild(d);
  }
  tip.style.display = "block";
  const box = container.getBoundingClientRect();
  let left = box.left + window.scrollX + x + 12;
  if (left + tip.offsetWidth > window.scrollX + document.documentElement.clientWidth - 8) left = box.left + window.scrollX + x - tip.offsetWidth - 12;
  tip.style.left = left + "px";
  tip.style.top = (box.top + window.scrollY + y - tip.offsetHeight / 2) + "px";
}
const hideTip = () => { tip.style.display = "none"; };

function niceTicks(lo, hi, n = 4) {
  const span = hi - lo || 1, step0 = span / n, mag = 10 ** Math.floor(Math.log10(step0));
  const step = [1, 2, 2.5, 5, 10].map(m => m * mag).find(s => s >= step0);
  const ticks = []; for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) ticks.push(+v.toFixed(6));
  return ticks;
}

// Gráfico de linhas: series = [{name, color, values:[...]}], labels = meses.
function lineChart(node, labels, series, fmt) {
  node.replaceChildren();
  const W = Math.max(300, node.clientWidth || 520), H = 220, m = { l: 44, r: 12, t: 10, b: 26 };
  const all = series.flatMap(s => s.values).filter(v => v != null);
  if (!all.length) { node.textContent = "Sem dados no período."; return; }
  let lo = Math.min(...all), hi = Math.max(...all); const pad = (hi - lo) * 0.15 || 1; lo -= pad; hi += pad;
  const ticks = niceTicks(lo, hi); lo = Math.min(lo, ticks[0]); hi = Math.max(hi, ticks[ticks.length - 1]);
  const x = i => m.l + (labels.length === 1 ? (W - m.l - m.r) / 2 : i * (W - m.l - m.r) / (labels.length - 1));
  const y = v => m.t + (hi - v) / (hi - lo) * (H - m.t - m.b);
  const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img" }, node);
  for (const t of ticks) {
    el("line", { x1: m.l, x2: W - m.r, y1: y(t), y2: y(t), stroke: css("--grid"), "stroke-width": 1 }, svg);
    el("text", { x: m.l - 6, y: y(t) + 4, "text-anchor": "end" }, svg).textContent = fmt(t);
  }
  const every = Math.ceil(labels.length / 6);
  labels.forEach((l, i) => { if ((i % every === 0 && labels.length - 1 - i >= every / 2) || i === labels.length - 1) el("text", { x: x(i), y: H - 6, "text-anchor": "middle" }, svg).textContent = mesLabel(l); });
  for (const s of series) {
    let d = "", pen = false;
    s.values.forEach((v, i) => { if (v == null) { pen = false; return; } d += (pen ? "L" : "M") + x(i) + " " + y(v); pen = true; });
    el("path", { d, fill: "none", stroke: s.color, "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }, svg);
    s.values.forEach((v, i) => { if (v != null) el("circle", { cx: x(i), cy: y(v), r: 3, fill: s.color, stroke: css("--surface"), "stroke-width": 2 }, svg); });
    const li = s.values.map((v, i) => v == null ? -1 : i).filter(i => i >= 0).pop();
    if (li != null && li >= 0) el("text", { x: x(li), y: y(s.values[li]) - 8, "text-anchor": "end", style: `fill:${css("--text-2")};font-weight:600` }, svg).textContent = fmt(s.values[li]);
  }
  const hair = el("line", { y1: m.t, y2: H - m.b, stroke: css("--muted"), "stroke-width": 1, visibility: "hidden" }, svg);
  const hit = el("rect", { x: m.l, y: 0, width: W - m.l - m.r, height: H, fill: "transparent", tabindex: 0 }, svg);
  const at = i => {
    hair.setAttribute("x1", x(i)); hair.setAttribute("x2", x(i)); hair.setAttribute("visibility", "visible");
    const r = svg.getBoundingClientRect(), sc = r.width / W;
    showTip(node, x(i) * sc, (m.t + 30) * sc, mesLabel(labels[i]), series.map(s => ({ color: s.color, value: s.values[i] == null ? "–" : fmt(s.values[i]), label: series.length > 1 ? s.name : "" })));
  };
  let cur = labels.length - 1;
  hit.addEventListener("pointermove", e => { const r = svg.getBoundingClientRect(); const px = (e.clientX - r.left) * W / r.width; let best = 0; labels.forEach((_, i) => { if (Math.abs(x(i) - px) < Math.abs(x(best) - px)) best = i; }); cur = best; at(best); });
  hit.addEventListener("pointerleave", () => { hair.setAttribute("visibility", "hidden"); hideTip(); });
  hit.addEventListener("focus", () => at(cur));
  hit.addEventListener("blur", () => { hair.setAttribute("visibility", "hidden"); hideTip(); });
  hit.addEventListener("keydown", e => { if (e.key === "ArrowLeft") cur = Math.max(0, cur - 1); else if (e.key === "ArrowRight") cur = Math.min(labels.length - 1, cur + 1); else return; at(cur); e.preventDefault(); });
}

function barChart(node, labels, values, fmt, lab = mesLabel, tipRows = null, cor = null, tipTitle = lab) {
  node.replaceChildren();
  const W = Math.max(300, node.clientWidth || 520), H = 220, m = { l: 36, r: 12, t: 10, b: 26 };
  const hi0 = Math.max(...values, 1), ticks = niceTicks(0, hi0), hi = Math.max(hi0, ticks[ticks.length - 1]);
  const bw = (W - m.l - m.r) / labels.length, y = v => m.t + (hi - v) / hi * (H - m.t - m.b);
  const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img" }, node);
  for (const t of ticks) {
    el("line", { x1: m.l, x2: W - m.r, y1: y(t), y2: y(t), stroke: css("--grid"), "stroke-width": 1 }, svg);
    el("text", { x: m.l - 6, y: y(t) + 4, "text-anchor": "end" }, svg).textContent = t;
  }
  const every = Math.ceil(labels.length / 6);
  labels.forEach((l, i) => {
    const bx = m.l + i * bw + 1, w = Math.max(1, bw - 2), top = y(values[i]), h = H - m.b - top;
    if (h > 0) {
      const r = Math.min(4, w / 2, h);
      el("path", { d: `M${bx} ${H - m.b}V${top + r}Q${bx} ${top} ${bx + r} ${top}H${bx + w - r}Q${bx + w} ${top} ${bx + w} ${top + r}V${H - m.b}Z`, fill: cor ? cor(i) : css("--s1") }, svg);
    }
    const hit = el("rect", { x: m.l + i * bw, y: m.t, width: bw, height: H - m.t - m.b, fill: "transparent", tabindex: 0 }, svg);
    const show = () => { const r = svg.getBoundingClientRect(), sc = r.width / W; showTip(node, (m.l + (i + .5) * bw) * sc, top * sc, tipTitle(l, i), tipRows ? tipRows(i) : [{ value: fmt(values[i]) }]); hit.setAttribute("fill", css("--accent-wash")); hit.setAttribute("fill-opacity", ".5"); };
    const hide = () => { hideTip(); hit.setAttribute("fill", "transparent"); };
    hit.addEventListener("pointerenter", show); hit.addEventListener("focus", show);
    hit.addEventListener("pointerleave", hide); hit.addEventListener("blur", hide);
    if ((i % every === 0 && labels.length - 1 - i >= every / 2) || i === labels.length - 1) el("text", { x: m.l + (i + .5) * bw, y: H - 6, "text-anchor": "middle" }, svg).textContent = lab(l, i);
  });
}

function table(node, head, rows) {
  node.replaceChildren();
  const tr = document.createElement("tr");
  for (const h of head) { const th = document.createElement("th"); th.textContent = h; tr.appendChild(th); }
  const thead = document.createElement("thead"); thead.appendChild(tr); node.appendChild(thead);
  const tb = document.createElement("tbody");
  for (const r of rows) { const tr = document.createElement("tr"); for (const c of r) { const td = document.createElement("td"); if (c && c.href) { const a = document.createElement("a"); a.href = c.href; a.textContent = c.texto; td.appendChild(a); } else td.textContent = c; tr.appendChild(td); } tb.appendChild(tr); }
  node.appendChild(tb);
}

function tile(label, value, delta) {
  const d = document.createElement("div"); d.className = "tile";
  for (const [cls, txt] of [["label", label], ["value", value], ["delta", delta]]) { const s = document.createElement("div"); s.className = cls; s.textContent = txt; d.appendChild(s); }
  return d;
}

const dataBR = d => d.slice(0, 10).split("-").reverse().join("/");
const num = (v, casas = 1) => v == null ? "–" : v.toFixed(casas).replace(".", ",");
