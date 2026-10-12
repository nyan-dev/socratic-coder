#!/usr/bin/env python3
"""Cross-file consistency checks for the socratic-coder skill package.

Run from the repository root:

    python3 scripts/validate.py

Exits non-zero if any invariant is broken. Uses only the standard library.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The Agent Skills standard allows exactly these frontmatter fields. Claude
# Code tolerates extras; stricter consumers reject them outright.
ALLOWED_FRONTMATTER_KEYS = {
    "name",
    "description",
    "license",
    "metadata",
    "allowed-tools",
    "compatibility",
}

MAX_NAME_LEN = 64
MAX_DESCRIPTION_LEN = 1024
MAX_BODY_LINES = 500

errors: list[str] = []
notes: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def parse_frontmatter(text: str) -> dict:
    """Parse the simple YAML used by SKILL.md: scalars, folded blocks, one
    level of nesting. Enough for this file, and no dependency on PyYAML."""
    if not text.startswith("---"):
        return {}
    _, block, _ = text.split("---", 2)
    result: dict = {}
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        if line.startswith("  ") or line.startswith("\t"):
            fail(f"unexpected indented line outside a block: {line!r}")
            i += 1
            continue

        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            fail(f"unparseable frontmatter line: {line!r}")
            i += 1
            continue

        key, rest = m.group(1), m.group(2).strip()

        if rest in (">", ">", "-", "|", "|-"):
            # Block scalar: collect following more-indented lines.
            collected = []
            i += 1
            while i < len(lines) and (not lines[i].strip() or lines[i].startswith("  ")):
                collected.append(lines[i].strip())
                i += 1
            result[key] = " ".join(p for p in collected if p)
            continue

        if rest == "":
            # Mapped block, e.g. metadata:
            nested: dict = {}
            i += 1
            while i < len(lines) and lines[i].startswith("  "):
                nm = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.*)$", lines[i])
                if not nm:
                    fail(f"unparseable nested line: {lines[i]!r}")
                else:
                    nested[nm.group(1)] = nm.group(2).strip().strip('"').strip("'")
                i += 1
            result[key] = nested
            continue

        result[key] = rest.strip('"').strip("'")
        i += 1

    return result


def first_sentence(text: str) -> str:
    """Return everything up to and including the first sentence-ending period
    followed by whitespace."""
    m = re.search(r"^.+?\.(?=\s|$)", text.strip())
    return (m.group(0) if m else text.strip()).strip()


def load_skill() -> tuple[dict, str]:
    path = ROOT / "SKILL.md"
    if not path.exists():
        fail("SKILL.md is missing")
        return {}, ""
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    body = text.split("---", 2)[2] if text.count("---") >= 2 else text
    return fm, body


def main() -> int:
    fm, body = load_skill()

    # --- frontmatter whitelist and shape -------------------------------
    for key in fm:
        if key not in ALLOWED_FRONTMATTER_KEYS:
            fail(
                f"SKILL.md frontmatter uses disallowed field {key!r}; "
                f"portable spec allows only {sorted(ALLOWED_FRONTMATTER_KEYS)}"
            )

    name = fm.get("name", "")
    description = fm.get("description", "")
    metadata = fm.get("metadata", {}) if isinstance(fm.get("metadata"), dict) else {}

    if not name:
        fail("SKILL.md is missing required field 'name'")
    if not description:
        fail("SKILL.md is missing required field 'description'")

    # --- name rules -----------------------------------------------------
    if name:
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
            fail(f"name {name!r} must be lowercase letters, digits, and single hyphens")
        if len(name) > MAX_NAME_LEN:
            fail(f"name is {len(name)} chars; maximum is {MAX_NAME_LEN}")
        if name != ROOT.name:
            fail(f"name {name!r} must match the directory name {ROOT.name!r}")

    # --- description rules ----------------------------------------------
    if description and len(description) > MAX_DESCRIPTION_LEN:
        fail(f"description is {len(description)} chars; maximum is {MAX_DESCRIPTION_LEN}")

    # --- body length -----------------------------------------------------
    body_lines = len([l for l in body.splitlines() if l.strip()])
    if body_lines > MAX_BODY_LINES:
        fail(f"SKILL.md body is {body_lines} non-blank lines; maximum is {MAX_BODY_LINES}")

    # --- version sync -----------------------------------------------------
    versions: dict[str, str] = {}
    versions["SKILL.md metadata.version"] = metadata.get("version", "")

    for label, rel in (
        (".claude-plugin/plugin.json", ".claude-plugin/plugin.json"),
        (".cursor-plugin/plugin.json", ".cursor-plugin/plugin.json"),
    ):
        p = ROOT / rel
        if not p.exists():
            fail(f"{label} is missing")
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            fail(f"{label} is not valid JSON: {e}")
            continue
        versions[label] = data.get("version", "")

    changelog = ROOT / "CHANGELOG.md"
    if changelog.exists():
        m = re.search(r"^## \[(\d+\.\d+\.\d+)\]", changelog.read_text(encoding="utf-8"), re.M)
        versions["CHANGELOG.md top entry"] = m.group(1) if m else ""
        if not m:
            fail("CHANGELOG.md has no '## [x.y.z]' release heading")
    else:
        fail("CHANGELOG.md is missing")
        versions["CHANGELOG.md top entry"] = ""

    real_versions = {v for v in versions.values() if v}
    if len(real_versions) > 1:
        fail("version mismatch across files: " + ", ".join(f"{k}={v or 'MISSING'}" for k, v in versions.items()))
    elif real_versions:
        notes.append(f"version {real_versions.pop()} consistent across {len(versions)} locations")

    # --- plugin description must equal the skill's first sentence ----------
    expected_desc = first_sentence(description) if description else ""
    for label, rel in (
        (".claude-plugin/plugin.json", ".claude-plugin/plugin.json"),
        (".cursor-plugin/plugin.json", ".cursor-plugin/plugin.json"),
    ):
        p = ROOT / rel
        if not p.exists():
            continue
        try:
            actual = json.loads(p.read_text(encoding="utf-8")).get("description", "")
        except json.JSONDecodeError:
            continue
        if expected_desc and actual != expected_desc:
            fail(
                f"{label} description does not match the first sentence of "
                f"SKILL.md description.\n    expected: {expected_desc!r}\n    found:    {actual!r}"
            )
        elif expected_desc:
            notes.append(f"{label} description matches skill's first sentence")

    # --- marketplace manifests ---------------------------------------------
    for rel in (".claude-plugin/marketplace.json", ".cursor-plugin/marketplace.json"):
        p = ROOT / rel
        if not p.exists():
            fail(f"{rel} is missing")
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            fail(f"{rel} is not valid JSON: {e}")
            continue
        plugins = data.get("plugins") or []
        if not plugins:
            fail(f"{rel} declares no plugins")
        for plug in plugins:
            if plug.get("source") != "./":
                fail(f"{rel}: plugin source should be './' for a root-level skill, found {plug.get('source')!r}")

    # --- Codex metadata -------------------------------------------------------
    oa = ROOT / "agents" / "openai.yaml"
    if not oa.exists():
        fail("agents/openai.yaml is missing")
    else:
        text = oa.read_text(encoding="utf-8")
        for field in ("display_name", "short_description", "default_prompt"):
            if not re.search(rf"^{field}:", text, re.M):
                fail(f"agents/openai.yaml is missing {field!r}")

    # --- README asset references ---------------------------------------------
    readme = ROOT / "README.md"
    if readme.exists():
        for path in re.findall(
            r"assets/[A-Za-z0-9._-]+\.(?:svg|jpe?g|png|gif|webp)",
            readme.read_text(encoding="utf-8"),
        ):
            if (ROOT / path).exists():
                notes.append(f"README asset {path} exists")
            else:
                fail(f"README.md references missing asset {path!r}")

    # --- report --------------------------------------------------------------
    for n in notes:
        print(f"  ok   {n}")
    if errors:
        print()
        for e in errors:
            print(f"  FAIL {e}")
        print(f"\n{len(errors)} problem(s) found.")
        return 1

    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
