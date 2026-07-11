#!/usr/bin/env python3
"""Mechanical validation for a wayfinder-driven OpenSpec change."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.S)
FIELD = re.compile(r"^([a-z_]+):\s*(.*)$")
CHECKBOX = re.compile(r"^- \[[ xX]\] (C-\d{2})\b", re.M)


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text()
    match = FRONT.match(text)
    if not match:
        raise ValueError("missing YAML frontmatter")
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        field = FIELD.match(line)
        if field:
            result[field.group(1)] = field.group(2).strip()
    return result


def list_value(raw: str) -> list[str]:
    raw = raw.strip()
    if raw == "[]":
        return []
    return [item.strip().strip("'\"") for item in raw.strip("[]").split(",") if item.strip()]


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for required in ("proposal.md", "trd.md", "tasks.md", "specs", "tickets", "tasks"):
        if not (root / required).exists():
            errors.append(f"missing {required}")

    ticket_ids: dict[str, Path] = {}
    blocking_unresolved: list[str] = []
    if not (root / "tickets/index.md").exists():
        errors.append("missing tickets/index.md status ledger")
    ticket_dependencies: dict[str, list[str]] = {}
    for path in sorted((root / "tickets").glob("D-*.md")) if (root / "tickets").exists() else []:
        try:
            meta = frontmatter(path)
        except ValueError as exc:
            errors.append(f"{path.name}: {exc}")
            continue
        ticket_id = meta.get("id", "")
        if not re.fullmatch(r"D-\d{3}", ticket_id) or not path.name.startswith(ticket_id + "-"):
            errors.append(f"{path.name}: invalid or mismatched ticket id")
        if ticket_id in ticket_ids:
            errors.append(f"duplicate ticket id {ticket_id}")
        ticket_ids[ticket_id] = path
        ticket_dependencies[ticket_id] = list_value(meta.get("depends_on", "[]"))
        status = meta.get("status")
        if status not in {"OPEN", "CLAIMED", "CLOSED", "DEFERRED"}:
            errors.append(f"{path.name}: invalid status {status}")
        if meta.get("blocking") == "true" and status not in {"CLOSED", "DEFERRED"}:
            blocking_unresolved.append(ticket_id)
        body = path.read_text()
        if status == "CLOSED":
            if meta.get("integrated") != "true":
                errors.append(f"{path.name}: closed ticket is not integrated")
            for heading in ("## Decision", "## Consequences"):
                if not re.search(re.escape(heading) + r"\n\n\S", body):
                    errors.append(f"{path.name}: closed ticket lacks {heading[3:].lower()}")
        if status == "DEFERRED" and meta.get("blocking") == "true":
            errors.append(f"{path.name}: deferred ticket cannot remain blocking")
        if status == "DEFERRED" and not re.search(r"## Deferred rationale\n\n\S", body):
            errors.append(f"{path.name}: deferred ticket lacks rationale")

    for ticket_id, path in ticket_ids.items():
        try:
            deps = list_value(frontmatter(path).get("depends_on", "[]"))
        except ValueError:
            continue
        for dep in deps:
            if dep not in ticket_ids:
                errors.append(f"{path.name}: unknown dependency {dep}")

    def detect_cycle(graph: dict[str, list[str]], label: str) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()
        def visit(node: str) -> None:
            if node in visiting:
                errors.append(f"{label} dependency cycle at {node}")
                return
            if node in visited:
                return
            visiting.add(node)
            for dep in graph.get(node, []):
                if dep in graph:
                    visit(dep)
            visiting.remove(node)
            visited.add(node)
        for node in graph:
            visit(node)
    detect_cycle(ticket_dependencies, "ticket")

    if blocking_unresolved:
        errors.append("unresolved blocking tickets: " + ", ".join(blocking_unresolved))

    trd = (root / "trd.md").read_text() if (root / "trd.md").exists() else ""
    for ticket_id, path in ticket_ids.items():
        try:
            meta = frontmatter(path)
        except ValueError:
            continue
        if meta.get("integrated") == "true" and ticket_id not in trd:
            errors.append(f"trd.md: missing integrated decision {ticket_id}")

    cycle_ids: dict[str, Path] = {}
    cycle_dependencies: dict[str, list[str]] = {}
    for path in sorted((root / "tasks").glob("C-*.md")) if (root / "tasks").exists() else []:
        if CHECKBOX.search(path.read_text()):
            errors.append(f"{path.name}: checkboxes belong only in tasks.md")
        try:
            meta = frontmatter(path)
        except ValueError as exc:
            errors.append(f"{path.name}: {exc}")
            continue
        cycle_id = meta.get("id", "")
        if not re.fullmatch(r"C-\d{2}", cycle_id) or not path.name.startswith(cycle_id + "-"):
            errors.append(f"{path.name}: invalid or mismatched cycle id")
        if cycle_id in cycle_ids:
            errors.append(f"duplicate cycle id {cycle_id}")
        cycle_ids[cycle_id] = path
        cycle_dependencies[cycle_id] = list_value(meta.get("depends_on", "[]"))
        for heading in ("## Outcome", "## Scope", "## Procedure", "## Tests and verification", "## Rollback", "## Stop conditions"):
            if not re.search(re.escape(heading) + r"\n\n\S", path.read_text()):
                errors.append(f"{path.name}: missing or empty {heading}")

    for cycle_id, deps in cycle_dependencies.items():
        for dep in deps:
            if dep not in cycle_ids:
                errors.append(f"{cycle_ids[cycle_id].name}: unknown dependency {dep}")
    detect_cycle(cycle_dependencies, "cycle")

    manifest = (root / "tasks.md").read_text() if (root / "tasks.md").exists() else ""
    manifest_ids = CHECKBOX.findall(manifest)
    if len(manifest_ids) != len(set(manifest_ids)):
        errors.append("tasks.md: duplicate cycle checkbox")
    for cycle_id in cycle_ids:
        if cycle_id not in manifest_ids:
            errors.append(f"tasks.md: missing cycle {cycle_id}")
    for cycle_id in manifest_ids:
        if cycle_id not in cycle_ids:
            errors.append(f"tasks.md: unknown cycle {cycle_id}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("change_dir", type=Path)
    args = parser.parse_args()
    errors = validate(args.change_dir.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Valid wayfinder-driven change: {args.change_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
