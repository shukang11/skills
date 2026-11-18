#!/usr/bin/env python3
"""Serve skill-map.html on localhost and rebuild it whenever the skills tree changes.

python3 scripts/serve-skill-map.py            # http://127.0.0.1:8777, opens a browser
python3 scripts/serve-skill-map.py --port 9000 --no-open

The default port is a preference, not a requirement: when it is taken, the server
walks to the next free one and prints the URL it landed on.

The graph is built by scripts/build-skill-map.py, so this server never re-implements
the parsing rules. It only decides *when* to run that script:

- the first request after a change rebuilds, so a plain refresh is always current
- a poller watches skills/ and the build script, rebuilds on change, and pushes
  `reload` over SSE so every open tab refreshes itself
- nothing in the repository is written: the build lands in a temp directory, the
  page and its data are held in memory. `skill-map.html` is no longer a repo file:
  it is gitignored, and only an explicit `--out` makes the build write one.
- the one-line notes on the skill cards live in NOTES below and are injected into
  the page per request, so the SKILL.md files stay English and a note change is a
  restart, not an edit to 70 files.

Endpoints:

  GET /           the map, with a live-reload badge injected at serve time
  GET /events     SSE stream, one `reload` per rebuild
  GET /graph.json the object the page draws (nodes, edges, meta)
  GET /doc/<id>   one node's file, rendered: {id, path, lines, mtime, html}
  GET /status     last build's counters, hubs and any build error
"""
import argparse
import ast
import atexit
import html
import http.server
import json
import pathlib
import queue
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ROOT / 'skills'
BUILD = ROOT / 'scripts' / 'build-skill-map.py'
WORK = pathlib.Path(tempfile.mkdtemp(prefix='skill-map-'))
GRAPH = WORK / 'skillgraph.json'
atexit.register(lambda: shutil.rmtree(WORK, ignore_errors=True))
DEFAULT_PORT = 8777

# One line per node, keyed by node id, injected into the page at request time.
# Held here rather than in the repository: the SKILL.md files stay English, and
# changing a note is a server restart, not a rebuild of every skill card.
# Keys: a skill name, or 'pb:<playbook>' for a playbook. Unknown ids fall back to
# the English description the build script reads from the frontmatter.
NOTES = {
    # ---- entry ----
    'pstack-mode': '唯一入口：按任务选一条 playbook，再逐步打开技能',
    # ---- playbooks ----
    'pb:feature': '新增或改动行为，最终落到代码',
    'pb:bug-fix': '先让信号只对这个 bug 变红，再动代码',
    'pb:design': '只出契约和规格，不写实现',
    'pb:prototype': '做一份能点的高保真模拟，用来定产品逻辑',
    'pb:refactor': '外部行为不变，只动结构',
    'pb:review': '审一段 diff，不改代码',
    'pb:simplify': '清理已经落地的残渣；用户不明确要求就别进',
    'pb:handoff': '中断与续接；暂停和恢复不是同一步',
    'pb:authoring': '写或改给 agent 读的文档',
    'pb:repo-audit': '这个仓库 agent 能不能直接开工？只读，停在建议表',
    'pb:investigate': '只回答一个问题，不改代码',
    'pb:wayfinder': '一个会话装不下、路线还不清；不写实现',
    # ---- engineering leaves ----
    'agent-ready-repository': '审仓库够不够格当 agent 的工作环境，逐条给可裁决的建议',
    'architect': '先画类型、签名和模块结构，再让实现把它填满',
    'arena': '同一件事并行跑 N 个完整候选，选一个做底再接上别人的长处',
    'blast-radius': '上线前找这次改动可能在哪炸，并跑真码证明它安全',
    'code-review': '分「规范」「规格」两条轴审 diff，不互相压价',
    'code-simplify': '只清残渣和具名的小范围，不评价新写的协议',
    'codebase-design': '深模块的共用词汇：接口、接缝、可测性',
    'compare-shapes': '同一任务至少摆两个形状，先写判据再融合',
    'correct': '把这个仓库里 agent 反复犯的错做成不可能再犯',
    'create-formal-verification-skill': '生成项目内的形式化验证技能：模型检验、不变量',
    'create-verification-skill': '生成项目内的验证技能：像用户一样驱动整个应用',
    'diagnosing-bugs': '难 bug 和性能回退的诊断循环',
    'domain-modeling': '建并打磨领域模型：术语表、ADR',
    'figure-it-out': '没有更窄的 playbook 合适时，装一套可审计的流程',
    'how': '讲 X 怎么跑起来的：运行时流程、分层、该放哪',
    'maintain-formal-verification-skill': '代码变了，把形式化模型和性质同步回现状',
    'maintain-verification-skill': '定期校对验证技能和功能图，最多开一个修正 PR',
    'prototype': '做一份可丢弃的高保真模拟，定产品逻辑或交互',
    'reflect': '用三个视角看本次会话，把教训路由成技能修改',
    'show-me-your-work': '长跑或无人值守时，留一份可审的决策流水',
    'statechart': '用 TLA+ 查状态机，画成 Mermaid，给出破规的最短路径',
    'swarm': '并行撒出 N 个工人，收成一份报告',
    'teach': '先跑 how 和 why，再合成一份讲透的讲解',
    'to-spec': '把已谈定的讨论收敛成一份规格，落到 .agents/notes',
    'typescript-best-practices': '读写 .ts / .tsx 时的 TypeScript 规矩',
    'wayfinder': '目的地清楚、路线不清楚：画决策票地图，一会话解一票',
    'why': '追这段代码为什么长这样：设计理由、权衡、回退、事后分析',
    # ---- productivity leaves ----
    'bro': '把刚才那条消息用大白话重说一遍',
    'grilling': '写代码前先盘问：建决策树，一轮推一层前沿',
    'handoff': '把断点压成一份状态胶囊，下个会话无缝接上',
    'in-your-own-words': '开工前先复述我理解的目标和问题，只复述不盘问',
    'ketchup': '用白话说清你上条消息之后变了什么，并列出手上等你定的事',
    'recall': '从本机真有的会话库里把前几场捡回来，交一份现状胶囊',
    'sharpen': '把 prompt 改深不改大：原始材料、专家方法、外部验证',
    'unslop': '去掉 AI 腔，按 ASD-STE100 收紧句子',
    'writing-for-agents': '写任何给 agent 读的文档：技能、AGENTS.md、指针',
    # ---- judgment ----
    'principle-attack-the-premise': '同一前提的两个修法都挂了，就先审前提',
    'principle-boundary-discipline': '校验和错误处理压在边界，内部只信类型',
    'principle-build-the-lever': '造工具去做或去证明，不要手工搬',
    'principle-encode-lessons-in-structure': '同一条指令写第二遍，就做成 lint 或脚本',
    'principle-exhaust-the-design-space': '没有先例的新交互，先做两三个原型对拼',
    'principle-experience-first': '产品取舍上，用户爽优先于实现省事',
    'principle-explain-the-number': '用数字之前先弄清是什么在限制它',
    'principle-fix-root-causes': '追到根因再修，先复现，一路问到底',
    'principle-guard-the-context-window': '上下文要满时，把量大的活路由给子代理',
    'principle-laziness-protocol': '偏向删除：最小改动，别急着加层',
    'principle-make-operations-idempotent': '命令和批处理要能重跑到同一个状态',
    'principle-migrate-callers-then-delete-legacy-apis': '迁调用方和删旧接口，同一波做完',
    'principle-minimize-reader-load': '数读者要跨几层、脑里藏多少状态，然后砍掉',
    'principle-model-the-domain': '有状态的逻辑，先定数据形状和它的组织原则',
    'principle-never-block-on-the-human': '可逆的事别问，先做再让人纠',
    'principle-outcome-oriented-execution': '有阶段的迁移直奔目标架构，别保中间态',
    'principle-prove-it-works': '宣布完成前，对着真东西验，不认代理信号',
    'principle-redesign-from-first-principles': '新需求并进旧设计时，从第一性重新推',
    'principle-separate-before-serializing-shared-state': '并发写同一份状态，先消除共享再谈串行',
    'principle-sequence-verifiable-units': '把活切成每步都能验的小单元，按顺序交付',
    'principle-test-behavior-not-implementation': '像用户那样调用，断言他看到的结果',
    'principle-type-system-discipline': '让非法状态不可表示，边界上解析外部数据',
}

DSN = re.compile(r'^\[?\s*(GET|POST)\s+(\S+)')


# ---------- one node's file, as HTML ----------

_FM = re.compile(r'\A---\n(.*?)\n---\n', re.S)
_BLOCK_START = re.compile(r'^(#{1,6}\s|\s*```|\s*[-*+]\s|\s*\d+[.)]\s|>)')


def _inline(s):
    s = html.escape(s)
    s = re.sub(r'`([^`]+)`', lambda m: '<code>%s</code>' % m.group(1), s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<![\w*])\*([^*\n]+)\*(?![\w*])', r'<i>\1</i>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', s)
    return s


def render_markdown(text):
    """Headings, paragraphs, lists, tables, fenced code, quotes, rules.

    Enough for the SKILL.md / playbook / reference files this repo writes; not a
    general Markdown implementation.
    """
    meta = ''
    m = _FM.match(text)
    if m:
        meta = '<div class="fm">%s</div>' % html.escape(m.group(1).strip())
        text = text[m.end():]
    out = [meta] if meta else []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        if ln.lstrip().startswith('```'):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].lstrip().startswith('```'):
                buf.append(lines[i])
                i += 1
            i += 1
            out.append('<pre><code>%s</code></pre>' % html.escape('\n'.join(buf)))
            continue
        m = re.match(r'(#{1,6})\s+(.*)', ln)
        if m:
            lvl = len(m.group(1))
            out.append('<h%d>%s</h%d>' % (lvl, _inline(m.group(2)), lvl))
            i += 1
            continue
        if re.match(r'^\s*([-*_])\1\1[-*_\s]*$', ln):
            out.append('<hr>')
            i += 1
            continue
        if ln.lstrip().startswith('|') and i + 1 < len(lines) and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i + 1]):
            head = [c.strip() for c in ln.strip().strip('|').split('|')]
            i += 2
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            out.append('<table><thead><tr>' +
                       ''.join('<th>%s</th>' % _inline(h) for h in head) + '</tr></thead><tbody>' +
                       ''.join('<tr>' + ''.join('<td>%s</td>' % _inline(c) for c in r) + '</tr>'
                               for r in rows) + '</tbody></table>')
            continue
        if ln.lstrip().startswith('>'):
            buf = []
            while i < len(lines) and lines[i].lstrip().startswith('>'):
                buf.append(lines[i].lstrip()[1:].strip())
                i += 1
            out.append('<blockquote>%s</blockquote>' % '<br>'.join(_inline(b) for b in buf))
            continue
        m = re.match(r'^(\s*)([-*+]|\d+[.)])\s+(.*)', ln)
        if m:
            tag = 'ol' if re.match(r'\d', m.group(2)) else 'ul'
            items = []
            while i < len(lines):
                mm = re.match(r'^(\s*)([-*+]|\d+[.)])\s+(.*)', lines[i])
                if not mm:
                    break
                depth = len(mm.group(1)) // 2
                items.append('<li%s>%s</li>' % (' style="margin-left:%dpx"' % (depth * 14) if depth else '',
                                                _inline(mm.group(3))))
                i += 1
            out.append('<%s>%s</%s>' % (tag, ''.join(items), tag))
            continue
        buf = []
        while i < len(lines) and lines[i].strip() and not _BLOCK_START.match(lines[i]) \
                and not lines[i].lstrip().startswith(('|', '```')):
            buf.append(lines[i].strip())
            i += 1
        out.append('<p>%s</p>' % _inline(' '.join(buf)))
    return '\n'.join(x for x in out if x)


def resolve_doc(node_id):
    """Map a node id to the file it describes, or None when it escapes the repo."""
    if not node_id:
        return None
    if node_id.startswith('pb:'):
        p = SKILLS / 'mode' / 'pstack-mode' / 'playbooks' / (node_id[3:] + '.md')
    elif node_id.startswith('skills/'):
        p = ROOT / node_id
    else:
        found = sorted(SKILLS.glob('*/%s/SKILL.md' % node_id))
        p = found[0] if found else None
    if p is None:
        return None
    try:
        p = p.resolve()
    except OSError:
        return None
    if p != ROOT.resolve() and ROOT.resolve() not in p.parents:
        return None
    return p if p.is_file() else None

BADGE = """
<div id="__live" style="position:fixed;right:12px;bottom:10px;z-index:9999;
  font:11px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;color:#8fa1c0;
  background:#111a2ce6;border:1px solid #22304d;border-radius:6px;padding:4px 8px;
  pointer-events:none">live · 连接中…</div>
<script>
(() => {
  const badge = document.getElementById('__live');
  const es = new EventSource('/events');
  es.onopen = () => { badge.textContent = 'live · 已连接，改文件会自动刷新'; };
  es.onmessage = (e) => {
    if (e.data.startsWith('reload')) {
      badge.textContent = 'live · 已重建，刷新中…';
      location.reload();
    }
  };
  es.onerror = () => { badge.textContent = 'live · 断线，重试中…'; };
})();
</script>
"""


def watched_files():
    yield BUILD
    if SKILLS.is_dir():
        for p in SKILLS.rglob('*'):
            if p.is_file() and p.suffix in ('.md', '.mjs', '.ts', '.js'):
                yield p


def signature():
    sig = []
    for p in watched_files():
        try:
            st = p.stat()
        except OSError:
            continue
        sig.append((str(p), st.st_mtime_ns, st.st_size))
    return tuple(sig)


class Map:
    """Runs the build script and remembers the result."""

    def __init__(self):
        self.lock = threading.Lock()
        self.sig = None
        self.builds = 0
        self.built_at = None
        self.error = None
        self.stats = {}
        self.html = None
        self.graph = None
        self.listeners = set()
        self.listeners_lock = threading.Lock()

    def build(self, why):
        with self.lock:
            self.sig = signature()
            proc = subprocess.run(
                [sys.executable, str(BUILD), '--out', str(WORK), '--json', str(GRAPH)],
                cwd=str(ROOT), capture_output=True, text=True)
            if proc.returncode != 0:
                self.error = (proc.stderr or proc.stdout).strip()[-4000:]
                print(f'build failed ({why}):\n{self.error}', file=sys.stderr)
                return False
            try:
                self.html = (WORK / 'skill-map.html').read_text(encoding='utf-8')
                self.graph = GRAPH.read_text(encoding='utf-8')
            except OSError as exc:
                self.error = f'build produced no map: {exc}'
                print(self.error, file=sys.stderr)
                return False
            self.error = None
            self.builds += 1
            self.built_at = time.strftime('%H:%M:%S')
            self.stats = self.parse(proc.stdout)
            print(f'rebuilt #{self.builds} ({why}) '
                  f"{self.stats.get('nodes', '?')} nodes, {self.stats.get('edges', '?')} edges",
                  flush=True)
            return True

    @staticmethod
    def parse(out):
        stats = {}
        m = re.search(r'nodes (\d+) edges (\d+)', out)
        if m:
            stats['nodes'] = int(m.group(1))
            stats['edges'] = int(m.group(2))
        for key in ('orphans', 'hubs'):
            m = re.search(rf'^{key} (.+)$', out, re.M)
            if m:
                try:
                    stats[key] = ast.literal_eval(m.group(1))
                except (ValueError, SyntaxError):
                    stats[key] = m.group(1)
        m = re.search(r'^kinds (.+)$', out, re.M)
        if m:
            try:
                stats['kinds'] = dict(ast.literal_eval(m.group(1)))
            except (ValueError, SyntaxError):
                stats['kinds'] = m.group(1)
        return stats

    def ensure(self, why='request'):
        if self.sig == signature():
            return True
        return self.build(why)

    def watch(self, interval):
        while True:
            time.sleep(interval)
            try:
                if signature() == self.sig:
                    continue
                if self.build('change'):
                    with self.listeners_lock:
                        targets = list(self.listeners)
                    for q in targets:
                        q.put('reload')
            except Exception as exc:  # keep the watcher alive whatever happens
                print(f'watcher: {exc}', file=sys.stderr)

    def subscribe(self):
        q = queue.Queue()
        with self.listeners_lock:
            self.listeners.add(q)
        return q

    def unsubscribe(self, q):
        with self.listeners_lock:
            self.listeners.discard(q)


MAP = Map()


class Handler(http.server.BaseHTTPRequestHandler):
    server_version = 'skill-map/1.0'

    def log_message(self, fmt, *args):
        if '/events' in self.path:
            return
        sys.stderr.write('  %s %s\n' % (self.command, self.path))

    def send_body(self, code, body, ctype='text/html; charset=utf-8', extra=None):
        data = body.encode('utf-8') if isinstance(body, str) else body
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split('?')[0]
        if path in ('/', '/index.html'):
            return self.serve_map()
        if path == '/events':
            return self.serve_events()
        if path == '/graph.json':
            return self.serve_graph()
        if path == '/status':
            return self.serve_status()
        if path.startswith('/doc/'):
            return self.serve_doc(path[len('/doc/'):])
        if path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return
        self.send_body(404, 'not found', 'text/plain; charset=utf-8')

    def serve_map(self):
        MAP.ensure('request')
        if MAP.html is None:
            return self.send_body(500, '<pre>build failed\n\n%s</pre>' % (MAP.error or ''),
                                  'text/html; charset=utf-8')
        html = MAP.html
        if 'window.SKILL_NOTES={' not in html:  # the page itself only reads it
            html = html.replace('<body>', '<body>\n<script>window.SKILL_NOTES=' +
                                json.dumps(NOTES, ensure_ascii=False) + '</script>', 1)
        if '<div id="__live"' not in html:
            html = html.replace('</body>', BADGE + '</body>')
        self.send_body(200, html)

    def serve_graph(self):
        MAP.ensure('request')
        if MAP.graph is None:
            return self.send_body(503, '{"error":"no graph yet"}', 'application/json')
        self.send_body(200, MAP.graph, 'application/json; charset=utf-8')

    def serve_status(self):
        body = json.dumps({
            'builds': MAP.builds,
            'builtAt': MAP.built_at,
            'watched': len(signature()),
            'repoFilesWritten': 0,
            'stats': MAP.stats,
            'error': MAP.error,
        }, ensure_ascii=False, indent=2)
        self.send_body(200, body, 'application/json; charset=utf-8')

    def serve_doc(self, raw_id):
        from urllib.parse import unquote
        node_id = unquote(raw_id)
        MAP.ensure('request')
        p = resolve_doc(node_id)
        if p is None:
            return self.send_body(404, 'no file for %s' % node_id, 'text/plain; charset=utf-8')
        try:
            text = p.read_text(encoding='utf-8')
        except OSError as exc:
            return self.send_body(500, 'cannot read %s: %s' % (p, exc), 'text/plain; charset=utf-8')
        body = json.dumps({
            'id': node_id,
            'path': p.relative_to(ROOT).as_posix(),
            'lines': len(text.splitlines()),
            'mtime': time.strftime('%Y-%m-%d %H:%M', time.localtime(p.stat().st_mtime)),
            'html': render_markdown(text),
        }, ensure_ascii=False)
        self.send_body(200, body, 'application/json; charset=utf-8')

    def serve_events(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Connection', 'keep-alive')
        self.end_headers()
        q = MAP.subscribe()
        try:
            self.wfile.write(b': connected\n\n')
            self.wfile.flush()
            while True:
                try:
                    msg = q.get(timeout=10)
                    self.wfile.write(f'data: {msg}\n\n'.encode())
                except queue.Empty:
                    self.wfile.write(b': ping\n\n')
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            MAP.unsubscribe(q)


class Server(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    ap = argparse.ArgumentParser(description='Live skill dependency map.')
    ap.add_argument('--port', type=int, default=None,
                    help=f'default {DEFAULT_PORT}; walks forward when taken')
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--interval', type=float, default=0.8, help='poll seconds (default 0.8)')
    ap.add_argument('--no-open', action='store_true', help='do not open a browser')
    args = ap.parse_args()

    print('building the map ...', flush=True)
    if not MAP.build('startup') and MAP.html is None:
        print('build failed and no previous map to serve', file=sys.stderr)
        return 1

    threading.Thread(target=MAP.watch, args=(args.interval,), daemon=True).start()
    ports = [args.port] if args.port else [DEFAULT_PORT + i for i in range(21)]
    httpd = None
    for port in ports:
        try:
            httpd = Server((args.host, port), Handler)
            break
        except OSError as exc:
            if args.port:
                print(f'cannot listen on {args.host}:{port}: {exc}\n'
                      f'try another port: --port {port + 1}', file=sys.stderr)
                return 1
            print(f'port {port} busy, trying {port + 1}', file=sys.stderr)
    if httpd is None:
        print(f'no free port in {ports[0]}-{ports[-1]}; pass --port explicitly', file=sys.stderr)
        return 1
    port = httpd.server_address[1]

    def stop(*_):
        raise SystemExit(0)

    for sig in (signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, stop)

    url = f'http://{args.host}:{port}/'
    print(f'watching {len(signature())} files under skills/ (poll {args.interval}s)', flush=True)
    print(f'serving {url}  (Ctrl-C to stop)', flush=True)
    if not args.no_open:
        threading.Timer(0.3, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nstopped')
    finally:
        httpd.server_close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
