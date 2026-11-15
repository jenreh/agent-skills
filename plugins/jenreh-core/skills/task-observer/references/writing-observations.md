# Writing an observation — the inline id snippet and the annotated format

Load triggers: writing an observation where `scripts/new-observation.sh` cannot run; a frontmatter field whose meaning, allowed values or quoting is unclear; a guard in the inline snippet firing

`SKILL.md` ("How to Log") holds the rules and a compact template. This file holds
the two long blocks those rules point to. Where `scripts/new-observation.sh` can
run, it is the only write path and the snippet below is not used.

## Contents

- The id-derivation snippet
- The annotated file format

## The id-derivation snippet

The id is the highest of three values, plus one: the highest numeric prefix in
`observation-log/`, the highest in `observation-log/archive/`, and the number in
`observation-log/archive/.id-floor`. The same command first sweeps stale resolved
files into `archive/`; archival is a side effect of deriving the id, not a
separate duty (`SKILL.md`, "Archival on Write"). Run it immediately before EVERY
write.

```bash
d="[ABSOLUTE PATH]/skill-observations/observation-log"   # the pinned workspace path, never relative to the cwd; it may contain a space, so keep it quoted; bash, not sh
today=$(date +%F)          # archival rides inside this command (see below):
n_files=$(find "$d" -maxdepth 1 -name '[0-9]*.md' ! -empty | wc -l | tr -d ' ')   # a zero-byte file gives awk no line to count
seen=$(cd "$d" && awk 'FNR==1 {n++; nextfile} END {print n+0}' [0-9]*.md 2>/dev/null)   # files the sweep's glob reaches, counted apart from the sweep
[ "$n_files" -gt 0 ] && [ "${seen:-0}" -eq 0 ] && { echo "ARCHIVAL SWEEP BROKEN — $n_files files present, 0 examined"; exit 1; }
( cd "$d" && LC_ALL=C awk -v today="$today" 'FNR==1 {st=""; r=""; sub(/^\357\273\277/, ""); fm=/^---[[:space:]]*$/; if (!fm) nextfile; next}
    fm && /^---[[:space:]]*$/ {if (st ~ /^(actioned|declined|superseded)$/ && r ~ /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$/ && r < today) print FILENAME; nextfile}
    fm && /^status:/ {st=$ 2}   # spaced on purpose: a skill load with arguments rewrites a digit right after $ (validator warns)
    fm && /^resolved:/ {r=$ 2}' [0-9]*.md 2>/dev/null | while IFS= read -r x; do mv -n "$x" archive/ 2>/dev/null; if [ -e "$x" ]; then echo "NOTE: $x not archived — archive/$x exists or the move failed"; fi; done )   # one awk for the set, one mv per stale resolved file, never over an archived one; bash
floor=$(sed '1!d; s/[^0-9]//g' "$d/archive/.id-floor" 2>/dev/null); floor=$((10#${floor:-0}))   # digits only: a CRLF or padded floor still reads
ids=$(for p in "$d"/[0-9]*.md "$d"/archive/[0-9]*.md; do [ -e "$p" ] && printf '%s\n' "${p##*/}"; done | grep -oE '^[0-9]+')   # globs and builtins: no `ls` a profile alias can rebind
[ "$(printf '%s' "$ids" | grep -c .)" -eq "$(find "$d" "$d/archive" -maxdepth 1 -name '[0-9]*.md' | wc -l)" ] || { echo "ID COMMAND BROKEN — the listing and find disagree on the prefixed files"; exit 1; }
hi=$(printf '%s\n' "$ids" | sort -n | tail -1); hi=$((10#${hi:-0}))   # from the files alone; 10#: a zero-padded prefix is not octal
[ "$hi" -lt "$floor" ] && echo "NOTE: highest file id $hi is below .id-floor $floor — ids issued without a file; the new id goes above the floor"
next_id=$(( (hi > floor ? hi : floor) + 1 ))      # never below the floor, whatever the listing saw
f="$d/$(printf '%04d' "$next_id")-<slug>.md"      # the target path, built from the id just derived
[ -n "$(find "$d" -maxdepth 2 -name "$(printf '%04d' "$next_id")-*.md")" ] && { echo "COLLISION — id $next_id already used; re-derive"; exit 1; }   # guard the id PREFIX across active + archive, not the path
(set -C; : > "$f") || exit 1                        # noclobber: create, never truncate an existing file
printf '%s\n' "$next_id" > "$d/archive/.id-floor"   # AFTER the create: an id check that writes no file never moves the floor
```

The listing guard tells "the log says zero" from "I could not read
the log", the sweep's count does the same for the archival loop, the prefix
guard refuses a number already in use under any slug, and the `noclobber`
create refuses an existing path — write the body only after that create
succeeds, with the editing tool, or a QUOTED heredoc (never unquoted) where
commands arrive unaltered: `references/observation-log.md` ("Editing an existing observation").
Load `references/observation-log.md` ("The guard line, the sweep's count
and the noclobber create") when any of them fires.

## The annotated file format

```markdown
---
id: 0
title: "Short descriptive title"
status: open            # open | actioned | declined | superseded | parked
type: open-source       # open-source | internal
skill: [skill-a, skill-b]        # existing skills this improves —
                                 # always a list, first entry primary, may be
                                 # empty: []; quote an entry holding a colon
proposes_skill: []               # new skills this argues for, by working
                                 # name; an observation can fill either
                                 # list or both
target_file: []                  # when the right home is not a skill at all:
                                 # the path the fix will be written to
siblings_checked: "family-name: a, b — a added; b excluded (b/SKILL.md §2)"
                                 # MANDATORY, never blank: the family name,
                                 # each member's verdict — every exclusion
                                 # names the section read in it, or the
                                 # literal assumed; none only where the
                                 # target belongs to no family
area: "which part of the skill or workflow"
date: YYYY-MM-DD
session_context: "what task was being worked on"
parked_until:           # MANDATORY when status is parked, empty otherwise:
                        #   one line naming the condition that unparks it
resolved:               # date resolved; leave empty while OPEN
resolution:             # what was done — set only when actioned/declined/superseded
reference:              # optional — path to saved session-local evidence
commands_verified:      # MANDATORY when the body quotes a command or predicate —
                        #   each `run` with its result, or `NOT RUN` with why; else none
---

**Issue:** [What happened — specific enough to understand weeks later
without the original conversation.]

**Suggested improvement:** [Concrete change. For existing skills, name the
section or rule; for new skills, scope and key components.]

**Principle:** [The generalisable takeaway — the most important field.]
```

**Every prose value is double-quoted, and so is a list entry holding a
colon.** `title`, `siblings_checked`, `area`, `session_context`,
`resolution`, `parked_until` and `reference` carry free text, and free
text contains `: ` as the common case; unquoted, that is invalid YAML —
the scan flags `key: a: b` as suspect; every consumer that PARSES it throws.
A plugin-scoped name in a `[]` list (`[plugin:name]`) loads under one
YAML parser and fails under another: quote it (`"…"`, inner `"` as `\"`);
bare kebab-case names, dates and status words stay bare. Load
`references/observation-log.md` ("Frontmatter fields") for the drift.
