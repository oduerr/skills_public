#!/usr/bin/env bash
set -euo pipefail

# link_external_skills.sh
# Creates symlinks from ~/.agents/skills/ (populated by fetch_external_skills.sh)
# into all other agent skill folders.
# Run after fetch_external_skills.sh.

SOURCE_DIR="${HOME}/.agents/skills"

if [ ! -d "$SOURCE_DIR" ]; then
  echo "Error: $SOURCE_DIR not found. Run fetch_external_skills.sh first." >&2
  exit 1
fi

TARGETS=(
  "$HOME/.claude/skills"
  "$HOME/.codex/skills"
  "$HOME/.gemini/skills"
  "$HOME/.openclaw/skills"
  "$HOME/.config/opencode/skills"
)

mkdir -p "${TARGETS[@]}"

echo "Linking external skills from $SOURCE_DIR"
for skill_dir in "$SOURCE_DIR"/*/; do
  [ -d "$skill_dir" ] || continue
  skill_name="$(basename "$skill_dir")"

  if [ ! -f "$skill_dir/SKILL.md" ]; then
    echo "Skip $skill_name: missing SKILL.md" >&2
    continue
  fi

  for tgt in "${TARGETS[@]}"; do
    link_path="$tgt/$skill_name"
    if [ -L "$link_path" ]; then
      current="$(readlink "$link_path")"
      if [ "$current" != "$skill_dir" ]; then
        rm -f "$link_path"
        ln -s "$skill_dir" "$link_path"
        echo "Updated: $link_path -> $skill_dir"
      fi
    elif [ -e "$link_path" ]; then
      echo "Skip $link_path: exists and is not a symlink" >&2
    else
      ln -s "$skill_dir" "$link_path"
      echo "Created: $link_path -> $skill_dir"
    fi
  done
done

echo "Done. Restart your CLI to pick up changes."
