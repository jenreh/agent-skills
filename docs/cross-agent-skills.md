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

## Portable core (D4)

Shared skills use only the portable `SKILL.md` core so the bytes are identical for every
agent:

- Frontmatter: `name` + `description` (write the description as activation triggers,
  "Use when …" — all three agents match on it). Optional `metadata`, `license`,
  `allowed-tools`, `argument-hint` degrade gracefully on agents that don't read them.
- Body: markdown instructions (keep under ~500 lines; push detail into `references/`).
- Optional `scripts/`, `references/`, `assets/` subfolders.

**Not allowed in shared skills:** Claude-only `context: fork` frontmatter, Codex-only
`openai.yaml`. Those break byte-identical reuse. If a skill genuinely needs a Claude-only
feature, keep that variant out of this repo and only in the project's `.claude/skills`.

`task validate` (or `python3 scripts/validate_skills.py`) enforces these rules.

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

## Verifying discovery per agent

After running `scripts/add-skills.sh` (or the Copier template's `include_skills` task):

- **Claude Code** — open the project, run `/skills` (or ask "list your skills"). The
  skills appear by name.
- **Codex** — run Codex in the project dir; it scans `.agents/skills` and follows the
  symlink.
- **Copilot** — in VS Code agent mode run `/skills`, or `gh copilot`; it resolves
  `.agents/skills`.

Re-verify after a fresh `git clone` to confirm the symlinks survive checkout.
