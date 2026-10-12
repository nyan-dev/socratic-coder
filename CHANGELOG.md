# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-11

First release.

### Added

- `SKILL.md`, the skill itself, packaged at the repository root so a single
  file serves Claude Code, Cursor, Codex, Gemini CLI, and anything else that
  reads the Agent Skills standard.
- The four-stage arc: blueprint, build in slices, break it on purpose,
  upgrade the rule.
- Machine learning positioned as a stage 4 option that is offered only when
  the stage 3 failure actually calls for it, rather than as the assumed
  destination of every project.
- Plugin manifests for Claude Code and Cursor, an `agents/openai.yaml` for
  Codex, and a `scripts/validate.py` consistency check.
- `examples/` for session transcripts.
- Pixel-art banner and logo artwork in `assets/`.
- A flowchart of the stage 4 triage decision in the README.

### Changed

- Generalized from the earlier working draft, which was scoped to MediaPipe
  and computer vision projects and asked for an ML project and a tech stack
  before asking what the user wanted to build.

[1.0.0]: https://github.com/nyan-dev/socratic-coder/releases/tag/v1.0.0
