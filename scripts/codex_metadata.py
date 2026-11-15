#!/usr/bin/env python3
"""Generate the Codex / ChatGPT metadata layer next to the portable skills.

Codex and the ChatGPT desktop app read three optional files that every other
agent ignores, so adding them never changes a SKILL.md:

  * <skill>/agents/openai.yaml     display name, short description, icon, and
                                   policy.allow_implicit_invocation
  * <plugin>/plugin.json           extensions.com.openai.interface (written by
                                   scripts/link-plugins.sh, not here)
  * .agents/plugins/marketplace.json  Codex's marketplace format

This script (stdlib only, called at the end of scripts/link-plugins.sh):

  1. copies the shared icon (assets/<ICON>) into every plugin's assets/ and
     into every skill whose openai.yaml references it, so each plugin and each
     skill folder stays self-contained when it is installed on its own;
  2. creates a stub agents/openai.yaml for a skill that has none. Existing files
     are hand-maintained and never overwritten. The stub's
     allow_implicit_invocation mirrors Claude's `disable-model-invocation`;
  3. rewrites .agents/plugins/marketplace.json from the plugin manifests.

scripts/validate_skills.py and scripts/validate_plugins.py check the result.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLUGINS = REPO / "plugins"
ICON = "jenreh.svg"
ICON_SRC = REPO / "assets" / ICON
ICON_REF = f"./assets/{ICON}"
BRAND_COLOR = "#4476AF"
MARKETPLACE_NAME = "jenreh"
MARKETPLACE_TITLE = "jenreh agent skills"
MAX_SHORT = 64

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_skills import parse_frontmatter  # noqa: E402


def sync_file(src: Path, dst: Path) -> bool:
    """Copy src to dst when missing or different. Returns True if written."""
    if dst.is_file() and dst.read_bytes() == src.read_bytes():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    return True


def display_name(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-"))


def short_description(fm: dict[str, str]) -> str:
    """First sentence of the description, cut to MAX_SHORT characters."""
    text = fm.get("description", "").strip()
    sentence = re.split(r"(?<=[.!?])\s", text, maxsplit=1)[0].rstrip(".")
    if len(sentence) > MAX_SHORT:
        sentence = sentence[: MAX_SHORT - 1].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return sentence


def stub_yaml(skill: Path) -> str:
    fm, _ = parse_frontmatter((skill / "SKILL.md").read_text(encoding="utf-8"))
    implicit = fm.get("disable-model-invocation", "").lower() != "true"
    short = short_description(fm).replace('"', "'")
    return (
        "interface:\n"
        f'  display_name: "{display_name(skill.name)}"\n'
        f'  short_description: "{short}"\n'
        f'  icon_small: "{ICON_REF}"\n'
        f'  icon_large: "{ICON_REF}"\n'
        f'  brand_color: "{BRAND_COLOR}"\n'
        "policy:\n"
        f"  allow_implicit_invocation: {'true' if implicit else 'false'}\n"
    )


def sync_skills() -> tuple[int, int]:
    created = copied = 0
    for skill in sorted(PLUGINS.glob("*/skills/*")):
        if not (skill / "SKILL.md").is_file():
            continue
        yaml_path = skill / "agents" / "openai.yaml"
        if not yaml_path.is_file():
            yaml_path.parent.mkdir(parents=True, exist_ok=True)
            yaml_path.write_text(stub_yaml(skill), encoding="utf-8")
            print(f"created {yaml_path.relative_to(REPO)} (review the generated text)")
            created += 1
        if ICON_REF in yaml_path.read_text(encoding="utf-8"):
            copied += sync_file(ICON_SRC, skill / "assets" / ICON)
    return created, copied


def write_marketplace() -> int:
    entries = []
    for plugin in sorted(p for p in PLUGINS.iterdir() if (p / "plugin.json").is_file()):
        manifest = json.loads((plugin / "plugin.json").read_text(encoding="utf-8"))
        sync_file(ICON_SRC, plugin / "assets" / ICON)
        interface = manifest.get("extensions", {}).get("com.openai", {}).get("interface", {})
        entries.append(
            {
                "name": manifest["name"],
                "source": {"source": "local", "path": f"./plugins/{plugin.name}"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": interface.get("category", "Coding"),
            }
        )
    out = REPO / ".agents" / "plugins" / "marketplace.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "name": MARKETPLACE_NAME,
        "interface": {"displayName": MARKETPLACE_TITLE},
        "plugins": entries,
    }
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(entries)


def main() -> int:
    if not ICON_SRC.is_file():
        print(f"ERROR: {ICON_SRC.relative_to(REPO)} not found", file=sys.stderr)
        return 2
    created, copied = sync_skills()
    n = write_marketplace()
    print(
        f"codex metadata: {created} openai.yaml created, {copied} skill icon(s) updated, "
        f"{n} plugins in .agents/plugins/marketplace.json"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
