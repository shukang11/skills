#!/usr/bin/env node
// 区间行为证据。默认把区间内新增或改动过的可运行测试，在锚点和区间末端各跑一次。
// 盖到锚点上的只有测试侧文件。把生产代码一起检出的话，锚点上跑的就是新代码，红绿会失真。
// 锚点不在区间末端的历史上、或区间写不出提交时，输出「无法计算」并退出非零，不报成没有测试改动。
// 没传 --workdir 时，进程退出前移除自己建的临时 worktree，出错退出也移除。
// 按提交复核另列改了生产代码、没改测试侧文件的提交，判定「无测试改动」，不跑测试。
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, realpathSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { basename, dirname, join, resolve, sep } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { parseArgs } from 'node:util';

// 文件名是 conftest.py / __init__.py / setup.py 时，目录规则也会命中，但它们不是一条测试。
const NOT_RUN = /(?:^|\/)(?:conftest|__init__|setup)\.py$/;

export const DEFAULT_TEST_RE = [
  String.raw`(?:^|/)[^/]*\.(?:test|spec)\.[^.]+$`,
  String.raw`(?:^|/)[^/]*_test\.go$`,
  String.raw`(?:^|/)test_[^/]*\.py$`,
  String.raw`(?:^|/)[^/]*_test\.py$`,
  String.raw`(?:^|/)tests/[^/]+\.rs$`,
  String.raw`(?:^|/)[^/]*Test\.java$`,
  String.raw`(?:^|/)[^/]*(?:Test|Tests)\.kt$`,
  String.raw`(?:^|/)(?:test|tests|__tests__)/[^/]+\.(?:py|js|mjs|cjs|ts|mts|cts|jsx|tsx|go|rb|php|java|kt|rs)$`,
].join('|');

export const DEFAULT_BRING_RE = String.raw`(?:^|/)(?:tests?|__tests__|fixtures?|__snapshots__|testdata)/|(?:^|/)conftest\.py$`;

const DOC_EXT = /\.(?:md|mdx|txt)$/;

const LOAD_FAILURE =
  /ERROR collecting|ModuleNotFoundError|ImportError|Failed to load url|Failed to resolve import|does not provide an export named|Cannot find module|ERR_MODULE_NOT_FOUND|SyntaxError|Worker forks emitted error|cannot find package|could not import|no required module provides package|could not compile|error\[E\d+/;

const FAILURE_LINES = [
  /^(FAILED |E {3})/,
  /^\s*FAIL\s/,
  /AssertionError|ERR_MODULE_NOT_FOUND|Cannot find module|ModuleNotFoundError|SyntaxError|error\[E\d+/,
  /Error \[|Error:/,
  /Expected|expected/,
];

const WEAK_FAILURE = [/^\s*not ok\b/, /^\s*error:/i];

export function isRunnableTest(filePath, source = DEFAULT_TEST_RE) {
  return compile(source).test(filePath) && !NOT_RUN.test(filePath);
}

export function matchesBring(filePath, source = DEFAULT_BRING_RE) {
  return compile(source).test(filePath);
}

export function splitNumstatPath(raw) {
  const braced = raw.match(/^(.*)\{([^}]*) => ([^}]*)\}(.*)$/);
  if (braced) {
    return { oldPath: `${braced[1]}${braced[2]}${braced[4]}`, path: `${braced[1]}${braced[3]}${braced[4]}` };
  }
  const arrow = raw.lastIndexOf(' => ');
  if (arrow === -1) return { oldPath: raw, path: raw };
  return { oldPath: raw.slice(0, arrow), path: raw.slice(arrow + 4) };
}

function compile(source) {
  if (source instanceof RegExp) return new RegExp(source.source, source.flags.replaceAll('g', ''));
  return new RegExp(source);
}

const USAGE = `用法：node fix-proof.mjs --range <起点>..<末端> --cmd '<测试命令，含 {files}>' [选项]

  --range <A..B>        区间，必填。A 必须是 B 的祖先
  --per-commit          按提交复核。列出改了可运行测试的提交，以及改了生产代码但没改测试侧文件的提交
  --cmd <命令>          测试命令，{files} 会换成空格分隔、已加引号的测试文件
  --tests <正则>        可运行测试，默认覆盖常见语言（见技能「开场」）
  --bring <正则>        额外盖到锚点上的测试侧文件，默认是测试目录、夹具、conftest.py
  --setup <cmd>         在临时 worktree 里装依赖
  --lockfile <路径>     该文件相对起点和末端的 blob 变了才重跑 --setup；不给则只装一次
  --workdir <目录>      指定后退出时保留该 worktree。不传则建在临时目录，退出时移除（含出错退出）
  --timeout <秒>        单次测试超时，默认 300

默认可运行测试正则：
${DEFAULT_TEST_RE}`;

function invokedDirectly() {
  const entry = process.argv[1];
  if (!entry) return false;
  try {
    return realpathSync(entry) === realpathSync(fileURLToPath(import.meta.url));
  } catch {
    return pathToFileURL(entry).href === import.meta.url;
  }
}

if (invokedDirectly()) main();

function main() {
  const { values: opt } = parseArgs({
    options: {
      range: { type: 'string' },
      'per-commit': { type: 'boolean', default: false },
      cmd: { type: 'string' },
      tests: { type: 'string', default: DEFAULT_TEST_RE },
      bring: { type: 'string', default: DEFAULT_BRING_RE },
      setup: { type: 'string' },
      lockfile: { type: 'string' },
      workdir: { type: 'string' },
      timeout: { type: 'string', default: '300' },
      help: { type: 'boolean', short: 'h' },
    },
  });
  if (opt.help) {
    console.log(USAGE);
    process.exit(0);
  }
  if (!opt.range || !opt.cmd) {
    console.log(USAGE);
    process.exit(2);
  }
  if (!opt.cmd.includes('{files}')) fatal('--cmd 里没有 {files}。');

  let testRe;
  let bringRe;
  try {
    testRe = compile(opt.tests);
    bringRe = compile(opt.bring);
  } catch {
    fatal('--tests 或 --bring 不是合法正则。');
  }
  const runnable = (filePath) => {
    testRe.lastIndex = 0;
    return testRe.test(filePath) && !NOT_RUN.test(filePath);
  };
  const testSide = (filePath) => {
    bringRe.lastIndex = 0;
    return runnable(filePath) || bringRe.test(filePath);
  };

  const range = parseRange(opt.range);
  if (!range) fatal('区间要写成 <起点>..<末端>，中间是两个点。');

  let repo;
  try {
    repo = git(['rev-parse', '--show-toplevel'], process.cwd()).trim();
  } catch {
    fatal('当前目录不是 git 仓库。');
  }
  const from = resolveRev(range.from, repo);
  const to = resolveRev(range.to, repo);
  if (!from) fatal(`解析不了区间起点 ${range.from}。`);
  if (!to) fatal(`解析不了区间末端 ${range.to}。`);
  if (spawnSync('git', ['merge-base', '--is-ancestor', from, to], { cwd: repo }).status !== 0) {
    fatal(`锚点 ${from} 不在 ${to} 的历史上。`);
  }

  const timeoutMs = Number(opt.timeout) * 1000;
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) fatal('--timeout 需要正数。');

  const ownedWorkdir = opt.workdir === undefined;
  const workdir = resolve(opt.workdir ?? join(tmpdir(), 'review-code-proof', basename(repo)));
  let cleaned = false;
  const cleanupWorkdir = () => {
    if (!ownedWorkdir || cleaned) return;
    cleaned = true;
    removeOwnedWorktree(repo, workdir);
  };
  if (ownedWorkdir) process.on('exit', cleanupWorkdir);
  const runner = createRunner({ repo, workdir, opt, timeoutMs });

  try {
    if (opt['per-commit']) printPerCommit({ repo, from, to, runnable, testSide, runner });
    else printRange({ repo, from, to, runnable, testSide, runner });
  } finally {
    cleanupWorkdir();
  }
}

function printRange({ repo, from, to, runnable, testSide, runner }) {
  const files = collect(git(['diff', '--find-renames', '--name-status', from, to], repo), runnable, testSide);
  const edits = assertionEdits(git(['diff', '--find-renames', '--numstat', from, to], repo), runnable);
  if (files.toRun.length === 0 && edits.length === 0) {
    console.log(`## 行为证据 ${from}..${to}\n\n无测试文件改动`);
    return;
  }
  const lines = [`## 行为证据 ${from}..${to}`, ''];
  if (files.toRun.length === 0) {
    lines.push('判定：已有断言被删改', '测试文件：无', `已有断言被删改：${edits.join('，')}`, '备注：无');
    console.log(lines.join('\n'));
    return;
  }
  const added = new Set(files.rows.filter((row) => row.status === 'A' || row.status === 'C').map((row) => row.path));
  const greenAt = files.toRun.some((filePath) => added.has(filePath)) ? '新增测试在锚点就绿' : '改动的测试在锚点就绿';
  const outcome = runner.pair(from, to, files.toRun, files.overlay, { greenAt });
  lines.push(
    `判定：${outcome.verdict}`,
    `测试文件：${labelRuns(files.rows, files.toRun)}`,
    `已有断言被删改：${edits.length ? edits.join('，') : '无'}`,
    `备注：${outcome.note || '无'}`,
  );
  console.log(lines.join('\n'));
}

function printPerCommit({ repo, from, to, runnable, testSide, runner }) {
  const shas = git(['log', '--no-merges', '--reverse', '--format=%H', `${from}..${to}`], repo).split('\n').filter(Boolean);
  const items = shas.map((sha) => {
    const rows = parseNameStatus(git(['diff-tree', '--no-commit-id', '--find-renames', '--name-status', '--root', '-r', sha], repo));
    return { sha, rows, ...classifyCommit(rows, runnable, testSide) };
  });
  const testCount = items.filter((item) => item.run).length;
  const bareCount = items.filter((item) => !item.run && item.prod && !item.side).length;
  const lines = [
    `## 按提交复核 ${from}..${to}`,
    '',
    `改动了测试文件的提交：${testCount} 个。`,
    `无测试改动的提交：${bareCount} 个。`,
    '',
  ];
  if (testCount === 0 && bareCount === 0) lines.push('没有改动测试文件的提交。');
  for (const item of items) {
    if (!item.run && !(item.prod && !item.side)) continue;
    if (!item.run) {
      lines.push(formatCommit(item.sha, { verdict: '无测试改动', prod: true, tests: '无', edits: '无', note: '无' }));
      continue;
    }
    const parent = resolveRev(`${item.sha}^`, repo);
    if (!parent) {
      lines.push(formatCommit(item.sha, { verdict: '跳过（根提交）', prod: item.prod }));
      continue;
    }
    const { rows } = item;
    const toRun = unique(rows.filter((row) => row.status !== 'D' && runnable(row.path)).map((row) => row.path));
    const overlay = unique(rows.filter((row) => row.status !== 'D' && testSide(row.path)).map((row) => row.path));
    const edits = assertionEdits(git(['diff', '--find-renames', '--numstat', parent, item.sha], repo), runnable);
    const editText = edits.join('，') || '无';
    if (toRun.length === 0) {
      lines.push(formatCommit(item.sha, {
        verdict: edits.length ? '已有断言被删改' : '无测试可运行',
        prod: item.prod,
        edits: editText,
      }));
      continue;
    }
    const added = new Set(rows.filter((row) => row.status === 'A' || row.status === 'C').map((row) => row.path));
    const greenAt = toRun.some((filePath) => added.has(filePath)) ? '新增测试在父提交就绿' : '改动的测试在父提交就绿';
    const outcome = runner.pair(parent, item.sha, toRun, overlay, { greenAt, redGreen: '父提交红 本提交绿', headRed: '本提交不绿' });
    lines.push(formatCommit(item.sha, {
      verdict: outcome.verdict,
      prod: item.prod,
      tests: toRun.join('，'),
      edits: editText,
      note: outcome.note,
    }));
  }
  console.log(lines.join('\n'));
}

function formatCommit(sha, { verdict, prod, tests, edits, note }) {
  const parts = [`- ${sha} 判定：${verdict}`, `生产代码：${prod ? '有' : '无'}`];
  if (tests !== undefined) parts.push(`测试文件：${tests}`);
  if (edits !== undefined) parts.push(`已有断言被删改：${edits}`);
  if (note !== undefined) parts.push(`备注：${note || '无'}`);
  return parts.join('。');
}

function classifyCommit(rows, runnable, testSide) {
  let prod = false;
  let side = false;
  let run = false;
  for (const row of rows) {
    const paths = row.oldPath === row.path ? [row.path] : [row.oldPath, row.path];
    for (const filePath of paths) {
      if (!filePath) continue;
      if (runnable(filePath)) run = true;
      if (testSide(filePath)) side = true;
      if (isProductionPath(filePath, testSide)) prod = true;
    }
  }
  return { prod, side, run };
}

// .agents/ 放的是 Agent 协作文件（技能、账本、决策记录），多由上游种子带来，不是本项目的产品代码。
function isProductionPath(filePath, testSide) {
  return !filePath.startsWith('.agents/') && !DOC_EXT.test(filePath) && !testSide(filePath);
}

function createRunner({ repo, workdir, opt, timeoutMs }) {
  let installedKey = null;
  let ready = false;
  function ensure() {
    if (ready) return;
    mkdirSync(dirname(workdir), { recursive: true });
    if (!existsSync(join(workdir, '.git'))) git(['worktree', 'add', '--detach', '--force', workdir, 'HEAD'], repo);
    ready = true;
  }
  function setupFor(rev) {
    if (!opt.setup) return null;
    const key = opt.lockfile ? (tryGit(['rev-parse', `${rev}:${opt.lockfile}`], repo) ?? 'absent') : 'once';
    if (key === installedKey) return null;
    const r = spawnSync('sh', ['-c', opt.setup], { cwd: workdir, encoding: 'utf8', maxBuffer: 64 << 20 });
    if (r.status !== 0) {
      installedKey = null;
      return tail(`${r.stdout ?? ''}\n${r.stderr ?? ''}`) || `退出码 ${r.status}`;
    }
    installedKey = key;
    return null;
  }
  function pair(left, right, toRun, overlay, names) {
    ensure();
    checkout(workdir, left);
    if (overlay.length) git(['checkout', right, '--', ...overlay], workdir);
    const leftSetup = setupFor(left);
    if (leftSetup) return { verdict: '环境失败', note: `起点上 --setup 失败：${leftSetup}` };
    const before = runTests(workdir, opt.cmd, toRun, timeoutMs);
    checkout(workdir, right);
    const rightSetup = setupFor(right);
    if (rightSetup) return { verdict: '环境失败', note: `末端上 --setup 失败：${rightSetup}` };
    const after = runTests(workdir, opt.cmd, toRun, timeoutMs);
    return judge(before, after, names);
  }
  return { pair };
}

function judge(before, after, names = {}) {
  const greenAt = names.greenAt ?? '新增测试在锚点就绿';
  const redGreen = names.redGreen ?? '锚点红 HEAD 绿';
  const headRed = names.headRed ?? 'HEAD 不绿';
  if (before.timedOut || after.timedOut) return { verdict: '超时', note: '单次测试超过 --timeout' };
  if (!after.ok) return { verdict: headRed, note: firstFailure(after.out) };
  if (before.ok) return { verdict: greenAt, note: '测试在起点上也是绿的' };
  if (LOAD_FAILURE.test(before.out)) return { verdict: '加载失败', note: firstFailure(before.out) };
  return { verdict: redGreen, note: firstFailure(before.out) };
}

function labelRuns(rows, toRun) {
  const added = new Set(rows.filter((row) => row.status === 'A' || row.status === 'C').map((row) => row.path));
  return toRun.map((filePath) => `${filePath}（${added.has(filePath) ? '新增' : '改动'}）`).join('，');
}

function collect(nameStatus, runnable, testSide) {
  const rows = parseNameStatus(nameStatus);
  const toRun = unique(rows.filter((row) => row.status !== 'D' && runnable(row.path)).map((row) => row.path));
  const overlay = unique(rows.filter((row) => row.status !== 'D' && testSide(row.path)).map((row) => row.path));
  return { rows, toRun, overlay };
}

function assertionEdits(numstat, runnable) {
  const edits = [];
  for (const line of numstat.split('\n').filter(Boolean)) {
    const [, del, ...rest] = line.split('\t');
    if (!del || del === '0' || del === '-') continue;
    const { oldPath, path } = splitNumstatPath(rest.join('\t'));
    if (runnable(path) || runnable(oldPath)) edits.push(`${path}(-${del})`);
  }
  return edits;
}

function parseNameStatus(text) {
  const rows = [];
  for (const line of text.split('\n')) {
    if (!line.trim()) continue;
    const parts = line.split('\t');
    const kind = parts[0][0];
    if (kind === 'R' || kind === 'C') rows.push({ status: kind, oldPath: parts[1], path: parts[2] });
    else rows.push({ status: kind, oldPath: parts[1], path: parts[1] });
  }
  return rows;
}

function checkout(workdir, rev) {
  git(['checkout', '-q', '-f', '--detach', rev], workdir);
  git(['clean', '-fdq'], workdir);
}

function runTests(workdir, cmd, files, timeoutMs) {
  const command = cmd.replaceAll('{files}', files.map(quote).join(' '));
  const r = spawnSync('sh', ['-c', command], { cwd: workdir, encoding: 'utf8', timeout: timeoutMs, maxBuffer: 64 << 20 });
  return { ok: r.status === 0, timedOut: r.error?.code === 'ETIMEDOUT', out: `${r.stdout ?? ''}\n${r.stderr ?? ''}` };
}

function firstFailure(output) {
  const lines = output.split('\n');
  for (const re of [...FAILURE_LINES, ...WEAK_FAILURE]) {
    const line = lines.find((item) => re.test(item) && !isBookkeeping(item));
    if (line) return clip(line);
  }
  const load = lines.find((item) => LOAD_FAILURE.test(item) && !isBookkeeping(item));
  if (load) return clip(load);
  return tail(output);
}

function tail(output) {
  const line = output.split('\n').map((item) => item.trim()).filter((item) => !isBookkeeping(item)).at(-1) ?? '';
  return clip(line);
}

function isBookkeeping(line) {
  const text = line.trim();
  if (!text) return true;
  if (/^Node\.js v/.test(text)) return true;
  if (/^#\s*(?:tests|suites|pass|fail|cancelled|skipped|todo|duration_ms)\b/.test(text)) return true;
  if (/^duration_ms\b/.test(text)) return true;
  return false;
}

function removeOwnedWorktree(repo, workdir) {
  try {
    const repoReal = realpathSync(repo);
    let workReal = null;
    try {
      workReal = realpathSync(workdir);
    } catch {
      workReal = null;
    }
    if (workReal && (workReal === repoReal || workReal.startsWith(`${repoReal}${sep}`) || repoReal.startsWith(`${workReal}${sep}`))) {
      return;
    }
    spawnSync('git', ['worktree', 'remove', '--force', workdir], { cwd: repo });
    if (existsSync(workdir)) rmSync(workdir, { recursive: true, force: true });
    spawnSync('git', ['worktree', 'prune', '--expire', 'now'], { cwd: repo });
  } catch {
    // 清理失败不改原来的退出结果。
  }
}

function clip(line) {
  return line.trim().replaceAll('|', '\\|').slice(0, 160);
}

function quote(value) {
  return `'${String(value).replaceAll("'", `'\\''`)}'`;
}

function unique(list) {
  return [...new Set(list)];
}

function parseRange(spec) {
  if (spec.includes('...')) return null;
  const parts = spec.split('..');
  if (parts.length !== 2 || !parts[0] || !parts[1]) return null;
  return { from: parts[0], to: parts[1] };
}

function resolveRev(rev, repo) {
  const r = spawnSync('git', ['rev-parse', '--verify', '--quiet', `${rev}^{commit}`], { cwd: repo, encoding: 'utf8' });
  if (r.status !== 0) return null;
  return r.stdout.trim();
}

function git(args, cwd) {
  const r = spawnSync('git', args, { cwd, encoding: 'utf8', maxBuffer: 64 << 20 });
  if (r.error) throw r.error;
  if (r.status !== 0) {
    const detail = `${r.stderr ?? ''}${r.stdout ?? ''}`.trim();
    throw new Error(detail || `git ${args[0]} 退出 ${r.status}`);
  }
  return r.stdout ?? '';
}

function tryGit(args, cwd) {
  try {
    return git(args, cwd).trim();
  } catch {
    return null;
  }
}

function fatal(message) {
  const line = `无法计算：${message}`;
  console.log(line);
  console.error(line);
  process.exit(1);
}
