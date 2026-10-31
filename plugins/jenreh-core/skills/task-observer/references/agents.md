# Cross-agent use — Claude Code, Codex, GitHub Copilot

Load triggers: installing or activating the skill under Codex or GitHub Copilot (CLI, VS Code agent mode, cloud agent); one workspace shared by more than one agent tool; translating a Claude-specific step (a `Skill` invocation, CLAUDE.md, a `SessionStart` hook) into another agent's equivalent; a log write refused by a sandbox or trust prompt in a non-Claude agent

The protocol in `SKILL.md` is written as capabilities, and its scripts are plain
bash. Nothing in the bundle is agent-specific, so one physical copy serves all
three agents. What differs is where each agent looks for instructions and skills,
how a skill gets loaded, and which directories its sandbox lets it write to. This
file is that mapping. When a step in `SKILL.md` names a Claude product feature,
use the row below for the agent in front of you.

Every product fact here comes from the vendors' documentation and changes. Verify
a path, flag or hook name against the agent's current docs before pinning it into
a user's config, and say so when you could not.

## Contents

- Capability map
- One workspace for all three agents
- Activation per agent
- Write access outside the project
- Hooks
- Translating the protocol's tool wording
- Install layout

## Capability map

| Capability | Claude Code | Codex | GitHub Copilot |
|---|---|---|---|
| Project instruction file | `CLAUDE.md` (may import `AGENTS.md` with an `@AGENTS.md` line) | `AGENTS.md` (repo root and nested; `~/.codex/AGENTS.md` for the user) | `AGENTS.md`, `.github/copilot-instructions.md` |
| Skill folders scanned | `.claude/skills/`, `~/.claude/skills/` | `.agents/skills/` from the cwd up to the repo root, `~/.agents/skills/` | `.github/skills/`, `.claude/skills/`, `.agents/skills/`, and the user-level equivalents |
| Loading a skill | the `Skill` tool, or `/skill-name` | matched on the description, or named explicitly with `$skill-name`; the agent reads `SKILL.md` | matched on the description, or `/skills` to list and pick; the agent reads `SKILL.md` |
| Session-start hook | `SessionStart` (`hookSpecificOutput.additionalContext`) | `SessionStart` in `hooks.json` or a `[hooks]` table (see "Hooks") | `sessionStart` in `.github/hooks/*.json` (see "Hooks") |
| Extra writable directory | `--add-dir`, `permissions.additionalDirectories` | `--add-dir`, `sandbox_workspace_write.writable_roots` | `--add-dir`, trusted directories |
| Present a staged file for install | none: report the staged path and a change summary in chat | same | same |
| Folder picker for a missing mount | none: ask the user for the path | none: ask the user for the path | none: ask the user for the path |
| Subagents | do not run the protocol and write nothing; findings go in the report | same | same |

Cowork-only rows in `references/environments.md` ("Environment mappings") do not
apply to any of the three.

## One workspace for all three agents

The failure shape: each agent gets its own default location, and one log becomes
three, each of which looks complete from inside (`SKILL.md`, workspace paragraph).
A user who runs two or three of these tools on the same projects needs one path
that none of them owns.

Pin a tool-neutral path outside every agent's config tree and outside any
skills-discovery directory, for example `~/.agents/task-observer/`, so the log lives
at `~/.agents/task-observer/skill-observations/observation-log/`. Put the same
absolute path in the activation block of every instruction file below. Do not
reuse `~/.claude/projects/<project-id>/` when more than one agent works the
project: that path is Claude Code's, and the other agents would need to be told
about a directory they have no reason to know.

Where the shell environment can carry it, also export `TASK_OBSERVER_WORKSPACE`
with the same path. `scripts/new-observation.sh` and `scripts/session-start-scan.sh`
read it when no path argument is passed, which keeps a script call correct in an
agent whose instruction file did not load. The activation block still passes the
path explicitly, since an environment variable is not visible to the model.

Before creating a workspace, search the plausible anchors of all three agents for
an existing one and adopt it (`references/environments.md`, "Anchoring the
workspace").

## Activation per agent

Description matching is the only tier that every agent shares, and it is the
weakest one (`references/environments.md`, "Recommended activation setup"). Add the
activation block from `references/environments.md` ("The activation block") to the
instruction file each agent reads:

- **Codex and Copilot:** `AGENTS.md` at the repository root. Both read it, so this
  is the one file to write. Copilot also reads `.github/copilot-instructions.md`;
  use that only when the project has no `AGENTS.md`.
- **Claude Code:** `CLAUDE.md`. Keep the block in `AGENTS.md` alone and put the
  line `@AGENTS.md` in `CLAUDE.md`, so the block exists once and cannot drift
  between the two files.
- **User-level:** the personal equivalent of each file (`~/.codex/AGENTS.md`,
  `~/.claude/CLAUDE.md`, Copilot's user-level instructions) when the skill should
  run in every project, not only this one.

Replace "invoke the task-observer skill" in the block with the wording of the
agent's loading mechanism only if the agent fails to load it from the plain
sentence. In Codex, naming it as `$task-observer` works. In every agent, loading
means the agent has read `SKILL.md`; the Session Start Protocol still has to run
after it.

Verify activation in a NEW session of each agent, never the one that installed it
(`references/environments.md`, "Verify activation in a NEW session — the installing
session cannot prove it").

## Write access outside the project

The workspace is deliberately not inside the repository, and sandboxed agents
refuse writes outside the working tree. This is the most likely first failure in
Codex and Copilot, and it looks like a read-only log.

- Grant the workspace directory as an additional writable root in that agent's
  configuration (the row in the capability map), not by loosening the whole
  sandbox.
- A refused write is a permission decision, not a transient error: apply the
  denial rule in `SKILL.md` ("How to Log") and tell the user which directory needs
  the grant. Do not retry through a different tool.
- Scheduled or headless runs carry the grant in the task definition, as for Claude
  Code (`references/environments.md`, "Environment mappings").

## Hooks

A hook is the only enforced activation tier, and the three agents expose it
differently. The injected message and the shell logic in `references/environments.md`
("A session-start hook (Claude Code and similar harnesses)") are portable; the
JSON envelope is not.

- **Claude Code:** `hookSpecificOutput.additionalContext`, as in that section.
- **Codex:** hooks are declared in `hooks.json` (`~/.codex/hooks.json` or
  `<repo>/.codex/hooks.json`) or in a `[hooks]` table of `config.toml`. A command
  hook has to be reviewed and trusted (`/hooks`) before it runs, so a freshly
  installed hook is silent until the user does that.
- **Copilot CLI:** hooks are JSON files in `.github/hooks/` (or the user's
  `~/.copilot/hooks/`) with `"version": 1`. Whether a `sessionStart` hook may inject
  context is unconfirmed in the CLI reference; test it. If it cannot, fall back to
  the instruction-file block, which is the tier below.

Check the envelope against each agent's current hooks reference, then run the hook
against fixtures as the Claude Code section prescribes: a nag that never fires and
a nag that is correctly silent look identical from a passing run.

## Translating the protocol's tool wording

`SKILL.md` and its references say "the Skill invocation", "one batched call" and "the
folder-picker tool". The rules behind those phrases hold in every agent; the
mechanics differ.

- **Skill invocation.** The rule is that the per-skill lookup runs in the same turn
  that loads the skill, taken from a load that happened. In Codex and Copilot the
  load is the agent reading `SKILL.md` (or a tool call that does), so the lookup
  (`scripts/skill-load.sh`) goes in the same turn as that read.
- **One batched call.** Where the agent runs tool calls one at a time, keep the
  intent: the workspace probe (`ls` of the pinned path) is the first tool call or
  rides with it, and no write precedes it. Never state whether the workspace is
  mounted without a probe made in the same turn.
- **Folder picker.** None of the three has one. A failed probe means asking the user
  for the path or for the write grant above, then falling through to the order in
  `references/environments.md` ("No link to the user's computer").
- **Presenting a staged skill.** Print the staged path and a change summary. The
  staging rule is unchanged: never edit the live skill in place, in any agent.

## Install layout

The skill folder is the same bytes for every agent. Install it once and expose it
to the others by symlink, as `docs/cross-agent-skills.md` in this repository does
(`.agents/skills` for Codex and Copilot, `.claude/skills` for Claude Code).

A symlinked skills entry changes the staging check: resolve the live path before
copying and prove the staged copy is a distinct file, not an equal one
(`references/skill-authoring.md`, "Editing skills — always start from the live
file"). With three agents pointing at one folder, an in-place edit changes the
skill for all of them at once.

A second agent tool that lists the same skills folder shows the description to its
own model and may start the skill by itself. Where that is unwanted, use that
agent's own skill-permission setting rather than removing the activation block
(`references/environments.md`, "Other agent tools that read the same skills
folder").
