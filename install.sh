#!/usr/bin/env bash
set -euo pipefail

repository_home="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source_home="$repository_home/skills"
shared_home="$repository_home/shared"
schema_home="$repository_home/schemas"

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
  mkdir -p "$skills_home/wayfinder/scripts"
  cp "$repository_home/scripts/validate-wayfinder-change.py" "$skills_home/wayfinder/scripts/"
  temp="$(mktemp -d "$skills_home/._personal-shared.XXXXXX")"
  cp -R "$shared_home/." "$temp/"
  backup="$skills_home/._personal-shared.previous"
  rm -rf "$backup"
  [[ ! -e "$skills_home/_personal-shared" ]] || mv "$skills_home/_personal-shared" "$backup"
  mv "$temp" "$skills_home/_personal-shared"
  rm -rf "$backup"
  echo "Installed personal skills in $skills_home"
}

install_for "${CODEX_HOME:-$HOME/.codex}/skills"
install_for "$HOME/.claude/skills"
install_for "$HOME/.config/opencode/skills"
install_for "$HOME/.factory/skills"

openspec_schema_home="${XDG_DATA_HOME:-$HOME/.local/share}/openspec/schemas"
mkdir -p "$openspec_schema_home"
for schema in "$schema_home"/*; do
  name="$(basename "$schema")"
  rm -rf "$openspec_schema_home/$name"
  cp -R "$schema" "$openspec_schema_home/$name"
done
echo "Installed personal OpenSpec schemas in $openspec_schema_home"
personal_bin="${XDG_BIN_HOME:-$HOME/.local/bin}"
mkdir -p "$personal_bin"
cp "$repository_home/scripts/validate-wayfinder-change.py" "$personal_bin/wayfinder-validate"
chmod +x "$personal_bin/wayfinder-validate"
echo "Installed wayfinder-validate in $personal_bin"
