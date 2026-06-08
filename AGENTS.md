# CitationHunter Skill

Agent Skills package for auditing research papers and claims for citation quality. Installable across Claude Code (most common host), Codex, Cursor, GitHub Copilot, Gemini CLI, and 50+ other [Agent Skills](https://agentskills.io) hosts. Pure prompt-driven skill — no Python runtime required.

## Structure
- `skills/citationhunter/SKILL.md` — canonical skill definition / runtime spec the model reads when the slash command fires
- `tests/` — pytest test suite validating plugin contracts and SKILL.md structure
- `.claude-plugin/plugin.json` — Claude Code plugin manifest (name, version, description, license)
- `.claude-plugin/marketplace.json` — Claude Code marketplace listing
- `.agents/plugins/marketplace.json` — cross-host agents marketplace listing
- `gemini-extension.json` — Gemini CLI extension manifest

## Commands

```bash
# Tests (pytest, configured in pyproject.toml)
uv run pytest                                      # full suite
uv run pytest tests/test_plugin_contract.py        # single file
uv run pytest tests/test_skill_structure.py -v     # verbose
uv run pytest --tb=short                           # short traceback

# Install skill globally
npx skills add . -g -y
```

Python 3.12+ required. Use `uv` for the env.

## Orientation
- This is an Agent Skills package, not a CLI tool. The product is the slash-command-invoked skill (`/citationhunter <input>` in most harnesses); there is no Python engine — the model IS the engine.
- CitationHunter uses only public APIs (Semantic Scholar, arXiv, CrossRef). No API keys are required.
- Feature design starts from the slash-command UX. Changes to search strategy, output format, or scoring must be reflected in `SKILL.md`.

## Version sync rule
When bumping the version, update ALL of these in the same commit — tests enforce this:
- `skills/citationhunter/SKILL.md` frontmatter (`version:`)
- `.claude-plugin/plugin.json` (`version`)
- `.claude-plugin/marketplace.json` (plugins[0].`version`)
- `gemini-extension.json` (`version`)
- `pyproject.toml` (`version`)

## Security hygiene
- Never commit API keys, auth tokens, or credentials. CitationHunter has none — keep it that way.
- All sources are public and unauthenticated.
- Do not add authenticated sources without a corresponding `SECURITY.md` update and test coverage.
