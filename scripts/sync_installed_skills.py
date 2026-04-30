#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import filecmp
import json
from pathlib import Path
import shutil
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS_ROOT = Path.home() / ".agents" / "skills"
CLAUDE_ROOT = Path.home() / ".claude" / "skills"
SYSTEM_ROOT = Path.home() / ".codex" / "skills" / ".system"
LOCAL_SYNC_ROOT = REPO_ROOT / "external" / "local-sync"
BACKUP_ROOT = REPO_ROOT.parent / "Nezikk-s-skills-entry-backups"


@dataclass(frozen=True)
class SeenSkill:
    name: str
    entry_root: Path
    real_path: Path


@dataclass(frozen=True)
class CanonicalSkill:
    name: str
    target_path: Path
    source_path: Path
    source_kind: str


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def read_skill_name(skill_dir: Path) -> str:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines()[:20]:
        if line.startswith("name:"):
            value = line.split(":", 1)[1].strip().strip("\"'")
            if value:
                return value
    return skill_dir.name


def repo_skills() -> dict[str, Path]:
    skills: dict[str, Path] = {}
    for skill_md in REPO_ROOT.rglob("SKILL.md"):
        if ".git" in skill_md.parts:
            continue
        if is_relative_to(skill_md, REPO_ROOT / "external"):
            continue
        if is_relative_to(skill_md, REPO_ROOT / ".worktrees"):
            continue
        skill_dir = skill_md.parent
        skills[read_skill_name(skill_dir)] = skill_dir
    return skills


def iter_installed(root: Path) -> list[SeenSkill]:
    if not root.exists():
        return []

    seen: list[SeenSkill] = []
    for entry in sorted(root.iterdir()):
        if entry.name.startswith("."):
            continue
        if not (entry.is_dir() or entry.is_symlink()):
            continue
        if not (entry / "SKILL.md").exists():
            continue
        real_path = entry.resolve()
        if SYSTEM_ROOT.exists() and is_relative_to(real_path, SYSTEM_ROOT.resolve()):
            continue
        seen.append(SeenSkill(entry.name, root, real_path))
    return seen


def same_tree(a: Path, b: Path) -> bool:
    comparison = filecmp.dircmp(a, b, ignore=[".git", "__pycache__", ".DS_Store"])
    if comparison.left_only or comparison.right_only or comparison.diff_files or comparison.funny_files:
        return False
    return all(same_tree(Path(comparison.left) / sub, Path(comparison.right) / sub) for sub in comparison.common_dirs)


def copy_skill_tree(source: Path, target: Path, replace: bool) -> None:
    if source.resolve() == target.resolve():
        return
    if target.exists():
        if not replace:
            return
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source,
        target,
        symlinks=True,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".DS_Store"),
    )


def write_local_source(target: Path, source: Path, seen_roots: list[Path], source_kind: str) -> None:
    imported_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    roots = ", ".join(str(path) for path in seen_roots)
    (target / "SOURCE.md").write_text(
        "\n".join(
            [
                "# Source",
                "",
                "Original repository: local installed skill",
                f"Original path: {source}",
                f"Seen in: {roots}",
                f"Imported at: {imported_at}",
                "Imported commit: unknown",
                "License: unknown",
                f"Local source kind: {source_kind}",
                "Local changes: preserved from installed copy",
                "Notes: Imported from existing local Claude/Codex skill directories.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def choose_canonical(name: str, installed: list[SeenSkill], own_skills: dict[str, Path]) -> CanonicalSkill:
    if name in own_skills:
        return CanonicalSkill(name, own_skills[name], own_skills[name], "repo-owned")

    agents = [item for item in installed if item.entry_root == AGENTS_ROOT]
    claude = [item for item in installed if item.entry_root == CLAUDE_ROOT]
    chosen = (agents or claude or installed)[0]
    return CanonicalSkill(name, LOCAL_SYNC_ROOT / name, chosen.real_path, "local-installed")


def planned_sync() -> tuple[dict[str, CanonicalSkill], dict[str, list[SeenSkill]], dict[str, Path]]:
    own = repo_skills()
    installed_by_name: dict[str, list[SeenSkill]] = {}
    for item in iter_installed(AGENTS_ROOT) + iter_installed(CLAUDE_ROOT):
        installed_by_name.setdefault(item.name, []).append(item)

    names = set(own) | set(installed_by_name)
    canonical = {
        name: choose_canonical(name, installed_by_name.get(name, []), own)
        for name in sorted(names)
    }
    return canonical, installed_by_name, own


def backup_entry(entry: Path, backup_dir: Path, label: str) -> dict[str, str]:
    record = {"entry": str(entry), "kind": "missing", "backup": ""}
    if not entry.exists() and not entry.is_symlink():
        return record

    destination = backup_dir / label / entry.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    if entry.is_symlink():
        record["kind"] = "symlink"
        record["target"] = str(entry.readlink())
        return record

    record["kind"] = "directory"
    record["backup"] = str(destination)
    shutil.copytree(entry, destination, symlinks=True)
    return record


def replace_with_link(entry: Path, target: Path) -> None:
    if entry.is_symlink() and entry.resolve() == target.resolve():
        return
    if entry.is_symlink():
        entry.unlink()
    elif entry.exists():
        shutil.rmtree(entry)
    entry.parent.mkdir(parents=True, exist_ok=True)
    entry.symlink_to(target)


def apply_sync() -> Path:
    canonical, installed_by_name, _own = planned_sync()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = BACKUP_ROOT / timestamp
    manifest: dict[str, object] = {
        "created_at": timestamp,
        "repo_root": str(REPO_ROOT),
        "entries": [],
    }

    for name, item in canonical.items():
        if item.source_kind == "local-installed":
            seen_roots = [seen.entry_root for seen in installed_by_name.get(name, []) if seen.real_path == item.source_path]
            copy_skill_tree(item.source_path, item.target_path, replace=True)
            write_local_source(item.target_path, item.source_path, seen_roots, item.source_kind)

        variant_index = 1
        for seen in installed_by_name.get(name, []):
            if seen.real_path == item.source_path:
                continue
            variant_target = LOCAL_SYNC_ROOT / "_variants" / name / f"{variant_index}-{seen.entry_root.name}"
            copy_skill_tree(seen.real_path, variant_target, replace=True)
            write_local_source(variant_target, seen.real_path, [seen.entry_root], "local-installed-variant")
            variant_index += 1

        for root, label in [(AGENTS_ROOT, "agents"), (CLAUDE_ROOT, "claude")]:
            entry = root / name
            before = backup_entry(entry, backup_dir, label)
            replace_with_link(entry, item.target_path)
            manifest["entries"].append(
                {
                    "skill": name,
                    "root": str(root),
                    "target": str(item.target_path),
                    "before": before,
                }
            )

    backup_dir.mkdir(parents=True, exist_ok=True)
    (backup_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return backup_dir


def print_plan() -> None:
    canonical, installed_by_name, own = planned_sync()
    print(f"Repository skills: {len(own)}")
    print(f"Installed skill names: {len(installed_by_name)}")
    print(f"Canonical skill names after sync: {len(canonical)}")
    print()
    for name, item in canonical.items():
        print(f"{name}: {item.source_kind}")
        print(f"  source: {item.source_path}")
        print(f"  target: {item.target_path}")
        variants = {seen.real_path for seen in installed_by_name.get(name, []) if seen.real_path != item.source_path}
        if variants:
            print("  variants preserved:")
            for variant in sorted(variants):
                print(f"    {variant}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Sync installed Claude/Codex skills into this repository.")
    parser.add_argument("--apply", action="store_true", help="perform the sync; default is dry-run")
    args = parser.parse_args(argv)

    if not args.apply:
        print_plan()
        print()
        print("Dry run only. Re-run with --apply to copy skills and replace entries with symlinks.")
        return 0

    backup_dir = apply_sync()
    print(f"Sync complete. Backup: {backup_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
