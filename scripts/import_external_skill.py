#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re
import shutil
import shlex
import subprocess
import sys
import tempfile
from urllib.parse import urlparse


@dataclass(frozen=True)
class ImportArgs:
    repo_url: str
    skill_name: str
    replace: bool
    no_link: bool


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def normalize_tokens(argv: list[str]) -> list[str]:
    if len(argv) == 1:
        return shlex.split(argv[0])
    return argv


def parse_import_args(argv: list[str]) -> ImportArgs:
    tokens = normalize_tokens(argv)
    if tokens[:3] == ["npx", "skills", "add"]:
        tokens = tokens[3:]

    parser = argparse.ArgumentParser(
        description="Import an external skill into this repository and link it to Claude/Codex."
    )
    parser.add_argument("repo_url")
    parser.add_argument("--skill", required=True, dest="skill_name")
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--no-link", action="store_true")
    parsed = parser.parse_args(tokens)

    return ImportArgs(
        repo_url=parsed.repo_url,
        skill_name=parsed.skill_name,
        replace=parsed.replace,
        no_link=parsed.no_link,
    )


def parse_github_repo(repo_url: str) -> tuple[str, str]:
    ssh_match = re.fullmatch(r"git@github\.com:([^/]+)/(.+?)(?:\.git)?", repo_url)
    if ssh_match:
        return ssh_match.group(1), ssh_match.group(2)

    parsed = urlparse(repo_url)
    if parsed.netloc != "github.com":
        raise ValueError(f"Only github.com repositories are supported: {repo_url}")

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise ValueError(f"GitHub URL must include owner and repo: {repo_url}")

    repo_name = parts[1]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]
    return parts[0], repo_name


def run(cmd: list[str], cwd: Path | None = None) -> str:
    completed = subprocess.run(
        cmd,
        cwd=cwd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def clone_repo(repo_url: str, destination: Path) -> None:
    run(["git", "clone", "--depth", "1", repo_url, str(destination)])


def current_commit(clone_dir: Path) -> str:
    return run(["git", "rev-parse", "HEAD"], cwd=clone_dir)


def detect_license(clone_dir: Path) -> str:
    for candidate in clone_dir.iterdir():
        if candidate.is_file() and candidate.name.lower().startswith("license"):
            return candidate.name
    return "unknown"


def find_skill_dir(clone_dir: Path, skill_name: str) -> Path:
    if (clone_dir / "SKILL.md").is_file():
        return clone_dir

    named = clone_dir / skill_name
    if (named / "SKILL.md").is_file():
        return named

    matches = sorted(path.parent for path in clone_dir.rglob("SKILL.md"))
    if not matches:
        raise FileNotFoundError(f"No SKILL.md found in cloned repository: {clone_dir}")

    for match in matches:
        if match.name == skill_name:
            return match

    raise FileNotFoundError(
        f"Could not find skill '{skill_name}'. Found: "
        + ", ".join(str(path.relative_to(clone_dir)) for path in matches)
    )


def write_source_metadata(
    source_path: Path,
    repo_url: str,
    owner: str,
    repo_name: str,
    commit: str,
    license_name: str,
    skill_name: str,
) -> None:
    imported_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    source_path.write_text(
        "\n".join(
            [
                "# Source",
                "",
                f"Original repository: {repo_url}",
                f"Owner: {owner}",
                f"Repository: {repo_name}",
                f"Imported at: {imported_at}",
                f"Imported commit: {commit}",
                f"License: {license_name}",
                f"Imported skill: {skill_name}",
                "Local changes: none",
                "Notes:",
                "",
            ]
        ),
        encoding="utf-8",
    )


def import_from_clone(
    clone_dir: Path,
    repo_root: Path,
    repo_url: str,
    owner: str,
    repo_name: str,
    skill_name: str,
    commit: str,
    replace: bool,
) -> Path:
    skill_dir = find_skill_dir(clone_dir, skill_name)
    external_repo_dir = repo_root / "external" / owner / repo_name
    target_dir = external_repo_dir / skill_name

    if target_dir.exists():
        if not replace:
            raise FileExistsError(
                f"Target already exists: {target_dir}. Re-run with --replace to overwrite it."
            )
        shutil.rmtree(target_dir)

    external_repo_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        skill_dir,
        target_dir,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".DS_Store"),
    )

    write_source_metadata(
        external_repo_dir / "SOURCE.md",
        repo_url=repo_url,
        owner=owner,
        repo_name=repo_name,
        commit=commit,
        license_name=detect_license(clone_dir),
        skill_name=skill_name,
    )
    return target_dir


def link_skill(imported_skill_dir: Path) -> None:
    root = repo_root()
    relative = imported_skill_dir.relative_to(root)
    run([str(root / "scripts" / "link-skill.sh"), str(relative)])


def main(argv: list[str]) -> int:
    args = parse_import_args(argv)
    owner, repo_name = parse_github_repo(args.repo_url)
    root = repo_root()

    with tempfile.TemporaryDirectory(prefix="skill-down-") as temp_dir:
        clone_dir = Path(temp_dir) / repo_name
        clone_repo(args.repo_url, clone_dir)
        commit = current_commit(clone_dir)
        imported = import_from_clone(
            clone_dir=clone_dir,
            repo_root=root,
            repo_url=args.repo_url,
            owner=owner,
            repo_name=repo_name,
            skill_name=args.skill_name,
            commit=commit,
            replace=args.replace,
        )

    if not args.no_link:
        link_skill(imported)

    print(f"Imported: {imported}")
    print(f"Source: {imported.parent / 'SOURCE.md'}")
    if args.no_link:
        print("Linking skipped because --no-link was set.")
    else:
        print("Linked to ~/.agents/skills and ~/.claude/skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
