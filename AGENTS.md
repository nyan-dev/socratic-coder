# Contributing

This file is for agents and for people working on this repository. `README.md`
is for people installing the skill.

## What this project is

A single skill, `SKILL.md`, that makes a coding assistant teach by building
instead of handing over finished code. The repository is packaged so the same
file installs everywhere.

## Key files

| File | Role |
| --- | --- |
| `SKILL.md` | The product. Root-level, single-skill layout. |
| `README.md` | Install and usage documentation for humans. |
| `.claude-plugin/plugin.json` | Claude Code plugin manifest. |
| `.claude-plugin/marketplace.json` | Lets the repo act as its own marketplace. |
| `.cursor-plugin/plugin.json` | Cursor plugin manifest. |
| `.cursor-plugin/marketplace.json` | Lets Cursor import the repo from GitHub. |
| `agents/openai.yaml` | Codex display metadata and a default prompt. |
| `assets/banner.jpg` | README hero image: pixel-art scene with the wordmark. |
| `assets/logo.jpg` | Project mark: pixel-art temple over a starry sky. |
| `assets/triage.svg` | README diagram: stage 3 failure routed to the three stage 4 fixes. |
| `examples/` | Session transcripts. |
| `scripts/validate.py` | Cross-file consistency checks. |

## Invariants

Do not break these. `scripts/validate.py` checks all of them.

- The version string is identical in four places: `SKILL.md` under
  `metadata.version`, `.claude-plugin/plugin.json`,
  `.cursor-plugin/plugin.json`, and the top entry in `CHANGELOG.md`.
- The `description` in each plugin manifest is exactly the first sentence of
  the `description` in `SKILL.md`.
- The `name` in `SKILL.md` frontmatter matches the repository directory name,
  is lowercase, and uses only digits and hyphens.
- `SKILL.md` frontmatter uses only the fields the Agent Skills standard
  allows: `name`, `description`, `license`, `metadata`, `allowed-tools`,
  `compatibility`. Claude Code tolerates extra fields; stricter consumers
  reject them outright.
- `SKILL.md` stays under 500 lines. Longer bodies split into `references/`.
- Every image referenced in `README.md` resolves to a file that exists.
  `scripts/validate.py` checks this.

## Style

Write plainly. This repository argues that AI-flavored prose is a problem,
so the documentation cannot be written in the register it argues against.

The badge row and the section emoji are deliberate exceptions, and they are
scoped tightly. Badges stay live and informative. Emoji mark sections and
never appear inside body prose.

- Badges must report something real that updates on its own: stars, install
  count, version, license. A static badge announcing the author or welcoming
  PRs announces nothing, and is the kind of filler this repository exists to
  argue against.
- Emoji belong in headings. None in body text, none in code blocks, none as
  list bullets.
- Avoid the "not X, but Y" construction. It is the single most common tell
  in generated text.
- No invented branded frameworks. Describe what something does rather than
  naming it after a concept.
- No hype adjectives. "Highly engineered", "world-class", and
  "revolutionary" describe nothing.
- Sentences should carry information. If a sentence could be removed without
  the reader losing anything, remove it.

## Before publishing

1. `python3 scripts/validate.py`
2. `npx skills add . --list` should discover `socratic-coder` at the root.
3. `claude plugin validate .`
4. Bump the version in all four invariant locations and add a changelog entry.
