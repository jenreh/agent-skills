# Cross-agent skills wiring convention

This repo is the single source of truth for portable [agent skills](https://agentskills.io)
shared across **Claude Code**, **Codex**, and **GitHub Copilot**. The same physical
`SKILL.md` folder is discovered by all three agents — no duplication, no per-agent forks.

## The convention (decisions D3 + D4)

- **Canonical files** live in `skills/<name>/SKILL.md` in this repo.
- **Vendored** into a consuming project under `.agents/agent-skills/` via `git subtree`.
- **Two symlinks** expose them to each agent from one copy:

```
.agents/agent-skills/   # git subtree of jenreh/agent-skills (the whole repo)
.agents/skills          -> agent-skills/skills              # Codex + Copilot read here
.claude/skills          -> ../.agents/agent-skills/skills   # Claude Code reads here
```

Both symlinks are **single-hop** and resolve directly to the real
`.agents/agent-skills/skills` directory — there are no symlink chains, which keeps
discovery reliable across agents and survives a fresh `git clone`.

### Why a wrapper dir + symlinks?

Skills live under `skills/` in this repo (leaving room for a top-level
`.claude-plugin/` marketplace). `git subtree add --prefix <p>` maps the **whole repo**
to `<p>`, so subtreeing straight into `.agents/skills` would nest skills at
`.agents/skills/skills/<name>`. Vendoring into `.agents/agent-skills` and pointing
`.agents/skills` at `agent-skills/skills` gives the flat `.agents/skills/<name>` layout
every agent expects.

## Skill format: Claude Code first (D4)

Skills are shared files, not byte-identical lowest-common-denominator copies. They are
tuned for Claude Code and stay usable in Codex and Copilot, which ignore frontmatter keys
they do not know.

- Frontmatter: `name` + `description` (key use case first, then "Use when …" triggers;
  Claude Code cuts `description` + `when_to_use` at 1,536 characters and shows `<` / `>`
  as `&lt;` / `&gt;`).
- Claude Code fields are welcome where they help:
  - `disable-model-invocation: true` for side-effect workflows (commit, release).
  - `allowed-tools` to pre-approve what the skill needs, as narrow rules such as
    `Bash(git diff *)` or `Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/*)`. Never a bare
    `Bash`, which approves every shell command for the turn.
  - `disallowed-tools` for read-only workflows (`code-review-high` drops `Edit`/`Write`).
  - `argument-hint` for skills people call with an argument.
  - `` !`command` `` lines to pre-fill context when the skill loads (for example
    `git status --short` in `commit-msg`). Pick commands that exit 0 in every normal case:
    a non-zero exit aborts the skill. Pre-approve them in `allowed-tools`, and word the
    text so an agent that does not run them knows to run them itself.
- Bundled scripts are called as `${CLAUDE_SKILL_DIR}/scripts/<file>`. A bare
  `scripts/<file>` runs from the user's working directory and breaks in a plugin install.
  Skills that use scripts start with a one-line note naming the skill directory, so an
  agent that leaves `${CLAUDE_SKILL_DIR}` unexpanded still finds the folder.
- Body: markdown instructions, critical rules near the top (after compaction Claude keeps
  only the first ~5,000 tokens of a skill). Aim for under 500 lines; push detail into
  `references/`.
- Optional `scripts/`, `references/`, `assets/`, `agents/` subfolders.

`task validate` (`skill-dojo validate`) checks these rules.

**Codex / ChatGPT metadata:** every skill carries an `agents/openai.yaml`. It is an extra
file that Codex and the ChatGPT desktop app read and every other agent ignores, so
`SKILL.md` stays identical. It sets the display name, a short description (64 characters
or less), the icon (`./assets/jenreh.svg`, copied into the skill so the folder stays
self-contained), and `policy.allow_implicit_invocation`. Codex ignores Claude's
`disable-model-invocation`, so a manual-only skill must also set
`allow_implicit_invocation: false`; the validator enforces that. A new skill gets a stub
from `task build` (`skill-dojo build`); edit the generated text, then run
`task lock:refresh`. Build never overwrites an `openai.yaml` it did not generate.

`task validate` (`skill-dojo validate`) enforces these rules.

## Plugin marketplace format (Claude Code + GitHub Copilot)

The `plugins/` directory and root `.claude-plugin/marketplace.json` are a second,
optional consumption path (see the [README](../README.md#plugin-marketplace)) for
ad-hoc projects that want an installable plugin instead of vendoring the whole repo.
Despite the `.claude-plugin/` name, this layer is **not Claude-only**:

- Both the GitHub Copilot CLI and VS Code's agent plugin loader check
  `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` as a fallback
  manifest location (after `.plugin/plugin.json`, root `plugin.json`, and
  `.github/plugin/plugin.json`). See the [Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference)
  and [VS Code agent plugins docs](https://code.visualstudio.com/docs/agent-customization/agent-plugins).
- `plugin.json` fields used here (`name`, `description`, `version`, `author`, `license`)
  and `marketplace.json` fields (`name`, `owner`, `metadata.pluginRoot`, per-plugin
  `source`) are recognized identically by both schemas.
- **Do not add a second manifest** (e.g. `.github/plugin/plugin.json`) — it would just
  duplicate what fallback detection already provides and risk drifting out of sync.
- MCP servers are portable as-is: both Claude Code and VS Code's agent plugin loader
  read server definitions from `.mcp.json` at the plugin root (e.g.
  `plugins/jenreh-core/.mcp.json`), so a single file works for every loader. Only
  `hooks.json` location differs — if a future plugin ships hooks, revisit:
  Claude-format plugins expect `hooks/hooks.json` and support the
  `${CLAUDE_PLUGIN_ROOT}` token, while Copilot-format plugins expect `hooks.json` at
  the plugin root and don't expand that token — pick whichever the auto-detected
  format (Claude, since we ship `.claude-plugin/`) requires.
- Skill and plugin `name` fields must stay plain kebab-case with no namespace prefix
  (e.g. `boost`, not `jenreh-core/boost`) — both loaders silently skip prefixed names.

## Agent Plugins 1.0.0 conformance

The plugins also target the vendor-neutral [Agent Plugins](https://agent-plugins.org)
specification (Working Draft 1.0.0; TSC members include Amazon, Cursor, Microsoft,
OpenAI and Vercel). It puts the manifest at `<plugin>/plugin.json` and the MCP config at
`<plugin>/mcp.json` — both at the plugin **root**, and it forbids declaring MCP servers
inline in `plugin.json` or loading them from an alternative path.

Rather than maintaining a second copy of each file, the spec paths are **symlinks** into
the existing Claude/Copilot locations, so there is exactly one file per plugin to edit:

```
plugins/jenreh-core/
├── plugin.json  -> .claude-plugin/plugin.json   # Agent Plugins spec path
├── mcp.json     -> .mcp.json                    # Agent Plugins spec path
├── .claude-plugin/plugin.json                   # the real file
├── .mcp.json                                    # the real file
└── skills/<name>/SKILL.md
```

This is explicitly allowed: symlinks "MAY resolve to targets within the plugin root",
and these relative links never leave it. `task build` (re)creates them
(`layout.manifest_symlinks` and `mcp_symlink` in `registry/config.yaml`); nothing is ever
duplicated.

The two real files carry the spec metadata alongside the Claude fields, which do not
collide:

- `plugin.json` gained `$schema`, `homepage`, `repository` and `keywords`. Claude Code
  accepts all four silently — verified with `claude plugin validate`.
- `.mcp.json` gained the required `$schema` plus an explicit `"type": "stdio"` per
  server. Claude Code has supported `type` on server entries all along, so this is a
  no-op for it and a hard requirement for the spec.

**One deliberate deviation:** `jenreh-python` and `jenreh-reflex` keep Claude Code's
top-level `dependencies` field, which is not part of the portable core. The spec treats
an unknown top-level field as non-fatal — "a client reports and ignores that field" —
so this costs a warning rather than rejection. Moving it under `extensions` would make
the manifest schema-clean but would silently break Claude Code's dependency
auto-install, which is the worse trade. `skill-dojo validate` reports it as a
known, accepted warning.

Run `task validate` to check conformance;
it mirrors both published schemas offline and also enforces that the spec paths and the
Claude files really are the same inode, so they cannot drift apart.

## Verifying discovery per agent

After running `skill-dojo vendor` (see the README; or the Copier template's
`include_skills` task):

- **Claude Code** — open the project, run `/skills` (or ask "list your skills"). The
  skills appear by name.
- **Codex** — run Codex in the project dir; it scans `.agents/skills` and follows the
  symlink. As a plugin marketplace: `codex plugin marketplace add jenreh/agent-skills`
  reads `.agents/plugins/marketplace.json`; install from the ChatGPT desktop app.
- **Copilot** — in VS Code agent mode run `/skills`, or `gh copilot`; it resolves
  `.agents/skills`.

Re-verify after a fresh `git clone` to confirm the symlinks survive checkout.
