#!/usr/bin/env node
// Behaviour evidence for a range. By default, run the tests added or changed inside the range
// twice: at the anchor and at the range end. Only test-side files are overlaid onto the anchor.
// Checking out production code too would run the new code at the anchor and distort red/green.
// When the anchor is not on the end point's history, or the range cannot be resolved to commits,
// print "cannot compute:" and exit non-zero. Never report that as "no test changes".
// Without --workdir the process removes the temporary worktree it created before exiting, error or not.
// The per-commit check lists commits that changed production code but no test-side file, marks them
// "no test changes", and runs no tests for them.
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, realpathSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { basename, dirname, join, resolve, sep } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { parseArgs } from 'node:util';

// Directory rules also match conftest.py / __init__.py / setup.py, which are not tests.
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

const USAGE = `usage: node fix-proof.mjs --range <start>..<end> --cmd '<test command with {files}>' [options]

  --range <A..B>        the range; required. A must be an ancestor of B
  --per-commit          check per commit: list commits that changed runnable tests, and commits that
                        changed production code without touching a test-side file
  --cmd <command>       test command; {files} is replaced with space-separated, quoted test files
  --tests <regex>       runnable tests; defaults cover the common languages (see the skill's opening)
  --bring <regex>       extra test-side files overlaid onto the anchor; defaults to test directories,
                        fixtures, and conftest.py
  --setup <cmd>         install dependencies inside the temporary worktree
  --lockfile <path>     rerun --setup only when this file's blob differs between start and end
  --workdir <dir>       keep the worktree on exit. Without it the worktree is built in a temp dir and
                        removed on exit, including an error exit
  --timeout <seconds>   timeout for one test run, default 300

Default runnable-test patterns:
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
  if (!opt.cmd.includes('{files}')) fatal('--cmd has no {files}.');

  let testRe;
  let bringRe;
  try {
    testRe = compile(opt.tests);
    bringRe = compile(opt.bring);
  } catch {
    fatal('--tests or --bring is not a valid regex.');
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
  if (!range) fatal('the range is written <start>..<end>, with two dots.');

  let repo;
  try {
    repo = git(['rev-parse', '--show-toplevel'], process.cwd()).trim();
  } catch {
    fatal('the current directory is not a git repository.');
  }
  const from = resolveRev(range.from, repo);
  const to = resolveRev(range.to, repo);
  if (!from) fatal(`cannot resolve the range start ${range.from}.`);
  if (!to) fatal(`cannot resolve the range end ${range.to}.`);
  if (spawnSync('git', ['merge-base', '--is-ancestor', from, to], { cwd: repo }).status !== 0) {
    fatal(`the anchor ${from} is not on ${to}'s history.`);
  }

  const timeoutMs = Number(opt.timeout) * 1000;
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) fatal('--timeout needs a positive number.');

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
    console.log(`## Behaviour evidence ${from}..${to}\n\nno test file changes`);
    return;
  }
  const lines = [`## Behaviour evidence ${from}..${to}`, ''];
  if (files.toRun.length === 0) {
    lines.push('verdict: existing assertions deleted or edited', 'test files: none', `existing assertions edited: ${edits.join(', ')}`, 'note: none');
    console.log(lines.join('\n'));
    return;
  }
  const added = new Set(files.rows.filter((row) => row.status === 'A' || row.status === 'C').map((row) => row.path));
  const greenAt = files.toRun.some((filePath) => added.has(filePath)) ? 'new test already green at anchor' : 'changed test already green at anchor';
  const outcome = runner.pair(from, to, files.toRun, files.overlay, { greenAt });
  lines.push(
    `verdict: ${outcome.verdict}`,
    `test files: ${labelRuns(files.rows, files.toRun)}`,
    `existing assertions edited: ${edits.length ? edits.join(', ') : 'none'}`,
    `note: ${outcome.note || 'none'}`,
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
    `## Per-commit check ${from}..${to}`,
    '',
    `commits that changed a test file: ${testCount}.`,
    `commits with no test changes: ${bareCount}.`,
    '',
  ];
  if (testCount === 0 && bareCount === 0) lines.push('No commit changed a test file.');
  for (const item of items) {
    if (!item.run && !(item.prod && !item.side)) continue;
    if (!item.run) {
      lines.push(formatCommit(item.sha, { verdict: 'no test changes', prod: true, tests: 'none', edits: 'none', note: 'none' }));
      continue;
    }
    const parent = resolveRev(`${item.sha}^`, repo);
    if (!parent) {
      lines.push(formatCommit(item.sha, { verdict: 'skipped (root commit)', prod: item.prod }));
      continue;
    }
    const { rows } = item;
    const toRun = unique(rows.filter((row) => row.status !== 'D' && runnable(row.path)).map((row) => row.path));
    const overlay = unique(rows.filter((row) => row.status !== 'D' && testSide(row.path)).map((row) => row.path));
    const edits = assertionEdits(git(['diff', '--find-renames', '--numstat', parent, item.sha], repo), runnable);
    const editText = edits.join(', ') || 'none';
    if (toRun.length === 0) {
      lines.push(formatCommit(item.sha, {
        verdict: edits.length ? 'existing assertions deleted or edited' : 'no runnable test',
        prod: item.prod,
        edits: editText,
      }));
      continue;
    }
    const added = new Set(rows.filter((row) => row.status === 'A' || row.status === 'C').map((row) => row.path));
    const greenAt = toRun.some((filePath) => added.has(filePath)) ? 'new test already green at parent' : 'changed test already green at parent';
    const outcome = runner.pair(parent, item.sha, toRun, overlay, { greenAt, redGreen: 'parent red, commit green', headRed: 'commit not green' });
    lines.push(formatCommit(item.sha, {
      verdict: outcome.verdict,
      prod: item.prod,
      tests: toRun.join(', '),
      edits: editText,
      note: outcome.note,
    }));
  }
  console.log(lines.join('\n'));
}

function formatCommit(sha, { verdict, prod, tests, edits, note }) {
  const parts = [`- ${sha} verdict: ${verdict}`, `production code: ${prod ? 'yes' : 'no'}`];
  if (tests !== undefined) parts.push(`test files: ${tests}`);
  if (edits !== undefined) parts.push(`existing assertions edited: ${edits}`);
  if (note !== undefined) parts.push(`note: ${note || 'none'}`);
  return parts.join('. ');
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

// .agents/ holds agent collaboration files (skills, ledgers, decision records), usually seeded from
// upstream. They are not this project's production code.
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
      return tail(`${r.stdout ?? ''}\n${r.stderr ?? ''}`) || `exit code ${r.status}`;
    }
    installedKey = key;
    return null;
  }
  function pair(left, right, toRun, overlay, names) {
    ensure();
    checkout(workdir, left);
    if (overlay.length) git(['checkout', right, '--', ...overlay], workdir);
    const leftSetup = setupFor(left);
    if (leftSetup) return { verdict: 'environment failure', note: `--setup failed at the start point: ${leftSetup}` };
    const before = runTests(workdir, opt.cmd, toRun, timeoutMs);
    checkout(workdir, right);
    const rightSetup = setupFor(right);
    if (rightSetup) return { verdict: 'environment failure', note: `--setup failed at the end point: ${rightSetup}` };
    const after = runTests(workdir, opt.cmd, toRun, timeoutMs);
    return judge(before, after, names);
  }
  return { pair };
}

function judge(before, after, names = {}) {
  const greenAt = names.greenAt ?? 'new test already green at anchor';
  const redGreen = names.redGreen ?? 'anchor red, HEAD green';
  const headRed = names.headRed ?? 'HEAD not green';
  if (before.timedOut || after.timedOut) return { verdict: 'timeout', note: 'a single test run exceeded --timeout' };
  if (!after.ok) return { verdict: headRed, note: firstFailure(after.out) };
  if (before.ok) return { verdict: greenAt, note: 'the test was already green at the start point' };
  if (LOAD_FAILURE.test(before.out)) return { verdict: 'load failure', note: firstFailure(before.out) };
  return { verdict: redGreen, note: firstFailure(before.out) };
}

function labelRuns(rows, toRun) {
  const added = new Set(rows.filter((row) => row.status === 'A' || row.status === 'C').map((row) => row.path));
  return toRun.map((filePath) => `${filePath} (${added.has(filePath) ? 'new' : 'changed'})`).join(', ');
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
    // A failed cleanup does not change the original exit result.
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
    throw new Error(detail || `git ${args[0]} exited ${r.status}`);
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
  const line = `cannot compute: ${message}`;
  console.log(line);
  console.error(line);
  process.exit(1);
}
