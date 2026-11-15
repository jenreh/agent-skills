# skill-creator

Create new skills, improve existing skills, and measure skill performance.
This skill is included in the [tools plugin](../../README.md); follow that
plugin's installation instructions for GitHub Copilot, Codex, or Claude Code.

## Workflow and format

Read [SKILL.md](SKILL.md) for the authoring, evaluation, and improvement workflow.
Skills use the [Agent Skills format](https://agentskills.io/specification):
a `SKILL.md` file with YAML metadata and instructions, with supporting scripts,
references, and assets alongside it. In this marketplace, use the project-local
[manage-agent-plugins skill](../../../../.agents/skills/manage-agent-plugins/SKILL.md)
to maintain plugin packaging, catalogs, and README listings.

## Included resources and requirements

- `agents/`: Instructions for grading, comparing, and analyzing evaluation results.
- `scripts/`: Python tools for validation, packaging, evaluation, and reports.
- `eval-viewer/`: A browser viewer for reviewing outputs and benchmark results.
- `assets/`: Templates for reviewing skill-selection examples.
- `references/`: Evaluation file schemas.

Authoring and manual evaluation use the tools available in the active client.
The automated description evaluation and optimization scripts invoke `claude -p`
and need Python plus an authenticated Claude Code CLI. Run module commands from
this skill's directory, as described in `SKILL.md`. Those scripts measure Claude
behavior; their results do not establish Copilot or Codex behavior.

When subagents are unavailable, follow the skill's manual evaluation guidance.
Use a browser to review generated HTML reports and evaluation feedback.
