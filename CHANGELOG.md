# Changelog

All notable changes to this repo are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versions are git tags.

## [Unreleased]

## [0.2.0] - 2026-07-02

### Changed

- Inverted the skill symlink direction so marketplace plugins are self-contained:
  each skill's real files now live under `plugins/jenreh-{core,python,reflex,terraform}/skills/`,
  and the top-level `skills/` entries are symlinks pointing into the plugins. This
  lets plugins be vendored independently without dangling references.
- Expanded the `appkit-mantine-reference` skill to Mantine 9.4: split the monolithic
  `inputs.md` into focused references (text, selection, toggle, datetime, specialized)
  and added coverage for charts, data display, layout, overlays, menus, navigation,
  tables, trees, typography, theming, feedback, extensions, and scheduling.

### Removed

- Dropped `runic`, `skills-creator`, and `skills-find` from `skills/` — these are
  standard skills already available through plugin marketplaces, so vendoring them
  here was redundant.

## [0.1.0] - 2026-06-13

### Added

- Initial canonical, portable agent-skills repo: single source of truth for skills
  shared across Claude Code, Codex, and GitHub Copilot.
- 27 skills migrated from `jenreh/project-kit` (a strict superset of `python-kit`),
  all verified portable-core (no Claude-only / Codex-only frontmatter).
- `scripts/add-skills.sh` — one-command vendor + cross-agent wiring (`git subtree`
  into `.agents/agent-skills` + `.agents/skills` / `.claude/skills` symlinks).
- `scripts/validate_skills.py` + `task validate` + GitHub Actions `validate` workflow.
- `docs/cross-agent-skills.md` documenting the D3/D4 conventions.
- Optional Claude Code marketplace layer (`.claude-plugin/marketplace.json`,
  `plugins/jenreh-{core,python,reflex,terraform}`) with skills symlinked back to
  `skills/` (no duplication).
