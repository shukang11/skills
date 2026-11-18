#!/usr/bin/env python3
"""Capture/verify scoped review manifests and diffs. Requires POSIX Python >=3.9."""
import argparse
import base64
import difflib
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys


class ScopeError(Exception):
    pass


def require_environment():
    if sys.version_info < (3, 9) or os.name != 'posix':
        raise ScopeError('requires POSIX Python >=3.9')
    if any(not isinstance(getattr(os, name, None), int)
           for name in ('O_DIRECTORY', 'O_NOFOLLOW')):
        raise ScopeError('requires POSIX O_DIRECTORY and O_NOFOLLOW support')
    dir_fd = getattr(os, 'supports_dir_fd', set())
    no_follow = getattr(os, 'supports_follow_symlinks', set())
    if not {os.open, os.stat, os.readlink}.issubset(dir_fd) or os.stat not in no_follow:
        raise ScopeError('requires dir_fd support for open/stat/readlink and '
                         'stat(follow_symlinks=False)')


def git(repo, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_OPTIONAL_LOCKS='0', GIT_LITERAL_PATHSPECS='1', GIT_NO_LAZY_FETCH='1')
    result = subprocess.run(['git', '-c', 'core.fsmonitor=false', '-C', str(repo),
                             *args], env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if result.returncode:
        raise ScopeError(result.stderr.decode('utf-8', 'replace').strip())
    return result.stdout


def commit(repo, revision):
    return git(repo, 'rev-parse', '--verify', '--end-of-options',
               revision + '^{commit}').decode().strip()


def scopes(values):
    result = []
    for value in values:
        parts = value.split('/')
        if (not value or value.startswith(('/', ':')) or '..' in parts
                or '.git' in parts or '\x00' in value):
            raise ScopeError('scope must be a literal relative file or directory')
        normalized = str(PurePosixPath(value))
        if normalized not in result:
            result.append(normalized)
    return sorted(result)


def read_worktree(repo, name):
    """Open each ancestor without following symlinks; hash link text itself."""
    parts = name.split('/')
    fd = os.open(repo, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            try:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                dir_fd=fd)
            except FileNotFoundError:
                return None, None
            except OSError as exc:
                raise ScopeError('unsafe or non-directory ancestor: ' + name) from exc
            os.close(fd)
            fd = child
        try:
            info = os.stat(parts[-1], dir_fd=fd, follow_symlinks=False)
        except FileNotFoundError:
            return None, None
        if stat.S_ISLNK(info.st_mode):
            data = os.fsencode(os.readlink(parts[-1], dir_fd=fd))
            mode = '120000'
        elif stat.S_ISREG(info.st_mode):
            leaf = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=fd)
            with os.fdopen(leaf, 'rb') as stream:
                opened = os.fstat(stream.fileno())
                if not stat.S_ISREG(opened.st_mode):
                    raise ScopeError('file type changed: ' + name)
                data = stream.read()
                mode = '100755' if opened.st_mode & stat.S_IXUSR else '100644'
        else:
            raise ScopeError('unsupported working-tree file type: ' + name)
        return {'mode': mode, 'sha256': hashlib.sha256(data).hexdigest()}, data
    finally:
        os.close(fd)


def check_scope_ancestors(repo, selected):
    for name in selected:
        parts = PurePosixPath(name).parts
        for depth in range(1, len(parts) + 1):
            relative = PurePosixPath(*parts[:depth])
            candidate = repo / str(relative)
            try:
                info = candidate.lstat()
            except FileNotFoundError:
                break
            if stat.S_ISLNK(info.st_mode):
                if depth < len(parts):
                    raise ScopeError('scope ancestor is a symlink: ' + str(relative))
                break
            if stat.S_ISDIR(info.st_mode):
                try:
                    (candidate / '.git').lstat()
                except FileNotFoundError:
                    continue
                raise ScopeError('nested Git repositories are unsupported: ' + str(relative))



def tree(repo, revision, selected):
    entries = {}
    for record in git(repo, 'ls-tree', '-r', '-z', revision, '--', *selected).split(b'\0'):
        if not record:
            continue
        meta, raw_name = record.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        if kind != 'blob':
            raise ScopeError('submodules are not supported in review scope')
        entries[os.fsdecode(raw_name)] = {'mode': mode, 'oid': oid}
    return entries


def index(repo, selected):
    entries = {}
    for record in git(repo, 'ls-files', '--stage', '-z', '--', *selected).split(b'\0'):
        if not record:
            continue
        meta, raw_name = record.split(b'\t', 1)
        mode, oid, stage = meta.decode().split()
        if mode == '160000' or stage != '0':
            raise ScopeError('submodules and unmerged index entries are unsupported')
        entries[os.fsdecode(raw_name)] = {'mode': mode, 'oid': oid}
    return entries


def materialize(repo, entries, cache):
    result, data = {}, {}
    for name, entry in entries.items():
        oid = entry['oid']
        if oid not in cache:
            cache[oid] = git(repo, 'cat-file', 'blob', oid)
        data[name] = cache[oid]
        result[name] = dict(entry, sha256=hashlib.sha256(cache[oid]).hexdigest())
    return result, data


def differences(before, after, before_data, after_data):
    changes = []
    for name in sorted(before.keys() | after.keys()):
        left, right = before.get(name), after.get(name)
        comparable = lambda item: None if item is None else (item['mode'], item['sha256'])
        if comparable(left) == comparable(right):
            continue
        change = {'path': name, 'before': left, 'after': right}
        a, b = before_data.get(name, b''), after_data.get(name, b'')
        try:
            if b'\0' in a or b'\0' in b:
                raise UnicodeError()
            a_text, b_text = a.decode('utf-8'), b.decode('utf-8')
            # JSON escapes unusual filenames. Line arrays preserve missing final newlines.
            change['text_diff_lines'] = list(difflib.unified_diff(
                a_text.splitlines(keepends=True), b_text.splitlines(keepends=True),
                fromfile='a/' + name, tofile='b/' + name))
        except UnicodeError:
            change['binary'] = True
        changes.append(change)
    return changes


def collect(repo, base, selected):
    check_scope_ancestors(repo, selected)
    head = commit(repo, 'HEAD')
    base_raw = tree(repo, base, selected)
    head_raw = tree(repo, head, selected)
    index_raw = index(repo, selected)
    untracked = sorted(os.fsdecode(p) for p in git(
        repo, 'ls-files', '--others', '--exclude-standard', '-z', '--',
        *selected).split(b'\0') if p)
    if any(name.endswith('/') for name in untracked):
        raise ScopeError('untracked directory placeholders/nested Git repositories are unsupported')
    cache = {}
    base_files, base_data = materialize(repo, base_raw, cache)
    head_files, head_data = materialize(repo, head_raw, cache)
    index_files, index_data = materialize(repo, index_raw, cache)
    names = sorted(base_raw.keys() | head_raw.keys() | index_raw.keys() | set(untracked))
    files, work_data, work_files = {}, {}, {}
    for name in names:
        entry, data = read_worktree(repo, name)
        files[name] = {'baseline': base_files.get(name), 'head': head_files.get(name),
                       'index': index_files.get(name), 'working_tree': entry,
                       'untracked': name in untracked}
        if entry is not None:
            work_files[name], work_data[name] = entry, data
    tracked = base_raw.keys() | index_raw.keys()
    tracked_work = {n: v for n, v in work_files.items() if n in tracked}
    index_work = {n: v for n, v in work_files.items() if n in index_raw}
    return {'head': head, 'files': files,
            'index_metadata_b64': base64.b64encode(git(
                repo, 'ls-files', '--stage', '--debug', '-z', '--', *selected)).decode(),
            'diffs': {
        'base_to_working_tree_tracked': differences(base_files, tracked_work, base_data, work_data),
        'head_to_index_staged': differences(head_files, index_files, head_data, index_data),
        'index_to_working_tree_unstaged': differences(index_files, index_work, index_data, work_data)}}


def stable_state(repo, base, selected):
    first = collect(repo, base, selected)
    if first != collect(repo, base, selected):
        raise ScopeError('selected state changed during collection; retry capture/verify')
    return first


def repository(path):
    repo = Path(path).resolve(strict=True)
    root = Path(os.fsdecode(git(repo, 'rev-parse', '--show-toplevel')).rstrip('\n')).resolve()
    if root != repo:
        raise ScopeError('--repo must be the working-tree root')
    return repo


def capture(args):
    repo = repository(args.repo)
    selected = scopes(args.path)
    base = commit(repo, args.base)
    output = Path(args.output).absolute()
    resolved = output.resolve()
    if resolved.is_relative_to(repo):
        raise ScopeError('report must be outside the repository')
    if output.exists() or output.is_symlink():
        raise ScopeError('report already exists')
    state = stable_state(repo, base, selected)
    report = {'format': 1, 'purpose': 'Review manifest and diffs; not a complete source snapshot. '
              'Read added files separately; hashes permit later verification.',
              'repo': str(repo), 'base': base, 'paths': selected, 'state': state}
    data = (json.dumps(report, ensure_ascii=True, indent=2) + '\n').encode()
    created = False
    try:
        fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        created = True
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
    except BaseException:
        if created:
            output.unlink(missing_ok=True)
        raise
    return 0


def verify(args):
    with open(args.report, 'r', encoding='utf-8') as stream:
        report = json.load(stream)
    if report['format'] != 1:
        raise ScopeError('unsupported report format')
    repo = repository(report['repo'])
    selected = scopes(report['paths'])
    base = commit(repo, report['base'])
    if base != report['base']:
        raise ScopeError('report baseline is not a fixed commit')
    try:
        current = stable_state(repo, base, selected)
    except ScopeError as exc:
        print('drift or unavailable selected state: ' + str(exc), file=sys.stderr)
        return 1
    if current != report['state']:
        print('review scope drift detected', file=sys.stderr)
        return 1
    print('review scope unchanged')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    cap = commands.add_parser('capture', help='create a private manifest outside the repository')
    cap.add_argument('--repo', required=True)
    cap.add_argument('--base', required=True, help='explicit commit/revision; no implicit merge-base')
    cap.add_argument('--path', action='append', required=True, help='literal relative file/directory (repeatable)')
    cap.add_argument('--output', required=True)
    ver = commands.add_parser('verify', help='reject HEAD or selected index/content drift')
    ver.add_argument('--report', required=True)
    args = parser.parse_args()
    try:
        require_environment()
        return capture(args) if args.command == 'capture' else verify(args)
    except (ScopeError, OSError, ValueError, KeyError, TypeError) as exc:
        print('error: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
