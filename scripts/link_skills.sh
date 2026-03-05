#!/usr/bin/env bash
set -euo pipefail

# Link all skills in this repo into global agent skill folders.
# This preserves other global skills by linking per-skill directories.

REPO_SKILLS_DIR="$(cd "$(dirname "$0")/.." && pwd)/skills"
if [ ! -d "$REPO_SKILLS_DIR" ]; then
  echo "Error: skills directory not found at $REPO_SKILLS_DIR" >&2
  exit 1
fi

GLOBAL_TARGETS=(
  "$HOME/.agents/skills"
  "$HOME/.claude/skills"
  "$HOME/.codex/skills"
  "$HOME/.gemini/skills"
  "$HOME/.openclaw/skills"
  "$HOME/.config/opencode/skills"
)

mkdir -p "${GLOBAL_TARGETS[@]}"

echo "Linking skills from $REPO_SKILLS_DIR"
for skill_dir in "$REPO_SKILLS_DIR"/*/ ; do
  [ -d "$skill_dir" ] || continue
  skill_name="$(basename "$skill_dir")"
  # Validate presence of SKILL.md
  if [ ! -f "$skill_dir/SKILL.md" ]; then
    echo "Skip $skill_name: missing SKILL.md" >&2
    continue
  fi
  for tgt in "${GLOBAL_TARGETS[@]}"; do
    mkdir -p "$tgt"
    link_path="$tgt/$skill_name"
    if [ -L "$link_path" ]; then
      # If symlink exists and points to a different target, replace it
      current_target="$(readlink "$link_path")"
      if [ "$current_target" != "$skill_dir" ]; then
        rm -f "$link_path"
        ln -s "$skill_dir" "$link_path"
        echo "Updated symlink: $link_path -> $skill_dir"
      fi
    elif [ -e "$link_path" ]; then
      echo "Skip $link_path: exists and is not a symlink" >&2
    else
      ln -s "$skill_dir" "$link_path"
      echo "Created symlink: $link_path -> $skill_dir"
    fi
  done
done

echo "Done. Restart CLIs to pick up changes if needed."
