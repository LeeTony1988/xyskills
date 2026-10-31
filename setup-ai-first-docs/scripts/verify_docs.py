#!/usr/bin/env python3
"""Verify an AI-first documentation system.

Checks the structural invariants that can be checked mechanically. It does not
judge whether the facts are correct; use the manual checklist in SKILL.md for that.

Usage:
    python verify_docs.py <project-root> [--strict]

Exit codes: 0 = no errors, 1 = errors (or warnings with --strict), 2 = usage error.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

STATUSES = {"planned", "in-progress", "done", "archived"}
ROADMAP_STATUSES = {"in-progress", "done", "archived"}

REQUIRED_FILES = [
    "AGENTS.md",
    "docs/README.md",
    "docs/HLD.md",
    "docs/spec.md",
    "docs/roadmap.md",
    "docs/features/status.md",
]

REQUIRED_TEMPLATES = [
    "AGENTS.md",
    "docs-README.md",
    "HLD.md",
    "spec.md",
    "roadmap.md",
    "features-status.md",
    "plan.md",
    "feature-spec.md",
]

REQUIRED_HEADINGS = {
    "docs/README.md": ["目录地图", "唯一事实源", ".scratch"],
    "docs/HLD.md": ["模块划分", "关键流程", "数据架构"],
    "docs/roadmap.md": ["演进账本"],
}

SPEC_SECTIONS = [
    "## Objective",
    "## Tech Stack",
    "## Project Structure",
    "## Commands",
    "## Code Style",
    "## Testing Strategy",
    "## Boundaries",
    "## Success Criteria",
    "## Open Questions",
]

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
GITIGNORE_PATTERNS = {
    ".scratch/",
    "**/.scratch/",
    "docs/features/*/.scratch/",
    "docs/features/**/.scratch/",
}


class Report:
    def __init__(self, root: Path, strict: bool = False) -> None:
        self.root = root
        self.strict = strict
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def ok(self, message: str) -> None:
        print(f"  ok  {message}")

    def summary(self) -> int:
        print()
        for warning in self.warnings:
            print(f"  WARN  {warning}")
        for error in self.errors:
            print(f"  ERROR {error}")
        print(f"\n{len(self.errors)} error(s), {len(self.warnings)} warning(s)")
        if self.errors:
            return 1
        if self.strict and self.warnings:
            return 1
        return 0


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def strip_code(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", "", text)
    return text


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def find_table(text: str, must_contain: list[str]) -> tuple[list[str], list[list[str]]] | None:
    """Return (header, rows) for the first pipe table whose header has all keywords."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        header = split_row(stripped)
        if not all(any(key in cell for cell in header) for key in must_contain):
            continue
        rows: list[list[str]] = []
        cursor = index + 1
        if cursor < len(lines) and is_separator(split_row(lines[cursor])):
            cursor += 1
        while cursor < len(lines) and lines[cursor].strip().startswith("|"):
            cells = split_row(lines[cursor])
            if not is_separator(cells):
                rows.append(cells)
            cursor += 1
        return header, rows
    return None


def cell_text(cell: str) -> str:
    match = LINK_RE.search(cell)
    if match:
        return match.group(0).split("]")[0].lstrip("![").strip()
    return cell.strip()


def extract_links(text: str) -> list[str]:
    links = []
    for match in LINK_RE.finditer(strip_code(text)):
        target = match.group(1).strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        if " " in target:
            target = target.split(" ", 1)[0]
        target = target.split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        if "<" in target or ">" in target:
            continue
        links.append(target)
    return links


def check_links(report: Report, path: Path, allow_scratch: bool = False) -> None:
    text = read(path)
    relative = path.relative_to(report.root).as_posix()
    for target in extract_links(text):
        if ".scratch/" in target and not allow_scratch:
            report.error(f"{relative}: committed doc links into local scratch: {target}")
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(report.root)
        except ValueError:
            report.warn(f"{relative}: link escapes project root: {target}")
            continue
        if not resolved.exists():
            report.error(f"{relative}: broken link: {target}")


def check_placeholders(report: Report, path: Path) -> None:
    text = read(path)
    if "{{" in text:
        report.error(f"{path.relative_to(report.root).as_posix()}: unreplaced template placeholder '{{{{...}}}}'")


def check_required_files(report: Report) -> None:
    for relative in REQUIRED_FILES:
        if not (report.root / relative).is_file():
            report.error(f"missing required file: {relative}")
    for name in REQUIRED_TEMPLATES:
        relative = f"docs/templates/{name}"
        if not (report.root / relative).is_file():
            report.error(f"missing template: {relative}")


def check_required_headings(report: Report) -> None:
    for relative, keywords in REQUIRED_HEADINGS.items():
        path = report.root / relative
        if not path.is_file():
            continue
        text = read(path)
        for keyword in keywords:
            if keyword not in text:
                report.error(f"{relative}: missing required section keyword '{keyword}'")


def check_spec_sections(report: Report) -> None:
    path = report.root / "docs/spec.md"
    if not path.is_file():
        return
    headings = {line.strip() for line in read(path).splitlines() if line.startswith("## ")}
    for expected in SPEC_SECTIONS:
        if expected not in headings:
            report.error(f"docs/spec.md: missing exact section '{expected}'")


def check_agents(report: Report) -> None:
    path = report.root / "AGENTS.md"
    if not path.is_file():
        return
    text = read(path)
    lines = len(text.splitlines())
    if lines > 120:
        report.error(f"AGENTS.md: {lines} lines (hard limit 120); move facts to spec/HLD and rules to docs/README.md")
    elif lines > 80:
        report.warn(f"AGENTS.md: {lines} lines (target 40-80); move details to spec/HLD and docs/README.md")
    elif lines < 40:
        report.warn(f"AGENTS.md: {lines} lines (target 40-80); add project identity, file index and boundaries")
    for pointer in [
        "docs/README.md",
        "docs/spec.md",
        "docs/HLD.md",
        "docs/roadmap.md",
        "docs/features/status.md",
    ]:
        if pointer not in text:
            report.error(f"AGENTS.md: missing pointer to {pointer}")


def check_placeholder_scan(report: Report) -> None:
    paths = [report.root / "AGENTS.md"]
    docs = report.root / "docs"
    if docs.is_dir():
        for path in docs.rglob("*.md"):
            if "templates" in path.parts:
                continue
            paths.append(path)
    for path in paths:
        if path.is_file():
            check_placeholders(report, path)


def check_links_all(report: Report) -> None:
    paths = [report.root / "AGENTS.md"]
    docs = report.root / "docs"
    if docs.is_dir():
        for path in docs.rglob("*.md"):
            if "templates" in path.parts:
                continue
            paths.append(path)
    for path in paths:
        if path.is_file():
            check_links(report, path, allow_scratch=".scratch" in path.parts)


def check_gitignore(report: Report) -> None:
    path = report.root / ".gitignore"
    if not path.is_file():
        report.error(".gitignore: missing; add 'docs/features/*/.scratch/'")
        return
    lines = {line.strip() for line in read(path).splitlines()}
    if not (lines & GITIGNORE_PATTERNS):
        report.error(".gitignore: missing scratch rule 'docs/features/*/.scratch/'")
        return
    report.ok(".gitignore contains scratch rule")

    git_dir = report.root / ".git"
    if not git_dir.exists():
        return

    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=report.root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return
    tracked = [line for line in result.stdout.splitlines() if "/.scratch/" in line]
    if tracked:
        report.error(f"git: {len(tracked)} scratch file(s) are tracked, e.g. {tracked[0]}")

    probe = "docs/features/__probe__/.scratch/probe.md"
    check = subprocess.run(
        ["git", "check-ignore", "-q", "--no-index", probe],
        cwd=report.root,
        capture_output=True,
        text=True,
        check=False,
    )
    if check.returncode != 0:
        report.warn("git: check-ignore did not match a representative scratch path")


def check_roadmap(report: Report) -> dict[str, str]:
    """Return feature dir name -> status from roadmap."""
    path = report.root / "docs/roadmap.md"
    result: dict[str, str] = {}
    if not path.is_file():
        return result
    text = read(path)
    table = find_table(text, ["时间", "状态"])
    if table is None:
        report.error("docs/roadmap.md: no ledger table with columns 时间 / 状态")
        return result
    header, rows = table
    status_index = next(i for i, cell in enumerate(header) if "状态" in cell)
    time_index = next(i for i, cell in enumerate(header) if "时间" in cell)

    for row in rows:
        if len(row) != 4:
            report.error(f"docs/roadmap.md: expected 4 columns, got {len(row)}: {' | '.join(row)}")
            continue
        if not DATE_RE.match(row[time_index]):
            report.error(f"docs/roadmap.md: bad date '{row[time_index]}' (use YYYY-MM-DD)")
        status = row[status_index]
        if status not in ROADMAP_STATUSES:
            report.error(
                f"docs/roadmap.md: invalid status '{status}' "
                "(roadmap only records in-progress / done / archived; planned stays in features/status.md)"
            )
            continue
        links = extract_links(row[1] if len(row) > 1 else "")
        feature = None
        for link in links:
            match = re.search(r"features/(feature-[^/]+)/plan\.md$", link)
            if match:
                feature = match.group(1)
                break
        if feature is None:
            report.warn(f"docs/roadmap.md: row has no feature plan link: {' | '.join(row)}")
            continue
        if feature in result and result[feature] != status:
            report.warn(f"docs/roadmap.md: duplicate feature row with conflicting status: {feature}")
        result[feature] = status
    report.ok(f"roadmap: {len(rows)} row(s)")
    return result


def check_status(report: Report, roadmap_status: dict[str, str]) -> dict[str, str]:
    path = report.root / "docs/features/status.md"
    result: dict[str, str] = {}
    if not path.is_file():
        return result
    text = read(path)
    table = find_table(text, ["Feature", "状态"])
    if table is None:
        report.error("docs/features/status.md: no feature map table with columns Feature / 状态")
        return result
    header, rows = table
    if not any("plan" in cell.lower() for cell in header):
        report.error("docs/features/status.md: feature map is missing a plan column")
    status_index = next(i for i, cell in enumerate(header) if "状态" in cell)
    feature_index = next(i for i, cell in enumerate(header) if "Feature" in cell)

    features_dir = report.root / "docs/features"
    dirs = [
        item.name
        for item in features_dir.iterdir()
        if item.is_dir() and not item.name.startswith(".") and item.name not in {"archive", "_archive"}
    ] if features_dir.is_dir() else []

    for row in rows:
        if len(row) != len(header):
            report.error(f"docs/features/status.md: expected {len(header)} columns, got {len(row)}: {' | '.join(row)}")
            continue
        feature = cell_text(row[feature_index])
        status = row[status_index]
        if status not in STATUSES:
            report.error(f"docs/features/status.md: invalid status '{status}' for {feature}")
            continue
        result[feature] = status
        feature_dir = features_dir / feature
        if not feature_dir.is_dir():
            report.error(f"docs/features/status.md: feature directory does not exist: {feature}")

    for feature in dirs:
        if feature not in result:
            report.error(f"docs/features/status.md: missing feature directory from map: {feature}")

    for feature, status in result.items():
        roadmap = roadmap_status.get(feature)
        if roadmap is not None and roadmap != status:
            report.error(f"status mismatch for {feature}: roadmap={roadmap}, status={status}")

    if any(status == "in-progress" for status in result.values()) and "当前焦点：`Idle`" in text:
        report.warn("docs/features/status.md: says Idle but has in-progress features")
    if not result and "Idle" not in text:
        report.warn("docs/features/status.md: no features; mark current focus as Idle")
    report.ok(f"status: {len(result)} feature(s)")
    return result


def check_feature(report: Report, feature_dir: Path) -> None:
    name = feature_dir.name
    plan = feature_dir / "plan.md"
    if not plan.is_file():
        report.error(f"{name}: missing plan.md")
        return

    plan_text = read(plan)
    for keyword in ["核心接口", "关键机制", "数据对象", "验收标准"]:
        if keyword not in plan_text:
            report.error(f"{name}/plan.md: missing required section keyword '{keyword}'")
    if "```mermaid" not in plan_text:
        report.warn(f"{name}/plan.md: no Mermaid diagram; add a module dependency or flow diagram if it aids understanding")

    scratch = feature_dir / ".scratch"
    spec = scratch / f"{name}-spec.md"
    if not spec.is_file():
        report.warn(f"{name}: missing .scratch/{name}-spec.md (ok before plan approval)")
    else:
        spec_text = read(spec)
        for keyword in ["行为规格", "验收映射"]:
            if keyword not in spec_text:
                report.error(f"{name}/.scratch/{name}-spec.md: missing section keyword '{keyword}'")

    tickets_dir = scratch / "tickets"
    if not tickets_dir.is_dir():
        report.warn(f"{name}: missing .scratch/tickets/ (ok before ticket breakdown)")
        return

    ticket_files = sorted(path for path in tickets_dir.iterdir() if path.is_file())
    if not ticket_files:
        report.warn(f"{name}: no tickets yet (ok before ticket breakdown)")
        return
    if len(ticket_files) < 3:
        report.warn(
            f"{name}: only {len(ticket_files)} ticket file(s); "
            "each feature expects at least 3 separate tickets: acceptance, code commit, docs update"
        )
    report.ok(f"{name}: plan + {len(ticket_files)} ticket file(s)")


def check_features(report: Report) -> None:
    features_dir = report.root / "docs/features"
    if not features_dir.is_dir():
        report.error("missing directory: docs/features")
        return
    for feature_dir in sorted(features_dir.iterdir()):
        if not feature_dir.is_dir() or feature_dir.name.startswith("."):
            continue
        if feature_dir.name in {"archive", "_archive"}:
            for archived in sorted(feature_dir.iterdir()):
                if archived.is_dir() and not archived.name.startswith("."):
                    check_feature(report, archived)
            continue
        check_feature(report, feature_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify an AI-first documentation system.")
    parser.add_argument("root", nargs="?", default=".", help="project root (default: .)")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"error: project root is not a directory: {root}", file=sys.stderr)
        return 2

    report = Report(root, strict=args.strict)
    print(f"Verifying AI-first docs: {root}")

    print("\n[structure]")
    check_required_files(report)
    check_required_headings(report)
    check_spec_sections(report)
    check_agents(report)
    check_placeholder_scan(report)

    print("\n[links]")
    check_links_all(report)

    print("\n[scratch]")
    check_gitignore(report)

    print("\n[roadmap / status]")
    roadmap_status = check_roadmap(report)
    check_status(report, roadmap_status)

    print("\n[features]")
    check_features(report)

    return report.summary()


if __name__ == "__main__":
    raise SystemExit(main())
