# Contributing to BowerBot

Thanks for your interest in contributing to BowerBot!

## Getting Started

```bash
git clone https://github.com/binary-core-llc/bowerbot.git
cd bowerbot
uv sync
```

## Commit Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/) and [Release Please](https://github.com/googleapis/release-please) for automated versioning and changelogs.

**Format:** `type: short description`

| Type | When to use |
|------|-------------|
| `feat` | New feature or tool |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that doesn't add a feature or fix a bug |
| `test` | Adding or updating tests |
| `chore` | Build, CI, or tooling changes |

**Examples:**

```
feat: add PolyHaven asset skill
fix: correct bounding box calculation for scaled references
docs: update configuration section in README
refactor: move lazy imports to top-level
```

A `feat` commit creates a minor version bump. A `fix` creates a patch bump. Add `!` after the type for breaking changes (e.g., `feat!: redesign skill interface`).

## Writing a Skill

The best way to contribute is writing a new **skill** for an asset provider. Each skill is a folder in `src/bowerbot/skills/` with:

```
my_provider/
  __init__.py
  my_provider.py      # Implements the Skill interface
  SKILL.md            # Natural language instructions for the LLM
```

See `skills/sketchfab/` for a complete example.

### Key rules

- **Skills never touch USD** — all `pxr` calls live in `engine/`
- **One SKILL.md per skill** — it's injected into the system prompt when active
- **Return ToolResult** — always return `ToolResult(success=True/False, ...)` from `execute()`

## Code Style

- Python 3.12+
- Type hints on all public methods
- No `.env` files — all config goes through `~/.bowerbot/config.json`
- Keep imports at the top of the file, not inside methods

## Running Tests

```bash
uv run pytest
```

## Pull Requests

1. Fork the repo and create a feature branch
2. Use conventional commit messages
3. Add tests for new functionality
4. Run `uv run pytest` before submitting
5. Keep PRs focused — one feature or fix per PR
