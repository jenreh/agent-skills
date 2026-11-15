#!/usr/bin/env python3
"""Validate SKILL.md folders shared by Claude Code, Codex, and Copilot.

Self-contained: only depends on the stdlib plus a tiny inline frontmatter parser,
so it runs identically on a laptop and in CI without a network round-trip.

Skills are tuned for Claude Code first. Claude-specific frontmatter
(`allowed-tools`, `argument-hint`, `disable-model-invocation`, `context`, ...)
is fine: Codex and Copilot ignore keys they do not know. Rules enforced:
  * Every skills/<name>/ folder has a SKILL.md, and the flat skills/ view mirrors
    plugins/*/skills/* exactly.
  * SKILL.md starts with a YAML frontmatter block delimited by `---`.
  * Frontmatter has non-empty `name` and `description`; `name` matches the folder.
  * `description` + `when_to_use` fits Claude Code's 1,536-character listing cap,
    and avoids `<` / `>` (Claude's listing shows them as &lt; / &gt;).
  * Bundled scripts are called via `${CLAUDE_SKILL_DIR}/scripts/...`, so they
    resolve from a plugin install instead of the user's working directory.
  * `allowed-tools` does not pre-approve a bare `Bash` (every shell command; warning).
  * Codex / ChatGPT metadata lives in `agents/openai.yaml` (an extra file the
    other agents ignore). Each skill has one, its icons exist, and
    a mismatch with `disable-model-invocation` is reported.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

MIN_DESC = 20
MAX_LISTING = 1536  # Claude Code truncates description + when_to_use here
MAX_BODY_LINES = 500  # Claude Code guidance: keep SKILL.md under 500 lines; warn only
MAX_SHORT_DESC = 64  # Codex short_description; warn only

RELATIVE_SCRIPT = re.compile(r"\b(?:python3?|node|bash|sh) scripts/")
BARE_BASH = re.compile(r"(?:^|[\s,\[])Bash(?=$|[\s,\]])")

YAML_SCALAR = r"^\s+{key}:\s*[\"']?(.*?)[\"']?\s*$"

REPO_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_DIR / "skills"
PLUGINS_DIR = REPO_DIR / "plugins"


def parse_frontmatter(text: str) -> tuple[dict[str, str], int]:
    """Return (flat string map of top-level scalar keys, body_line_count).

    A deliberately small parser: we only need top-level scalar keys (name,
    description, possibly folded with `>` or `|`). Nested mappings (metadata:)
    are skipped, which is fine — we never assert on them.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing opening '---' frontmatter delimiter")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        raise ValueError("missing closing '---' frontmatter delimiter")

    data: dict[str, str] = {}
    i = 1
    while i < end:
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        # Only consider top-level keys (no leading indentation).
        if raw[0] in (" ", "\t"):
            i += 1
            continue
        if ":" not in raw:
            i += 1
            continue
        key, _, val = raw.partition(":")
        key = key.strip()
        val = val.strip()
        if val in (">", "|", ">-", "|-", ">+", "|+"):
            # Folded/literal scalar: gather subsequent indented lines.
            block: list[str] = []
            j = i + 1
            while j < end and (not lines[j].strip() or lines[j][:1] in (" ", "\t")):
                block.append(lines[j].strip())
                j += 1
            data[key] = " ".join(b for b in block if b)
            i = j
            continue
        data[key] = val.strip().strip("'\"")
        i += 1

    return data, len(lines) - end - 1


def yaml_value(text: str, key: str) -> str | None:
    """Value of an indented scalar `key:` in a small YAML file, or None."""
    match = re.search(YAML_SCALAR.format(key=re.escape(key)), text, re.MULTILINE)
    return match.group(1) if match else None


def check_openai_yaml(folder: Path, fm: dict[str, str], warnings: list[str]) -> list[str]:
    path = folder / "agents" / "openai.yaml"
    if not path.is_file():
        return [f"{folder.name}: no agents/openai.yaml (run scripts/link-plugins.sh)"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    implicit = yaml_value(text, "allow_implicit_invocation") or "true"
    manual_only = fm.get("disable-model-invocation", "").lower() == "true"
    # A mismatch can be deliberate (e.g. auto-invoke in Codex, manual in Claude),
    # so it is reported, not rejected.
    if manual_only and implicit != "false":
        warnings.append(f"{folder.name}: manual-only in Claude, but Codex may auto-invoke it")
    elif not manual_only and implicit == "false":
        warnings.append(f"{folder.name}: manual-only in Codex, but Claude may auto-invoke it")

    for key in ("icon_small", "icon_large"):
        ref = yaml_value(text, key)
        if ref and not (folder / ref).is_file():
            errors.append(f"{folder.name}: agents/openai.yaml {key} '{ref}' not found")

    short = yaml_value(text, "short_description") or ""
    if len(short) > MAX_SHORT_DESC:
        warnings.append(f"{folder.name}: short_description is {len(short)} chars (>{MAX_SHORT_DESC})")
    return errors


def validate_skill(folder: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    skill_md = folder / "SKILL.md"
    if not skill_md.is_file():
        return [f"{folder.name}: no SKILL.md"], []

    text = skill_md.read_text(encoding="utf-8")
    try:
        fm, body_lines = parse_frontmatter(text)
    except ValueError as exc:
        return [f"{folder.name}: {exc}"], []

    name = fm.get("name", "").strip()
    desc = fm.get("description", "").strip()

    if not name:
        errors.append(f"{folder.name}: frontmatter missing 'name'")
    elif name != folder.name:
        errors.append(f"{folder.name}: name '{name}' != folder name")

    if not desc:
        errors.append(f"{folder.name}: frontmatter missing 'description'")
    else:
        listing = desc + fm.get("when_to_use", "")
        if len(desc) < MIN_DESC:
            errors.append(f"{folder.name}: description too short ({len(desc)} chars)")
        if len(listing) > MAX_LISTING:
            errors.append(
                f"{folder.name}: description + when_to_use is {len(listing)} chars; "
                f"Claude Code truncates at {MAX_LISTING}"
            )
        if "<" in listing or ">" in listing:
            warnings.append(f"{folder.name}: '<' or '>' in description shows as &lt;/&gt; in Claude")

    body = text.split("---", 2)[2] if text.count("---") >= 2 else text
    for match in sorted(set(RELATIVE_SCRIPT.findall(body))):
        warnings.append(
            f"{folder.name}: '{match}' runs from the user's cwd; use "
            "'${CLAUDE_SKILL_DIR}/scripts/'"
        )
    if BARE_BASH.search(fm.get("allowed-tools", "")):
        warnings.append(f"{folder.name}: allowed-tools pre-approves every Bash command; narrow it")

    if (folder / "openai.yaml").exists():
        errors.append(f"{folder.name}: openai.yaml belongs in agents/openai.yaml")
    errors.extend(check_openai_yaml(folder, fm, warnings))

    if body_lines > MAX_BODY_LINES:
        warnings.append(
            f"{folder.name}: SKILL.md body is {body_lines} lines "
            f"(>{MAX_BODY_LINES}; consider moving detail to references/)"
        )

    return errors, warnings


def check_flat_view() -> list[str]:
    """The flat skills/ view must mirror plugins/*/skills/* exactly.

    Broken symlinks are invisible to the per-folder checks (is_dir() is False),
    so a skill moved between plugins would otherwise vanish silently.
    """
    errors: list[str] = []
    for entry in sorted(SKILLS_DIR.iterdir()):
        if entry.is_symlink() and not entry.exists():
            errors.append(f"skills/{entry.name}: broken symlink (run scripts/link-plugins.sh)")
    if PLUGINS_DIR.is_dir():
        for sdir in sorted(PLUGINS_DIR.glob("*/skills/*")):
            if sdir.is_dir() and not (SKILLS_DIR / sdir.name).exists():
                errors.append(
                    f"skills/{sdir.name}: missing link to {sdir.relative_to(REPO_DIR)} "
                    "(run scripts/link-plugins.sh)"
                )
    return errors


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print(f"ERROR: {SKILLS_DIR} not found", file=sys.stderr)
        return 2

    folders = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
    if not folders:
        print("ERROR: no skills found", file=sys.stderr)
        return 2

    all_errors: list[str] = check_flat_view()
    all_warnings: list[str] = []
    for folder in folders:
        errs, warns = validate_skill(folder)
        all_errors.extend(errs)
        all_warnings.extend(warns)

    for w in all_warnings:
        print(f"WARN  {w}")
    for e in all_errors:
        print(f"ERROR {e}")

    print(
        f"\nValidated {len(folders)} skills: "
        f"{len(all_errors)} error(s), {len(all_warnings)} warning(s)."
    )
    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
