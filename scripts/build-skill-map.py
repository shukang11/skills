#!/usr/bin/env python3
"""Regenerate skill-map.html from the skills tree.

Nodes: every SKILL.md, every playbook, and every .md file a skill's body points at
(a markdown link, or a backticked path inside that skill's own directory).
Edges: routes (the entry or a playbook step points at it), calls (an explicit
"read this" hand-off), mentions (a passing reference), reads (a skill pointing at
its own reference file), trigger and registry (the entry's Non-negotiables and Layers).

The map is no longer a repo file: scripts/serve-skill-map.py builds it into a temp
directory and serves it. Run this script directly only when you want a snapshot.

Run from the repository root: python3 scripts/build-skill-map.py --out /tmp/map

Options:
  --out DIR    where skill-map.html lands (default: a fresh temp dir)
  --json PATH  where the page's graph data lands (default: /tmp/skillgraph.json)
"""
import argparse, os, pathlib, re, json, collections, tempfile
_ap=argparse.ArgumentParser(description='Regenerate skill-map.html from the skills tree.')
_ap.add_argument('--out', default=None,
                help='directory for skill-map.html (default: a temp dir; the map is no longer a repo file)')
_ap.add_argument('--json', default='/tmp/skillgraph.json', help="where to write the graph data")
_args=_ap.parse_args()
OUT=pathlib.Path(_args.out) if _args.out else pathlib.Path(tempfile.mkdtemp(prefix='skill-map-'))
GRAPH_OUT=pathlib.Path(_args.json)
OUT.mkdir(parents=True, exist_ok=True)
root=pathlib.Path('.')
SK=re.compile(r'`([a-z][a-z0-9-]{2,})`')
LINK=re.compile(r'\]\((\.\./[^)]*SKILL\.md)\)')
# a markdown link or a backticked path that ends in .md: both count as reading that file
MDCAND=re.compile(r'(?:`|\]\()([^`()\s]+\.md)[`)]?')
def _first_sentence(s, limit=190):
    s=re.sub(r'\s+', ' ', s).strip().strip('"').strip().replace('\\"', '"')
    cut=re.split(r'(?<=[.!?])\s', s)[0].strip()
    return cut if len(cut)<=limit else cut[:limit-1]+'…'

def _skill_note(txt):
    """The frontmatter description, folded or quoted, cut to one sentence.
    The page shows this on a card; serve-skill-map.py overrides it with a
    one-line Chinese note at request time."""
    m=re.match(r'\A---\n(.*?)\n---\n', txt, re.S)
    if not m: return ''
    fm=m.group(1)
    d=re.search(r'^description:[ \t]*(.*)$', fm, re.M)
    if not d: return ''
    val=d.group(1).strip()
    if val in ('', '>-', '>', '|-', '|', '>+', '|+'):
        block=[]
        for line in fm[d.end():].splitlines():
            if line.strip() and not line.startswith((' ', '\t')): break
            block.append(line.strip())
        val=' '.join(x for x in block if x)
    return _first_sentence(val)

def _playbook_note(txt):
    for line in txt.splitlines():
        s=line.strip()
        if s and not s.startswith(('#', '---', '|')): return _first_sentence(s, 120)
    return ''

skills={}
for p in sorted(root.glob('skills/*/*/SKILL.md')):
    grp=p.parts[1]; name=p.parent.name
    txt=p.read_text(encoding='utf-8')
    skills[name]=dict(group=grp, path=str(p), dmi='disable-model-invocation: true' in txt,
                      lines=len(txt.splitlines()), note=_skill_note(txt))
entry='pstack-mode'
pbroot=pathlib.Path(f'skills/{skills[entry]["group"]}/{entry}/playbooks')
playbooks={p.stem:str(p) for p in sorted(pbroot.glob('*.md'))}
nodes=[]; edges=[]
for n,i in skills.items():
    nodes.append(dict(id=n, kind='entry' if n==entry else i['group'], lines=i['lines'], dmi=i['dmi'],
                      note=i['note']))
for n,p in playbooks.items():
    ptxt=pathlib.Path(p).read_text(encoding='utf-8')
    nodes.append(dict(id='pb:'+n, label=n, kind='playbook', lines=len(ptxt.splitlines()),
                      note=_playbook_note(ptxt)))
for n,p in playbooks.items():
    for ln in pathlib.Path(p).read_text(encoding='utf-8').splitlines():
        for t in sorted(set(SK.findall(ln))):
            if t in skills: edges.append(dict(s='pb:'+n, t=t, k='routes'))

# 入口的 playbook 表用 markdown 链接指向 playbooks/<name>.md
entry_txt = pathlib.Path(skills[entry]['path']).read_text(encoding='utf-8')
for m in set(re.findall(r'playbooks/([a-z0-9-]+)\.md', entry_txt)):
    if m in playbooks: edges.append(dict(s=entry, t='pb:'+m, k='routes'))
def _sections(t):
    parts = re.split(r'^## (.+)$', t, flags=re.M)
    out = {}
    for i in range(1, len(parts), 2):
        out[parts[i].strip()] = parts[i + 1]
    return out

_entry_txt = pathlib.Path(skills[entry]['path']).read_text(encoding='utf-8')
_entry_secs = _sections(_entry_txt)
for _name in set(SK.findall(_entry_txt)):
    if _name not in skills or _name == entry:
        continue
    if re.search(rf'`{re.escape(_name)}`', _entry_secs.get('Non-negotiables', '')):
        edges.append(dict(s=entry, t=_name, k='trigger'))
    elif re.search(rf'`{re.escape(_name)}`', _entry_secs.get('Layers', '') + _entry_secs.get('Principles', '')):
        edges.append(dict(s=entry, t=_name, k='registry'))
    else:
        edges.append(dict(s=entry, t=_name, k='routes'))

for n,i in skills.items():
    if n == entry:
        continue
    src=n
    for ln in pathlib.Path(i['path']).read_text(encoding='utf-8').splitlines():
        low=ln.lower()
        for t in sorted(set(SK.findall(ln))):
            if t==n or t not in skills: continue
            if any(w in low for w in ('read ','open ','call ','hand ')): k='calls'
            else: k='mentions'
            edges.append(dict(s=src, t=t, k=k))
        for m in LINK.findall(ln):
            b=pathlib.Path(m).name
            if b in skills and b!=n: edges.append(dict(s=src, t=b, k='calls'))
        for m in MDCAND.findall(ln):
            if m.startswith(('..', '/')) or '://' in m: continue
            rid=pathlib.Path(os.path.normpath(pathlib.Path(i['path']).parent/m))
            if rid.is_file(): edges.append(dict(s=src, t=rid.as_posix(), k='reads'))
prio={'routes':0,'trigger':1,'calls':2,'registry':3,'mentions':4,'reads':5}
seen=set(); ded=[]
for e in sorted(edges,key=lambda x:(prio[x['k']],x['s'],x['t'])):
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
    hubs=[[k,v] for k,v in sorted(indeg.items(),key=lambda kv:(-kv[1],kv[0]))
          if k in skills][:10]))
GRAPH_OUT.write_text(json.dumps(data, ensure_ascii=False))
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
  #side{width:318px;min-width:0;flex:none;position:relative;overflow:hidden;
    border-right:1px solid var(--line);background:var(--panel);display:flex;flex-direction:column;
    transition:width .14s ease}
  body.side-hidden #side{width:0 !important;border-right:0}
  body.dragging #side,body.dragging #doc{transition:none}
  body.dragging{cursor:col-resize}
  body.dragging *{user-select:none}
  #sideHead{display:flex;align-items:center;gap:4px;padding:12px 8px 4px 16px;flex:none}
  h1{font-size:13px;margin:0;padding:0;flex:1;white-space:nowrap}
  .btn{background:#0c1424;color:var(--dim);border:1px solid var(--line);border-radius:5px;
    padding:1px 7px;cursor:pointer;font-size:12px;line-height:1.6;flex:none}
  .btn:hover{color:#fff;border-color:#3b4f74}
  .grip{position:absolute;top:0;bottom:0;width:6px;cursor:col-resize;z-index:8}
  .grip:hover,body.dragging .grip{background:#3b4f7466}
  #sideGrip{right:0}
  #docGrip{left:0}
  #sideOpen{position:absolute;left:9px;top:9px;z-index:7;display:none;background:#111a2ce6;
    color:var(--dim);border:1px solid var(--line);border-radius:6px;padding:2px 8px;cursor:pointer;font-size:12px}
  #sideOpen:hover{color:#fff}
  body.side-hidden #sideOpen{display:block}
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
  /* ---- card view ---- */
  #cards{position:absolute;inset:0;overflow:auto;padding:15px 20px 64px;display:none}
  body.view-cards #cards{display:block}
  body.view-cards canvas,body.view-cards #hint,body.view-cards #tip{display:none}
  body.view-cards #fRegistry,body.view-cards #fCross,body.view-cards #fMentions{display:none}
  #cards .sec{margin:0 0 22px}
  #cards .sec>h3{margin:0 0 10px;font-size:10.5px;font-weight:600;letter-spacing:.09em;
    text-transform:uppercase;color:#8fa1c0;display:flex;align-items:baseline;gap:10px}
  #cards .sec>h3 em{font:400 11px ui-sans-serif,sans-serif;letter-spacing:0;text-transform:none;color:#5b6d8c}
  #cards .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(248px,1fr));gap:11px}
  .card{background:#111a2c;border:1px solid var(--line);border-radius:10px;padding:11px 13px 10px;
    cursor:pointer;display:flex;flex-direction:column;gap:7px;min-height:108px;
    transition:border-color .12s ease,transform .12s ease,box-shadow .12s ease}
  .card:hover{border-color:#3f567f;transform:translateY(-1px);box-shadow:0 8px 20px #00000059}
  .card.sel{border-color:#7fb2ff;box-shadow:inset 0 0 0 1px #7fb2ff55}
  .card .nm{display:flex;align-items:center;gap:7px;font-size:12.5px;font-weight:600;color:#eaf1ff;
    word-break:break-all;line-height:1.35}
  .card .nm .dot{width:7px;height:7px;border-radius:50%;flex:none}
  .card .ds{font-size:12px;line-height:1.6;color:#b3c2da}
  .card .mt{margin-top:auto;display:flex;justify-content:space-between;gap:8px;
    font-size:10.5px;color:#6b7d9c}
  .card .mt .mn{color:#8d7fd0}
  #cards .empty{padding:40px 4px;color:var(--dim);font-size:12px}
  #doc{width:0;min-width:0;flex:none;position:relative;border-left:1px solid var(--line);background:var(--panel);
    display:flex;flex-direction:column;overflow:hidden;transition:width .16s ease}
  #doc.open{min-width:300px}
  #doc.float{position:fixed;z-index:30;height:72vh;max-height:88vh;border:1px solid var(--line);
    border-radius:8px;box-shadow:0 18px 48px #000000a6}
  #doc.float:not(.open){display:none}
  #doc.full{position:fixed;left:0 !important;top:0 !important;width:100vw !important;
    height:100vh !important;max-height:none;border-radius:0;border:0;min-width:0;z-index:40}
  #doc.float #dochead{cursor:move}
  #dochead{display:flex;align-items:center;gap:7px;padding:9px 12px;border-bottom:1px solid var(--line);flex:none}
  #dochead b{font-size:12px;word-break:break-all}
  #dochead .sp{color:var(--dim);font-size:10.5px;margin-left:auto;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  #dochead button{background:#0c1424;color:var(--dim);border:1px solid var(--line);border-radius:5px;
    padding:1px 7px;cursor:pointer;font-size:12px;line-height:1.6}
  #dochead button:hover{color:#fff;border-color:#3b4f74}
  #docbody{flex:1;overflow:auto;padding:14px 18px 48px;font-size:12.5px;line-height:1.65}
  #docbody h1{font-size:16px;margin:2px 0 9px}
  #docbody h2{font-size:13.5px;margin:17px 0 6px;padding-bottom:3px;border-bottom:1px solid var(--line)}
  #docbody h3{font-size:12.5px;margin:13px 0 4px;color:#c9d6ee}
  #docbody h4{font-size:12px;margin:11px 0 3px;color:#c9d6ee}
  #docbody p{margin:0 0 9px}
  #docbody ul,#docbody ol{margin:0 0 9px;padding-left:19px}
  #docbody li{margin:2px 0}
  #docbody code{background:#0c1424;border:1px solid var(--line);border-radius:4px;padding:0 3px;
    font:11.5px ui-monospace,SFMono-Regular,Menlo,monospace}
  #docbody pre{background:#0c1424;border:1px solid var(--line);border-radius:6px;padding:9px 11px;
    overflow:auto;margin:0 0 10px}
  #docbody pre code{background:none;border:0;padding:0;font-size:11.5px;line-height:1.5}
  #docbody table{border-collapse:collapse;margin:0 0 10px;font-size:11.5px;display:block;overflow:auto}
  #docbody th,#docbody td{border:1px solid var(--line);padding:3px 7px;text-align:left;vertical-align:top}
  #docbody th{background:#0c1424;white-space:nowrap}
  #docbody blockquote{margin:0 0 9px;padding-left:10px;border-left:2px solid var(--line);color:var(--dim)}
  #docbody a{color:#7fb2ff}
  #docbody hr{border:0;border-top:1px solid var(--line);margin:14px 0}
  #docbody .fm{color:var(--dim);font-size:11px;border:1px solid var(--line);border-radius:6px;
    padding:8px 10px;margin:0 0 12px;white-space:pre-wrap}
  #docbody .hint{color:var(--dim);font-size:12px}
</style>
</head>
<body>
<div id="wrap">
  <aside id="side">
    <div id="sideHead"><h1>技能看板 · Skill map</h1><button class="btn" id="viewBtn" title="切换到关系图">▦</button><button class="btn" id="sideToggle" title="collapse sidebar">«</button></div>
    <div id="meta"></div>
    <div id="controls">
      <input type="text" id="q" placeholder="按名字或介绍过滤…">
      <label class="chk" id="fRegistry"><input type="checkbox" id="showRegistry"> entry → every skill</label>
      <label class="chk" id="fCross"><input type="checkbox" id="showCross" checked> skill → skill</label>
      <label class="chk" id="fMentions"><input type="checkbox" id="showMentions"> bare mentions</label>
      <label class="chk" id="fReads"><input type="checkbox" id="showReads"> reference files</label>
    </div>
    <div id="legend"></div>
    <div id="detail"></div>
    <div class="grip" id="sideGrip" title="drag to resize"></div>
  </aside>
  <div id="stage"><canvas id="c"></canvas><div id="tip"></div><div id="cards"></div>
    <button id="sideOpen" title="show sidebar">»</button>
    <div id="hint">拖动平移 · 滚轮缩放 · 点圆点或名字读全文 · 双击全屏</div></div>
  <section id="doc">
    <div class="grip" id="docGrip" title="drag to resize"></div>
    <div id="dochead"><b id="doctitle"></b><span class="sp" id="docpath"></span>
      <button class="btn" id="docfloat" title="float / dock">⧉</button><button class="btn" id="docfs" title="full screen / restore">⤢</button><button class="btn" id="docclose" title="close">×</button></div>
    <div id="docbody"><div class="hint">点左侧卡片或图上的节点，这里显示它的全文。</div></div>
  </section>
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

function isRegistry(e) { return e.k === 'registry'; }
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
      : e.k === 'trigger' ? '#b98cf0' : isRegistry(e) ? '#4d5f80' : '#7f97c4';
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
    n.lab = null;
    if (!visible(n)) continue;
    const hot = selected === n || near.has(n);
    const fade = (selected && !hot) || (query && !n.id.toLowerCase().includes(query));
    const sx = n.x * cam.k + cam.x, sy = n.y * cam.k + cam.y;
    if (sy < -30 || sy > H() + 30 || sx < -40 || sx > W() + 260) continue;
    ctx.globalAlpha = fade ? .14 : 1;
    const lx = sx + radius(n) * cam.k + 6;
    ctx.textAlign = 'left';
    const tw = ctx.measureText(labelOf(n)).width;
    n.lab = {x: lx - 3, y: sy - 8, w: tw + 6, h: 16};
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
  if (best) return best;
  // the label counts as the node: the dot is small, the name is the target
  for (const n of nodes) {
    const r = n.lab;
    if (!r || !visible(n)) continue;
    if (sx >= r.x && sx <= r.x + r.w && sy >= r.y && sy <= r.y + r.h) return n;
  }
  return null;
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
  if (dragNode && !dragMoved) { select(dragNode); }
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
    el.onclick = () => { const n = byId.get(el.getAttribute('data-go')); if (n) select(n); };
  });
}

/* ---- card view: one card per node, a one-line note each ---- */
const NOTES = window.SKILL_NOTES || {};
const VIEW_KEY = 'skillmap.view';
const cardEl = document.getElementById('cards');
const SECTIONS = [
  ['entry', '入口', '从这里进'],
  ['playbook', 'playbook · 流程', '按任务类型选一条'],
  ['engineering', '工程叶子', '做到本职就停'],
  ['productivity', '协作叶子', '做到本职就停'],
  ['judgment', '判据', '跨叶子反复用的规矩'],
  ['reference', '参考文件', '按路径读，不直接点']
];
const escHtml = s => String(s).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const noteOf = n => NOTES[n.id] || n.note || '';
const inCards = () => document.body.classList.contains('view-cards');

function renderCards() {
  const q = query, parts = [];
  for (const sec of SECTIONS) {
    const kind = sec[0];
    if (kind === 'reference' && !showReads) continue;
    const pool = nodes.filter(n => n.kind === kind)
      .filter(n => !q || n.id.toLowerCase().indexOf(q) >= 0 || noteOf(n).toLowerCase().indexOf(q) >= 0)
      .sort((a, b) => labelOf(a).localeCompare(labelOf(b)));
    if (!pool.length) continue;
    parts.push('<section class="sec"><h3>' + sec[1] + '<em>' + pool.length + ' 项 · ' + sec[2] +
      '</em></h3><div class="grid">' + pool.map(n =>
        '<div class="card' + (selected === n ? ' sel' : '') + '" data-go="' + n.id + '">' +
          '<div class="nm"><span class="dot" style="background:' + COLOR[n.kind] + '"></span>' +
            escHtml(labelOf(n)) + '</div>' +
          '<div class="ds">' + escHtml(noteOf(n) || '（暂无介绍）') + '</div>' +
          '<div class="mt"><span>' + n.in + ' 入 · ' + n.out + ' 出' +
            (n.manual ? ' · <span class="mn">只能手动点</span>' : '') + '</span>' +
            '<span>' + n.lines + ' 行</span></div>' +
        '</div>').join('') + '</div></section>');
  }
  cardEl.innerHTML = parts.join('') || '<div class="empty">没有匹配的技能。</div>';
  cardEl.querySelectorAll('.card').forEach(el => {
    el.onclick = () => { const n = byId.get(el.getAttribute('data-go')); if (n) select(n); };
  });
}

function applyView(v) {
  const cards = v === 'cards';
  document.body.classList.toggle('view-cards', cards);
  const b = document.getElementById('viewBtn');
  b.textContent = cards ? '▦' : '◉';
  b.title = cards ? '切到关系图' : '切到卡片';
  storeVal(VIEW_KEY, cards ? 'cards' : 'graph');
  if (cards) renderCards(); else { resize(); fit(); }
  renderDetail();
}

document.getElementById('viewBtn').onclick = () => applyView(inCards() ? 'graph' : 'cards');
document.getElementById('q').addEventListener('input', () => { if (inCards()) renderCards(); });
document.getElementById('showReads').addEventListener('change', () => { if (inCards()) renderCards(); });

/* ---- document drawer: click a node, read its file ---- */
const docEl = document.getElementById('doc');
const docBody = document.getElementById('docbody');
const docTitle = document.getElementById('doctitle');
const docPath = document.getElementById('docpath');
let docId = null;

const esc = s => String(s).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));

function layout() {
  if (docEl.classList.contains('float') && docEl.classList.contains('open')) {
    placeDoc(docXY ? docXY.x : 40, docXY ? docXY.y : 68, false);
  }
  resize(); fit();
}

/* ---- panels: collapse, drag to resize, remember ---- */
const sideEl = document.getElementById('side');
const SIDE_KEY = 'skillmap.sideW', DOC_KEY = 'skillmap.docW', HIDE_KEY = 'skillmap.sideHidden';
let docW = 0;

const clampN = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const storeVal = (k, v) => { try { localStorage.setItem(k, String(v)); } catch (e) {} };
const loadVal = k => { try { return localStorage.getItem(k); } catch (e) { return null; } };

function dragPanel(grip, spec) {
  grip.addEventListener('pointerdown', ev => {
    ev.preventDefault();
    grip.setPointerCapture(ev.pointerId);
    document.body.classList.add('dragging');
    const startX = ev.clientX, startW = spec.width();
    let raf = 0;
    const move = e => {
      spec.apply(clampN(spec.next(startW, startX, e.clientX), spec.min, spec.max()));
      if (!raf) raf = requestAnimationFrame(() => { raf = 0; resize(); });
    };
    const up = () => {
      grip.removeEventListener('pointermove', move);
      grip.removeEventListener('pointerup', up);
      grip.removeEventListener('pointercancel', up);
      document.body.classList.remove('dragging');
      spec.save(spec.width());
      resize(); fit();
    };
    grip.addEventListener('pointermove', move);
    grip.addEventListener('pointerup', up);
    grip.addEventListener('pointercancel', up);
  });
}

const sideWidth = () => sideEl.getBoundingClientRect().width;
dragPanel(document.getElementById('sideGrip'), {
  width: sideWidth,
  min: 210,
  max: () => Math.max(240, Math.min(760, window.innerWidth - 300)),
  next: (w, x0, x) => w + (x - x0),
  apply: w => { sideEl.style.width = w + 'px'; },
  save: w => storeVal(SIDE_KEY, Math.round(w))
});

dragPanel(document.getElementById('docGrip'), {
  width: () => docEl.getBoundingClientRect().width,
  min: 300,
  max: () => Math.max(320, window.innerWidth - 300),
  next: (w, x0, x) => w + (x0 - x),
  apply: w => {
    docW = w;
    if (docEl.classList.contains('open')) docEl.style.width = w + 'px';
  },
  save: w => storeVal(DOC_KEY, Math.round(w))
});

function setSide(visible) {
  document.body.classList.toggle('side-hidden', !visible);
  storeVal(HIDE_KEY, visible ? '0' : '1');
  document.getElementById('sideToggle').textContent = '«';
  setTimeout(layout, 150);
}

document.getElementById('sideToggle').onclick = () => setSide(false);
document.getElementById('sideOpen').onclick = () => setSide(true);

(function restorePanels() {
  const sw = parseInt(loadVal(SIDE_KEY) || '', 10);
  if (sw) sideEl.style.width = clampN(sw, 210, 760) + 'px';
  if (loadVal(HIDE_KEY) === '1') document.body.classList.add('side-hidden');
  const dw = parseInt(loadVal(DOC_KEY) || '', 10);
  if (dw) docW = clampN(dw, 300, Math.max(320, window.innerWidth - 300));
})();

/* ---- floating mode: out of flow, dragged by its own header ---- */
const FLOAT_KEY = 'skillmap.docFloat', XY_KEY = 'skillmap.docXY';
const docHead = document.getElementById('dochead');
const floatBtn = document.getElementById('docfloat');
let docXY = null;

function placeDoc(x, y, persist) {
  const w = docEl.getBoundingClientRect().width || docW || 620;
  const keepX = Math.min(180, w * 0.5), keepY = 44;
  x = Math.round(Math.max(-w + keepX, Math.min(x, window.innerWidth - keepX)));
  y = Math.round(Math.max(6, Math.min(y, window.innerHeight - keepY)));
  docEl.style.left = x + 'px';
  docEl.style.top = y + 'px';
  docXY = {x, y};
  if (persist !== false) storeVal(XY_KEY, JSON.stringify(docXY));
}

function setFloat(on) {
  docEl.classList.toggle('float', on);
  floatBtn.textContent = on ? '▤' : '⧉';
  storeVal(FLOAT_KEY, on ? '1' : '0');
  if (on) {
    const d = docXY || {x: Math.max(16, window.innerWidth - (docW || 620) - 40), y: 68};
    docEl.style.width = Math.round(docW || clampN(window.innerWidth * 0.44, 340, 760)) + 'px';
    placeDoc(d.x, d.y, false);
  } else {
    docEl.style.left = '';
    docEl.style.top = '';
  }
  layout();
}

floatBtn.onclick = () => setFloat(!docEl.classList.contains('float'));

docHead.addEventListener('pointerdown', ev => {
  if (!docEl.classList.contains('float') || docEl.classList.contains('full')) return;
  if (ev.target.closest('button')) return;
  ev.preventDefault();
  docHead.setPointerCapture(ev.pointerId);
  const r = docEl.getBoundingClientRect();
  const ox = ev.clientX - r.left, oy = ev.clientY - r.top;
  document.body.classList.add('moving');
  const move = e => placeDoc(e.clientX - ox, e.clientY - oy, false);
  const up = () => {
    docHead.removeEventListener('pointermove', move);
    docHead.removeEventListener('pointerup', up);
    docHead.removeEventListener('pointercancel', up);
    document.body.classList.remove('moving');
    if (docXY) storeVal(XY_KEY, JSON.stringify(docXY));
  };
  docHead.addEventListener('pointermove', move);
  docHead.addEventListener('pointerup', up);
  docHead.addEventListener('pointercancel', up);
});

(function restoreFloat() {
  const xy = loadVal(XY_KEY);
  if (xy) { try { docXY = JSON.parse(xy); } catch (e) {} }
  if (loadVal(FLOAT_KEY) === '1') {
    docEl.classList.add('float');
    floatBtn.textContent = '▤';
    const d = docXY || {x: 40, y: 68};
    placeDoc(d.x, d.y, false);
  }
})();

async function openDoc(id) {
  docEl.classList.add('open');
  docEl.style.width = Math.round(docW || clampN(window.innerWidth * 0.44, 340, 760)) + 'px';
  if (docEl.classList.contains('float')) {
    placeDoc(docXY ? docXY.x : Math.max(16, window.innerWidth - (docW || 620) - 40),
             docXY ? docXY.y : 68, false);
  }
  docId = id;
  const n = byId.get(id);
  docTitle.textContent = n ? labelOf(n) : id;
  docPath.textContent = '';
  docBody.innerHTML = '<div class="hint">loading…</div>';
  setTimeout(layout, 180);
  try {
    const r = await fetch('/doc/' + encodeURIComponent(id));
    if (!r.ok) throw new Error((await r.text()).trim() || ('HTTP ' + r.status));
    const j = await r.json();
    if (docId !== id) return;
    docPath.textContent = j.path + ' · ' + j.lines + ' lines';
    docBody.innerHTML = j.html;
    docBody.scrollTop = 0;
  } catch (err) {
    if (docId !== id) return;
    docBody.innerHTML = '<div class="fm">读不到正文。这个页面需要本地服务：\n\n' +
      'python3 scripts/serve-skill-map.py\n\n' + esc(err && err.message ? err.message : err) + '</div>';
  }
}

function select(n) {
  selected = n;
  renderDetail();
  if (n) openDoc(n.id);
  if (inCards()) renderCards();
}

function closeDoc() {
  docEl.classList.remove('open', 'full');
  docEl.style.width = '';
  document.getElementById('docfs').textContent = '⤢';
  docId = null;
  setTimeout(layout, 180);
}

document.getElementById('docclose').onclick = closeDoc;
document.getElementById('docfs').onclick = () => {
  docEl.classList.toggle('full');
  document.getElementById('docfs').textContent = docEl.classList.contains('full') ? '⤡' : '⤢';
  layout();
};
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && (docEl.classList.contains('open') || docEl.classList.contains('full'))) closeDoc();
});
canvas.addEventListener('dblclick', ev => {
  const r = canvas.getBoundingClientRect();
  const n = pick(ev.clientX - r.left, ev.clientY - r.top);
  if (!n) return;
  select(n);
  if (!docEl.classList.contains('full')) document.getElementById('docfs').click();
});
document.getElementById('legend').innerHTML =
  Object.keys(COLOR).map(k => '<div class="lg"><span class="dot" style="background:' + COLOR[k] +
    '"></span>' + KIND[k] + '</div>').join('') +
  '<div class="lg" style="margin-top:5px"><svg width="22" height="8"><line x1="0" y1="4" x2="22" y2="4" stroke="#7f97c4" stroke-width="1.6"/></svg>playbook step or hand-off</div>' +
  '<div class="lg"><svg width="22" height="8"><line x1="0" y1="4" x2="22" y2="4" stroke="#b98cf0" stroke-width="1.6"/></svg>situation trigger (Non-negotiables)</div>' +
  '<div class="lg"><svg width="22" height="8"><line x1="0" y1="4" x2="22" y2="4" stroke="#4d5f80" stroke-width="1.4"/></svg>entry registry edge (toggle)</div>' +
  '<div class="lg"><svg width="14" height="14"><circle cx="7" cy="7" r="4.5" fill="#334" stroke="#94a3b8" stroke-dasharray="2 2"/></svg>manual only: nothing routes to it</div>';
document.getElementById('meta').innerHTML =
  '<b>' + DATA.meta.total + '</b> skills, all <b>' + DATA.meta.dmi + '</b> closed to discovery<br>' +
  '<b>' + DATA.meta.playbooks + '</b> playbooks · <b>' + DATA.meta.edges + '</b> edges · <b>' +
  DATA.meta.orphans.length + '</b> unreachable';

resize(); fit(); renderDetail();
applyView(loadVal(VIEW_KEY) || 'cards');
(function loop() { if (!inCards()) draw(); requestAnimationFrame(loop); })();
window.addEventListener('resize', () => { if (!inCards()) { resize(); fit(); } });
</script>
</body>
</html>
"""

# manual = 只有入口注册表提到它，没有任何 playbook 或技能真的指向它
entry_ids = {n['id'] for n in nodes if n['kind'] == 'entry'}
def is_registry(e):
    return e['k'] == 'registry'
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
map_out=OUT/'skill-map.html'
map_out.write_text(TEMPLATE.replace('__DATA__', payload), encoding='utf-8')
print('wrote', map_out, map_out.stat().st_size, 'bytes')
