#!/usr/bin/env bash
# (Re)build the repo's two layouts from a single source of truth.
#
# Source of truth: the REAL skill folders live under each plugin:
#     plugins/<plugin>/skills/<name>/SKILL.md
# This is what Claude Code's marketplace installs (a plugin folder is copied
# standalone, so its skills must be real files — never symlinks that escape it).
#
# This script:
#   * writes each plugin's .claude-plugin/plugin.json
#   * regenerates the flat, portable view used by Codex/Copilot:
#       skills/<name> -> ../plugins/<plugin>/skills/<name>   (read in place)
# Skills are NEVER duplicated — the flat skills/ dir points back at the plugins.
set -euo pipefail
cd "$(dirname "$0")/.."

declare -a PLUGINS=(jenreh-core jenreh-python jenreh-reflex jenreh-terraform)

desc_jenreh_core="Cross-cutting agent skills (boost, commit-msg, create-readme, release, …)."
desc_jenreh_python="Python archetype skills (python-coding, runic, docker-multi-stage, …)."
desc_jenreh_reflex="reflex.dev / AppKit web skills (appkit-*, reflex-*)."
desc_jenreh_terraform="Terraform / infra skills (terraform-*)."

# 1) Write plugin.json for each plugin.
for plugin in "${PLUGINS[@]}"; do
  pdir="plugins/$plugin"
  mkdir -p "$pdir/.claude-plugin" "$pdir/skills"
  descvar="desc_${plugin//-/_}"
  cat > "$pdir/.claude-plugin/plugin.json" <<EOF
{
  "name": "$plugin",
  "description": "${!descvar}",
  "version": "0.1.0",
  "author": { "name": "Jens Rehpöhler" },
  "license": "MIT"
}
EOF
done

# 2) Rebuild the flat skills/ view from the real skill folders in the plugins.
mkdir -p skills
find skills -maxdepth 1 -type l -delete
count=0
for plugin in "${PLUGINS[@]}"; do
  for sdir in "plugins/$plugin/skills"/*/; do
    [ -d "$sdir" ] || continue
    skill=$(basename "$sdir")
    if [ -e "skills/$skill" ] && [ ! -L "skills/$skill" ]; then
      echo "ERROR: skills/$skill exists as a real path (expected a generated symlink)" >&2
      exit 1
    fi
    ln -sfn "../plugins/$plugin/skills/$skill" "skills/$skill"
    count=$((count + 1))
  done
  n=$(find "plugins/$plugin/skills" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')
  echo "plugin $plugin: $n skills"
done
echo "linked $count skills into the flat skills/ view"
