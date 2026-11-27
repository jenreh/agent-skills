---
name: release
description: Bump version, generate an AI-written changelog, and publish a GitHub release. Use when the user says "release", "publish", or "bump version".
disable-model-invocation: true
allowed-tools: Bash(git status *) Bash(grep *) Bash(task release:build *) AskUserQuestion
argument-hint: "[patch|minor|major]"
metadata:
  jenreh.registry/id: "jenreh:jenreh-tools"
  jenreh.registry/kind: "local"
  jenreh.registry/version: "0.1.0"
  jenreh.registry/source-marketplace: "jenreh/agent-skills"
  jenreh.registry/source-commit: "43748cbfd1e10079f1c194be5f68b1de59dc359b"
  jenreh.registry/source-license: "MIT"
  jenreh.registry/source-path: "plugins/jenreh-tools/skills/release"
  jenreh.registry/source-digest: "f9b9e43eccc2c7fd45f04f760209fbaea4ae88f15f3e288aef958de2f8d0a318"
  jenreh.registry/risk-tier: "standard"
  jenreh.registry/data-classification: "internal"
---

# Release

Ask the user which version bump to apply, then run `task release:build`.

Working tree (Claude Code fills this in; elsewhere run `git status --short`):
!`git status --short`

If it lists uncommitted changes, tell the user and ask whether to continue: the release
task commits and pushes.

If the skill was invoked with `patch`, `minor`, or `major`, use that and skip Step 1.

## Step 1 — ask

Use `AskUserQuestion` to ask:

**Question:** "Which version component should be bumped?"
**Header:** "Version bump"
**Options:**
- `patch` — backwards-compatible bug fixes and minor improvements (Recommended)
- `minor` — new backwards-compatible features
- `major` — breaking changes

## Step 2 — confirm current version

```bash
grep '^version = ' pyproject.toml | cut -d '"' -f2
```

Show the user: "Current version is X.Y.Z — bumping **[choice]** will release X.Y.Z+1. Proceed?"

If they say no, stop.

## Step 3 — run the release

```bash
task release:build -- <choice>
```

Stream the output so the user can see progress. The task will:
1. Bump the version in all tracked files
2. Commit and push
3. Generate an AI-written changelog from commits since the last tag
4. Create a GitHub release with that changelog

## Step 4 — report

After the task completes, show the new version and the GitHub release URL from the output.
