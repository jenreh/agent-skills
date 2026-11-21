---
name: brand
description: Brand voice, visual identity, messaging frameworks, asset management, brand consistency. Activate for branded content, tone of voice, marketing assets, brand compliance, style guides.
argument-hint: "[update|review|create] [args]"
metadata:
  author: claudekit
  version: "1.0.0"
  jenreh.registry/id: "jenreh:jenreh-design"
  jenreh.registry/kind: "local"
  jenreh.registry/version: "0.3.0"
  jenreh.registry/source-marketplace: "jenreh/agent-skills"
  jenreh.registry/source-commit: "43748cbfd1e10079f1c194be5f68b1de59dc359b"
  jenreh.registry/source-license: "MIT"
  jenreh.registry/source-path: "plugins/jenreh-design/skills/brand"
  jenreh.registry/source-digest: "114ecd6600da19972e1eb970d59a1408cb408d40caa1782e9f3a933251e73ae5"
  jenreh.registry/risk-tier: "standard"
  jenreh.registry/data-classification: "internal"
  jenreh.registry/supported-channels: "beta,stable"
allowed-tools: Bash(node ${CLAUDE_SKILL_DIR}/scripts/*)
---

# Brand

> Skill directory: `${CLAUDE_SKILL_DIR}` (the folder that contains this SKILL.md; use that folder if your agent shows the placeholder unexpanded). Bundled script paths below are relative to it.

Brand identity, voice, messaging, asset management, and consistency frameworks.

## When to Use

- Brand voice definition and content tone guidance
- Visual identity standards and style guide development
- Messaging framework creation
- Brand consistency review and audit
- Asset organization, naming, and approval
- Color palette management and typography specs

## Quick Start

**Inject brand context into prompts:**
```bash
node ${CLAUDE_SKILL_DIR}/scripts/inject-brand-context.cjs
node ${CLAUDE_SKILL_DIR}/scripts/inject-brand-context.cjs --json
```

**Validate an asset:**
```bash
node ${CLAUDE_SKILL_DIR}/scripts/validate-asset.cjs <asset-path>
```

**Extract/compare colors:**
```bash
node ${CLAUDE_SKILL_DIR}/scripts/extract-colors.cjs --palette
node ${CLAUDE_SKILL_DIR}/scripts/extract-colors.cjs <image-path>
```

## Brand Sync Workflow

```bash
# 1. Edit docs/brand-guidelines.md (or use /brand update)
# 2. Sync to design tokens
node ${CLAUDE_SKILL_DIR}/scripts/sync-brand-to-tokens.cjs
# 3. Verify
node ${CLAUDE_SKILL_DIR}/scripts/inject-brand-context.cjs --json | head -20
```

**Files synced:**
- `docs/brand-guidelines.md` → Source of truth
- `assets/design-tokens.json` → Token definitions
- `assets/design-tokens.css` → CSS variables

## Subcommands

| Subcommand | Description | Reference |
|------------|-------------|-----------|
| `update` | Update brand identity and sync to all design systems | `references/update.md` |

## References

| Topic | File |
|-------|------|
| Voice Framework | `references/voice-framework.md` |
| Visual Identity | `references/visual-identity.md` |
| Messaging | `references/messaging-framework.md` |
| Consistency | `references/consistency-checklist.md` |
| Guidelines Template | `references/brand-guideline-template.md` |
| Asset Organization | `references/asset-organization.md` |
| Color Management | `references/color-palette-management.md` |
| Typography | `references/typography-specifications.md` |
| Logo Usage | `references/logo-usage-rules.md` |
| Approval Checklist | `references/approval-checklist.md` |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/inject-brand-context.cjs` | Extract brand context for prompt injection |
| `scripts/sync-brand-to-tokens.cjs` | Sync brand-guidelines.md → design-tokens.json/css |
| `scripts/validate-asset.cjs` | Validate asset naming, size, format |
| `scripts/extract-colors.cjs` | Extract and compare colors against palette |

## Templates

| Template | Purpose |
|----------|---------|
| `templates/brand-guidelines-starter.md` | Complete starter template for new brands |

## Routing

1. Parse subcommand from `$ARGUMENTS` (first word)
2. Load corresponding `references/{subcommand}.md`
3. Execute with remaining arguments
