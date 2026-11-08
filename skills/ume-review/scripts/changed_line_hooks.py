#!/usr/bin/env python3
"""Report pre-commit hook findings and formatter rewrites on changed lines.

The reporter builds a temporary worktree of the reviewed head, runs the
repository's pre-commit hooks there, and never modifies the user's checkout.
It prints one JSON object and exits 0 when clean, 1 when changed lines carry
hook findings or formatter rewrites, and 2 when the hooks could not run.
"""

from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
import tempfile
from json import dumps
from pathlib import Path
from shutil import rmtree

COLOR_CODES = re.compile(r"\x1b\[[0-9;]*m")
HOOK_HEADER = re.compile(r"^(?P<name>.+?)\.{2,}\s*(?P<result>Passed|Failed|Skipped)$")
HOOK_ID = re.compile(r"^- hook id:\s*(?P<identifier>\S+)\s*$")
FINDING = re.compile(
    r"^(?P<path>.+?):(?P<line>\d+)(?::(?P<column>\d+))?(?::\s*(?P<message>.*))?$"
)
HUNK = re.compile(rb"^@@ -\d+(?:,\d+)? \+(?P<start>\d+)(?:,(?P<count>\d+)?)? @@", re.MULTILINE)
STYLISH_FINDING = re.compile(r"^\s+(?P<line>\d+):\d+\s+(?:error|warning)\s+(?P<message>.+)$")
EXCERPT_LIMIT = 160


class CouldNotRun(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def run_git(repo: Path, *args: str) -> bytes:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (subprocess.CalledProcessError, OSError) as error:
        raise CouldNotRun(f"git {' '.join(args)} failed: {error}") from error
    return completed.stdout


def resolve_revision(repo: Path, revision: str) -> str:
    output = run_git(repo, "rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}")
    return output.decode().strip()


def changed_line_map(repo: Path, base: str, head: str) -> dict[str, set[int]]:
    listing = run_git(
        repo, "diff", "--find-renames", "--name-status", "--diff-filter=d", "-z", base, head
    )
    entries = iter(listing.split(b"\0"))
    changed: dict[str, set[int]] = {}
    for status in entries:
        if not status:
            continue
        original = next(entries).decode()
        path = next(entries).decode() if status.startswith(b"R") else original
        diff = run_git(
            repo,
            "diff",
            "--no-color",
            "--no-ext-diff",
            "--no-textconv",
            "--find-renames",
            "-U0",
            base,
            head,
            "--",
            original,
            path,
        )
        lines: set[int] = set()
        for hunk in HUNK.finditer(diff):
            first = int(hunk.group("start"))
            span = int(hunk.group("count") or 1)
            lines.update(range(first, first + span))
        if lines:
            changed[path] = lines
    return changed


def create_worktree(repo: Path, head: str, directory: Path) -> None:
    run_git(repo, "worktree", "add", "--detach", str(directory), head)


def remove_worktree(repo: Path, directory: Path) -> None:
    errors: list[str] = []
    try:
        run_git(repo, "worktree", "remove", "--force", str(directory))
    except CouldNotRun as error:
        errors.append(error.reason)
        rmtree(directory, ignore_errors=True)
    try:
        run_git(repo, "worktree", "prune")
    except CouldNotRun as error:
        errors.append(error.reason)
    if errors:
        raise CouldNotRun("; ".join(errors))


def snapshot_files(worktree: Path, changed: dict[str, set[int]]) -> dict[str, list[bytes]]:
    snapshots: dict[str, list[bytes]] = {}
    for path in changed:
        target = worktree / path
        if target.is_file():
            snapshots[path] = target.read_bytes().splitlines(keepends=True)
    return snapshots


def run_pre_commit(
    worktree: Path, changed: dict[str, set[int]], hook: str | None = None
) -> subprocess.CompletedProcess:
    command = ["pre-commit", "run"]
    if hook is not None:
        command.append(hook)
    command.extend(["--color=never", "--verbose", "--files", *sorted(changed)])
    try:
        return subprocess.run(
            command,
            cwd=worktree,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except OSError as error:
        raise CouldNotRun(f"cannot start pre-commit: {error}") from error


def parse_sections(output: str) -> list[dict]:
    sections: list[dict] = []
    current: dict | None = None
    for raw_line in COLOR_CODES.sub("", output).splitlines():
        header = HOOK_HEADER.match(raw_line)
        if header:
            current = {
                "name": header.group("name").strip(),
                "id": None,
                "result": header.group("result"),
            }
            sections.append(current)
            continue
        hook_id = HOOK_ID.match(raw_line)
        if hook_id and current is not None:
            current["id"] = hook_id.group("identifier")
    return sections


def diagnostic_path(raw: str, worktree: Path) -> str:
    path = Path(raw.strip().replace("\\", "/"))
    if not path.is_absolute():
        path = worktree / path
    try:
        return path.resolve().relative_to(worktree.resolve()).as_posix()
    except ValueError:
        return ""


def collect_findings(
    output: str, changed: dict[str, set[int]], worktree: Path
) -> tuple[list[dict], int]:
    kept: list[dict] = []
    dropped = 0
    current: dict = {}
    stylish_path = ""
    for raw_line in COLOR_CODES.sub("", output).splitlines():
        header = HOOK_HEADER.match(raw_line)
        if header:
            current = {"id": None, **header.groupdict()}
            stylish_path = ""
            continue
        hook_id = HOOK_ID.match(raw_line)
        if hook_id:
            current["id"] = hook_id.group("identifier")
            continue
        finding = FINDING.match(raw_line)
        if finding is not None:
            path = diagnostic_path(finding.group("path"), worktree)
        else:
            finding = STYLISH_FINDING.match(raw_line)
            path = stylish_path
        if finding is None:
            candidate = diagnostic_path(raw_line, worktree)
            if candidate in changed:
                stylish_path = candidate
            continue
        line = int(finding.group("line"))
        hook = current.get("id") or current.get("name") or "unknown"
        message = (finding.group("message") or "").strip()
        if line in changed.get(path, set()):
            kept.append({"path": path, "line": line, "hook": hook, "message": message})
        else:
            dropped += 1
    return kept, dropped


def excerpt(lines: list[bytes]) -> str:
    text = b"".join(lines).decode(errors="replace")
    return text.replace("\r", " ␍ ").replace("\n", " ⏎ ").strip()[:EXCERPT_LIMIT]


def collect_rewrites(
    worktree: Path, snapshots: dict[str, list[bytes]], changed: dict[str, set[int]]
) -> tuple[list[dict], int]:
    kept: list[dict] = []
    dropped = 0
    for relative, before in snapshots.items():
        current = worktree / relative
        if not current.is_file():
            continue
        after = current.read_bytes().splitlines(keepends=True)
        matcher = difflib.SequenceMatcher(None, before, after, autojunk=False)
        for tag, old_start, old_stop, new_start, new_stop in matcher.get_opcodes():
            if tag == "equal":
                continue
            old_lines = set(range(old_start + 1, old_stop + 1))
            if tag == "insert":
                old_lines = {old_start, old_start + 1}
            if not old_lines & changed[relative]:
                dropped += 1
                continue
            kept.append(
                {
                    "path": relative,
                    "line": min(old_lines & changed[relative]),
                    "before": excerpt(before[old_start:old_stop]),
                    "after": excerpt(after[new_start:new_stop]),
                }
            )
    return kept, dropped


def inspect_hooks(worktree: Path, changed: dict[str, set[int]], snapshots: dict) -> dict:
    completed = run_pre_commit(worktree, changed)
    sections = parse_sections(completed.stdout.decode(errors="replace"))
    if completed.returncode != 0 and not any(
        section["result"] == "Failed" for section in sections
    ):
        raise CouldNotRun(f"pre-commit exited {completed.returncode} without a failed hook")
    report = {
        "hooks": [],
        "findings": [],
        "formatter_rewrites": [],
        "dropped_unchanged_findings": 0,
        "dropped_unchanged_rewrites": 0,
    }
    for section in sections:
        if len(sections) > 1:
            if not section["id"]:
                raise CouldNotRun("cannot isolate hook without a hook id")
            run_git(worktree, "reset", "--hard", "HEAD")
            run_git(worktree, "clean", "-fdx")
            completed = run_pre_commit(worktree, changed, section["id"])
        output = completed.stdout.decode(errors="replace")
        results = parse_sections(output)
        if len(results) != 1:
            raise CouldNotRun("expected one isolated hook summary")
        result = results[0]
        findings, dropped_findings = collect_findings(output, changed, worktree)
        rewrites, dropped_rewrites = collect_rewrites(worktree, snapshots, changed)
        accounted = findings or rewrites or dropped_findings or dropped_rewrites
        if result["result"] == "Failed" and not accounted:
            hook = result["id"] or result["name"]
            raise CouldNotRun(f"hook {hook} failed without diagnostics or rewrites")
        if completed.returncode != 0 and result["result"] != "Failed":
            raise CouldNotRun(f"pre-commit exited {completed.returncode} without a failed hook")
        report["hooks"].append({"id": result["id"] or result["name"], "result": result["result"]})
        report["findings"].extend(findings)
        report["formatter_rewrites"].extend(rewrites)
        report["dropped_unchanged_findings"] += dropped_findings
        report["dropped_unchanged_rewrites"] += dropped_rewrites
    report["status"] = "findings" if report["findings"] or report["formatter_rewrites"] else "clean"
    return report


def emit(report: dict) -> None:
    print(dumps(report, indent=2, sort_keys=True))


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("base", help="base revision for the changed-line range")
    cli.add_argument("--repo", default=".", help="repository to inspect")
    args = cli.parse_args()

    worktree: Path | None = None
    repo: Path | None = None
    report: dict = {}
    exit_code = 0
    try:
        repo = Path(
            run_git(Path(args.repo).resolve(), "rev-parse", "--show-toplevel").decode().strip()
        )
        base = resolve_revision(repo, args.base)
        head = resolve_revision(repo, "HEAD")
        changed = changed_line_map(repo, base, head)
        worktree = Path(tempfile.mkdtemp(prefix="ume-changed-line-hooks-"))
        create_worktree(repo, head, worktree)
        if not (worktree / ".pre-commit-config.yaml").is_file():
            raise CouldNotRun("no pre-commit configuration at the reviewed head")
        report = {
            "status": "clean",
            "base": base,
            "head": head,
            "hooks": [],
            "findings": [],
            "formatter_rewrites": [],
            "dropped_unchanged_findings": 0,
            "dropped_unchanged_rewrites": 0,
        }
        if changed:
            snapshots = snapshot_files(worktree, changed)
            report.update(inspect_hooks(worktree, changed, snapshots))
        else:
            report["note"] = "no changed files in the range"
        exit_code = 1 if report["status"] == "findings" else 0
    except CouldNotRun as error:
        report = {
            "status": "could-not-run",
            "reason": error.reason,
            "findings": [],
            "formatter_rewrites": [],
        }
        exit_code = 2
    finally:
        if worktree is not None and repo is not None:
            try:
                remove_worktree(repo, worktree)
            except CouldNotRun as error:
                report["cleanup_error"] = error.reason
                if exit_code == 0:
                    exit_code = 2
                    report["status"] = "could-not-run"
                    report["reason"] = error.reason
        report["worktree_removed"] = worktree is None or not worktree.exists()
        emit(report)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
