---
name: code-simplifier
description: Simplify and refine recently changed code for clarity, consistency, and maintainability while preserving its exact behavior. Use when the user asks to simplify code, reduce nesting, remove redundant abstractions, improve naming, or apply the code-simplifier workflow. Follow the target project's language and conventions.
metadata:
  short-description: Simplify recently changed code for readability and maintainability while preserving behavior.
---

# Code simplifier

Improve clarity through focused edits that preserve existing functionality.
Prefer readable, explicit code over clever or compact rewrites. Work within the
requested files or recently modified code unless the user expands the scope.

## Establish the target

Use named files and functions first. Otherwise inspect current-session changes,
including staged and unstaged diffs and relevant untracked files. If no changed
code can be identified, ask for the target rather than rewriting unrelated files.

Read the affected functions and relevant callers. Establish inputs, outputs,
error handling, state changes, and async behavior before editing. Follow applicable
repository instructions, including AGENTS.md and CLAUDE.md, and the conventions
of the actual language and framework. Do not impose React or module-system rules
on Python code or other unrelated projects.

## Refine with restraint

- Reduce redundant branches, unnecessary nesting, and repeated calculations.
- Remove dead code and abstractions that add no useful responsibility or contract.
- Use names that explain intent and consolidate closely related logic.
- Remove comments that merely repeat the code; preserve explanations of intent,
  constraints, and non-obvious behavior.
- Prefer explicit conditionals over nested ternaries or dense one-liners.

Keep useful abstractions and separation of concerns. Avoid combining unrelated
responsibilities, removing error handling for style, or introducing features.
Preserve public signatures, return types, exceptions, logging, resource lifetimes,
and observable behavior. Keep edits within the target apart from necessary
import updates.

Compare old and new paths for evaluation order, short-circuiting, side effects,
mutation, lazy iteration, and exception timing. Leave ambiguous behavior intact
until the requirements or evidence resolve it. Fewer lines alone do not establish
an improvement.

## Verify and report

Review the resulting diff for unintended behavior changes and unrelated edits.
Use relevant existing checks when verification is requested or required by the
project's instructions. Reuse focused tests and appropriate formatting, lint,
or type checks; inspect available commands before assuming Taskfile targets.

Report missing tools or environment conditions that prevent verification.
Summarize the significant improvements with file locations, checks actually run,
and remaining limitations. Do not claim equivalence only because the code looks
simpler.

## Attribution

Adapted from Anthropic's code-simplifier agent. This version removes the fixed
model selection and follows the target project's conventions instead of
unconditional JavaScript and React rules. The original Apache 2.0 license is
retained at `licenses/anthropic-apache-2.0.txt` relative to the installed plugin
root.
