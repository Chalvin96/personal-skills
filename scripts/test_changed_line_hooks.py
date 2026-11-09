import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location
from shutil import which
from signal import SIGINT, SIGTERM
from unittest.mock import patch


K_SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "ume-review"
    / "scripts"
    / "changed_line_hooks.py"
)

K_BASE_APP = "keep = 1\nold = 2\ntail = 3\n"
K_HEAD_APP = "keep = 1\nnew = 2\ntail = 3\n"

K_HOOK_WITH_FINDINGS = (
    "#!/usr/bin/env python3\n"
    "import sys\n"
    "\n"
    'print("Check Lines.....................................Failed")\n'
    'print("- hook id: check-lines")\n'
    'print("- exit code: 1")\n'
    "print()\n"
    'print("src/app.py:2: name shadows nothing")\n'
    'print("src/app.py:3: legacy drift remains")\n'
    "sys.exit(1)\n"
)

K_HOOK_WITH_LEGACY_FINDING = (
    "#!/usr/bin/env python3\n"
    "import sys\n"
    "\n"
    'print("Check Lines.....................................Failed")\n'
    'print("- hook id: check-lines")\n'
    'print("- exit code: 1")\n'
    "print()\n"
    'print("src/app.py:3: legacy drift remains")\n'
    "sys.exit(1)\n"
)

K_HOOK_REWRITING_CHANGED_LINE = (
    "#!/usr/bin/env python3\n"
    "import sys\n"
    "from pathlib import Path\n"
    "\n"
    'target = Path("src/app.py")\n'
    "text = target.read_text()\n"
    'target.write_text(text.replace("new = 2", "new  = 2"))\n'
    'print("Reformat........................................Failed")\n'
    'print("- hook id: reformat")\n'
    'print("- files were modified by this hook")\n'
    "sys.exit(1)\n"
)

K_HOOK_REWRITING_UNCHANGED_LINE = (
    "#!/usr/bin/env python3\n"
    "import sys\n"
    "from pathlib import Path\n"
    "\n"
    'target = Path("src/app.py")\n'
    "text = target.read_text()\n"
    'target.write_text(text.replace("tail = 3", "tail = 3 "))\n'
    'print("Reformat........................................Failed")\n'
    'print("- hook id: reformat")\n'
    'print("- files were modified by this hook")\n'
    "sys.exit(1)\n"
)

K_PRE_COMMIT_CONFIG = "repos:\n  - repo: local\n    hooks: []\n"


def run_git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=repo, text=True, stderr=subprocess.PIPE
    )


def build_repo(root: Path) -> tuple[Path, str]:
    repo = root / "project"
    repo.mkdir()
    run_git(repo, "init", "-q")
    run_git(repo, "config", "user.email", "tester@example.com")
    run_git(repo, "config", "user.name", "Tester")
    app = repo / "src" / "app.py"
    app.parent.mkdir()
    app.write_text(K_BASE_APP, encoding="utf-8")
    (app.parent / "other.py").write_text("other = 1\n", encoding="utf-8")
    (repo / ".pre-commit-config.yaml").write_text(K_PRE_COMMIT_CONFIG, encoding="utf-8")
    run_git(repo, "add", ".")
    run_git(repo, "commit", "-q", "-m", "base")
    base = run_git(repo, "rev-parse", "HEAD").strip()
    app.write_text(K_HEAD_APP, encoding="utf-8")
    run_git(repo, "add", ".")
    run_git(repo, "commit", "-q", "-m", "head")
    return repo, base


def install_fake_pre_commit(root: Path, source: str) -> Path:
    binary = root / "bin"
    binary.mkdir(exist_ok=True)
    target = binary / "pre-commit"
    target.write_text(source, encoding="utf-8")
    target.chmod(0o755)
    return binary


def run_reporter(
    repo: Path,
    base: str,
    path_dirs: list[str],
    *,
    keep_path: bool = True,
    overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    extra = os.pathsep.join(path_dirs)
    suffix = env["PATH"] if keep_path else ""
    env["PATH"] = os.pathsep.join([part for part in (extra, suffix) if part])
    env.update(overrides or {})
    command = [sys.executable, str(K_SCRIPT), "--repo", str(repo), base]
    return subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        check=False,
    )


class ChangedLineHooksTest(unittest.TestCase):
    def setUp(self) -> None:
        self._directory = tempfile.TemporaryDirectory()
        self.root = Path(self._directory.name)
        self.repo, self.base = build_repo(self.root)
        self.addCleanup(self._directory.cleanup)

    def report(self, result: subprocess.CompletedProcess) -> dict:
        self.assertEqual("", result.stderr, result.stderr)
        return json.loads(result.stdout)

    def assert_checkout_untouched(self) -> None:
        status = run_git(self.repo, "status", "--porcelain")
        self.assertEqual("", status)
        worktrees = run_git(self.repo, "worktree", "list")
        self.assertEqual(1, len(worktrees.strip().splitlines()), worktrees)

    def test_finding_on_changed_line_is_kept(self) -> None:
        binary = install_fake_pre_commit(self.root, K_HOOK_WITH_FINDINGS)

        result = run_reporter(self.repo, self.base, [str(binary)])

        self.assertEqual(1, result.returncode)
        report = self.report(result)
        self.assertEqual("findings", report["status"])
        self.assertEqual(
            [
                {
                    "path": "src/app.py",
                    "line": 2,
                    "hook": "check-lines",
                    "message": "name shadows nothing",
                }
            ],
            report["findings"],
        )
        self.assertEqual(1, report["dropped_unchanged_findings"])
        self.assertTrue(report["worktree_removed"])
        self.assert_checkout_untouched()

    def test_finding_on_unchanged_line_only_is_clean(self) -> None:
        binary = install_fake_pre_commit(self.root, K_HOOK_WITH_LEGACY_FINDING)

        result = run_reporter(self.repo, self.base, [str(binary)])

        self.assertEqual(0, result.returncode)
        report = self.report(result)
        self.assertEqual("clean", report["status"])
        self.assertEqual([], report["findings"])
        self.assertEqual(1, report["dropped_unchanged_findings"])
        self.assertTrue(report["worktree_removed"])
        self.assert_checkout_untouched()

    def test_formatter_rewrite_on_changed_line_is_reported(self) -> None:
        binary = install_fake_pre_commit(self.root, K_HOOK_REWRITING_CHANGED_LINE)

        result = run_reporter(self.repo, self.base, [str(binary)])

        self.assertEqual(1, result.returncode)
        report = self.report(result)
        self.assertEqual([], report["findings"])
        rewrites = report["formatter_rewrites"]
        self.assertEqual(1, len(rewrites))
        self.assertEqual("src/app.py", rewrites[0]["path"])
        self.assertEqual(2, rewrites[0]["line"])
        self.assertIn("new = 2", rewrites[0]["before"])
        self.assertIn("new  = 2", rewrites[0]["after"])
        self.assertTrue(report["worktree_removed"])
        self.assert_checkout_untouched()

    def test_formatter_rewrite_on_unchanged_line_is_dropped(self) -> None:
        binary = install_fake_pre_commit(self.root, K_HOOK_REWRITING_UNCHANGED_LINE)

        result = run_reporter(self.repo, self.base, [str(binary)])

        self.assertEqual(0, result.returncode)
        report = self.report(result)
        self.assertEqual("clean", report["status"])
        self.assertEqual([], report["formatter_rewrites"])
        self.assertEqual(1, report["dropped_unchanged_rewrites"])
        self.assertTrue(report["worktree_removed"])

    def test_missing_pre_commit_binary_is_could_not_run(self) -> None:
        neighboring = install_fake_pre_commit(
            self.root,
            f"#!{sys.executable}\nprint('Check........................Passed')\n",
        )
        (neighboring / "git").symlink_to(which("git"))
        available = run_reporter(self.repo, self.base, [str(neighboring)], keep_path=False)
        self.assertEqual(0, available.returncode)
        git_directory = self.root / "git-only"
        git_directory.mkdir()
        (git_directory / "git").symlink_to(neighboring / "git")
        self.assertEqual(["git"], [path.name for path in git_directory.iterdir()])

        result = run_reporter(self.repo, self.base, [str(git_directory)], keep_path=False)

        self.assertEqual(2, result.returncode)
        report = self.report(result)
        self.assertEqual("could-not-run", report["status"])
        self.assertIn("pre-commit", report["reason"])
        self.assertTrue(report["worktree_removed"])
        self.assert_checkout_untouched()

    def run_hook(self, body: str) -> tuple[subprocess.CompletedProcess, dict]:
        source = f"#!{sys.executable}\nfrom pathlib import Path\nimport sys\n{body}"
        binary = install_fake_pre_commit(self.root, source)
        result = run_reporter(self.repo, self.base, [str(binary)])
        return result, self.report(result)

    def test_unexplained_failure_and_passed_summary(self) -> None:
        for status, expected in (("Failed", 2), ("Passed", 0)):
            with self.subTest(status=status):
                result, report = self.run_hook(
                    f"print('Check........................{status}')\n"
                    "print('- hook id: check')\n"
                    f"sys.exit({int(status == 'Failed')})\n"
                )
                self.assertEqual(expected, result.returncode)
                self.assertEqual("could-not-run" if expected else "clean", report["status"])

    def test_failed_discovery_with_passed_hooks_is_not_clean(self) -> None:
        for failure, expected in ((1, 2), (0, 0)):
            with self.subTest(failure=failure):
                result, report = self.run_hook(
                    "hook = sys.argv[2] if sys.argv[2] != '--color=never' else None\n"
                    "for name in ('first', 'second') if hook is None else (hook,):\n"
                    "    print(f'{name}........................Passed')\n"
                    "    print(f'- hook id: {name}')\n"
                    f"sys.exit({failure} if hook is None else 0)\n"
                )
                self.assertEqual(expected, result.returncode)
                self.assertEqual("could-not-run" if failure else "clean", report["status"])

    def test_eslint_stylish_changed_and_unchanged_lines(self) -> None:
        result, report = self.run_hook(
            "print('ESLint........................Failed')\n"
            "print('- hook id: eslint')\n"
            "print(Path('src/app.py').resolve())\n"
            "print('  2:1  error  new problem  no-unused-vars')\n"
            "print('  3:1  warning  old problem  no-unused-vars')\n"
            "sys.exit(1)\n"
        )
        self.assertEqual(1, result.returncode)
        self.assertEqual([2], [item["line"] for item in report["findings"]])
        self.assertEqual(1, report["dropped_unchanged_findings"])

    def test_equivalent_paths_and_unchanged_lines(self) -> None:
        for expression in ("'./src/app.py'", "str(Path('src/app.py').resolve())", "'src\\\\app.py'"):
            with self.subTest(expression=expression):
                result, report = self.run_hook(
                    "print('Check........................Failed')\n"
                    "print('- hook id: check')\n"
                    f"name = {expression}\n"
                    "print(f'{name}:2: changed')\n"
                    "print(f'{name}:3: old')\n"
                    "sys.exit(1)\n"
                )
                self.assertEqual(1, result.returncode)
                self.assertEqual([2], [item["line"] for item in report["findings"]])
                self.assertEqual(1, report["dropped_unchanged_findings"])

    def test_linter_runs_on_reviewed_snapshot_after_formatter(self) -> None:
        result, report = self.run_hook(
            "hook = sys.argv[2] if sys.argv[2] != '--color=never' else None\n"
            "if hook in (None, 'format'):\n"
            "    path = Path('src/app.py')\n"
            "    path.write_text('# heading\\n' + path.read_text())\n"
            "    print('Format........................Failed')\n"
            "    print('- hook id: format')\n"
            "if hook in (None, 'lint'):\n"
            "    print('Lint........................Failed')\n"
            "    print('- hook id: lint')\n"
            "    for number, line in enumerate(Path('src/app.py').read_text().splitlines(), 1):\n"
            "        if line.startswith(('new', 'tail')):\n"
            "            print(f'src/app.py:{number}: problem')\n"
            "sys.exit(1)\n"
        )
        self.assertEqual(1, result.returncode)
        self.assertEqual([2], [item["line"] for item in report["findings"]])
        self.assertEqual(1, report["dropped_unchanged_findings"])

    def test_rewrite_uses_reviewed_line_after_earlier_deletion(self) -> None:
        result, report = self.run_hook(
            "Path('src/app.py').write_text('new  = 2\\ntail = 3\\n')\n"
            "print('Format........................Failed')\n"
            "print('- hook id: format')\n"
            "sys.exit(1)\n"
        )
        self.assertEqual(1, result.returncode)
        self.assertEqual([2], [item["line"] for item in report["formatter_rewrites"]])
        self.assertEqual(0, report["dropped_unchanged_rewrites"])

    def test_renamed_file_keeps_only_edited_lines(self) -> None:
        run_git(self.repo, 'mv', 'src/app.py', 'src/renamed.py')
        run_git(self.repo, 'commit', '-qm', 'rename')
        result, report = self.run_hook(
            "print('Check........................Failed')\n"
            "print('- hook id: check')\n"
            "print('src/renamed.py:2: changed')\n"
            "print('src/renamed.py:3: old')\n"
            "sys.exit(1)\n"
        )
        self.assertEqual(1, result.returncode)
        self.assertEqual([2], [item["line"] for item in report["findings"]])
        self.assertEqual(1, report["dropped_unchanged_findings"])

    def test_pure_deletion_and_replacement_lines(self) -> None:
        path = self.repo / 'src/app.py'
        path.write_text('keep = 1\nnew = 2\n')
        run_git(self.repo, 'add', '.')
        run_git(self.repo, 'commit', '-qm', 'delete tail')
        result, report = self.run_hook(K_HOOK_WITH_FINDINGS.split('\n', 1)[1])
        self.assertEqual(1, result.returncode)
        self.assertEqual([2], [item["line"] for item in report["findings"]])
        path.write_text('keep = 1\nold = 2\n')
        run_git(self.repo, 'add', '.')
        run_git(self.repo, 'commit', '-qm', 'only deletion from base')
        result, report = self.run_hook('raise RuntimeError("hooks should not run")\n')
        self.assertEqual(0, result.returncode)
        self.assertEqual([], report['findings'])

    def test_line_ending_rewrite_changed_and_unchanged(self) -> None:
        for line, expected in ((2, 1), (3, 0)):
            with self.subTest(line=line):
                result, report = self.run_hook(
                    "path = Path('src/app.py')\n"
                    "lines = path.read_bytes().splitlines(keepends=True)\n"
                    f"lines[{line - 1}] = lines[{line - 1}].replace(b'\\n', b'\\r\\n')\n"
                    "path.write_bytes(b''.join(lines))\n"
                    "print('Format........................Failed')\n"
                    "print('- hook id: format')\n"
                    "sys.exit(1)\n"
                )
                self.assertEqual(expected, result.returncode)
                self.assertEqual(expected, len(report['formatter_rewrites']))
                self.assertEqual(1 - expected, report['dropped_unchanged_rewrites'])

    def test_config_comes_from_reviewed_commit(self) -> None:
        config = self.repo / '.pre-commit-config.yaml'
        config.unlink()
        result, report = self.run_hook("print('Check........................Passed')\n")
        self.assertEqual(0, result.returncode)
        run_git(self.repo, 'add', '.')
        run_git(self.repo, 'commit', '-qm', 'remove config')
        config.write_text(K_PRE_COMMIT_CONFIG)
        result, report = self.run_hook("print('Check........................Passed')\n")
        self.assertEqual(2, result.returncode)
        self.assertIn('configuration', report['reason'])

    def test_cleanup_failures_preserve_report_and_exit_code(self) -> None:
        spec = spec_from_file_location('changed_hooks', K_SCRIPT)
        module = module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        for cleanup in ('remove', 'prune', None):
            with self.subTest(cleanup=cleanup):
                original = module.run_git

                def git(repo, *args):
                    if args[:2] == ('worktree', cleanup) or (
                        cleanup == 'prune' and args[:2] == ('worktree', 'remove')
                    ):
                        raise module.CouldNotRun(f'{cleanup} failed')
                    return original(repo, *args)

                install_fake_pre_commit(self.root, K_HOOK_WITH_FINDINGS)
                env = {'PATH': str(self.root / 'bin') + os.pathsep + os.environ['PATH']}
                argv = [str(K_SCRIPT), '--repo', str(self.repo), self.base]
                with (
                    patch.dict(os.environ, env),
                    patch.object(module, 'run_git', side_effect=git),
                    patch.object(sys, 'argv', argv),
                    patch.object(module, 'emit') as emit,
                ):
                    code = module.main()
                report = emit.call_args.args[0]
                self.assertEqual(1, code)
                self.assertEqual('findings', report['status'])
                self.assertEqual(bool(cleanup), bool(report.get('cleanup_error')))


    def test_stylish_header_resets_for_unchanged_file(self) -> None:
        for second_line in (2, 3):
            with self.subTest(second_line=second_line):
                result, report = self.run_hook(
                    "print('ESLint........................Failed')\n"
                    "print('- hook id: eslint')\n"
                    "print('src/app.py')\n"
                    "print('  3:1  warning  old problem')\n"
                    "print('src/other.py')\n"
                    f"print('  {second_line}:1  error  other problem')\n"
                    "sys.exit(1)\n"
                )
                self.assertEqual(0, result.returncode)
                self.assertEqual([], report['findings'])
                self.assertEqual(2, report['dropped_unchanged_findings'])

    def test_git_environment_cannot_touch_user_checkout(self) -> None:
        binary = install_fake_pre_commit(
            self.root,
            f"#!{sys.executable}\nimport sys\n"
            "hook = sys.argv[2] if sys.argv[2] != '--color=never' else None\n"
            "for name in ('first', 'second') if hook is None else (hook,):\n"
            "    print(f'{name}........................Passed')\n"
            "    print(f'- hook id: {name}')\n",
        )
        app = self.repo / 'src/app.py'
        for overrides in ({'GIT_DIR': str(self.repo / '.git'),
                           'GIT_WORK_TREE': str(self.repo),
                           'GIT_INDEX_FILE': str(self.repo / '.git/index')}, {}):
            with self.subTest(overrides=bool(overrides)):
                app.write_text('precious dirty work\n')
                result = run_reporter(self.repo, self.base, [str(binary)], overrides=overrides)
                self.assertEqual('precious dirty work\n', app.read_text())
                self.assertEqual(0, result.returncode, result.stdout)

    def test_ruff_full_locations_and_unresolved_paths(self) -> None:
        for path, line, expected in (('src/app.py', 2, 1), ('src/app.py', 3, 0),
                                     ('missing.py', 2, 2)):
            with self.subTest(path=path, line=line):
                result, report = self.run_hook(
                    "print('Ruff........................Failed')\n"
                    "print('- hook id: ruff')\n"
                    f"print('  --> {path}:{line}:8')\n"
                    "sys.exit(1)\n"
                )
                self.assertEqual(expected, result.returncode)
                if expected == 2:
                    self.assertEqual('could-not-run', report['status'])
                    self.assertEqual(self.base, report['base'])
                    self.assertEqual(self.base, report['merge_base'])
                else:
                    self.assertEqual(1 - expected, report['dropped_unchanged_findings'])

    def test_range_uses_merge_base_when_base_advanced(self) -> None:
        head = run_git(self.repo, 'rev-parse', 'HEAD').strip()
        run_git(self.repo, 'checkout', '-qb', 'advanced-base', self.base)
        (self.repo / 'src/app.py').write_text('keep = 1\nold = 2\nbase_tail = 4\n')
        run_git(self.repo, 'commit', '-qam', 'advance base')
        advanced = run_git(self.repo, 'rev-parse', 'HEAD').strip()
        run_git(self.repo, 'checkout', '-q', '--detach', head)
        self.base, branch_point = advanced, self.base
        result, report = self.run_hook(K_HOOK_WITH_FINDINGS.split('\n', 1)[1])
        self.assertEqual(1, result.returncode)
        self.assertEqual([2], [item['line'] for item in report['findings']])
        self.assertEqual(advanced, report['base'])
        self.assertEqual(branch_point, report['merge_base'])

    def test_duplicate_hook_ids_run_once_with_multiple_summaries(self) -> None:
        for count in (2, 1):
            with self.subTest(count=count):
                (self.root / 'bin' / 'invocations').unlink(missing_ok=True)
                result, report = self.run_hook(
                    "marker = Path(__file__).with_name('invocations')\n"
                    "if sys.argv[2] != '--color=never':\n"
                    "    if marker.exists():\n"
                    "        raise RuntimeError('hook ran twice')\n"
                    "    marker.write_text('ran')\n"
                    f"for index in range({count}):\n"
                    "    print(f'Check {index}........................Passed')\n"
                    "    print('- hook id: check')\n"
                )
                self.assertEqual(0, result.returncode, report)
                self.assertEqual(count, len(report['hooks']))

    def test_signals_still_emit_json_and_remove_worktree(self) -> None:
        for number in (SIGTERM, SIGINT, None):
            with self.subTest(signal=number):
                body = "print('Check........................Passed')\n"
                if number is not None:
                    body += f"import os\nos.kill(os.getppid(), {int(number)})\n"
                result, report = self.run_hook(body)
                self.assertEqual(2 if number is not None else 0, result.returncode)
                self.assertEqual('could-not-run' if number is not None else 'clean', report['status'])
                self.assertTrue(report['worktree_removed'])
                self.assert_checkout_untouched()

    def test_empty_success_is_not_applicable(self) -> None:
        for body, status in (("print('No hooks apply')\n", 'not applicable'),
                             ("print('Check........................Passed')\n", 'clean')):
            with self.subTest(status=status):
                result, report = self.run_hook(body)
                self.assertEqual(0, result.returncode)
                self.assertEqual(status, report['status'])
                if status == 'not applicable':
                    self.assertTrue(report['reason'])

    def test_non_utf8_path_is_reported_without_traceback(self) -> None:
        for name in ('odd-\udcff.py', 'ordinary.py'):
            with self.subTest(name=name):
                path = self.repo / name
                path.write_text('new\n')
                run_git(self.repo, 'add', '--', name)
                run_git(self.repo, 'commit', '-qm', 'add path')
                result, report = self.run_hook(
                    "import os\n"
                    "print('Check........................Failed', flush=True)\n"
                    "print('- hook id: check', flush=True)\n"
                    f"os.write(1, os.fsencode({name!r} + ':1: problem\\n'))\n"
                    "sys.exit(1)\n"
                )
                self.assertEqual(1, result.returncode, result.stderr)
                self.assertEqual(name, report['findings'][0]['path'])

    def test_unexpected_exception_exits_two_with_cleanup(self) -> None:
        spec = spec_from_file_location('changed_hooks', K_SCRIPT)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        for error in (ValueError('unexpected'), None):
            with self.subTest(error=error):
                argv = [str(K_SCRIPT), '--repo', str(self.repo), self.base]
                with (
                    patch.object(sys, 'argv', argv),
                    patch.object(module, 'inspect_hooks', side_effect=error,
                                 return_value={'status': 'clean'}),
                    patch.object(module, 'emit') as emit,
                ):
                    code = module.main()
                report = emit.call_args.args[0]
                self.assertEqual(2 if error else 0, code)
                self.assertTrue(report['worktree_removed'])

    def test_successful_cleanup_does_not_prune(self) -> None:
        spec = spec_from_file_location('changed_hooks', K_SCRIPT)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        for failed in (False, True):
            with self.subTest(failed=failed):
                original = module.run_git
                calls = []

                def git(repo, *args):
                    calls.append(args[:2])
                    if failed and args[:2] == ('worktree', 'remove'):
                        raise module.CouldNotRun('remove failed')
                    return original(repo, *args)

                argv = [str(K_SCRIPT), '--repo', str(self.repo), self.base]
                with (
                    patch.object(sys, 'argv', argv),
                    patch.object(module, 'run_git', side_effect=git),
                    patch.object(module, 'inspect_hooks', return_value={'status': 'clean'}),
                    patch.object(module, 'emit') as emit,
                ):
                    code = module.main()
                report = emit.call_args.args[0]
                self.assertEqual(2 if failed else 0, code)
                self.assertEqual(failed, ('worktree', 'prune') in calls)
                self.assertEqual(failed, report['worktree_prune_ran'])


    def test_unexpected_cleanup_error_exits_two(self) -> None:
        spec = spec_from_file_location('changed_hooks', K_SCRIPT)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        for error in (RuntimeError('unexpected cleanup error'), None):
            with self.subTest(error=error):
                original = module.remove_worktree

                def remove(repo, directory, report):
                    original(repo, directory, report)
                    if error:
                        raise error

                argv = [str(K_SCRIPT), '--repo', str(self.repo), self.base]
                with (
                    patch.object(sys, 'argv', argv),
                    patch.object(module, 'remove_worktree', side_effect=remove),
                    patch.object(module, 'inspect_hooks', return_value={
                        'status': 'findings', 'findings': [{'line': 2}],
                    }),
                    patch.object(module, 'emit') as emit,
                ):
                    code = module.main()
                report = emit.call_args.args[0]
                self.assertEqual(2 if error else 1, code)
                self.assertEqual([{'line': 2}], report['findings'])
                self.assertTrue(report['worktree_removed'])


if __name__ == "__main__":
    unittest.main()
