#!/usr/bin/env python3
"""Real Git integration checks; all repositories and reports are temporary."""
import importlib.util
import contextlib
import io
import json
import os
import shlex
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).with_name('review-scope.py')
SPEC = importlib.util.spec_from_file_location('review_scope', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReviewScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        (self.repo / 'chosen').mkdir()
        for name in ['mixed', 'delete', 'mode', 'space name', 'line\nbreak']:
            (self.repo / 'chosen' / name).write_text('baseline\n')
        (self.repo / 'outside').write_text('outside\n')
        (self.repo / '.gitignore').write_text('*.ignored\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'baseline')
        self.base = self.git('rev-parse', 'HEAD').strip().decode()
        self.report = self.root / 'report.json'

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], stderr=subprocess.PIPE)

    def cli(self, *args, expected=0):
        result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True)
        self.assertEqual(result.returncode, expected, result.stderr.decode())
        return result

    def capture(self, *extra, expected=0):
        return self.cli('capture', '--repo', self.repo, '--base', self.base,
                        '--path', 'chosen', '--output', self.report, *extra, expected=expected)

    def verify(self, expected=0):
        return self.cli('verify', '--report', self.report, expected=expected)

    def test_full_manifest_and_three_diffs_preserve_index(self):
        mixed = self.repo / 'chosen/mixed'
        mixed.write_text('later commit\n')
        self.git('add', 'chosen/mixed')
        self.git('commit', '-qm', 'later')
        mixed.write_text('staged\n')
        self.git('add', 'chosen/mixed')
        mixed.write_text('unstaged\n')
        (self.repo / 'chosen/delete').unlink()
        (self.repo / 'chosen/space name').write_text('space changed\n')
        (self.repo / 'chosen/line\nbreak').write_text('newline changed\n')
        (self.repo / 'chosen/new').write_text('untracked content\n')
        (self.repo / 'chosen/secret.ignored').write_text('do not read this\n')
        (self.repo / 'chosen/mode').chmod(0o755)
        secret = self.root / 'external-secret'
        secret.write_text('outside symlink target secret\n')
        (self.repo / 'chosen/link').symlink_to(secret)
        index_before = (self.repo / '.git/index').read_bytes()
        self.capture()
        self.verify()
        self.assertEqual(index_before, (self.repo / '.git/index').read_bytes())
        self.assertEqual(self.report.stat().st_mode & 0o777, 0o600)
        report_text = self.report.read_text()
        report = json.loads(report_text)
        files = report['state']['files']
        self.assertNotIn('chosen/secret.ignored', files)
        self.assertNotIn('outside symlink target secret', report_text)
        self.assertNotIn('do not read this', report_text)
        self.assertTrue(files['chosen/new']['untracked'])
        self.assertIsNone(files['chosen/delete']['working_tree'])
        self.assertEqual(files['chosen/link']['working_tree']['mode'], '120000')
        self.assertEqual(files['chosen/mode']['working_tree']['mode'], '100755')
        self.assertIn('chosen/line\nbreak', files)
        diffs = report['state']['diffs']
        for key in diffs:
            self.assertIn('chosen/mixed', [x['path'] for x in diffs[key]])
        staged = next(x for x in diffs['head_to_index_staged'] if x['path'] == 'chosen/mixed')
        self.assertIn('-later commit\n', staged['text_diff_lines'])
        self.assertIn('+staged\n', staged['text_diff_lines'])
        (self.repo / 'outside').write_text('scope outside changed\n')
        self.git('add', 'outside')
        self.verify()
        after_outside = (self.repo / '.git/index').read_bytes()
        self.verify()
        self.assertEqual(after_outside, (self.repo / '.git/index').read_bytes())

    def test_each_kind_of_drift(self):
        cases = ['untracked', 'content', 'delete', 'rename', 'permission', 'symlink', 'stage', 'head', 'index_flag']
        for case in cases:
            with self.subTest(case=case):
                if self.report.exists():
                    self.report.unlink()
                self.capture()
                if case == 'untracked':
                    (self.repo / 'chosen/new').write_text('new')
                elif case == 'content':
                    (self.repo / 'chosen/mixed').write_text('changed')
                elif case == 'delete':
                    (self.repo / 'chosen/delete').unlink()
                elif case == 'rename':
                    (self.repo / 'chosen/space name').rename(self.repo / 'chosen/renamed')
                elif case == 'permission':
                    (self.repo / 'chosen/mode').chmod(0o755)
                elif case == 'symlink':
                    (self.repo / 'chosen/link').symlink_to('/does/not/exist')
                elif case == 'stage':
                    (self.repo / 'chosen/mixed').write_text('staged')
                    self.git('add', 'chosen/mixed')
                elif case == 'head':
                    self.git('commit', '--allow-empty', '-qm', 'new HEAD')
                elif case == 'index_flag':
                    self.git('update-index', '--assume-unchanged', 'chosen/mixed')
                self.verify(expected=1)
                self.git('update-index', '--no-assume-unchanged', 'chosen/mixed')
                self.git('reset', '--hard', '-q', self.base)
                self.git('clean', '-fdq')

    def test_symlink_target_changes_and_ancestor_rejection(self):
        link = self.repo / 'chosen/link'
        link.symlink_to('/secret-one')
        self.capture()
        link.unlink()
        link.symlink_to('/secret-two')
        self.verify(expected=1)
        self.report.unlink()
        (self.repo / 'alias').symlink_to(self.repo / 'chosen', target_is_directory=True)
        self.capture('--path', 'alias/mixed', expected=2)
        self.assertFalse(self.report.exists())
        # A captured directory replaced by an outside link must fail verification.
        self.capture()
        (self.repo / 'chosen').rename(self.repo / 'saved')
        (self.repo / 'chosen').symlink_to(self.root, target_is_directory=True)
        self.verify(expected=1)

    def test_invalid_scopes_output_and_help(self):
        self.cli('--help')
        self.cli('capture', '--help')
        self.cli('verify', '--help')
        for path in ['../outside', '/tmp', ':(glob)**', 'chosen/../outside', '.git/config']:
            self.capture('--path', path, expected=2)
            self.assertFalse(self.report.exists())
        self.capture('--output', self.repo / 'report.json', expected=2)
        self.capture()
        original = self.report.read_bytes()
        self.capture(expected=2)
        self.assertEqual(original, self.report.read_bytes())
        # Literal wildcard does not select any files.
        self.report.unlink()
        self.cli('capture', '--repo', self.repo, '--base', self.base,
                 '--path', 'chosen/*', '--output', self.report)
        self.assertEqual(json.loads(self.report.read_text())['state']['files'], {})

    def test_no_external_filters_hooks_or_inherited_git_overrides(self):
        marker = self.root / 'external-command-ran'
        command = 'touch ' + shlex.quote(str(marker))
        (self.repo / '.gitattributes').write_text('chosen/* filter=reviewcheck diff=reviewcheck\n')
        self.git('config', 'filter.reviewcheck.clean', command)
        self.git('config', 'filter.reviewcheck.process', command)
        self.git('config', 'diff.reviewcheck.command', command)
        self.git('config', 'diff.reviewcheck.textconv', command)
        self.git('config', 'core.fsmonitor', command)
        hook = self.repo / '.git/hooks/post-index-change'
        hook.write_text('#!/bin/sh\n' + command + '\n')
        hook.chmod(0o755)
        (self.repo / 'chosen/mixed').write_text('working change\n')
        with mock.patch.dict(os.environ, {
                'GIT_EXTERNAL_DIFF': command,
                'GIT_INDEX_FILE': str(self.root / 'wrong-index'),
                'GIT_DIR': str(self.root / 'wrong-git-dir'),
                'GIT_WORK_TREE': str(self.root / 'wrong-worktree')}):
            self.capture()
            self.verify()
        self.assertFalse(marker.exists())
        self.assertFalse((self.root / 'wrong-index').exists())
        changes = json.loads(self.report.read_text())['state']['diffs']
        self.assertIn('chosen/mixed', [x['path'] for x in changes['index_to_working_tree_unstaged']])

    def test_missing_promisor_blob_does_not_run_remote_helper(self):
        oid = self.git('rev-parse', 'HEAD:chosen/mixed').decode().strip()
        (self.repo / '.git/objects' / oid[:2] / oid[2:]).unlink()
        self.git('config', 'remote.origin.url', 'reviewtest::unused')
        self.git('config', 'remote.origin.promisor', 'true')
        self.git('config', 'remote.origin.partialclonefilter', 'blob:none')
        self.git('config', 'protocol.reviewtest.allow', 'always')
        helper_dir = self.root / 'helpers'
        helper_dir.mkdir()
        marker = self.root / 'remote-helper-ran'
        helper = helper_dir / 'git-remote-reviewtest'
        helper.write_text('#!/bin/sh\ntouch ' + shlex.quote(str(marker)) + '\nexit 1\n')
        helper.chmod(0o755)

        def git_files():
            return {str(path.relative_to(self.repo)): path.read_bytes()
                    for path in (self.repo / '.git').rglob('*') if path.is_file()}

        before = git_files()
        with mock.patch.dict(os.environ, {
                'PATH': str(helper_dir) + os.pathsep + os.environ.get('PATH', ''),
                'GIT_NO_LAZY_FETCH': '0'}):
            self.capture(expected=2)
        self.assertFalse(marker.exists())
        self.assertFalse(self.report.exists())
        self.assertEqual(before, git_files())

    def test_untracked_nested_repository_is_rejected_for_directory_and_explicit_file(self):
        self.capture()
        nested = self.repo / 'chosen/nested'
        nested.mkdir()
        subprocess.check_call(['git', '-C', str(nested), 'init', '-q'])
        (nested / 'value').write_text('before\n')
        nested_metadata = {str(path.relative_to(nested)): path.read_bytes()
                           for path in (nested / '.git').rglob('*') if path.is_file()}
        self.verify(expected=1)
        self.report.unlink()
        self.capture(expected=2)
        self.assertFalse(self.report.exists())
        for path in ['chosen/nested', 'chosen/nested/value', 'chosen/nested/missing']:
            with self.subTest(path=path):
                self.cli('capture', '--repo', self.repo, '--base', self.base,
                         '--path', path, '--output', self.report, expected=2)
                self.assertFalse(self.report.exists())
        (nested / 'value').write_text('after\n')
        self.capture(expected=2)
        self.assertEqual(nested_metadata, {
            str(path.relative_to(nested)): path.read_bytes()
            for path in (nested / '.git').rglob('*') if path.is_file()})

    def test_missing_platform_capability_fails_before_repository_access(self):
        commands = [
            ['capture', '--repo', str(self.repo), '--base', self.base,
             '--path', 'chosen', '--output', str(self.report)],
            ['verify', '--report', str(self.report)],
        ]
        for command in commands:
            with self.subTest(command=command[0]):
                stderr = io.StringIO()
                with mock.patch.dict(MODULE.os.__dict__), \
                        mock.patch.object(sys, 'argv', [str(SCRIPT), *command]), \
                        mock.patch.object(MODULE, 'repository') as repository, \
                        contextlib.redirect_stderr(stderr):
                    del MODULE.os.O_NOFOLLOW
                    self.assertEqual(MODULE.main(), 2)
                    repository.assert_not_called()
                self.assertIn('O_NOFOLLOW', stderr.getvalue())
                self.assertFalse(self.report.exists())
        with mock.patch.object(MODULE.os, 'supports_dir_fd', set()), \
                mock.patch.object(sys, 'argv', [str(SCRIPT), *commands[0]]), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(MODULE.main(), 2)
        for command in [[], ['capture'], ['verify']]:
            with mock.patch.object(MODULE, 'require_environment',
                                   side_effect=MODULE.ScopeError('unsupported')) as check, \
                    mock.patch.object(sys, 'argv', [str(SCRIPT), *command, '--help']), \
                    contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    MODULE.main()
                self.assertEqual(caught.exception.code, 0)
                check.assert_not_called()

    def test_capture_race_does_not_publish_report(self):
        args = type('Args', (), dict(repo=str(self.repo), base=self.base,
                    path=['chosen'], output=str(self.report)))()
        original_collect = MODULE.collect
        count = 0

        def mutate_after_first(*values):
            nonlocal count
            state = original_collect(*values)
            count += 1
            if count == 1:
                (self.repo / 'chosen/mixed').write_text('racing writer\n')
            return state

        with mock.patch.object(MODULE, 'collect', side_effect=mutate_after_first):
            with self.assertRaises(MODULE.ScopeError):
                MODULE.capture(args)
        self.assertFalse(self.report.exists())


if __name__ == '__main__':
    unittest.main()
