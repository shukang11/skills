#!/usr/bin/env python3
"""Regenerate skill-map.html from the skills tree.

Nodes: every SKILL.md, every playbook, and every reference file a skill links to.
Edges: routes (the entry or a playbook step points at it), calls (an explicit
"read this" hand-off), mentions (a passing reference), reads (a skill pointing at
its own reference file).

Run from the repository root: python3 scripts/build-skill-map.py
"""
import pathlib, re, json, collections
root=pathlib.Path('.')
SK=re.compile(r'`([a-z][a-z0-9-]{2,})`')
LINK=re.compile(r'\]\((\.\./[^)]*SKILL\.md)\)')
REF=re.compile(r'\]\((references/[^)]+)\)')
skills={}
for p in sorted(root.glob('skills/*/*/SKILL.md')):
    grp=p.parts[1]; name=p.parent.name
    txt=p.read_text(encoding='utf-8')
    skills[name]=dict(group=grp, path=str(p), dmi='disable-model-invocation: true' in txt,
                      lines=len(txt.splitlines()))
entry='pstack-mode'
pbroot=pathlib.Path(f'skills/{skills[entry]["group"]}/{entry}/playbooks')
playbooks={p.stem:str(p) for p in sorted(pbroot.glob('*.md'))}
nodes=[]; edges=[]
for n,i in skills.items():
    nodes.append(dict(id=n, kind='entry' if n==entry else i['group'], lines=i['lines'], dmi=i['dmi']))
for n,p in playbooks.items():
    nodes.append(dict(id='pb:'+n, label=n, kind='playbook', lines=len(pathlib.Path(p).read_text(encoding='utf-8').splitlines())))
for n,p in playbooks.items():
    for ln in pathlib.Path(p).read_text(encoding='utf-8').splitlines():
        for t in set(SK.findall(ln)):
            if t in skills: edges.append(dict(s='pb:'+n, t=t, k='routes'))
for n,i in skills.items():
    src=entry if n==entry else n
    for ln in pathlib.Path(i['path']).read_text(encoding='utf-8').splitlines():
        low=ln.lower()
        for t in set(SK.findall(ln)):
            if t==n or t not in skills: continue
            if n==entry: k='routes'
            elif any(w in low for w in ('read ','open ','call ','hand ')): k='calls'
            else: k='mentions'
            edges.append(dict(s=src, t=t, k=k))
        for m in LINK.findall(ln):
            b=pathlib.Path(m).name
            if b in skills and b!=n: edges.append(dict(s=src, t=b, k='calls'))
        for m in REF.findall(ln):
            rid=str(pathlib.Path(i['path']).parent/m)
            if pathlib.Path(rid).is_file(): edges.append(dict(s=src, t=rid, k='reads'))
prio={'routes':0,'calls':1,'mentions':2,'reads':3}
seen=set(); ded=[]
for e in sorted(edges,key=lambda x:prio[x['k']]):
    key=(e['s'],e['t'])
    if key in seen: continue
    seen.add(key); ded.append(e)
edges=ded
refids=sorted({e['t'] for e in edges if e['t'].startswith('skills/')})
for r in refids:
    nodes.append(dict(id=r, label=pathlib.Path(r).name, kind='reference',
                      lines=len(pathlib.Path(r).read_text(encoding='utf-8').splitlines())))
indeg=collections.Counter(e['t'] for e in edges)
outdeg=collections.Counter(e['s'] for e in edges)
for n in nodes:
    n['in']=indeg[n['id']]; n['out']=outdeg[n['id']]
data=dict(nodes=nodes, edges=edges, meta=dict(
    total=len(skills), dmi=sum(1 for i in skills.values() if i['dmi']),
    playbooks=len(playbooks), refs=len(refids), edges=len(edges),
    orphans=[n for n in skills if indeg[n]==0],
    hubs=[[k,v] for k,v in indeg.most_common(10) if k in skills]))
pathlib.Path('/tmp/skillgraph.json').write_text(json.dumps(data, ensure_ascii=False))
print('nodes', len(nodes), 'edges', len(edges))
print('orphans', data['meta']['orphans'])
print('hubs', data['meta']['hubs'])
print('kinds', collections.Counter(e['k'] for e in edges))

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Skill routing map</title>
<style>
  :root{--bg:#0a0f1c;--panel:#111a2c;--line:#22304d;--text:#e6ecf8;--dim:#8fa1c0}
  *{box-sizing:border-box}
  html,body{height:100%;margin:0;background:var(--bg);color:var(--text);
    font:13px/1.5 ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif;overflow:hidden}
  #wrap{display:flex;height:100%}
  #side{width:320px;min-width:320px;border-right:1px solid var(--line);background:var(--panel);
    display:flex;flex-direction:column}
  h1{font-size:13px;margin:0;padding:14px 16px 6px}
  #meta{padding:0 16px 12px;color:var(--dim);font-size:11.5px;border-bottom:1px solid var(--line);line-height:1.7}
  #meta b{color:var(--text)}
  #controls{padding:10px 16px;border-bottom:1px solid var(--line);display:flex;flex-wrap:wrap;gap:8px;align-items:center}
  label.chk{display:flex;align-items:center;gap:5px;color:var(--dim);cursor:pointer;font-size:11.5px}
  input[type=text]{width:100%;padding:6px 8px;border-radius:6px;border:1px solid var(--line);
    background:#0c1424;color:var(--text);font-size:12px}
  button{background:#182238;color:var(--text);border:1px solid var(--line);border-radius:6px;
    padding:4px 9px;font-size:11.5px;cursor:pointer}
  button.on{background:#24324f;border-color:#3b5079}
  #legend{padding:10px 16px;border-bottom:1px solid var(--line);display:flex;flex-direction:column;gap:3px}
  .lg{display:flex;align-items:center;gap:7px;color:var(--dim);font-size:11.5px}
  .dot{width:9px;height:9px;border-radius:50%;flex:none}
  #detail{padding:12px 16px;overflow:auto;flex:1}
  #detail h2{font-size:13px;margin:0 0 3px;word-break:break-all}
  #detail .sub{color:var(--dim);font-size:11px;margin-bottom:8px}
  .grp{margin-top:11px}
  .grp .t{color:var(--dim);font-size:10.5px;text-transform:uppercase;letter-spacing:.07em;margin-bottom:3px}
  .row{display:flex;align-items:center;gap:6px;padding:1.5px 0;cursor:pointer;font-size:11.5px}
  .row:hover{color:#fff;text-decoration:underline}
  .row .k{color:var(--dim);font-size:10px;margin-left:auto;flex:none}
  #stage{flex:1;position:relative}
  canvas{display:block;width:100%;height:100%;cursor:grab}
  #tip{position:absolute;pointer-events:none;background:#0a1122f2;border:1px solid var(--line);
    border-radius:6px;padding:5px 8px;font-size:11.5px;max-width:300px;display:none;z-index:5}
  #tip .m{color:var(--dim);font-size:10.5px}
  #hint{position:absolute;left:12px;bottom:10px;color:#5b6b8a;font-size:11px}
</style>
</head>
<body>
<div id="wrap">
  <aside id="side">
    <h1>Skill routing map</h1>
    <div id="meta"></div>
    <div id="controls">
      <input type="text" id="q" placeholder="filter by name…">
      <button id="mode" class="on">radial</button>
      <label class="chk"><input type="checkbox" id="showRefs"> reference files</label>
      <label class="chk"><input type="checkbox" id="showMentions"> bare mentions</label>
      <label class="chk"><input type="checkbox" id="onlyJudgment"> judgment only</label>
    </div>
    <div id="legend"></div>
    <div id="detail"></div>
  </aside>
  <div id="stage"><canvas id="c"></canvas><div id="tip"></div>
    <div id="hint">drag to pan · wheel to zoom · click a node</div></div>
</div>
<script>
const DATA = __DATA__;
const COLOR = {entry:'#f43f5e', playbook:'#f59e0b', engineering:'#60a5fa',
  judgment:'#a78bfa', productivity:'#34d399', reference:'#64748b'};
const KIND = {entry:'entry', playbook:'playbook', engineering:'engineering leaf',
  judgment:'judgment · principle-*', productivity:'productivity leaf', reference:'reference file'};
const EC = {routes:'#8ea2c8', calls:'#5b8fd6', mentions:'#33425e', reads:'#2a3550'};
const FONT = 11;

const nodes = DATA.nodes.map(n => Object.assign({}, n));
const byId = new Map(nodes.map(n => [n.id, n]));
const edges = DATA.edges.filter(e => byId.has(e.s) && byId.has(e.t))
  .map(e => ({s: byId.get(e.s), t: byId.get(e.t), k: e.k}));

let showRefs = false, showMentions = false, onlyJudgment = false;
let mode = 'radial', selected = null, query = '';
const cam = {x: 0, y: 0, k: 1};

const canvas = document.getElementById('c'), ctx = canvas.getContext('2d');
const tip = document.getElementById('tip');
const dpr = window.devicePixelRatio || 1;
const W = () => canvas.clientWidth, H = () => canvas.clientHeight;

function visible(n) {
  if (n.kind === 'reference') return showRefs;
  if (onlyJudgment) return n.kind === 'judgment' || n.kind === 'entry';
  return true;
}
function edgeVisible(e) {
  if (!visible(e.s) || !visible(e.t)) return false;
  return e.k !== 'mentions' || showMentions;
}
function radius(n) { return 4.5 + Math.min(11, Math.sqrt(n.in || 0) * 3.2); }
function labelOf(n) { return n.label || n.id; }

function resize() { canvas.width = W() * dpr; canvas.height = H() * dpr; }
function toWorld(sx, sy) { return {x: (sx - cam.x) / cam.k, y: (sy - cam.y) / cam.k}; }

function forcePositions() {
  nodes.forEach(n => { n.x = n.rx; n.y = n.ry; });
  const vis = nodes.filter(visible);
  for (let step = 0; step < 380; step++) {
    for (const a of vis) for (const b of vis) {
      if (a === b) continue;
      let dx = a.x - b.x, dy = a.y - b.y, d2 = dx * dx + dy * dy;
      if (d2 < 1) { dx = Math.random() - .5; dy = Math.random() - .5; d2 = .5; }
      if (d2 > 120000) continue;
      const f = 1500 / d2;
      a.vx = (a.vx || 0) + dx * f; a.vy = (a.vy || 0) + dy * f;
    }
    for (const e of edges) {
      if (!edgeVisible(e)) continue;
      const dx = e.t.x - e.s.x, dy = e.t.y - e.s.y, d = Math.hypot(dx, dy) || 1;
      const rest = e.k === 'reads' ? 50 : 100, f = (d - rest) * 0.011;
      e.s.vx = (e.s.vx || 0) + dx / d * f; e.s.vy = (e.s.vy || 0) + dy / d * f;
      e.t.vx = (e.t.vx || 0) - dx / d * f; e.t.vy = (e.t.vy || 0) - dy / d * f;
    }
    for (const n of vis) {
      n.vx *= .84; n.vy *= .84; n.x += n.vx; n.y += n.vy;
    }
  }
}
function layout() {
  if (mode === 'force') forcePositions(); else nodes.forEach(n => { n.x = n.rx; n.y = n.ry; });
  fit();
}
function fit() {
  const vis = nodes.filter(visible);
  if (!vis.length) return;
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity, maxPx = 0;
  for (const n of vis) {
    x0 = Math.min(x0, n.x); x1 = Math.max(x1, n.x);
    y0 = Math.min(y0, n.y); y1 = Math.max(y1, n.y);
    maxPx = Math.max(maxPx, Math.min(230, labelOf(n).length * 5.9 + 12));
  }
  const pad = 16, side = maxPx + 14;
  const bw = Math.max(1, x1 - x0), bh = Math.max(1, y1 - y0);
  const kx = (W() - (side * 2 + pad * 2)) / bw;
  const ky = (H() - (26 * 2 + pad * 2)) / bh;
  cam.k = Math.max(0.12, Math.min(2.4, Math.min(kx, ky)));
  cam.x = W() / 2 - ((x0 + x1) / 2) * cam.k;
  cam.y = H() / 2 - ((y0 + y1) / 2) * cam.k;
}

function draw() {
  const near = new Set();
  if (selected) for (const e of edges) {
    if (!edgeVisible(e)) continue;
    if (e.s === selected) near.add(e.t);
    if (e.t === selected) near.add(e.s);
  }
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, W(), H());
  ctx.save(); ctx.translate(cam.x, cam.y); ctx.scale(cam.k, cam.k);

  for (const e of edges) {
    if (!edgeVisible(e)) continue;
    const hot = selected && (e.s === selected || e.t === selected);
    ctx.globalAlpha = hot ? .95 : (selected ? .07 : (e.k === 'routes' ? .26 : .13));
    ctx.strokeStyle = EC[e.k];
    ctx.lineWidth = (hot ? 1.7 : e.k === 'routes' ? 1 : .8) / cam.k;
    ctx.setLineDash(e.k === 'mentions' ? [3 / cam.k, 4 / cam.k] : []);
    ctx.beginPath(); ctx.moveTo(e.s.x, e.s.y); ctx.lineTo(e.t.x, e.t.y); ctx.stroke();
  }
  ctx.setLineDash([]);

  for (const n of nodes) {
    if (!visible(n)) continue;
    const hot = selected === n || near.has(n);
    ctx.globalAlpha = (selected && !hot) || (query && !n.id.toLowerCase().includes(query)) ? .16 : 1;
    ctx.beginPath(); ctx.arc(n.x, n.y, radius(n), 0, Math.PI * 2);
    ctx.fillStyle = COLOR[n.kind]; ctx.fill();
    if (selected === n) { ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.8 / cam.k; ctx.stroke(); }
  }
  ctx.restore();

  // labels in screen space: constant size, no clipping drift
  ctx.font = FONT + 'px ui-sans-serif,-apple-system,sans-serif';
  ctx.textBaseline = 'middle';
  for (const n of nodes) {
    if (!visible(n)) continue;
    const hot = selected === n || near.has(n);
    const fade = (selected && !hot) || (query && !n.id.toLowerCase().includes(query));
    const sx = n.x * cam.k + cam.x, sy = n.y * cam.k + cam.y;
    if (sx < -50 || sy < -30 || sx > W() + 220 || sy > H() + 30) continue;
    const cos = Math.cos(n.ang || 0);
    const right = mode === 'radial' ? cos > 0.25 : true;
    const left = mode === 'radial' ? cos < -0.25 : false;
    ctx.globalAlpha = fade ? .16 : 1;
    ctx.fillStyle = hot ? '#ffffff' : '#c2cfe4';
    ctx.textAlign = left ? 'right' : 'left';
    const r = radius(n) * cam.k;
    if (mode === 'radial' && (left || right)) {
      ctx.fillText(labelOf(n), left ? sx - r - 5 : sx + r + 5, sy);
    } else {
      ctx.textAlign = 'center'; ctx.textBaseline = 'bottom';
      ctx.fillText(labelOf(n), sx, sy - r - 4);
      ctx.textBaseline = 'middle';
    }
  }
  ctx.globalAlpha = 1;
}

let dragNode = null, dragMoved = false, panning = false;
function pick(sx, sy) {
  const w = toWorld(sx, sy);
  let best = null, bd = 1e9;
  for (const n of nodes) {
    if (!visible(n)) continue;
    const d = Math.hypot(n.x - w.x, n.y - w.y);
    if (d < radius(n) + 7 / cam.k && d < bd) { bd = d; best = n; }
  }
  return best;
}
canvas.addEventListener('mousedown', ev => {
  const rect = canvas.getBoundingClientRect();
  const n = pick(ev.clientX - rect.left, ev.clientY - rect.top);
  dragMoved = false;
  if (n) dragNode = n; else { panning = true; canvas.style.cursor = 'grabbing'; }
});
canvas.addEventListener('mousemove', ev => {
  const rect = canvas.getBoundingClientRect();
  const mx = ev.clientX - rect.left, my = ev.clientY - rect.top;
  if (dragNode) { const w = toWorld(mx, my); dragMoved = true; dragNode.x = w.x; dragNode.y = w.y; }
  else if (panning) { cam.x += ev.movementX; cam.y += ev.movementY; }
  const n = pick(mx, my);
  canvas.style.cursor = n ? 'pointer' : (panning ? 'grabbing' : 'grab');
  if (n && !panning) {
    tip.style.display = 'block';
    tip.style.left = Math.min(mx + 14, W() - 310) + 'px';
    tip.style.top = Math.min(my + 14, H() - 66) + 'px';
    tip.innerHTML = '<b>' + labelOf(n) + '</b><div class="m">' + KIND[n.kind] + ' · ' +
      n.in + ' in · ' + n.out + ' out · ' + n.lines + ' lines</div>';
  } else tip.style.display = 'none';
});
window.addEventListener('mouseup', () => {
  if (dragNode && !dragMoved) { selected = dragNode; renderDetail(); }
  dragNode = null; panning = false; canvas.style.cursor = 'grab';
});
canvas.addEventListener('wheel', ev => {
  ev.preventDefault();
  const rect = canvas.getBoundingClientRect();
  const mx = ev.clientX - rect.left, my = ev.clientY - rect.top, w = toWorld(mx, my);
  cam.k = Math.max(.12, Math.min(3.5, cam.k * (ev.deltaY < 0 ? 1.12 : .89)));
  cam.x = mx - w.x * cam.k; cam.y = my - w.y * cam.k;
}, {passive: false});

document.getElementById('q').addEventListener('input', e => { query = e.target.value.trim().toLowerCase(); });
document.getElementById('showRefs').addEventListener('change', e => { showRefs = e.target.checked; layout(); });
document.getElementById('showMentions').addEventListener('change', e => { showMentions = e.target.checked; });
document.getElementById('onlyJudgment').addEventListener('change', e => { onlyJudgment = e.target.checked; layout(); });
document.getElementById('mode').addEventListener('click', e => {
  mode = mode === 'radial' ? 'force' : 'radial';
  e.target.textContent = mode; e.target.classList.toggle('on', mode === 'radial');
  layout();
});

function refCount(n) { return edges.filter(e => e.s === n && e.t.kind === 'reference').length; }
function renderDetail() {
  const d = document.getElementById('detail');
  if (!selected) {
    const hubs = DATA.meta.hubs.slice(0, 10).map(([n, c]) =>
      '<div class="row" data-go="' + n + '">' + n + '<span class="k">' + c + ' in</span></div>').join('');
    d.innerHTML = '<h2>Nothing selected</h2><div class="sub">No skill here is auto-discovered: all ' +
      DATA.meta.dmi + ' set <code>disable-model-invocation: true</code>. The only way in is a pointer ' +
      'from the entry, a playbook step, or another skill. This graph is that pointer surface.</div>' +
      '<div class="grp"><div class="t">Most pointed-at</div>' + hubs + '</div>';
    bindRows(); return;
  }
  const inbound = edges.filter(e => e.t === selected && edgeVisible(e));
  const outbound = edges.filter(e => e.s === selected && edgeVisible(e));
  const list = (arr, dir) => arr.length ? arr.map(e => {
    const other = dir === 'in' ? e.s : e.t;
    return '<div class="row" data-go="' + other.id + '">' + labelOf(other) +
      '<span class="k">' + e.k + '</span></div>';
  }).join('') : '<div class="sub">none</div>';
  d.innerHTML = '<h2>' + labelOf(selected) + '</h2><div class="sub">' + KIND[selected.kind] + '<br>' +
    selected.in + ' inbound · ' + selected.out + ' outbound · ' + selected.lines + ' lines' +
    (selected.kind === 'reference' ? '' : ' · reads ' + refCount(selected) + ' reference files') + '</div>' +
    '<div class="grp"><div class="t">Reached from (' + inbound.length + ')</div>' + list(inbound, 'in') + '</div>' +
    '<div class="grp"><div class="t">Points to (' + outbound.length + ')</div>' + list(outbound, 'out') + '</div>';
  bindRows();
}
function bindRows() {
  document.querySelectorAll('#detail .row').forEach(el => {
    el.onclick = () => { const n = byId.get(el.getAttribute('data-go')); if (n) { selected = n; renderDetail(); } };
  });
}
document.getElementById('legend').innerHTML =
  Object.keys(COLOR).map(k =>
    '<div class="lg"><span class="dot" style="background:' + COLOR[k] + '"></span>' + KIND[k] + '</div>').join('') +
  '<div class="lg" style="margin-top:6px"><svg width="22" height="8"><line x1="0" y1="4" x2="22" y2="4" stroke="#8ea2c8" stroke-width="1.6"/></svg>routes from the entry or a playbook</div>' +
  '<div class="lg"><svg width="22" height="8"><line x1="0" y1="4" x2="22" y2="4" stroke="#5b8fd6" stroke-width="1.6"/></svg>explicit "read this" hand-off</div>' +
  '<div class="lg"><svg width="22" height="8"><line x1="0" y1="4" x2="22" y2="4" stroke="#33425e" stroke-width="1.6" stroke-dasharray="3 3"/></svg>passing mention (off by default)</div>';
document.getElementById('meta').innerHTML =
  '<b>' + DATA.meta.total + '</b> skills, all <b>' + DATA.meta.dmi + '</b> closed to discovery<br>' +
  '<b>' + DATA.meta.playbooks + '</b> playbooks · <b>' + DATA.meta.edges + '</b> edges · <b>' +
  DATA.meta.orphans.length + '</b> unreachable';

resize(); layout(); renderDetail();
(function loop() { draw(); requestAnimationFrame(loop); })();
window.addEventListener('resize', () => { resize(); fit(); });
</script>
</body>
</html>
"""
# ---------- layout and write ----------
import math, collections as _c
layers = {'entry': 0, 'playbook': 1, 'engineering': 2, 'productivity': 2,
          'judgment': 3, 'reference': 4}
R = {0: 0, 1: 175, 2: 375, 3: 545, 4: 700}
STEP = {2: 36, 3: 34, 4: 40}
slots = _c.defaultdict(list)
for n in data['nodes']:
    slots[layers[n['kind']]].append(n)
for ring, ns in slots.items():
    ns.sort(key=lambda n: (n['kind'], -n.get('in', 0), n['id']))
    for i, n in enumerate(ns):
        ang = -math.pi / 2 + 2 * math.pi * (i + 0.5) / len(ns)
        r = R[ring] + STEP.get(ring, 0) * (i % 3)
        n['rx'], n['ry'] = r * math.cos(ang), r * math.sin(ang)
        n['ang'] = ang

payload = json.dumps(data, ensure_ascii=False)
pathlib.Path('skill-map.html').write_text(TEMPLATE.replace('__DATA__', payload), encoding='utf-8')
print('wrote skill-map.html', pathlib.Path('skill-map.html').stat().st_size, 'bytes')
