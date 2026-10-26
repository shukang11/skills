#!/usr/bin/env node
// 用户级：符号链接到本仓库。项目级：把技能目录复制进目标仓库。

import {
  cpSync,
  existsSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  readlinkSync,
  realpathSync,
  renameSync,
  rmSync,
  symlinkSync,
} from 'node:fs';
import { homedir } from 'node:os';
import { basename, dirname, isAbsolute, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const skillsRoot = join(repoRoot, 'skills');
const USER_NAMESPACE = 'shukang';
const SKIP_DIRS = new Set(['node_modules', '.git']);

function usage() {
  return `用法:
  node scripts/install.mjs --user [技能名...]
  node scripts/install.mjs --project <仓库路径> [技能名...]
  node scripts/install.mjs --list [--user | --project <仓库路径>]
  node scripts/install.mjs --uninstall (--user | --project <仓库路径>) [技能名...]

用户级写入符号链接。不带技能名时，把整个 skills/ 链接为 ~/.agents/skills/${USER_NAMESPACE}。
带技能名时，逐个链接到 ~/.agents/skills/<技能名>。

项目级把技能目录复制到 <仓库>/.agents/skills/<技能名>/。不带技能名时复制全部。
再次执行会覆盖已安装的同名副本。

技能名可用逗号或空格分隔，all 表示全部。
`;
}

function lstatOrNull(target) {
  try {
    return lstatSync(target);
  } catch (error) {
    if (error.code === 'ENOENT') return null;
    throw error;
  }
}

function isInside(parent, child) {
  const rel = relative(resolve(parent), resolve(child));
  return rel !== '' && rel !== '..' && !rel.startsWith(`..${sep}`) && !isAbsolute(rel);
}

function samePath(left, right) {
  try {
    return realpathSync(left) === realpathSync(right);
  } catch {
    return resolve(left) === resolve(right);
  }
}

function isEphemeralCheckout() {
  const parts = repoRoot.split(sep);
  return parts.includes('_npx') || parts.includes('.npm') || parts.includes('node_modules');
}

function discoverSkills() {
  const found = [];
  const seen = new Map();

  function walk(dir) {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (!entry.isDirectory() || SKIP_DIRS.has(entry.name)) continue;
      const skillDir = join(dir, entry.name);
      const skillMd = join(skillDir, 'SKILL.md');
      if (existsSync(skillMd)) {
        const name = readSkillName(skillMd, skillDir);
        if (seen.has(name)) {
          throw new Error(`技能名重复: ${name}（${seen.get(name)} 与 ${skillDir}）`);
        }
        seen.set(name, skillDir);
        found.push({ name, dir: skillDir });
        continue;
      }
      walk(skillDir);
    }
  }

  if (!existsSync(skillsRoot)) throw new Error(`未找到技能目录: ${skillsRoot}`);
  walk(skillsRoot);
  found.sort((a, b) => a.name.localeCompare(b.name));
  return found;
}

function readSkillName(skillMd, skillDir) {
  const text = readFileSync(skillMd, 'utf8');
  const frontmatter = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  const name = frontmatter?.[1].match(/^name:\s*["']?([a-z0-9-]+)["']?\s*$/m)?.[1];
  const folder = basename(skillDir);
  if (!name || name !== folder) {
    throw new Error(`${skillDir} 的 frontmatter name 必须与目录名一致`);
  }
  return name;
}

function parseArgs(argv) {
  const args = { user: false, project: null, list: false, uninstall: false, help: false, names: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === '--help' || token === '-h') args.help = true;
    else if (token === '--user') args.user = true;
    else if (token === '--list') args.list = true;
    else if (token === '--uninstall') args.uninstall = true;
    else if (token === '--project') {
      const value = argv[i + 1];
      if (!value || value.startsWith('--')) throw new Error('--project 需要仓库路径');
      args.project = value;
      i += 1;
    } else if (token === '--install') {
      const value = argv[i + 1];
      if (!value || value.startsWith('--')) throw new Error('--install 需要技能名');
      args.names.push(...splitNames(value));
      i += 1;
    } else if (token.startsWith('--')) {
      throw new Error(`未知参数: ${token}\n\n${usage()}`);
    } else {
      args.names.push(...splitNames(token));
    }
  }
  return args;
}

function splitNames(value) {
  return value.split(',').map((part) => part.trim()).filter(Boolean);
}

function selectSkills(skills, names) {
  if (names.length === 0 || (names.length === 1 && names[0] === 'all')) {
    return { skills, all: true };
  }
  if (names.includes('all')) throw new Error('all 不能和其他技能名一起用');
  const byName = new Map(skills.map((skill) => [skill.name, skill]));
  const selected = [];
  for (const name of names) {
    const skill = byName.get(name);
    if (!skill) {
      throw new Error(`未找到技能 [${name}]。可选: ${skills.map((item) => item.name).join(', ')}`);
    }
    if (!selected.includes(skill)) selected.push(skill);
  }
  return { skills: selected, all: false };
}

function userBase() {
  return join(homedir(), '.agents', 'skills');
}

function projectBase(project) {
  let root;
  try {
    root = realpathSync(resolve(project));
  } catch {
    throw new Error(`项目目录不存在: ${resolve(project)}`);
  }
  if (!lstatSync(root).isDirectory()) throw new Error(`项目路径不是目录: ${root}`);
  if (samePath(root, repoRoot) || isInside(repoRoot, root)) {
    throw new Error(`拒绝把技能拷贝进技能仓库自身: ${root}`);
  }
  return join(root, '.agents', 'skills');
}

function ensureContainer(base) {
  const existing = lstatOrNull(base);
  if (existing?.isSymbolicLink()) {
    throw new Error(`${base} 本身是链接。请先移除该链接，再安装到它下面。`);
  }
  mkdirSync(base, { recursive: true });
}

function linkTarget(linkPath) {
  return resolve(dirname(linkPath), readlinkSync(linkPath));
}

function pointsAtRepo(linkPath) {
  try {
    const target = linkTarget(linkPath);
    return samePath(target, skillsRoot) || isInside(skillsRoot, target) || samePath(target, repoRoot);
  } catch {
    return false;
  }
}

function namespaceCovers(base) {
  const dest = join(base, USER_NAMESPACE);
  const stat = lstatOrNull(dest);
  if (!stat?.isSymbolicLink()) return false;
  return samePath(dest, skillsRoot);
}

function placeLink(dest, source) {
  const existing = lstatOrNull(dest);
  if (existing && !existing.isSymbolicLink()) {
    throw new Error(`${dest} 已存在且不是链接，未覆盖`);
  }
  if (existing?.isSymbolicLink()) rmSync(dest);
  symlinkSync(source, dest, process.platform === 'win32' ? 'junction' : 'dir');
}

function installUser(selected, all, catalog) {
  if (isEphemeralCheckout()) {
    throw new Error('当前是 npx 临时目录，不能做用户级链接。请在技能仓库的克隆里执行 --user，或用 --project 拷贝到目标仓库。');
  }
  const base = userBase();
  ensureContainer(base);
  if (all) {
    const dest = join(base, USER_NAMESPACE);
    placeLink(dest, skillsRoot);
    console.log(`已链接整库: ${dest} -> ${skillsRoot}`);
    for (const skill of catalog) {
      const flat = join(base, skill.name);
      const stat = lstatOrNull(flat);
      if (!stat) continue;
      if (stat.isSymbolicLink() && pointsAtRepo(flat)) {
        rmSync(flat);
        console.log(`已移除重复链接: ${flat}`);
      } else {
        console.warn(`注意: ${flat} 与整库中的 ${skill.name} 同名，只会加载先发现的那个`);
      }
    }
    return;
  }

  for (const skill of selected) {
    const dest = join(base, skill.name);
    placeLink(dest, skill.dir);
    console.log(`已链接: ${skill.name} -> ${dest}`);
  }
  if (namespaceCovers(base)) {
    console.warn(`注意: ~/.agents/skills/${USER_NAMESPACE} 已链接整库，同名技能只会加载先发现的那个`);
  }
}

function assertCopyable(dest) {
  const existing = lstatOrNull(dest);
  if (!existing) return;
  if (existing.isSymbolicLink()) return;
  if (existing.isDirectory()) {
    if (!existsSync(join(dest, 'SKILL.md'))) {
      throw new Error(`${dest} 已存在且不是技能目录，未覆盖`);
    }
    return;
  }
  throw new Error(`${dest} 已存在且不是目录，未覆盖`);
}

function overwritesSource(skillDir, dest) {
  if (lstatOrNull(dest)?.isSymbolicLink()) return false;
  return isInside(skillDir, dest) || samePath(skillDir, dest);
}

function copySkill(base, skill) {
  const dest = join(base, skill.name);
  if (overwritesSource(skill.dir, dest)) {
    throw new Error(`拒绝把 ${skill.name} 拷贝到其源目录内部`);
  }
  assertCopyable(dest);
  const tmp = join(base, `.${skill.name}.installing`);
  rmSync(tmp, { recursive: true, force: true });
  try {
    cpSync(skill.dir, tmp, { recursive: true });
    const existing = lstatOrNull(dest);
    if (existing?.isSymbolicLink()) rmSync(dest);
    else if (existing) rmSync(dest, { recursive: true, force: true });
    renameSync(tmp, dest);
  } catch (error) {
    rmSync(tmp, { recursive: true, force: true });
    throw error;
  }
  const installed = lstatSync(dest);
  if (installed.isSymbolicLink()) throw new Error(`${dest} 安装后仍是链接`);
  console.log(`已拷贝: ${skill.name} -> ${dest}`);
}

function installProject(project, skills) {
  const base = projectBase(project);
  for (const skill of skills) {
    const dest = join(base, skill.name);
    if (overwritesSource(skill.dir, dest)) {
      throw new Error(`拒绝把 ${skill.name} 拷贝到其源目录内部`);
    }
    assertCopyable(dest);
  }
  ensureContainer(base);
  for (const skill of skills) copySkill(base, skill);
}

function uninstallUser(skills, all) {
  const base = userBase();
  if (!all) {
    for (const skill of skills) {
      const dest = join(base, skill.name);
      if (!lstatOrNull(dest)) {
        if (namespaceCovers(base)) {
          console.log(`${skill.name} 只存在于整库链接 ${USER_NAMESPACE} 中。移除整库请执行 --uninstall --user`);
        } else {
          console.log(`${skill.name} 未安装`);
        }
        continue;
      }
      removeUserSkillLink(base, skill, true);
    }
    return;
  }

  for (const skill of skills) removeUserSkillLink(base, skill, false);
  const dest = join(base, USER_NAMESPACE);
  const stat = lstatOrNull(dest);
  if (!stat) console.log(`整库链接不存在: ${dest}`);
  else if (!stat.isSymbolicLink()) throw new Error(`${dest} 不是链接，未删除`);
  else if (!pointsAtRepo(dest)) throw new Error(`${dest} 指向仓库外部，未删除`);
  else {
    rmSync(dest);
    console.log(`已移除整库链接: ${dest}`);
  }
}

function removeUserSkillLink(base, skill, strict) {
  const dest = join(base, skill.name);
  const stat = lstatOrNull(dest);
  if (!stat) return;
  if (!stat.isSymbolicLink()) {
    const message = `${dest} 不是链接，未删除`;
    if (strict) throw new Error(message);
    console.warn(`跳过: ${message}`);
    return;
  }
  if (!pointsAtRepo(dest)) {
    const message = `${dest} 指向仓库外部，未删除`;
    if (strict) throw new Error(message);
    console.warn(`跳过: ${message}`);
    return;
  }
  rmSync(dest);
  console.log(`已移除链接: ${dest}`);
}

function uninstallProject(project, skills) {
  const base = projectBase(project);
  for (const skill of skills) {
    const dest = join(base, skill.name);
    const stat = lstatOrNull(dest);
    if (!stat) {
      console.log(`${skill.name} 未安装`);
      continue;
    }
    if (stat.isSymbolicLink()) {
      rmSync(dest);
      console.log(`已移除链接: ${dest}`);
      continue;
    }
    if (!stat.isDirectory() || !existsSync(join(dest, 'SKILL.md'))) {
      throw new Error(`${dest} 不是本安装器写入的技能目录，未删除`);
    }
    rmSync(dest, { recursive: true, force: true });
    console.log(`已删除副本: ${dest}`);
  }
}

function listSkills(base, scope, skills) {
  console.log(`\n范围: ${scope === 'user' ? '用户级' : '项目级'}`);
  console.log(`目录: ${base}`);
  if (scope === 'user' && namespaceCovers(base)) {
    console.log(`整库: ${join(base, USER_NAMESPACE)} -> ${skillsRoot}`);
  }
  for (const skill of skills) {
    const dest = join(base, skill.name);
    const stat = lstatOrNull(dest);
    let label = '未安装';
    if (stat?.isSymbolicLink()) label = `链接 -> ${linkTarget(dest)}`;
    else if (stat?.isDirectory() && existsSync(join(dest, 'SKILL.md'))) label = '已拷贝';
    else if (stat) label = '路径被占用';
    else if (scope === 'user' && namespaceCovers(base)) label = `经整库链接 ${USER_NAMESPACE}`;
    console.log(`  ${skill.name.padEnd(28)} ${label}`);
  }
  console.log('');
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
    return;
  }
  if (args.user && args.project) throw new Error('用户级和项目级只能选一个');
  if (!args.user && !args.project) {
    if (args.list) args.user = true;
    else throw new Error(usage());
  }
  if (args.list && args.uninstall) throw new Error('--list 和 --uninstall 不能同时用');

  const skills = discoverSkills();
  const selected = selectSkills(skills, args.names);
  const base = args.project ? projectBase(args.project) : userBase();

  if (args.list) {
    listSkills(base, args.project ? 'project' : 'user', skills);
    return;
  }
  if (args.uninstall) {
    if (args.project) uninstallProject(args.project, selected.skills);
    else uninstallUser(selected.skills, selected.all);
    return;
  }
  if (args.project) installProject(args.project, selected.skills);
  else installUser(selected.skills, selected.all, skills);
}

try {
  main();
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
