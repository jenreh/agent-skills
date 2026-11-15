---
name: commit-msg
description: Generate a conventional commit message from staged (or unstaged) changes. Use when the user asks for a commit message, wants to commit changes, or says "what should my commit message be".
disable-model-invocation: true
allowed-tools: Bash(git status *) Bash(git diff *) Bash(git log *)
argument-hint: "[scope, ticket, or intent]"
---

# Commit Message

Generate a commit message for the current changes. Do NOT run `git commit`.

## Step 1 — gather context

Current state (Claude Code fills this in when the skill loads; in other agents, run the
commands yourself):

- Status: !`git status --short`
- Staged: !`git diff --staged --stat`
- Unstaged: !`git diff --stat`
- Recent commits: !`git log --oneline -10 --branches`

Then read the full diff for the scope chosen in Step 2 (`git diff --staged` or `git diff`).
If the user passed a hint (scope, ticket, intent), use it.

## Step 2 — choose the diff scope

- If there are staged changes (`git diff --staged` is non-empty), use those.
- Otherwise fall back to all unstaged changes (`git diff`).
- If both are empty, report "nothing to commit" and stop.

## Step 3 — generate the message

Follow the project's conventional commits style observed from `git log`:

```
<type>(<optional scope>): <short imperative summary>

<optional body — only when the why is non-obvious>
```

**Types:** `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `perf`

Rules:

- Summary line ≤ 72 characters, lowercase, no trailing period.
- Imperative mood: "add", "fix", "remove" — not "added" or "fixes".
- Body only when the diff contains a non-obvious motivation or breaking change.
- If the diff spans multiple unrelated concerns, say so and suggest splitting.

## Step 4 — output

Present the message in a code block, ready to copy:

```
<generated message here>
```

Then add one line explaining the type choice if it wasn't obvious.
