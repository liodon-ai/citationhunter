# CitationHunter

Audit research papers and claims for citation quality. Identifies missing citations, weak references, contradictory evidence, and produces a structured citation coverage score.

Think of it as "Grammarly for citations" - focused on scientific validity and completeness, not grammar.

## Quick Start

```
/citationhunter "Transformer models dominate most NLP tasks."
/citationhunter https://arxiv.org/abs/1706.03762
/citationhunter "Attention Is All You Need"
```

## Install

### Agent Skills (Claude Code, Codex, Cursor, Copilot, Gemini CLI, and 50+ hosts)

```bash
npx skills add liodon-ai/citationhunter -g
```

### Claude Code (marketplace)

```
/plugin marketplace add liodon-ai/citationhunter
```

### Manual

```bash
git clone https://github.com/liodon-ai/citationhunter.git
ln -s "$(pwd)/citationhunter/skills/citationhunter" ~/.claude/skills/citationhunter
```

## What It Does

| Input | Output |
|-------|--------|
| A sentence or claim | Missing citations, contradictory evidence, coverage score |
| An arXiv link | Full paper audit: missing + weak + contradictory citations |
| A paper title | Paper lookup + citation audit |
| A PDF/LaTeX file | Full paper audit with method gap analysis |

## Output Sections

1. **Citation Coverage Score** (0-10) - How well the claim/paper is supported
2. **Missing Citations** - Unsupported key statements with suggested papers
3. **Weak Citations** - Outdated/irrelevant references with stronger alternatives
4. **Contradictory Evidence** - Papers that challenge the claim
5. **Methodological Gaps** - Missing baselines, ablations, limitations

## Sources

- Semantic Scholar (primary)
- arXiv
- CrossRef
- OpenAlex (fallback)
- Web search (supplementary)

No API keys required. All sources are public.

## License

MIT
