#!/usr/bin/env bash
set -euo pipefail

repository_home="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source_home="$repository_home/skills"
shared_home="$repository_home/shared"

install_for() {
  local skills_home="$1"
  mkdir -p "$skills_home"
  for skill in "$source_home"/*; do
    local name
    name="$(basename "$skill")"
    [[ -f "$skill/SKILL.md" ]] || { echo "Invalid skill: $skill" >&2; exit 1; }
    temp="$(mktemp -d "$skills_home/.${name}.XXXXXX")"
    cp -R "$skill/." "$temp/"
    backup="$skills_home/.${name}.previous"
    rm -rf "$backup"
    [[ ! -e "$skills_home/$name" ]] || mv "$skills_home/$name" "$backup"
    if ! mv "$temp" "$skills_home/$name"; then
      [[ ! -e "$backup" ]] || mv "$backup" "$skills_home/$name"
      exit 1
    fi
    rm -rf "$backup"
  done
  rm -rf "$skills_home/_personal-shared"
  cp -R "$shared_home" "$skills_home/_personal-shared"
  echo "Installed personal skills in $skills_home"
}

install_for "${CODEX_HOME:-$HOME/.codex}/skills"
install_for "$HOME/.claude/skills"
install_for "$HOME/.config/opencode/skills"
install_for "$HOME/.factory/skills"
