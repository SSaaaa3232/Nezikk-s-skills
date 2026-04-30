#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/link-skill.sh <skill-dir-relative-to-repo> [skill-name]

Examples:
  ./scripts/link-skill.sh nskill
  ./scripts/link-skill.sh external/KKKKhazix/khazix-skills/neat-freak
  ./scripts/link-skill.sh external/vendor/repo/custom-folder custom-name

Creates symlinks in:
  ~/.agents/skills/<skill-name>
  ~/.claude/skills/<skill-name>
USAGE
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage
  exit 2
fi

skill_rel="${1%/}"
skill_dir="$repo_root/$skill_rel"

if [[ ! -d "$skill_dir" ]]; then
  echo "Skill directory not found: $skill_rel" >&2
  exit 1
fi

if [[ ! -f "$skill_dir/SKILL.md" ]]; then
  echo "SKILL.md not found in: $skill_rel" >&2
  exit 1
fi

target="$(cd "$skill_dir" && pwd -P)"
skill_name="${2:-$(basename "$target")}"

if [[ -z "$skill_name" || "$skill_name" == "." || "$skill_name" == ".." || "$skill_name" == */* ]]; then
  echo "Invalid skill name: $skill_name" >&2
  exit 1
fi

resolve_link_target() {
  local link_path="$1"
  local raw_target
  raw_target="$(readlink "$link_path")"

  if [[ "$raw_target" == /* ]]; then
    printf '%s\n' "$raw_target"
    return
  fi

  local link_dir
  link_dir="$(cd "$(dirname "$link_path")" && pwd -P)"
  local raw_dir
  raw_dir="$(dirname "$raw_target")"
  local raw_base
  raw_base="$(basename "$raw_target")"

  if [[ -d "$link_dir/$raw_dir" ]]; then
    printf '%s/%s\n' "$(cd "$link_dir/$raw_dir" && pwd -P)" "$raw_base"
  else
    printf '%s/%s\n' "$link_dir" "$raw_target"
  fi
}

link_one() {
  local label="$1"
  local skills_root="$2"
  local link_path="$skills_root/$skill_name"

  mkdir -p "$skills_root"

  if [[ -L "$link_path" ]]; then
    local existing
    existing="$(resolve_link_target "$link_path")"
    if [[ "$existing" == "$target" ]]; then
      echo "$label already linked: $link_path -> $target"
      return
    fi
    echo "$label link already exists and points elsewhere:" >&2
    echo "  $link_path -> $existing" >&2
    echo "Remove it manually before relinking." >&2
    exit 1
  fi

  if [[ -e "$link_path" ]]; then
    echo "$label path already exists and is not a symlink: $link_path" >&2
    echo "Move or remove it manually before linking." >&2
    exit 1
  fi

  ln -s "$target" "$link_path"
  echo "$label linked: $link_path -> $target"
}

link_one "Codex" "$HOME/.agents/skills"
link_one "Claude" "$HOME/.claude/skills"
