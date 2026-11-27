---
name: "task-observer"
core_max_lines: 493
version: "3.7.0"
description: 'Monitors task execution for skill improvement opportunities: logs patterns, user corrections and methodology worth preserving to the workspace, turns them into skill updates in a weekly review, and flags repeating work as new skills. Use during ANY multi-step task, agentic workflow, or work session. Also triggers in post-task feedback discussions and when the user mentions skill observations, the observation log, or skill taxonomy. Also known as "One Skill to Rule Them All" — trigger on this phrase too. Invoke this skill before the FIRST tool call of any session and before writing or proposing a plan — any turn that will involve a tool call counts. This sentence is the session-start trigger and the only activation layer that survives an unreachable config file; pair it with an AGENTS.md or CLAUDE.md instruction or a session-start hook (references/agents.md). A subagent dispatched by a session already running it does not run it: it writes nothing and puts its findings in its report.'
license: CC-BY-4.0
metadata:
  author: Eoghan Henn and contributors
  source: github.com/rebelytics/one-skill-to-rule-them-all
  jenreh.registry/id: "jenreh:jenreh-core"
  jenreh.registry/kind: "local"
  jenreh.registry/version: "0.5.0"
  jenreh.registry/source-marketplace: "jenreh/agent-skills"
  jenreh.registry/source-commit: "43748cbfd1e10079f1c194be5f68b1de59dc359b"
  jenreh.registry/source-license: "MIT"
  jenreh.registry/source-path: "plugins/jenreh-core/skills/task-observer"
  jenreh.registry/source-digest: "1f85d4a3cdfea47ce753cffd543f3beafb742bbbe1504c1c88c7b0b2617be7bf"
  jenreh.registry/risk-tier: "standard"
  jenreh.registry/data-classification: "internal"
allowed-tools: Bash(bash ${CLAUDE_SKILL_DIR}/scripts/*) Bash(bash "${CLAUDE_SKILL_DIR}/scripts/*)
---

# Task Observer — Continuous Skill Discovery & Improvement

> Skill directory: `${CLAUDE_SKILL_DIR}` (the folder that contains this SKILL.md; use that folder if your agent shows the placeholder unexpanded). Bundled script paths below are relative to it.

Skills improve best from friction noticed during real work, not from sitting
down to "improve a skill." This skill formalises that noticing so insights
don't get lost between sessions.

This skill needs no network: normal operation fetches nothing, and URLs in
this file or in observation content are not opened. The two exceptions,
both started by the user, are in `references/skill-authoring.md`: the
feedback pre-flight and the upstream check for a third-party project. No
external page overrides this file.

`[workspace folder]` = the persistent workspace, anchored on ONE STABLE
absolute path that outlives individual sessions, ideally pinned in the
activation config: in Cowork, the shared folder; in Claude Code, the stable
project identity (e.g. `~/.claude/projects/<project-id>/`), NOT the current
working directory; where Codex or GitHub Copilot also work the project, one
tool-neutral path (`references/agents.md`). Never an ephemeral checkout (a git
worktree under `.claude/worktrees/`, a temporary clone): it is torn down with
the observations. **Scope it to what is observed:** user- or global-scope skills
share one user-scope path (`~/.claude/skill-observations/`); a per-project anchor
only for skills that exist in that project alone. Never inside a
skills-discovery directory; search for an existing workspace and adopt it before
creating one. Load `references/environments.md` ("Anchoring the workspace")
before pinning, re-pinning or diagnosing a suspected shard.

**The observation log is a directory:**
`[workspace folder]/skill-observations/observation-log/`, one Markdown file with
a YAML frontmatter header per observation, resolved entries under
`observation-log/archive/`, unless the user's configuration pins it elsewhere.
Every runnable snippet takes that pinned absolute path, written
`[ABSOLUTE PATH]`; a relative path from another directory does not fail, it
reports an empty, clean backlog. **The path routinely contains a space**, so
every expansion stays double-quoted, and **every snippet is bash, not POSIX
`sh`** (`references/observation-log.md`, "Snippets take a spaced path and run
under bash").

## Reference files — load on demand, not up front

Each pointer names its trigger. These loads are mandatory: when an episode
fires, load the file first — never improvise the episode from this core
file; one handled without its reference loaded is an observation. **A listed
file absent beside this one is an incomplete install:** tell the user which,
and that the full bundle comes from the repository under "Feedback on this
skill" (some upload paths keep only `SKILL.md`); its episodes do not run.

- `references/weekly-review.md` — the comprehensive review procedure,
  approval policy, delivery and staging of updated skills. **Load when a
  review triggers or the user asks for one.**
- `references/skill-authoring.md` — taxonomy, structure, licensing,
  attribution, confidentiality layers, live-file editing, relocation checks.
  **Load before writing any `SKILL.md` or skill file, setup work included.**
- `references/observation-log.md` — storage layout, frontmatter fields,
  helper snippets, archival details, and the reasoning behind the rules.
  **Load when setting up the log for the first time, when archiving, when
  an id or frontmatter looks wrong, or before changing how anything reads
  the log** — and wherever a pointer below names it.
- `references/writing-observations.md` — the inline id snippet and the
  annotated frontmatter template. **Load when `scripts/new-observation.sh`
  cannot run, or a field's meaning or quoting is unclear.**
- `references/acting.md` — when and how to act on an observation, and the
  bookkeeping. **Load before acting on, resolving, dismissing or citing any
  observation.**
- `references/signals.md` — what is and isn't worth logging. **Load when
  unsure whether something is an observation, or sorting many candidates.**
- `references/environments.md` — activation and config setup, compaction
  behaviour, bundle manifest, handoff-doc mode for storage-less
  environments. **Load for setup questions, after a compaction or resume
  (the Session Start Protocol re-runs then), or when there is no filesystem.**
- `references/agents.md` — running under Codex or GitHub Copilot, or one
  workspace shared by several agent tools: instruction files, skill paths,
  hooks, sandbox write grants. **Load when the agent is not Claude, or when
  a Claude-specific step has no equivalent here.**
- `references/migration.md` — the one-time scripted conversion of a
  pre-3.0 single-file `log.md`. **Load only when the Session Start
  Protocol detects a legacy log.** Fresh installs never read it.
- `references/starter-principles.md` — an optional, provenance-stripped
  seed set of generic cross-cutting principles. **Load only when the
  starter-set reconciliation is due** (Session Start step 1: the
  `starter-principles-reviewed.txt` marker is absent or names an older
  starter set) — never on an ordinary session start.

## Session Start Protocol

1. **Storage.** One `ls` of the pinned path is the existence check and the
   workspace-mount probe, carried INSIDE the session's first batched tool
   call together with the session-start skill loads (`references/environments.md`,
   "The probe rides inside the first batched call"). If it fails, the first
   response is the environment's folder-picker tool (Cowork:
   `request_cowork_directory`), not handoff-doc mode, which is only for
   environments with no filesystem at all. A permission-classifier refusal of
   that request falls under the **How to Log** denial rule (one identical retry,
   told to the user, never another tool). Refused again, or no folder-picker or
   device-bridge tool after one tool search: load `references/environments.md`
   ("No link to the user's computer") and keep its order. Never assert the
   mount's state from an environment flag, a config file in context or an
   earlier turn: that needs a probe in the same turn. **A successful probe does
   not mean the activation config fired:** on turn 1 load the session-start
   skills directly, and read the config file yourself if it is not in context
   (`references/environments.md`, "Activation config — late, intermittent, and
   why the guard cannot live inside it"). If the workspace sits under an
   ephemeral path (`.claude/worktrees/`, a temporary clone,
   `scratch-workspaces/`), warn and re-anchor on a stable path; where none
   resolves, use report-back mode (`references/environments.md`, "Claude Code
   Projects"). Then RUN the one idempotent command in
   `references/observation-log.md` ("Workspace creation"); it refuses a pre-3.0
   `log.md` layout (load `references/migration.md` first). Never create the
   artefacts by hand. Then the **starter-set reconciliation**, due when
   `skill-observations/starter-principles-reviewed.txt` is absent or older than
   the set in `references/starter-principles.md`: load that file and follow its
   **Reconciliation** section; never pre-populate silently. Name the skill's
   frontmatter `version:` in the start-up lines (read from the file, never
   fetched) and list its `references/` and `scripts/`: a file the core names
   that is absent is reported there ("Reference files").
2. **Scan.** Read only the frontmatter of each file in `observation-log/`
   (the header between the first two `---` lines, never the bodies) and hold
   `status`, `skill`, `proposes_skill`, `title` and the active principles'
   headings (`principles=` in the checkpoint line) in awareness; don't surface
   them unprompted. This scan does not satisfy the per-skill check at each skill
   load (`references/observation-log.md`, "Why the session-start scan does not
   satisfy the per-skill check"). **An empty scan over a log known to be
   non-empty is a broken command**: the script's guard halts on it
   (`references/observation-log.md`, "An empty scan over a non-empty log is a
   broken command").

   ```bash
   bash "${CLAUDE_SKILL_DIR}/scripts/session-start-scan.sh" "[ABSOLUTE PATH]"
   ```

   Read its output whole, never through `tail`, `head` or `grep`. **Only the
   print can be refused, so it runs last**; a refused print is never an empty
   log (`references/observation-log.md`, "A refused print is not an empty log").

3. **Review trigger.** Read `skill-observations/last-review-date.txt`: a date
   = when the last review ran; `never` = none yet; a missing file is abnormal,
   recreate it with `never`. A `review-started.txt` not reading `completed`, or a
   scheduler reporting a later run, means "fired YYYY-MM-DD, no review
   recorded": treat the review as due. If due (`never` or 7+ days) AND there are
   OPEN observations: in an interactive session offer it in one line, once per
   session, and carry on with the user's task unless they opt in. Up to ~15 open,
   offer the full review; above that, a bounded slice ("the 10 oldest", "just
   the ones targeting <skill>") stating how many are open and roughly how many
   distinct findings they represent (`references/weekly-review.md`). Only a
   scheduled/autonomous run loads `references/weekly-review.md` and runs the
   review unprompted; a session whose output a caller owns does neither
   (`references/environments.md`, "Sessions whose output channel is owned by a
   caller").
4. **Activation.** Once per session: if no AGENTS.md, CLAUDE.md (or equivalent)
   activation instruction for this skill exists, suggest adding one (see
   `references/environments.md`); after a scan `GAP:` line, open with the
   gap and the missing instruction, plainly. Skip if configured. This step
   runs only once the skill is invoked, so it verifies a working setup and
   cannot detect a missing one — it is not the safety net for a
   never-activated install; the outside checks are in that reference.
5. **Concurrency.** There is no shared log file to guard: each observation
   is its own file, so creating one never collides with another session's
   entry; re-read one before changing its _status_ (How to Log).
6. **Targets and staged work.** Resolve each distinct `skill:` value in the
   scanned frontmatter against the installed skill set and mention, in one line,
   any that no longer resolve or resolve but cannot run
   (`references/skill-authoring.md`, "Runtime prerequisites"); say what you
   resolved against. If `skill-updates/` holds anything, reconcile it before
   announcing it: `diff -rq` each staged copy against live, classify it, and name
   every directory no manifest entry covers (`references/weekly-review.md`,
   "Staged-work reconciliation gate", load it first). Then say "N staged updates
   awaiting review" in one line.
7. **First run, or a named past session.** If the log is empty and the
   project has history (handover or decision docs, commit history, test
   scripts, a notes or memory directory, an existing CLAUDE.md), offer a
   one-off backfill pass over those artefacts; when the user names a
   finished session, run the same pass scoped to it. Entries cite the
   durable artefact (file and section) in `session_context`, never a
   session. Procedure: `references/environments.md` ("First-run backfill").

## When to Observe

Active for the entire task session — execution, post-task feedback, review
discussion, meta-discussion about skills or methodology, and strategy
conversations about how work should be done. **The observation mindset
does not deactivate when the conversation shifts from doing the work to
discussing it**; review-phase feedback is often the highest-signal input.
Inactive only for casual conversation and quick factual questions with no
tools or deliverables involved.

## What to Watch For

**New skill:** a reusable multi-step workflow, a methodology the user
explains that no skill captures, a recurring task type, a process the user
describes as "I always do it this way". **Improve a skill:** the agent
violates a documented rule (the skill needs enforcement, not louder rules);
a user correction reveals a missing rule or edge case; a better workflow or
technique emerges than the skill recommends; a wrong assumption; new
tooling obsoletes a step; a principle that applies to other skills too.
**Simplify a skill:** a section never relevant across many sessions, a rule
from a single unvalidated observation, contradictory rules, a rule the
agent consistently fails to follow — convert to structural enforcement or
remove. Full catalogue with examples: `references/signals.md`.

**An unresolved defect is an observation, at a bounded point.** When a
defect that is not itself the deliverable takes a second hypothesis, load
`references/signals.md` ("An unresolved defect is an observation, at a
bounded point") and log the evidenced problem report, not a fifth probe.

**Do NOT log:** one-off corrections that don't generalise; preferences
already captured in a skill; tool bugs unrelated to methodology;
observations needing proprietary client information to be useful in an
open-source skill (unless an internal skill is the right home). When
unsure, run `references/signals.md` ("The generalisability test"): mostly
no → task context, not an observation. Before minting a `proposes_skill`
name, reuse a fitting existing candidate — independently logged proposals
for one skill rarely share a name.

**Check for a restatement before writing.** List the open observations that
name the same target skill (the session-start scan holds their titles) and read
those titles. If the finding is the same one restated (same rule, same failure
shape, a different example), extend the existing entry: append the instance,
add the session to `session_context`, widen `title:`. On one measured log, about
forty of ninety-one open entries were one finding restated.

**Validate the target at write time.** `skill:` names a skill that exists
now and performs the operation the Issue describes, written as its bare
name (`plugin:name` only where two skills share it). If the
right home is not a skill — an instructions file, a memory note, the
register a routine reads — put that path in `target_file:`, not the
nearest skill; a skill not yet built goes in `proposes_skill:`.

**Check the target's siblings at write time, and record that you did.**
Resolve the target against `skill-observations/skill-families.md`; for each
sibling either add it to `skill:` or say in the body why it does not apply.
Fast test: **could this sentence survive having the tool's or subject's name
removed?** If yes, it belongs to every sibling. Record the outcome in the
mandatory `siblings_checked:` field, including "checked — instance-specific, no
propagation": only the recorded field makes a missing judgement visible. Load
`references/observation-log.md` ("Skill families and the sibling check") for the
registry spec and the fallback when no registry exists.

**Log your own rule violations.** Breaking a rule that a skill or a project
instruction file documents is a first-class observation, not an
embarrassment to move past: it is the only evidence that the rule's
_enforcement_ is too weak, and nobody but the agent can see it. Log it in
the same turn, and name which protection was actually in play — written
down, loaded into context, or backed by a checkpoint. The restatement check
above surfaces the earlier entry when one exists, so the count arrives
without extra work.

**Second violation of the same rule: stop proposing text.** A rule that has
failed twice with no intervening `actioned` fix has a protection problem,
not a wording problem. From the second occurrence the proposed improvement
must be a structural barrier — a hook that refuses the call, a lint rule, a
default that makes the wrong path unavailable — never a clearer sentence, a
bolder warning, or the same rule moved somewhere more prominent. Load
`references/signals.md` ("Second violation — why a barrier, not a
rewording") before proposing either.

## How to Log

Write the observation file **within the same turn or the next, without
interrupting the user's task** — never batch mentally for later; the act
of writing is the enforcement mechanism.

**Mandatory checkpoint after every 3rd completed todo item.** After marking
the 3rd, 6th, 9th (etc.) item complete you must **write to disk** — not
merely ask yourself whether anything is pending. Write any pending
observation files, or append a one-line `no observations` acknowledgement
to `skill-observations/checkpoints.log`. The required action is a concrete
write; a remembered "ask whether" is not enforcement. Roughly every third
completion is the rule; the count need not be precise. (Exception for a
priced-write workspace: `references/environments.md`.)

**A denied or failed write is not a read-only log.** A transient failure (I/O
error, timeout, tool error with no permission decision) gets one retry. A
permission or classifier denial is authoritative: tell the user in one line what
was denied and why it mattered, then carry the observations in report-back or
handoff mode (`references/environments.md`); at most one identical retry of a
classifier denial, never a different tool. A mode that refuses every write by
design: defer, don't retry (`references/environments.md`, "A mode that forbids
every write by design").

**Deliverable-event flush.** Whenever a unit of work is declared complete
to a human — a file handed over, a render, a staged skill file, a
completion notification, a final report, a finished todo batch — write any
pending observation files at that moment. These checkpoints already
involve a tool call, so the flush rides on work you were doing anyway.
(Why both checkpoints are writes rather than questions:
`references/observation-log.md`.)

**A failed write to an external system is a flush trigger in its own
right**: a tool result carrying `permission stream closed`, `permission
denied`, or a harness interrupt. Flush before doing anything else with the
failure (observed: an unattended run hit a permission error on its first
external write and ended with no report and no logged observation).

**Two gaps this pairing still leaves** (no todos, and "major deliverable" is
self-assessed): before adding or changing any enforcement trigger, load
`references/observation-log.md` ("Two gaps the checkpoint pairing still leaves
— and the rule behind both").

**Id and filename.** Each observation is `NNNN-short-slug.md` (zero-padded id

- a kebab-case slug from the title); id = max(active prefixes, archive prefixes,
  `observation-log/archive/.id-floor`) + 1, derived immediately before EVERY write,
  including the first and only one of a session. An earlier read of the log is not
  a substitute, and the id the session-start scan printed is never an input to a
  write. Where a helper can run,
  `bash ${CLAUDE_SKILL_DIR}/scripts/new-observation.sh <slug> "[ABSOLUTE PATH]"`
  is the only write path: it sweeps archival, derives the id, guards it, creates
  the file with `noclobber`, and prints the created path. Elsewhere, load
  `references/writing-observations.md` ("The id-derivation snippet") and run its
  snippet. Write the body only after the create succeeds, with the editing tool or
  a QUOTED heredoc (`references/observation-log.md`, "Editing an existing
  observation"). Load `references/observation-log.md` ("Run the snippet
  immediately before every write") when skipping feels reasonable or two files
  share an id, and ("The guard line, the sweep's count and the noclobber create")
  when a guard fires.

**Resolve each id at its own write time** — run the snippet before EACH
file, never pre-compute a range, and put the value it printed into both the
filename and the `id:` field. Load `references/observation-log.md`
("Resolve each id at its own write time") before batching or parallelising.

**An empty or zero result is a claim about the instrument** until an
independent probe shows the population is empty; and **a structural probe that
comes back empty where content existed before is a stop signal, not a create**:
HALT and re-probe, never let an append recreate a missing target. Load
`references/observation-log.md` ("Every instrument gets the same guard") before
writing any new scan, count, grep or query over the log, and ("A structural
probe that comes back empty is a stop signal") before writing after such a
probe.

**File format.** YAML frontmatter (the metadata every scan reads) followed
by the Issue → Improvement → Principle body. **The frontmatter is mandatory;
always write `status: open` and a non-empty `siblings_checked:` at creation
time**: reviews treat a missing `status` as OPEN, and a missing
`siblings_checked:` as logged without a sibling check. `parked_until:` is
mandatory when `status: parked`; `commands_verified:` when the body quotes a
command. Field meanings: `references/writing-observations.md` ("The annotated
file format").

```markdown
---
id: 0
title: "Short descriptive title"
status: open # open | actioned | declined | superseded | parked
type: open-source # open-source | internal
skill: [skill-a, skill-b]
proposes_skill: []
target_file: []
siblings_checked: "family-name: a, b — a added; b excluded (b/SKILL.md §2)"
area: "which part of the skill or workflow"
date: YYYY-MM-DD
session_context: "what task was being worked on"
parked_until:
resolved:
resolution:
reference:
commands_verified:
---

**Issue:** [What happened, specific enough to understand weeks later.]

**Suggested improvement:** [Concrete change; name the section or rule.]

**Principle:** [The generalisable takeaway, the most important field.]
```

**Every prose value is double-quoted, and so is a list entry holding a colon**
(`[\"plugin:name\"]`); bare kebab-case names, dates and status words stay bare.
Load `references/observation-log.md` ("Frontmatter fields") for the drift.

**`parked` means decided, not pending:** sound but blocked on an external
precondition, out of the work queue, never archived, `parked_until:`
mandatory and naming a condition that can actually occur. Load
`references/observation-log.md` ("The `parked` status — decided, not
pending") before setting, reviewing or unparking a parked status.

**Context preservation:** if an observation depends on session-local data,
save it into the workspace first and set `reference:` to a durable path a
fresh session can resolve. Load `references/observation-log.md` ("Context
preservation — the `reference:` field") when setting `reference:`.

**Confidentiality at logging time:** for `type: open-source` observations,
the Issue/Improvement fields may reference specifics for context, but the
Principle must be fully generalised — no client names, domains, or details
traceable to a real project. Full confidentiality layers:
`references/skill-authoring.md`.

**Changing an existing observation:** re-read that one file, edit only the
frontmatter fields you are changing (`status`, `parked_until`, `resolved`,
`resolution`), never batch-rewrite the directory. Archival is a plain `mv`.

## Referencing Observations

Cite an observation by the `id` field in its frontmatter (= the `NNNN-`
filename prefix), never a `grep -n` line number, which is positional metadata;
in chat write every surfaced id as `observation NNNN`, never a bare number. An
id must fall inside the range across `observation-log/`, `archive/` and
`.id-floor`; one far outside it is a line number misread as an id.

## Taxonomy (quick version)

**Open-source** — client-agnostic, methodology-driven, useful to other
practitioners. **Internal** — contains user/client/project specifics or
personal preferences. Default to open-source when it could go either way,
stripping specifics. The boundary is also a confidentiality boundary and
the two errors are not symmetric — over-classifying as internal costs only
reach, under-classifying can leak — so when genuinely uncertain, prefer
internal and promote later. Full requirements (attribution, licensing,
structure): `references/skill-authoring.md`.

## Archival on Write

Archival rides inside id derivation (the helper or the snippet), so it runs
whenever an id is issued and cannot be skipped without failing the write; the
scheduled review archives too, as a backstop. A file is archived when its own
frontmatter says `status: actioned`, `declined` or `superseded` AND has a
`resolved:` date **before today**; files resolved today stay until the next day.
A resolved file with no readable `resolved:` date gets today's date instead of
being archived. One file per `mv`; a bulk move outside the sweep is verified by
conservation: `references/observation-log.md` ("Archival").

## Surfacing Protocol

Default: at end of session, as a grouped summary — improvements grouped by
skill, new-skill candidates listed separately; for each, one sentence plus
suggested type; ask which to act on. Surface earlier when an observation
needs user input to be complete, when a skill is actively producing wrong
output, or when observations cluster on one skill.

**Deferral wears a second disguise: not a promise, but an argument** ("let's
gather more data first"). Before writing any "later" into a
recommendation, load `references/signals.md` ("Deferral disguised as
diligence") and name which specific observation would change the decision
and when it could arrive.

**Default to log-and-defer.** Surfacing an observation is not an invitation
to act on it: state that it is logged for the next review, and stop.
Reserve in-session application strictly for the triggers under "Acting on
Observations". Do NOT routinely offer a binary "apply now vs leave for next
review" choice; for users who run regular reviews that offer is unwanted
friction, and if a user has said they always defer, suppress it entirely.

**Log-and-defer means the observation is the sole carrier of the change.**
Applying an insight to the work in front of you is fine; writing the rule
anywhere a later run reads it (a state file, a prompt, a handoff doc, an
instruction file) is acting on it. Load `references/acting.md` ("Log-and-defer:
the observation is the sole carrier") before writing any such bridge.

**Self-check before surfacing:** observations were logged throughout the
whole session (including discussion phases) without interrupting the task; each follows
Issue → Improvement → Principle; each is typed; existing-skill items name
the section; no open-source Principle contains client-identifying info;
every file carries `status:` and a non-empty `siblings_checked:` (if one lacks
it, do the sibling check now, never back-fill `none`); every id the summary
names is one a create printed this session, re-listed this turn, never recalled.

## Acting on Observations

**Load `references/acting.md` before acting on, resolving, dismissing or citing
any observation.** The short form:

- Act only in (1) the comprehensive review, (2) an explicit request that NAMES
  THE ARTEFACT ("update the X skill", "act on observation #N"), (3) an
  in-session correction when a skill produces wrong output. "From now on…" names
  a behaviour, not an artefact: log it. Otherwise: log, don't act.
- A harness's skill-save or skill-proposal control installs; it does not stage.
  Never use it in a workspace that stages under `skill-updates/`.
- Read the full body before resolving; a title is an index entry.
- Every change goes to a staged copy from a fresh read of the live file, handed
  to the user to install. Substantial changes and new skills:
  `references/skill-authoring.md` first.
- **Set the status in the same turn you act** (`status: actioned`,
  `resolved:`, `resolution:`), including for fixes that landed as ordinary work.

## Feedback on this skill

If the user has methodology feedback, offer to draft a report for
github.com/rebelytics/one-skill-to-rule-them-all, running the feedback
pre-flight in `references/skill-authoring.md` first; if the problem is the
agent not following the skill's rules, acknowledge and correct it instead.
