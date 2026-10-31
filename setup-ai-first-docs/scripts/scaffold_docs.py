#!/usr/bin/env python3
"""Scaffold an AI-first documentation system.

Creates only missing files; never overwrites existing project documents.
Also installs the reusable templates into docs/templates/ and ensures
docs/features/*/.scratch/ is ignored by Git.

Usage:
    python scaffold_docs.py <project-root> [--project-name NAME] [--owner NAME]
    python scaffold_docs.py <project-root> --feature <slug>
    python scaffold_docs.py <project-root> --refresh-templates
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_DIR / "assets" / "templates"

# main docs: template -> target
MAIN_DOCS = {
    "AGENTS.md.template": "AGENTS.md",
    "docs-README.md.template": "docs/README.md",
    "HLD.md.template": "docs/HLD.md",
    "spec.md.template": "docs/spec.md",
    "roadmap.md.template": "docs/roadmap.md",
    "features-status.md.template": "docs/features/status.md",
}

# reusable copies the project owns after setup: template -> docs/templates/<name>
PROJECT_TEMPLATES = {
    "AGENTS.md.template": "AGENTS.md",
    "docs-README.md.template": "docs-README.md",
    "HLD.md.template": "HLD.md",
    "spec.md.template": "spec.md",
    "roadmap.md.template": "roadmap.md",
    "features-status.md.template": "features-status.md",
    "feature-plan.md.template": "plan.md",
    "feature-spec.md.template": "feature-spec.md",
}

GITIGNORE_PATTERNS = {
    ".scratch/",
    "**/.scratch/",
    "docs/features/*/.scratch/",
    "docs/features/**/.scratch/",
}

SLUG_RE = re.compile(r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")


def read_template(name: str) -> str:
    path = TEMPLATES_DIR / name
    if not path.is_file():
        raise SystemExit(f"error: template not found: {path}")
    return path.read_text(encoding="utf-8")


def render(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def write_if_missing(path: Path, content: str, force: bool = False) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)
    return True


def ensure_gitignore(root: Path) -> str:
    path = root / ".gitignore"
    existing = ""
    if path.exists():
        existing = path.read_text(encoding="utf-8")

    lines = {line.strip() for line in existing.splitlines()}
    if lines & GITIGNORE_PATTERNS:
        return "present"

    block = (
        ("\n" if existing and not existing.endswith("\n") else "")
        + "# AI-first docs: local scratch workspace, never commit\n"
        + "docs/features/*/.scratch/\n"
    )
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(block)
    return "added"


def create_feature(root: Path, slug: str, values: dict[str, str]) -> list[Path]:
    feature_dir = root / "docs" / "features" / f"feature-{slug}"
    plan = feature_dir / "plan.md"
    spec = feature_dir / ".scratch" / f"feature-{slug}-spec.md"
    tickets = feature_dir / ".scratch" / "tickets"

    created: list[Path] = []
    feature_values = dict(values)
    feature_values["FEATURE_NAME"] = slug

    if write_if_missing(plan, render(read_template("feature-plan.md.template"), feature_values)):
        created.append(plan)
    if write_if_missing(spec, render(read_template("feature-spec.md.template"), feature_values)):
        created.append(spec)
    tickets.mkdir(parents=True, exist_ok=True)
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold AI-first project documentation.")
    parser.add_argument("root", nargs="?", default=".", help="project root (default: .)")
    parser.add_argument("--project-name", default=None, help="project name for {{PROJECT_NAME}}")
    parser.add_argument("--owner", default="项目维护者", help="default owner for {{OWNER}}")
    parser.add_argument("--feature", default=None, metavar="SLUG", help="also create feature-<slug> skeleton")
    parser.add_argument(
        "--refresh-templates",
        action="store_true",
        help="overwrite docs/templates/* with this skill's templates (project docs are untouched)",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"error: project root is not a directory: {root}", file=sys.stderr)
        return 2

    slug = None
    if args.feature:
        slug = args.feature[8:] if args.feature.startswith("feature-") else args.feature
    if slug is not None and not SLUG_RE.match(slug):
        print(
            "error: --feature must use letters, digits and hyphens; kebab-case is recommended; "
            "e.g. user-login or feature-user-login",
            file=sys.stderr,
        )
        return 2

    project_name = args.project_name or root.name
    values = {
        "PROJECT_NAME": project_name,
        "DATE": date.today().isoformat(),
        "OWNER": args.owner,
    }

    (root / "docs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "templates").mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    skipped: list[Path] = []

    for template_name, target in MAIN_DOCS.items():
        path = root / target
        if write_if_missing(path, render(read_template(template_name), values)):
            created.append(path)
        else:
            skipped.append(path)

    for template_name, target_name in PROJECT_TEMPLATES.items():
        path = root / "docs" / "templates" / target_name
        content = read_template(template_name)
        if write_if_missing(path, content, force=args.refresh_templates):
            created.append(path)
        else:
            skipped.append(path)

    gitignore_state = ensure_gitignore(root)

    feature_created: list[Path] = []
    if slug:
        feature_created = create_feature(root, slug, values)

    print(f"AI-first docs scaffold: {root}")
    if created:
        print("\ncreated:")
        for path in created:
            print(f"  + {path.relative_to(root)}")
    if feature_created:
        print("\nfeature skeleton:")
        for path in feature_created:
            print(f"  + {path.relative_to(root)}")
    if skipped:
        print("\nkept existing:")
        for path in skipped:
            print(f"  = {path.relative_to(root)}")
    print(f"\n.gitignore scratch rule: {gitignore_state}")

    print("\nnext:")
    print("  1. fill docs/spec.md, docs/HLD.md, docs/roadmap.md, docs/features/status.md")
    print("  2. fill docs/README.md, then AGENTS.md (pointers must exist first)")
    print("  3. run: python <skill-dir>/scripts/verify_docs.py <project-root>")
    if slug:
        print("  4. add the feature row to roadmap.md and features/status.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
