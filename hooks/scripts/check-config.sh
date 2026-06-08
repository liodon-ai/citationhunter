#!/bin/bash
set -euo pipefail

# CitationHunter requires no API keys — all sources (Semantic Scholar, arXiv, CrossRef) are public.
echo "/citationhunter: Ready. No API keys or configuration required."
echo "  Audit a claim:  /citationhunter \"Transformers dominate most NLP tasks.\""
echo "  Audit a paper:  /citationhunter https://arxiv.org/abs/1706.03762"
echo "  Audit by title: /citationhunter \"Attention Is All You Need\""
