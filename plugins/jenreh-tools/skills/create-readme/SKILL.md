---
name: create-readme
description: Create a comprehensive, well-structured README.md for the project. Use when asked to write, generate, or update a project README. Trigger on "create readme", "write readme", "generate readme", or /readme.
license: MIT
metadata:
  author: jens-rehpoehler
  version: "1.0"
  jenreh.registry/id: "jenreh:jenreh-tools"
  jenreh.registry/kind: "local"
  jenreh.registry/version: "0.1.0"
  jenreh.registry/source-marketplace: "jenreh/agent-skills"
  jenreh.registry/source-commit: "43748cbfd1e10079f1c194be5f68b1de59dc359b"
  jenreh.registry/source-license: "MIT"
  jenreh.registry/source-path: "plugins/jenreh-tools/skills/create-readme"
  jenreh.registry/source-digest: "f9b9e43eccc2c7fd45f04f760209fbaea4ae88f15f3e288aef958de2f8d0a318"
  jenreh.registry/risk-tier: "standard"
  jenreh.registry/data-classification: "internal"
allowed-tools: WebFetch(domain:raw.githubusercontent.com)
argument-hint: "[focus or audience]"
---

# Create README

## Role

Senior software engineer. READMEs must be appealing, informative, easy to read.

## Workflow

1. Review entire project and workspace — structure, stack, config, existing docs.
2. Fetch inspiration from these examples for structure, tone, content:
   - https://raw.githubusercontent.com/Azure-Samples/serverless-chat-langchainjs/refs/heads/main/README.md
   - https://raw.githubusercontent.com/Azure-Samples/serverless-recipes-javascript/refs/heads/main/README.md
   - https://raw.githubusercontent.com/sinedied/run-on-output/refs/heads/main/README.md
   - https://raw.githubusercontent.com/sinedied/smoke/refs/heads/main/README.md
3. If project logo/icon exists in `assets/` or repo root, use it in the header.
4. Write the README.

## Rules

- **GFM** (GitHub Flavored Markdown) throughout.
- Use [GitHub admonitions](https://github.com/orgs/community/discussions/16925) (`> [!NOTE]`, `> [!WARNING]`, etc.) where appropriate.
- Keep it concise — no filler sections.
- Do NOT include: LICENSE, CONTRIBUTING, CHANGELOG sections (dedicated files exist).
- Do NOT overuse emojis — use sparingly and only where they add clarity.
