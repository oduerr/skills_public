#!/usr/bin/env bash
set -euo pipefail

# fetch_external_skills.sh
# Clones trusted external skill repos and copies skills into ~/.agents/skills/
# Re-run to update. Skills are never committed to your repo.

DEST_DIR="${HOME}/.agents/skills"
mkdir -p "$DEST_DIR"

# ---------------------------------------------------------------------------
# Edit this list to add/remove external skills
# Format: fetch "repo_url" "subdir_in_repo"
# ---------------------------------------------------------------------------
fetch() {
  local repo_url="$1"
  local subdir="$2"
  local skill_name
  skill_name="$(basename "$subdir")"

  echo "Fetching $skill_name ..."

  local tmp
  tmp="$(mktemp -d)"
  trap "rm -rf '$tmp'" RETURN

  git clone --depth 1 --filter=blob:none --sparse --quiet "$repo_url" "$tmp"
  git -C "$tmp" sparse-checkout set "$subdir"

  rm -rf "$DEST_DIR/$skill_name"
  cp -r "$tmp/$subdir" "$DEST_DIR/$skill_name"
  echo "  -> $DEST_DIR/$skill_name"
}

fetch "https://github.com/anthropics/skills" "skills/pptx"
fetch "https://github.com/anthropics/skills" "skills/pdf"
fetch "https://github.com/anthropics/skills" "skills/docx"
fetch "https://github.com/anthropics/skills" "skills/xlsx"
fetch "https://github.com/anthropics/skills" "skills/skill-creator"
fetch "https://github.com/anthropics/skills" "skills/frontend-design"

echo "Done. Run link_skills.sh to symlink into all agent folders."