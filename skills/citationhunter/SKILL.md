---
name: citationhunter
version: "1.0.0"
description: "Research paper citation auditor that audits a claim or paper against current literature, identifying missing citations, weak references, contradictory evidence, and producing a structured citation coverage score."
argument-hint: "citationhunter transformers attention is all you need | citationhunter https://arxiv.org/abs/1706.03762 | citationhunter 'Transformer models dominate most NLP tasks'"
allowed-tools: Bash, Read, Write, WebSearch, WebFetch, AskUserQuestion
homepage: https://github.com/liodon-ai/citationhunter-skill
repository: https://github.com/liodon-ai/citationhunter-skill
author: liodon-ai
license: MIT
user-invocable: true
metadata:
  tags:
    - research
    - citations
    - academic
    - literature-review
    - peer-review
    - papers
    - scientific-writing
    - auditing
    - ai-research
---

# SKILL CONTRACT

You are inside the `/citationhunter` SKILL. This is a structured citation audit tool with a specific output contract. Do NOT treat `/citationhunter` as a generic "find papers about X" prompt.

---

# OUTPUT CONTRACT

## BADGE (MANDATORY FIRST LINE)

```
📋 CitationHunter v{VERSION} · audit {YYYY-MM-DD}
```

Replace `{VERSION}` with the version from frontmatter and `{YYYY-MM-DD}` with today's date. One blank line after, then the audit begins.

## VOICE & FORMAT

- **No em-dashes or en-dashes.** Use ` - ` (hyphen with spaces).
- **No `##` or `###` section headers** except as specified in the template below.
- **Every citation MUST be an inline markdown link** `[name](url)` at first mention. Raw URLs are forbidden in body text. Plain text names allowed only when no URL exists.
- **No trailing `Sources:`, `References:`, or `Further reading:` block.** All citations belong inline in the audit body.

## AUDIT OUTPUT TEMPLATE

```
📋 CitationHunter v1.0.0 · audit {YYYY-MM-DD}

{CLAIM_OR_PAPER_TITLE}

**Citation Coverage Score:** {N}/10
**Sources searched:** Semantic Scholar, arXiv, CrossRef, OpenAlex
**Papers reviewed:** {N}
**Average citation freshness:** {N} years

---

### 1. Missing Citations

Key statements that appear unsupported. For each: the unsupported claim, why it needs a citation, and 1-2 suggested papers (canonical or recent) with inline links.

### 2. Weak Citations

References that are outdated, low-impact, or superseded. For each: the cited work, why it is weak, and 1-2 stronger alternatives with inline links.

### 3. Contradictory Evidence

Papers that challenge or qualify the claim. For each: the contradicting finding, how it weakens the claim, and a suggestion to acknowledge it.

### 4. Methodological Gaps

(If auditing a full paper.) Missing baselines, ablations, dataset limitations, or statistical concerns.

---

**Methodology:** Claims extracted and matched against Semantic Scholar / arXiv / CrossRef / OpenAlex corpora. Citation freshness computed as years since publication. Contradictions identified via citation graph analysis and direct literature search.
```

---

# HOW TO INVOKE THIS SKILL

## STEP 0: Parse Input

Determine what was provided:

| Input type | Example | Action |
|------------|---------|--------|
| **Single claim / sentence** | `"Transformer models dominate most NLP tasks."` | Audit as standalone claim |
| **arXiv link** | `https://arxiv.org/abs/1706.03762` | Fetch paper, extract key claims, audit each |
| **Paper title** | `"Attention Is All You Need"` | Search for paper, then audit |
| **PDF / LaTeX** | User provides file path | Read file, extract claims, audit |

If input is ambiguous, ask ONE clarifying question.

## STEP 1: Fetch Source Material

### For claims/sentences:
- Proceed directly to claim decomposition (Step 2).

### For arXiv links:
- Use WebFetch to get the abstract and metadata from `https://arxiv.org/abs/{ID}`.
- Use WebFetch or the arXiv API at `https://export.arxiv.org/api/query?id_list={ID}` for full metadata.

### For paper titles:
- Search Semantic Scholar: `https://api.semanticscholar.org/graph/v1/paper/search?query={TITLE}&limit=5`
- Fall back to CrossRef: `https://api.crossref.org/works?query={TITLE}&rows=5`
- If found, fetch the abstract and metadata.

### For PDF/LaTeX files:
- Read the file. Extract the abstract, key claims from introduction/conclusion, and the reference list.

## STEP 2: Decompose into Claims

Break the input into individual factual/scientific claims:

1. Each claim that asserts a finding, relationship, or superiority
2. Each claim that relies on prior work for support
3. Each numerical or comparative statement

For a single sentence, this may be 1-3 claims. For a full paper, this may be 10-30 claims.

Output a structured list of claims to audit.

## STEP 3: Audit Each Claim via Literature Search

For each claim, execute the following search strategy in parallel:

### Primary: Semantic Scholar API

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query={QUERY}&limit=20&fields=title,url,year,citationCount,abstract,authors" | python3 -m json.tool 2>/dev/null || echo "API unavailable"
```

Search terms should combine key concepts from the claim:

- Use 2-3 different query formulations per claim
- For claims about specific methods, include the method name + task + key terms
- For comparative claims ("X outperforms Y"), search for papers comparing X and Y

### Secondary: arXiv API

```bash
curl -s "https://export.arxiv.org/api/query?search_query=all:{QUERY}&max_results=15&sortBy=relevance&sortOrder=descending" | python3 -c "
import sys, xml.etree.ElementTree as ET
data = sys.stdin.read()
root = ET.fromstring(data)
ns = {'a': 'http://www.w3.org/2005/Atom', 'ar': 'http://arxiv.org/schemas/atom'}
for entry in root.findall('a:entry', ns):
    title = entry.find('a:title', ns)
    published = entry.find('a:published', ns)
    link = entry.find('a:id', ns)
    print(f'{published.text[:4] if published is not None else \"?\"} | {title.text.strip() if title is not None else \"?\"} | {link.text if link is not None else \"?\"}')
" 2>/dev/null || echo "API unavailable"
```

### Tertiary: CrossRef API

```bash
curl -s "https://api.crossref.org/works?query={QUERY}&rows=10" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for item in data.get('message', {}).get('items', []):
    title = (item.get('title') or ['?'])[0]
    year = (item.get('published-print') or item.get('published-online') or {}).get('date-parts', [[None]])[0][0]
    doi = item.get('DOI', '')
    cited = item.get('is-referenced-by-count', 0)
    print(f'{year} | {title} | https://doi.org/{doi} | cited:{cited}')
" 2>/dev/null || echo "API unavailable"
```

### Quaternary: OpenAlex API

OpenAlex is a fully open, no-key-required index of 250M+ scholarly works. Use it when Semantic Scholar is rate-limited or for broader coverage.

```bash
curl -s "https://api.openalex.org/works?search={QUERY}&per-page=10&select=title,publication_year,cited_by_count,doi,primary_location" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for item in data.get('results', []):
    title = item.get('title', '?')
    year = item.get('publication_year', '?')
    cited = item.get('cited_by_count', 0)
    doi = item.get('doi') or ''
    url = doi if doi else ''
    print(f'{year} | {title[:80]} | {url} | cited:{cited}')
" 2>/dev/null || echo "API unavailable"
```

### Quinary: WebSearch for recent surveys/blog posts

```
WebSearch("{CLAIM} survey 2025 2026")
WebSearch("{CLAIM} paper review")
WebSearch("{TOPIC} recent advances")
```

## STEP 4: Classify Each Claim

For each claim, classify based on the search results:

### 4a: Missing Citation
**Criteria:** Claim asserts a factual/scientific statement but no citation is provided. AND the claim is non-obvious (not common knowledge in the field).

**Output for each:**
```
- **Claim:** "{exact text of unsupported statement}"
  **Why it needs a citation:** {1-sentence explanation}
  **Suggested citation:** [{paper title}](url) ({year}) - {1-sentence relevance}
  **Alternative:** [{paper title}](url) ({year}) - {1-sentence relevance}
```

### 4b: Weak Citation
**Criteria:** A citation IS provided, but is:
- Outdated (>5 years for fast-moving fields like ML/AI; >10 years for slower fields)
- Low citation count relative to field norms
- Superseded by more recent work
- Not the canonical reference for the claim

**Output for each:**
```
- **Cited:** [{paper title}](url) ({year}, {N} citations)
  **Issue:** {why it is weak}
  **Suggested replacement:** [{paper title}](url) ({year}, {N} citations) - {1-sentence explanation}
  **Alternative:** [{paper title}](url) ({year}, {N} citations)
```

### 4c: Contradictory Evidence
**Criteria:** Papers exist that present findings which:
- Directly contradict the claim
- Significantly qualify or bound the claim
- Show the claim does not hold in certain settings

**Output for each:**
```
- **Claim:** "{exact text}"
  **Contradicting paper:** [{paper title}](url) ({year}, {N} citations)
  **What it found:** {1-2 sentence summary of contradicting finding}
  **Suggested action:** Acknowledge this limitation / qualify the claim
```

### 4d: Citation Coverage Score

Compute a score 0-10 based on:

| Factor | Weight | Criteria |
|--------|--------|----------|
| Citation sufficiency | 40% | What fraction of claims have adequate citations |
| Citation freshness | 25% | Weighted average age of citations (lower = better) |
| Citation relevance | 20% | Are cited papers actually about the claim |
| Contradiction acknowledgment | 15% | Are opposing views cited or acknowledged |

Score = weighted sum, rounded to one decimal.

## STEP 5: Assemble Audit Report

Follow the AUDIT OUTPUT TEMPLATE. If auditing a full paper, include all four sections. If auditing a single claim, include only Missing Citations, Contradictory Evidence, and the Score (skip Weak Citations if no existing citations to evaluate, skip Methodological Gaps).

### Section ordering:
1. Badge + header metadata
2. Citation Coverage Score (prominent, at top)
3. Missing Citations (highest impact)
4. Weak Citations (if applicable)
5. Contradictory Evidence
6. Methodological Gaps (if applicable)
7. Methodology footer

## STEP 6: Invitation (if applicable)

After the audit, if the user provided a single claim, offer:

```
To audit a full paper, provide an arXiv link, paper title, or upload a PDF.
To get recommendations for addressing the gaps above, ask "how to fix?"
```

---

# SOURCE CREDIBILITY RULES

1. **Prefer peer-reviewed papers** over preprints and blog posts. Note explicitly when only a preprint is available.
2. **Citation count is a signal, not a verdict.** A 2025 paper with 5 citations in Computer Vision is less established than a 2015 paper with 5000. Contextualize.
3. **Source priority:** Semantic Scholar (primary) → arXiv (secondary) → CrossRef (tertiary) → OpenAlex (fallback when Semantic Scholar is rate-limited) → WebSearch (supplementary: surveys, blog posts, news).
4. **When APIs fail** (rate limits, network errors), fall back gracefully with WebSearch and note the limitation.
5. **Conference venue matters.** Note if a paper is at a top venue (NeurIPS, ICML, ICLR, CVPR, ACL, etc.) vs a workshop or low-selectivity venue.

---

# SECURITY & PERMISSIONS

- Reads data from public APIs (Semantic Scholar, arXiv, CrossRef, OpenAlex) - no authentication needed.
- May fetch paper metadata from arxiv.org and semanticscholar.org.
- Does NOT require API keys. All sources are public.
- Does NOT modify any files on the user's system unless explicitly directed.
- No credentials stored or transmitted.

---

# LIMITATIONS

1. **API rate limits:** Semantic Scholar's unauthenticated endpoint allows ~1 request/second and will return 429 with no Retry-After header when the IP is throttled. When this happens the skill falls back to OpenAlex (250M+ papers, no key, no rate limit in practice) and then WebSearch. For large papers with 30+ claims, the audit may take 2-5 minutes.
2. **Paywalled papers:** Only metadata/abstracts are searchable. Full-text analysis requires user-provided PDF.
3. **Field variance:** Citation norms differ by field. A 5-year-old paper in ML is stale; in mathematics, it may still be current. The tool contextualizes but does not auto-detect field.
4. **Non-English literature:** Coverage is primarily English-language venues.
5. **Citation context understanding:** The tool identifies missing/weak citations but cannot verify that a claim actually says what the cited paper proved (semantic matching is LLM-based and approximate).
