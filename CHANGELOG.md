# Changelog

All notable changes to this repo are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versions are git tags.

## [Unreleased]

### Added

- Codex / ChatGPT integration: every skill has an `agents/openai.yaml` with a display
  name, short description, the `jenreh.svg` icon, and `allow_implicit_invocation`
  (`false` for the manual-only `commit-msg`, `release`, `code-cleanup`, `drawio-skill`,
  and `mermaid-skill`, which Codex would otherwise start on its own). Each `plugin.json`
  carries an `extensions.com.openai.interface` card, and `.agents/plugins/marketplace.json`
  lists the plugins in Codex's format, so `codex plugin marketplace add jenreh/agent-skills`
  works. `scripts/codex_metadata.py` generates the layer; the validators check it.
- `jenreh-tools` 0.1.0: new plugin for developer tool skills (`commit-msg`, `create-readme`,
  `drawio-skill`, `mermaid-skill`, `release`).
- `jenreh-agents` 0.1.0: new plugin with `building-pydantic-ai-agents`, `deepeval`,
  `deepeval-tracing`, and `deepeval-otel`, vendored from Arvato Systems' `nmxdi-agents`
  1.1.1 (Apache-2.0, license kept in `licenses/`).
- `jenreh-core` 0.5.0: `brainstorming`, `deep-research`, `doc-coauthoring`, and
  `skill-creator` skills. `skill-creator`'s `SKILL.md` is slimmed: description optimization
  and the Claude.ai / Cowork notes moved to `references/`.
- `jenreh-python` 0.6.0: `code-simplifier`, `systematic-debugging`, and
  `test-driven-development` skills.
- `jenreh-reflex` 0.4.1: `appkit-user` 1.2 documents `authenticated_page` with a `template`
  callable and the `PageLayout` argument of the login and password-reset page factories.
  `appkit-mantine-reference` 1.8 adds the app helpers (`mn.theme_wrapper`, `mn.ThemeState`,
  `mn.LoadingState`, `mn.with_loading_reset`, `mn.delete_dialog`) and hidden form fields via
  `mn.form.input`. `reflex-state-and-architecture` 1.2 says where page layouts live.
  `appkit-mantine-reference` 1.9 trims `SKILL.md` by about a third: one component index
  replaces the category list and decision tree, and the project-specific `alloq_commons`
  formatting helpers are removed.
- `jenreh-python` 0.6.0: `appkit-commons` 2.3 lists the secret providers
  (`SECRET_PROVIDER`, `SECRET_NAMESPACE`) and the `appkit-secrets` CLI.
- `jenreh-design` 0.2.0: `hallmark` skill, vendored from
  [Nutlope/hallmark](https://github.com/Nutlope/hallmark) (MIT, license kept in the skill folder).
- `jenreh-graphdb` 0.1.0: new plugin for graph database skills. `runic-ogm`'s `SKILL.md`
  points to the cookbook for search, custom repositories, polymorphism, and embedded tests
  instead of repeating them.
- `jenreh-reflex` 0.3.6: `appkit-commons` 2.2 adds the ASGI middleware section
  (`ForceHTTPSMiddleware`, `SecurityHeadersMiddleware`). `appkit-user` 1.1 describes the login
  throttle as stored in `auth_login_throttle`, shared across workers and restarts.
- `jenreh-reflex` 0.3.5: `appkit-user` covers the login throttle (`login_rate_limit`,
  `get_login_throttle()`) and the forced password reset on login.
- `jenreh-core` 0.4.0: `task-observer` skill, which logs skill-improvement opportunities during
  multi-step tasks and turns them into skill updates in a weekly review.
- `jenreh-reflex` 0.3.4: skills updated for Reflex 0.10.1 (`reflex>=0.10.1`).
  `appkit-user` documents `trusted_proxy_hops` for `router.session.client_ip` behind a proxy and
  repeated cookie headers, `appkit-commons` adds sticky-session and `REFLEX_BACKEND_START_METHOD`
  deployment rules, and `reflex-state-and-architecture` covers `rx.form.FormData` and sequence
  `on_load`.
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

### Changed

- Skills are now tuned for Claude Code instead of kept byte-identical across agents:
  - Bundled scripts run via `${CLAUDE_SKILL_DIR}/scripts/...`, so they work from a plugin
    install. This fixes `design` (pointed at `~/.claude/skills/design`), `ui-ux-pro-max`
    (pointed at `${CLAUDE_PLUGIN_ROOT}/.claude/skills/...`), and the cwd-relative calls in
    `brand`, `design-system`, `ui-styling`, `hallmark`, `task-observer`, `drawio-skill`,
    `mermaid-skill`, and `skill-creator`.
  - `allowed-tools` pre-approves those scripts and the read-only commands each workflow
    needs. Bare `Bash` grants in `drawio-skill`, `commit-msg`, `release`, `code-cleanup`,
    and `boost` are narrowed to specific commands; paid image generation in `design` still
    asks.
  - `commit-msg` and `release` pre-fill git status (and diff stats and recent commits) when
    they load. `release` accepts `patch`, `minor`, or `major` as an argument and warns on a
    dirty tree.
  - `code-review-high` cannot edit files while it runs (`disallowed-tools`).
  - `argument-hint` on the skills people call with an argument.
  - `boost` uses the plugin-namespaced MCP tool names; `hallmark`'s description no longer
    has `<` / `>`, which Claude's skill listing shows as `&lt;` / `&gt;`.
  - `drawio-skill` and `mermaid-skill` are model-invocable again (Claude and Codex start them
    on their own).
  - The four skills over 500 lines now keep their rules in `SKILL.md` and move detail into
    `references/`, loaded on demand: `task-observer` 700 → 493 (`references/acting.md`,
    `references/writing-observations.md`; its own bundle gate and selftests pass),
    `reflex-state-and-architecture` 575 → 448 (`backend-patterns.md`,
    `mantine-examples.md`), `terraform-refactor-module` 538 → 290 (`worked-example.md`,
    `module-readme-template.md`), `appkit-commons` 533 → 398 (`path-prefix.md`,
    `scheduler.md`, `middleware.md`). Anti-pattern tables moved near the top, since Claude
    keeps only the first ~5,000 tokens of a skill after compaction.
  - The validator warns on SKILL.md files over 500 lines (was 600), cwd-relative script calls, bare `Bash` grants, and angle brackets
    in descriptions, and fails on descriptions over Claude Code's 1,536-character cap.
- `jenreh-core` 0.5.0: `commit-msg`, `create-readme`, `release`, `drawio-skill`, and
  `mermaid-skill` moved to `jenreh-tools`; `code-cleanup` moved to `jenreh-python`;
  `frontend-design` moved to `jenreh-design` (0.3.0). Reinstall the target plugin to keep them.
- `code-cleanup`: `allowed-tools` uses the plugin-namespaced MCP tool names
  (`mcp__plugin_jenreh-core_context7__*`), so the pre-approval matches again.
- `scripts/link-plugins.sh` keeps each plugin's own version and license instead of writing
  `0.3.0` / MIT into every manifest. The validators now fail on broken or missing links in
  `skills/` and on plugins missing from `marketplace.json` or listed with a different version.
- `jenreh-graphdb` 0.1.0: `runic-ogm` and `runic-migrate` moved here from `jenreh-python`.
- `jenreh-python` 0.5.0: `appkit-commons` moved here from `jenreh-reflex` (0.4.0).
  `jenreh-reflex` already depends on `jenreh-python`.

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
