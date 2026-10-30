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

# 入口的 playbook 表用 markdown 链接指向 playbooks/<name>.md
entry_txt = pathlib.Path(skills[entry]['path']).read_text(encoding='utf-8')
for m in set(re.findall(r'playbooks/([a-z0-9-]+)\.md', entry_txt)):
    if m in playbooks: edges.append(dict(s=entry, t='pb:'+m, k='routes'))
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
  :root{--bg:#0a101c;--panel:#111a2c;--line:#22304d;--text:#e6ecf8;--dim:#8fa1c0}
  *{box-sizing:border-box}
  html,body{height:100%;margin:0;background:var(--bg);color:var(--text);
    font:13px/1.5 ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif;overflow:hidden}
  #wrap{display:flex;height:100%}
  #side{width:318px;min-width:318px;border-right:1px solid var(--line);background:var(--panel);
    display:flex;flex-direction:column}
  h1{font-size:13px;margin:0;padding:13px 16px 5px}
  #meta{padding:0 16px 11px;color:var(--dim);font-size:11.5px;border-bottom:1px solid var(--line);line-height:1.7}
  #meta b{color:var(--text)}
  #controls{padding:9px 16px;border-bottom:1px solid var(--line);display:flex;flex-wrap:wrap;gap:7px;align-items:center}
  label.chk{display:flex;align-items:center;gap:5px;color:var(--dim);cursor:pointer;font-size:11.5px}
  input[type=text]{width:100%;padding:6px 8px;border-radius:6px;border:1px solid var(--line);
    background:#0c1424;color:var(--text);font-size:12px}
  #legend{padding:9px 16px;border-bottom:1px solid var(--line);display:flex;flex-direction:column;gap:3px}
  .lg{display:flex;align-items:center;gap:7px;color:var(--dim);font-size:11.5px}
  .dot{width:9px;height:9px;border-radius:50%;flex:none}
  #detail{padding:11px 16px;overflow:auto;flex:1}
  #detail h2{font-size:13px;margin:0 0 3px;word-break:break-all}
  #detail .sub{color:var(--dim);font-size:11px;margin-bottom:8px}
  .grp{margin-top:10px}
  .grp .t{color:var(--dim);font-size:10.5px;text-transform:uppercase;letter-spacing:.07em;margin-bottom:3px}
  .row{display:flex;align-items:center;gap:6px;padding:1.5px 0;cursor:pointer;font-size:11.5px}
  .row:hover{color:#fff;text-decoration:underline}
  .row .k{color:var(--dim);font-size:10px;margin-left:auto;flex:none}
  #stage{flex:1;position:relative}
  canvas{display:block;width:100%;height:100%;cursor:grab}
  #tip{position:absolute;pointer-events:none;background:#0a1122f2;border:1px solid var(--line);
    border-radius:6px;padding:5px 8px;font-size:11.5px;max-width:300px;display:none;z-index:5}
  #tip .m{color:var(--dim);font-size:10.5px}
  #hint{position:absolute;left:12px;bottom:9px;color:#54658a;font-size:11px}
</style>
</head>
<body>
<div id="wrap">
  <aside id="side">
    <h1>Skill routing map</h1>
    <div id="meta"></div>
    <div id="controls">
      <input type="text" id="q" placeholder="filter by name…">
      <label class="chk"><input type="checkbox" id="showRegistry"> entry → every skill</label>
      <label class="chk"><input type="checkbox" id="showCross" checked> skill → skill</label>
      <label class="chk"><input type="checkbox" id="showMentions"> bare mentions</label>
      <label class="chk"><input type="checkbox" id="showReads"> reference files</label>
    </div>
    <div id="legend"></div>
    <div id="detail"></div>
  </aside>
  <div id="stage"><canvas id="c"></canvas><div id="tip"></div>
    <div id="hint">drag to pan · wheel to zoom · click a node to focus</div></div>
</div>
<script>
const DATA = __DATA__;
const COLOR = {entry:'#f43f5e', playbook:'#f59e0b', engineering:'#60a5fa',
  judgment:'#a78bfa', productivity:'#34d399', reference:'#64748b'};
const KIND = {entry:'entry', playbook:'playbook', engineering:'engineering leaf',
  judgment:'judgment · principle-*', productivity:'productivity leaf', reference:'reference file'};
const FONT = 11;

const nodes = DATA.nodes.map(n => Object.assign({}, n));
const byId = new Map(nodes.map(n => [n.id, n]));
const edges = DATA.edges.filter(e => byId.has(e.s) && byId.has(e.t))
  .map(e => ({s: byId.get(e.s), t: byId.get(e.t), k: e.k}));

let showRegistry = false, showCross = true, showMentions = false, showReads = false;
let selected = null, query = '', hovered = null;
const cam = {x: 0, y: 0, k: 1};

const canvas = document.getElementById('c'), ctx = canvas.getContext('2d');
const tip = document.getElementById('tip');
const dpr = window.devicePixelRatio || 1;
const W = () => canvas.clientWidth, H = () => canvas.clientHeight;
const labelOf = n => n.label || n.id;
const radius = n => 4 + Math.min(9, Math.sqrt(n.in || 0) * 2.6);

function isRegistry(e) { return e.k === 'routes' && e.s.kind === 'entry' && e.t.kind !== 'playbook'; }
function visible(n) { return n.kind === 'reference' ? showReads : true; }
function edgeVisible(e) {
  if (!visible(e.s) || !visible(e.t)) return false;
  if (isRegistry(e)) return showRegistry;
  if (e.k === 'mentions') return showMentions;
  if (e.k === 'reads') return showReads;
  if (e.k === 'calls') return showCross;
  return true;
}
function resize() { canvas.width = W() * dpr; canvas.height = H() * dpr; }
function toWorld(sx, sy) { return {x: (sx - cam.x) / cam.k, y: (sy - cam.y) / cam.k}; }

function fit() {
  const vis = nodes.filter(visible);
  if (!vis.length) return;
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity, maxPx = 0;
  for (const n of vis) {
    x0 = Math.min(x0, n.x); x1 = Math.max(x1, n.x);
    y0 = Math.min(y0, n.y); y1 = Math.max(y1, n.y);
    maxPx = Math.max(maxPx, Math.min(260, labelOf(n).length * 5.9 + 16));
  }
  const bw = Math.max(1, x1 - x0) + 60, bh = Math.max(1, y1 - y0) + 80;
  const kx = (W() - (maxPx + 40) - 30) / bw;
  const ky = (H() - 90) / bh;
  cam.k = Math.max(0.14, Math.min(2.2, Math.min(kx, ky)));
  cam.x = W() / 2 - ((x0 + x1) / 2) * cam.k - maxPx / 2 + 10;
  cam.y = H() / 2 - ((y0 + y1) / 2) * cam.k;
}

const COLUMNS = [
  {x: 90,   w: 60,  label: 'ENTRY'},
  {x: 430,  w: 150, label: 'PLAYBOOKS'},
  {x: 830,  w: 250, label: 'SKILLS'},
  {x: 1230, w: 260, label: 'JUDGMENT'},
  {x: 1570, w: 250, label: 'REFERENCE FILES'}
];

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

  // 列底色与列名
  for (const c of COLUMNS) {
    ctx.fillStyle = 'rgba(255,255,255,0.014)';
    ctx.fillRect(c.x - 34, -2600, c.w + 68, 5200);
  }

  for (const e of edges) {
    if (!edgeVisible(e)) continue;
    const hot = selected && (e.s === selected || e.t === selected);
    const forward = e.t.x >= e.s.x;
    const x1 = e.s.x + radius(e.s) * (forward ? 1 : -1), x2 = e.t.x - radius(e.t) * (forward ? 1 : -1);
    const mid = (x1 + x2) / 2;
    ctx.globalAlpha = hot ? .95 : (selected ? .05 : (isRegistry(e) ? .12 : .22));
    ctx.strokeStyle = e.k === 'reads' || e.k === 'mentions' ? '#3a4a68'
      : isRegistry(e) ? '#4d5f80' : '#7f97c4';
    ctx.lineWidth = (hot ? 1.7 : 1) / cam.k;
    ctx.setLineDash(e.k === 'mentions' || e.k === 'reads' ? [3 / cam.k, 4 / cam.k] : []);
    ctx.beginPath(); ctx.moveTo(e.s.x + radius(e.s) * (forward ? 1 : -1), e.s.y);
    if (forward) ctx.bezierCurveTo(mid, e.s.y, mid, e.t.y, x2, e.t.y);
    else ctx.bezierCurveTo(e.s.x + 90, e.s.y - 40, e.t.x + 90, e.t.y + 40, x2, e.t.y);
    ctx.stroke();
  }
  ctx.setLineDash([]);

  for (const n of nodes) {
    if (!visible(n)) continue;
    const hot = selected === n || near.has(n);
    ctx.globalAlpha = (selected && !hot) || (query && !n.id.toLowerCase().includes(query)) ? .15 : 1;
    ctx.beginPath(); ctx.arc(n.x, n.y, radius(n), 0, Math.PI * 2);
    ctx.fillStyle = COLOR[n.kind]; ctx.fill();
    if (n.manual) {
      ctx.strokeStyle = 'rgba(148,163,184,0.85)';
      ctx.lineWidth = 1 / cam.k;
      ctx.setLineDash([2 / cam.k, 2 / cam.k]);
      ctx.beginPath(); ctx.arc(n.x, n.y, radius(n) + 3.5 / cam.k, 0, Math.PI * 2); ctx.stroke();
      ctx.setLineDash([]);
    }
    if (selected === n) { ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.8 / cam.k; ctx.stroke(); }
  }
  ctx.restore();

  ctx.font = FONT + 'px ui-sans-serif,-apple-system,sans-serif';
  ctx.textBaseline = 'middle';
  for (const n of nodes) {
    if (!visible(n)) continue;
    const hot = selected === n || near.has(n);
    const fade = (selected && !hot) || (query && !n.id.toLowerCase().includes(query));
    const sx = n.x * cam.k + cam.x, sy = n.y * cam.k + cam.y;
    if (sy < -30 || sy > H() + 30 || sx < -40 || sx > W() + 260) continue;
    ctx.globalAlpha = fade ? .14 : 1;
    const lx = sx + radius(n) * cam.k + 6;
    ctx.textAlign = 'left';
    const tw = ctx.measureText(labelOf(n)).width;
    ctx.fillStyle = 'rgba(10,16,28,' + (fade ? 0.25 : 0.86) + ')';
    ctx.beginPath();
    ctx.roundRect(lx - 3, sy - 8, tw + 6, 16, 3);
    ctx.fill();
    ctx.fillStyle = hot ? '#ffffff' : '#c6d3e8';
    ctx.fillText(labelOf(n), lx, sy);
  }
  ctx.globalAlpha = 1;

  // 列头固定在视口顶部
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';
  for (const c of COLUMNS) {
    const hx = (c.x - 34) * cam.k + cam.x;
    if (hx < -80 || hx > W()) continue;
    ctx.font = '600 10px ui-sans-serif,sans-serif';
    ctx.fillStyle = 'rgba(143,161,192,0.75)';
    ctx.fillText(c.label, hx, 14);
    ctx.strokeStyle = 'rgba(143,161,192,0.14)';
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(hx, 26); ctx.lineTo(hx, H()); ctx.stroke();
  }
}

let dragNode = null, dragMoved = false, panning = false;
function pick(sx, sy) {
  const w = toWorld(sx, sy);
  let best = null, bd = 1e9;
  for (const n of nodes) {
    if (!visible(n)) continue;
    const d = Math.hypot(n.x - w.x, n.y - w.y);
    if (d < radius(n) + 8 / cam.k && d < bd) { bd = d; best = n; }
  }
  return best;
}
canvas.addEventListener('mousedown', ev => {
  const r = canvas.getBoundingClientRect();
  const n = pick(ev.clientX - r.left, ev.clientY - r.top);
  dragMoved = false;
  if (n) dragNode = n; else { panning = true; canvas.style.cursor = 'grabbing'; }
});
canvas.addEventListener('mousemove', ev => {
  const r = canvas.getBoundingClientRect();
  const mx = ev.clientX - r.left, my = ev.clientY - r.top;
  if (dragNode) { const w = toWorld(mx, my); dragMoved = true; dragNode.x = w.x; dragNode.y = w.y; }
  else if (panning) { cam.x += ev.movementX; cam.y += ev.movementY; }
  const n = pick(mx, my);
  hovered = n;
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
  const r = canvas.getBoundingClientRect();
  const mx = ev.clientX - r.left, my = ev.clientY - r.top, w = toWorld(mx, my);
  cam.k = Math.max(.1, Math.min(3.5, cam.k * (ev.deltaY < 0 ? 1.12 : .89)));
  cam.x = mx - w.x * cam.k; cam.y = my - w.y * cam.k;
}, {passive: false});

document.getElementById('q').addEventListener('input', e => { query = e.target.value.trim().toLowerCase(); });
for (const [id, set] of [['showRegistry', v => showRegistry = v], ['showCross', v => showCross = v],
                         ['showMentions', v => showMentions = v], ['showReads', v => showReads = v]]) {
  document.getElementById(id).addEventListener('change', e => { set(e.target.checked); fit(); });
}

function renderDetail() {
  const d = document.getElementById('detail');
  if (!selected) {
    const hubs = DATA.meta.hubs.slice(0, 10).map(([n, c]) =>
      '<div class="row" data-go="' + n + '">' + n + '<span class="k">' + c + ' in</span></div>').join('');
    d.innerHTML = '<h2>Nothing selected</h2><div class="sub">All ' + DATA.meta.total +
      ' skills set <code>disable-model-invocation: true</code>, so nothing is auto-discovered. ' +
      'Left to right: the entry picks a playbook, the playbook names the skills, the skills read judgment. ' +
      'Click any node to isolate its wires.</div>' +
      '<div class="grp"><div class="t">Most pointed-at</div>' + hubs + '</div>' +
      '<div class="grp"><div class="t">Manual only · nothing routes here (' + DATA.meta.manual.length + ')</div>' +
      DATA.meta.manual.map(n => '<div class="row" data-go="' + n + '">' + n + '</div>').join('') + '</div>';
    bindRows(); return;
  }
  const ins = edges.filter(e => e.t === selected && edgeVisible(e));
  const outs = edges.filter(e => e.s === selected && edgeVisible(e));
  const list = (arr, dir) => arr.length ? arr.map(e => {
    const o = dir === 'in' ? e.s : e.t;
    return '<div class="row" data-go="' + o.id + '">' + labelOf(o) + '<span class="k">' + e.k + '</span></div>';
  }).join('') : '<div class="sub">none</div>';
  d.innerHTML = '<h2>' + labelOf(selected) + '</h2><div class="sub">' + KIND[selected.kind] + '<br>' +
    selected.in + ' inbound · ' + selected.out + ' outbound · ' + selected.lines + ' lines</div>' +
    '<div class="grp"><div class="t">Reached from (' + ins.length + ')</div>' + list(ins, 'in') + '</div>' +
    '<div class="grp"><div class="t">Points to (' + outs.length + ')</div>' + list(outs, 'out') + '</div>';
  bindRows();
}
function bindRows() {
  document.querySelectorAll('#detail .row').forEach(el => {
    el.onclick = () => { const n = byId.get(el.getAttribute('data-go')); if (n) { selected = n; renderDetail(); } };
  });
}
document.getElementById('legend').innerHTML =
  Object.keys(COLOR).map(k => '<div class="lg"><span class="dot" style="background:' + COLOR[k] +
    '"></span>' + KIND[k] + '</div>').join('') +
  '<div class="lg" style="margin-top:5px"><svg width="22" height="8"><line x1="0" y1="4" x2="22" y2="4" stroke="#7f97c4" stroke-width="1.6"/></svg>playbook step or hand-off</div>' +
  '<div class="lg"><svg width="22" height="8"><line x1="0" y1="4" x2="22" y2="4" stroke="#4d5f80" stroke-width="1.4"/></svg>entry registry edge (toggle)</div>' +
  '<div class="lg"><svg width="14" height="14"><circle cx="7" cy="7" r="4.5" fill="#334" stroke="#94a3b8" stroke-dasharray="2 2"/></svg>manual only: nothing routes to it</div>';
document.getElementById('meta').innerHTML =
  '<b>' + DATA.meta.total + '</b> skills, all <b>' + DATA.meta.dmi + '</b> closed to discovery<br>' +
  '<b>' + DATA.meta.playbooks + '</b> playbooks · <b>' + DATA.meta.edges + '</b> edges · <b>' +
  DATA.meta.orphans.length + '</b> unreachable';

resize(); fit(); renderDetail();
(function loop() { draw(); requestAnimationFrame(loop); })();
window.addEventListener('resize', () => { resize(); fit(); });
</script>
</body>
</html>
"""

# manual = 只有入口注册表提到它，没有任何 playbook 或技能真的指向它
entry_ids = {n['id'] for n in nodes if n['kind'] == 'entry'}
def is_registry(e):
    return e['k'] == 'routes' and e['s'] in entry_ids and by_kind(e['t']) != 'playbook'
def by_kind(i):
    for n in nodes:
        if n['id'] == i: return n['kind']
    return 'reference'
routed = {e['t'] for e in edges if not is_registry(e) and e['k'] != 'reads'}
for n in nodes:
    n['manual'] = n['kind'] != 'reference' and n['id'] not in routed

# ---------- layered architecture layout ----------
import math, collections as _c

LAYER_X = {'entry': 90, 'playbook': 430, 'engineering': 830, 'productivity': 830,
           'judgment': 1230, 'reference': 1570}
GAP = {'entry': 60, 'playbook': 56, 'engineering': 42, 'productivity': 42,
       'judgment': 46, 'reference': 34}

byname = {n['id']: n for n in nodes}
for n in nodes:
    n['layer'] = (0 if n['kind'] == 'entry' else 1 if n['kind'] == 'playbook'
                  else 2 if n['kind'] in ('engineering', 'productivity')
                  else 3 if n['kind'] == 'judgment' else 4)

# 第一遍：按名字排
cols = _c.defaultdict(list)
for n in nodes:
    cols[n['layer']].append(n)

def place(order):
    y = 0
    for n in order:
        n['y'] = y
        y += GAP[n['kind']]
    off = y / 2
    for n in order:
        n['y'] -= off

for n in nodes:
    n['y'] = 0
for layer in sorted(cols):
    place(cols[layer])
for n in cols[0]:
    n['y'] = 0

# 叶子的次序：按连接到的 playbook 的平均 y
def bary(n, cand, frm):
    ys = [c['y'] for c in cand if (frm(c['id'], n['id']) or frm(n['id'], c['id']))]
    return sum(ys) / len(ys) if ys else n['y']

def links_from(ids):
    return [(e['s'], e['t']) for e in edges if e['k'] != 'reads']
L = links_from(None)
def is_link(a, b): return (a, b) in L or (b, a) in L

def bary_targets(n, pool):
    ys = [c['y'] for c in pool if is_link(n['id'], c['id'])]
    return sum(ys) / len(ys) if ys else n['y']

for _ in range(4):
    cols[1].sort(key=lambda n: bary_targets(n, cols[2]))
    place(cols[1])
    for layer in (2, 3, 4):
        pool = cols[layer]
        pool.sort(key=lambda n: bary(n, cols[layer - 1], is_link))
        place(pool)

place(cols[1])
for n in cols[0]:
    n['y'] = 0

for n in nodes:
    n['x'] = LAYER_X.get(n['kind'], 900)

data['nodes'] = nodes
data['meta']['manual'] = sorted(n['id'] for n in nodes if n.get('manual'))
payload = json.dumps(data, ensure_ascii=False)
pathlib.Path('skill-map.html').write_text(TEMPLATE.replace('__DATA__', payload), encoding='utf-8')
print('wrote skill-map.html', pathlib.Path('skill-map.html').stat().st_size, 'bytes')
