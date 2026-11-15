#!/usr/bin/env bash
# (Re)build the repo's two layouts from a single source of truth.
#
# Source of truth: the REAL skill folders live under each plugin:
#     plugins/<plugin>/skills/<name>/SKILL.md
# This is what a marketplace install copies standalone (a plugin folder is
# copied on its own, so its skills must be real files — never symlinks that
# escape it). The generated plugins/<plugin>/.claude-plugin/plugin.json is
# read by Claude Code, the GitHub Copilot CLI, and VS Code alike — all three
# check .claude-plugin/ as a fallback manifest location, so this one manifest
# serves every tool (see docs/cross-agent-skills.md). Do not add a second,
# Copilot-specific manifest — it would just duplicate this and drift.
#
# Agent Plugins 1.0.0 (https://agent-plugins.org) puts the manifest at
# `<plugin>/plugin.json` and the MCP config at `<plugin>/mcp.json`. Rather than
# maintaining two copies, the spec paths are symlinks into the Claude/Copilot
# locations — the spec allows this as long as they resolve inside the plugin
# root, which relative links to `.claude-plugin/plugin.json` and `.mcp.json` do.
#
# This script:
#   * writes each plugin's .claude-plugin/plugin.json
#   * links <plugin>/plugin.json -> .claude-plugin/plugin.json  (Agent Plugins)
#   * links <plugin>/mcp.json    -> .mcp.json                   (Agent Plugins)
#   * regenerates the flat, portable view used by Codex/Copilot:
#       skills/<name> -> ../plugins/<plugin>/skills/<name>   (read in place)
# Skills are NEVER duplicated — the flat skills/ dir points back at the plugins.
set -euo pipefail
cd "$(dirname "$0")/.."

declare -a PLUGINS=(jenreh-agents jenreh-core jenreh-design jenreh-graphdb jenreh-python jenreh-reflex jenreh-terraform jenreh-tools)

PLUGIN_SCHEMA="https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
REPO_URL="https://github.com/jenreh/agent-skills"
# Versions are per plugin and owned by the existing manifest: the script keeps
# whatever version .claude-plugin/plugin.json already has (bump it there and in
# .claude-plugin/marketplace.json). A brand-new plugin starts at DEFAULT_VERSION.
DEFAULT_VERSION="0.1.0"

desc_jenreh_agents="AI agent skills: building-pydantic-ai-agents, deepeval, deepeval-tracing, deepeval-otel."
desc_jenreh_core="Cross-cutting skills: boost, brainstorming, deep-research, doc-coauthoring, mein-schreibstil, plain-writing, skill-creator, task-observer."
desc_jenreh_design="Design skills: brand, design, design-system, frontend-design, hallmark, ui-styling, ui-ux-pro-max."
desc_jenreh_graphdb="Graph database skills: runic-ogm, runic-migrate."
desc_jenreh_python="Python skills: python-coding, python-clean-code, appkit-commons, code-cleanup, code-review-high, code-simplifier, docker-multi-stage, github-actions-cicd, systematic-debugging, test-driven-development."
desc_jenreh_reflex="reflex.dev / AppKit web skills: appkit-mantine-reference, appkit-user, reflex-docs, reflex-state-and-architecture, reflex-testing-state."
desc_jenreh_terraform="Terraform / infra skills: AVM modules, refactor, acceptance tests, search-import, stacks, style-guide, test."
desc_jenreh_tools="Developer tool skills: commit-msg, create-readme, drawio-skill, mermaid-skill, release."

# JSON array bodies (without the brackets). Empty = omit the field.
keywords_jenreh_agents='"agent-skills", "claude-code", "agents", "pydantic-ai", "deepeval", "opentelemetry"'
keywords_jenreh_core='"agent-skills", "claude-code", "writing", "research", "skills"'
keywords_jenreh_design='"agent-skills", "claude-code", "design", "frontend", "ui"'
keywords_jenreh_graphdb='"agent-skills", "claude-code", "graph", "cypher", "python"'
keywords_jenreh_python='"agent-skills", "claude-code", "python", "docker", "ci-cd"'
keywords_jenreh_reflex='"agent-skills", "claude-code", "reflex", "python", "frontend"'
keywords_jenreh_terraform='"agent-skills", "claude-code", "terraform", "azure", "iac"'
keywords_jenreh_tools='"agent-skills", "claude-code", "git", "release", "documentation", "diagrams"'

# Codex / ChatGPT plugin card: extensions.com.openai.interface. The icon is
# copied into each plugin's assets/ by scripts/codex_metadata.py.
OPENAI_ICON="./assets/jenreh.svg"
OPENAI_BRAND_COLOR="#4476AF"
title_jenreh_agents="jenreh Agents";       short_jenreh_agents="Build, evaluate, and trace AI agents in Azure or AWS"; category_jenreh_agents="Coding"
title_jenreh_core="jenreh Core";           short_jenreh_core="Prompting, research, writing, and skill authoring";     category_jenreh_core="Productivity"
title_jenreh_design="jenreh Design";       short_jenreh_design="Brand, design systems, and frontend UI design";       category_jenreh_design="Design"
title_jenreh_graphdb="jenreh Graph DB";    short_jenreh_graphdb="Model, query, and migrate graph databases with runic"; category_jenreh_graphdb="Coding"
title_jenreh_python="jenreh Python";       short_jenreh_python="Python style, clean code, debugging, TDD, and CI";    category_jenreh_python="Coding"
title_jenreh_reflex="jenreh Reflex";       short_jenreh_reflex="Build reflex.dev apps with AppKit and Mantine";       category_jenreh_reflex="Coding"
title_jenreh_terraform="jenreh Terraform"; short_jenreh_terraform="Write, test, refactor, and import Terraform";       category_jenreh_terraform="Coding"
title_jenreh_tools="jenreh Tools";         short_jenreh_tools="Commit messages, releases, READMEs, and diagrams";    category_jenreh_tools="Productivity"

# SPDX license per plugin; MIT unless a plugin vendors differently licensed skills.
license_jenreh_agents='Apache-2.0'

# `dependencies` is a Claude Code field. Agent Plugins reports it as an unknown
# top-level field and ignores it, which is a warning — not a rejection.
deps_jenreh_agents=''
deps_jenreh_core=''
deps_jenreh_design=''
deps_jenreh_graphdb='{ "name": "jenreh-python" }'
deps_jenreh_python='{ "name": "jenreh-core" }'
deps_jenreh_reflex='{ "name": "jenreh-core" }, { "name": "jenreh-python" }'
deps_jenreh_terraform=''
deps_jenreh_tools=''

# 1) Write plugin.json for each plugin, then expose it at the spec path.
for plugin in "${PLUGINS[@]}"; do
  pdir="plugins/$plugin"
  mkdir -p "$pdir/.claude-plugin" "$pdir/skills"
  key="${plugin//-/_}"
  descvar="desc_$key"
  kwvar="keywords_$key"
  depvar="deps_$key"
  licvar="license_$key"
  license="${!licvar:-MIT}"
  titlevar="title_$key"
  shortvar="short_$key"
  catvar="category_$key"

  version="$DEFAULT_VERSION"
  if [ -f "$pdir/.claude-plugin/plugin.json" ]; then
    version=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("version") or sys.argv[2])' \
      "$pdir/.claude-plugin/plugin.json" "$DEFAULT_VERSION")
  fi

  {
    printf '{\n'
    printf '  "$schema": "%s",\n' "$PLUGIN_SCHEMA"
    printf '  "name": "%s",\n' "$plugin"
    printf '  "description": "%s",\n' "${!descvar}"
    printf '  "version": "%s",\n' "$version"
    printf '  "author": { "name": "Jens Rehpöhler" },\n'
    printf '  "homepage": "%s",\n' "$REPO_URL"
    printf '  "repository": "%s",\n' "$REPO_URL"
    printf '  "license": "%s",\n' "$license"
    printf '  "keywords": [%s]' "${!kwvar}"
    if [ -n "${!depvar}" ]; then
      printf ',\n  "dependencies": [%s]' "${!depvar}"
    fi
    printf ',\n  "extensions": {\n'
    printf '    "com.openai": {\n'
    printf '      "interface": {\n'
    printf '        "displayName": "%s",\n' "${!titlevar}"
    printf '        "shortDescription": "%s",\n' "${!shortvar}"
    printf '        "longDescription": "%s",\n' "${!descvar}"
    printf '        "developerName": "Jens Rehpöhler",\n'
    printf '        "category": "%s",\n' "${!catvar}"
    printf '        "websiteURL": "%s",\n' "$REPO_URL"
    printf '        "brandColor": "%s",\n' "$OPENAI_BRAND_COLOR"
    printf '        "composerIcon": "%s",\n' "$OPENAI_ICON"
    printf '        "logo": "%s"\n' "$OPENAI_ICON"
    printf '      }\n    }\n  }'
    printf '\n}\n'
  } > "$pdir/.claude-plugin/plugin.json"

  ln -sfn .claude-plugin/plugin.json "$pdir/plugin.json"

  # mcp.json is optional; only link it where a Claude .mcp.json actually exists.
  if [ -f "$pdir/.mcp.json" ]; then
    ln -sfn .mcp.json "$pdir/mcp.json"
  else
    rm -f "$pdir/mcp.json"
  fi
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

# 3) Codex / ChatGPT layer: icons, missing agents/openai.yaml stubs, and
#    .agents/plugins/marketplace.json (see the script's docstring).
python3 scripts/codex_metadata.py
