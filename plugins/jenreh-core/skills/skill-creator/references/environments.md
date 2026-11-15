# Running skill-creator outside Claude Code

> Skill directory: `${CLAUDE_SKILL_DIR}` (the folder that contains SKILL.md). Paths below are relative to it.

## Claude.ai

In Claude.ai, the core workflow is the same (draft → test → review → improve → repeat), but because Claude.ai doesn't have subagents, some mechanics change. Here's what to adapt:

**Running test cases**: No subagents means no parallel execution. For each test case, read the skill's SKILL.md, then follow its instructions to accomplish the test prompt yourself. Do them one at a time. This is less rigorous than independent subagents (you wrote the skill and you're also running it, so you have full context), but it's a useful sanity check — and the human review step compensates. Skip the baseline runs — just use the skill to complete the task as requested.

**Reviewing results**: If you can't open a browser (e.g., Claude.ai's VM has no display, or you're on a remote server), skip the browser reviewer entirely. Instead, present results directly in the conversation. For each test case, show the prompt and the output. If the output is a file the user needs to see (like a .docx or .xlsx), save it to the filesystem and tell them where it is so they can download and inspect it. Ask for feedback inline: "How does this look? Anything you'd change?"

**Benchmarking**: Skip the quantitative benchmarking — it relies on baseline comparisons which aren't meaningful without subagents. Focus on qualitative feedback from the user.

**The iteration loop**: Same as before — improve the skill, rerun the test cases, ask for feedback — just without the browser reviewer in the middle. You can still organize results into iteration directories on the filesystem if you have one.

**Description optimization**: This section requires the `claude` CLI tool (specifically `claude -p`) which is only available in Claude Code. Skip it if you're on Claude.ai.

**Blind comparison**: Requires subagents. Skip it.

**Packaging**: The `package_skill.py` script works anywhere with Python and a filesystem. On Claude.ai, you can run it and the user can download the resulting `.skill` file.

**Updating an existing skill**: The user might be asking you to update an existing skill, not create a new one. In this case:
- **Preserve the original name.** Note the skill's directory name and `name` frontmatter field -- use them unchanged. E.g., if the installed skill is `research-helper`, output `research-helper.skill` (not `research-helper-v2`).
- **Copy to a writeable location before editing.** The installed skill path may be read-only. Copy to `/tmp/skill-name/`, edit there, and package from the copy.
- **If packaging manually, stage in `/tmp/` first**, then copy to the output directory -- direct writes may fail due to permissions.

---

## Cowork

If you're in Cowork, the main things to know are:

- You have subagents, so the main workflow (spawn test cases in parallel, run baselines, grade, etc.) all works. (However, if you run into severe problems with timeouts, it's OK to run the test prompts in series rather than parallel.)
- You don't have a browser or display, so when generating the eval viewer, use `--static <output_path>` to write a standalone HTML file instead of starting a server. Then proffer a link that the user can click to open the HTML in their browser.
- For whatever reason, the Cowork setup seems to disincline Claude from generating the eval viewer after running the tests, so just to reiterate: whether you're in Cowork or in Claude Code, after running tests, you should always generate the eval viewer for the human to look at examples before revising the skill yourself and trying to make corrections, using `generate_review.py` (not writing your own boutique html code). Sorry in advance but I'm gonna go all caps here: GENERATE THE EVAL VIEWER *BEFORE* evaluating inputs yourself. You want to get them in front of the human ASAP!
- Feedback works differently: since there's no running server, the viewer's "Submit All Reviews" button will download `feedback.json` as a file. You can then read it from there (you may have to request access first).
- Packaging works — `package_skill.py` just needs Python and a filesystem.
- Description optimization (`run_loop.py` / `run_eval.py`) should work in Cowork just fine since it uses `claude -p` via subprocess, not a browser, but please save it until you've fully finished making the skill and the user agrees it's in good shape.
- **Updating an existing skill**: The user might be asking you to update an existing skill, not create a new one. Follow the update guidance in the Claude.ai section above.

---

## Codex

Codex (CLI, IDE extension, ChatGPT desktop app, or Codex cloud) reads the same `SKILL.md`, so the whole workflow applies. These are the differences:

- **Skill directory**: Codex does not expand `${CLAUDE_SKILL_DIR}`. Use the folder that contains this skill's `SKILL.md` wherever the instructions name that placeholder, for example `python <that folder>/eval-viewer/generate_review.py`.
- **Where new skills go**: Codex discovers skills in `.agents/skills/<name>/` (the current folder, its parents up to the repo root) and in `~/.agents/skills/<name>/` for skills the user wants in every repo. Ask the user which one they want, and write the new skill there instead of `.claude/skills/`. A skill in `.agents/skills` is only visible to Claude Code if `.claude/skills` links to it.
- **Name clash**: Codex ships its own system skill called `skill-creator`. If the user wants this one, have them invoke it explicitly with `$skill-creator` and check that the loaded `SKILL.md` is this file.
- **Codex metadata**: give every new skill an `agents/openai.yaml` next to `SKILL.md`. Codex and the ChatGPT desktop app read it for the display name, a short description (64 characters or less), the icon and `policy.allow_implicit_invocation`. Codex ignores Claude's `disable-model-invocation`, so a skill that should only run on request also needs `allow_implicit_invocation: false`. See this skill's own `agents/openai.yaml` for the shape.
- **Running test cases**: Codex has subagents (the `multi_agent` feature, on by default; `spawn_agent` when `multi_agent_v2` is enabled). Spawn the with-skill and baseline runs in the same turn, as described in the main workflow. If subagents are switched off in the user's config, run the test cases one at a time yourself, as on Claude.ai, and skip the baselines.
- **Timing data**: Codex subagents do not report `total_tokens` and `duration_ms` the way Claude Code task notifications do. Record the wall-clock time you observe in `timing.json` and leave `total_tokens` out rather than guessing. The benchmark then compares time only.
- **Sandbox**: in the default `workspace-write` sandbox, Codex can only write inside the workspace. Keep the eval workspace (`<skill-name>-workspace/`) inside the project folder, or ask for approval before writing elsewhere. Starting the viewer's local HTTP server can also be blocked; if it fails, use `--static <output_path>` and give the user the file path.
- **Reviewing results**: the CLI and IDE extension usually run on the user's machine, so the browser viewer works as described. In Codex cloud there is no display: use `--static <output_path>` and handle feedback as in the Cowork section (the "Submit All Reviews" button downloads `feedback.json`). The rule from the Cowork section still holds: generate the viewer before you evaluate the outputs yourself.
- **Description optimization**: `run_eval.py` and `run_loop.py` call `claude -p` and check whether Claude Code triggered the skill. They measure Claude's triggering, not Codex's. If the `claude` CLI is installed, run them anyway: the description is shared, and a description that triggers well in Claude usually triggers well in Codex. If it is not installed, skip the scripts. For a rough Codex check, run a few of the trigger queries with `codex exec --json "<query>"` and look in the event output for a read of the skill's `SKILL.md`.
- **Blind comparison**: works if subagents are available; skip it otherwise.
- **Packaging**: `package_skill.py` works as is. For Codex users, a checked-in `.agents/skills/<name>/` folder or a plugin marketplace entry is often the more useful way to share the skill than a `.skill` file.
- **Updating an existing skill**: keep the original name and folder, as described in the Claude.ai section. Skills under `/etc/codex/skills` or bundled with Codex are read-only: copy them into `.agents/skills/` or `~/.agents/skills/` and edit the copy.
