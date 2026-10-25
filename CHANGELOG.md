# Changelog

All notable changes to this repo are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versions are git tags.

## [Unreleased]

### Added

- `jenreh-python` 0.4.0: `code-review-high` skill, a high-effort, recall-oriented review of
  the current diff.
- `jenreh-reflex` 0.3.3: `appkit-mantine-reference` covers Mantine 9.6 and 9.7.3 (Lightbox,
  ActionBar, Gauge/Waffle/Matrix/Candlestick charts, chart reference areas and dots, Toolbar,
  Tour, Notifications, JsonViewer, resizable AppShell) on Reflex 0.10. The per-release notes
  left `SKILL.md` and now live in the reference file of each component, so the skill loads
  about 100 fewer lines. New rules: undeclared props silently become CSS (use
  `custom_attrs`), Reflex 0.10 has no auto setters, JS function props go in `rx.Var`.
  Props the wrappers now declare (TimeGrid `value`/`on_change`, Tree `on_select`/`on_check`,
  Table/CloseButton `variant`, HoverCard/Popover positioning and transitions, picker
  `presets`, MaskInput options, AngleSlider `format_label`, `light_hidden`/`dark_hidden`)
  replace the earlier `custom_attrs` workarounds.

### Fixed

- `appkit-mantine-reference`: the RichTextEditor example used `on_change` and `toolbar=`
  (the wrapper takes `on_update` and `toolbar_config=`); the theme reference documented a
  non-existent `mn.virtual_color`; `alloq_commons` number helpers are now marked as
  alloq-only. An audit against the wrapper source fixed about 30 sections that listed props
  the wrappers do not declare (Marquee, Scroller, Collapse, OverflowList, Spoiler,
  RollingNumber, MaskInput, MarkdownPreview, Tree, TimeGrid, Popover, HoverCard, ...), and
  the color section now uses Mantine's 0–9 shades instead of Radix 1–12.
- `appkit-commons`: documents `service_registry().snapshot()` / `restore()` for tests.
- `appkit-commons`: `service_registry` is imported from `appkit_commons.registry`, not the
  package root.

## [0.3.0] - 2026-08-08

### Added

- Conformance with the vendor-neutral [Agent Plugins 1.0.0](https://agent-plugins.org)
  spec. The spec paths it requires at each plugin root are `ln -s` symlinks onto the
  existing Claude files, so there is still exactly one file per plugin to maintain:
  `plugins/<p>/plugin.json -> .claude-plugin/plugin.json` and
  `plugins/<p>/mcp.json -> .mcp.json`. The spec permits this — symlinks may resolve to
  targets inside the plugin root — and nothing is duplicated.
- `scripts/validate_plugins.py`, an offline mirror of the two published schemas, wired
  into `task validate` / `task validate:plugins` and the CI workflow. Beyond the schemas
  it enforces that each spec path and its Claude counterpart are the same inode, so the
  two views cannot drift.

### Changed

- Bumped all four marketplace plugins from `0.1.0` to `0.3.0` to match this repo's
  release tag — their versions had never moved despite the skill churn in 0.2.0
  (skills added, removed, and `appkit-mantine-reference` expanded). Also fixed
  `jenreh-core` and `jenreh-python` descriptions in `marketplace.json` and
  `scripts/link-plugins.sh`, which still named `skills-creator`, `skills-find`, and
  `runic` after they were dropped.
- Extended the Claude manifests with the spec metadata that does not collide with them:
  `plugin.json` gained `$schema`, `homepage`, `repository` and `keywords`; `.mcp.json`
  gained the required `$schema` and an explicit `"type": "stdio"` per server (Claude Code
  already accepted `type`). `claude plugin validate` still passes on all four plugins.
  `jenreh-python` / `jenreh-reflex` keep Claude Code's top-level `dependencies`, which the
  spec reports and ignores rather than rejecting — moving it under `extensions` would
  break Claude Code's dependency auto-install.
- `scripts/link-plugins.sh` now generates the full manifest (it had drifted from the
  hand-edited `repository` / `dependencies` fields and would have clobbered them) and
  creates the spec symlinks.
- Documented that the `plugins/` marketplace layer (`.claude-plugin/plugin.json`,
  `.claude-plugin/marketplace.json`) already works for GitHub Copilot CLI and VS Code's
  agent plugins, not just Claude Code — both check `.claude-plugin/` as a fallback
  manifest location, so no dual manifest is needed. Added `copilot plugin ...` install
  instructions to the README alongside the existing `/plugin ...` Claude Code commands,
  and a maintainer note in `docs/cross-agent-skills.md` about keeping it that way.

### Fixed

- `reflex-testing-state/SKILL.md` frontmatter: an unindented continuation line ended the
  folded `description:` block early, so the YAML failed to parse and the skill loaded with
  all metadata silently dropped.
- `.claude-plugin/marketplace.json`: plugin `source` values now use the `./<name>` form
  the marketplace schema requires; all four entries previously failed validation.

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
