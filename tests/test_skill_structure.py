import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "citationhunter"


def _skill_text() -> str:
    return (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")


class TestSkillFrontmatter(unittest.TestCase):
    def test_required_frontmatter_fields(self) -> None:
        text = _skill_text()
        for field in ("name:", "version:", "description:", "argument-hint:", "allowed-tools:", "user-invocable:"):
            self.assertIn(field, text, f"SKILL.md frontmatter missing: {field}")

    def test_user_invocable_is_true(self) -> None:
        self.assertIn("user-invocable: true", _skill_text())

    def test_allowed_tools_includes_websearch_and_webfetch(self) -> None:
        text = _skill_text()
        match = re.search(r"allowed-tools:\s*(.+)", text)
        self.assertIsNotNone(match, "allowed-tools field not found")
        tools = match.group(1)
        self.assertIn("WebSearch", tools)
        self.assertIn("WebFetch", tools)

    def test_allowed_tools_includes_bash(self) -> None:
        text = _skill_text()
        match = re.search(r"allowed-tools:\s*(.+)", text)
        self.assertIsNotNone(match)
        self.assertIn("Bash", match.group(1))

    def test_name_is_citationhunter(self) -> None:
        text = _skill_text()
        match = re.search(r"^name:\s*(\S+)", text, re.MULTILINE)
        self.assertIsNotNone(match, "name field not found in frontmatter")
        self.assertEqual("citationhunter", match.group(1))

    def test_homepage_field_present(self) -> None:
        self.assertIn("homepage:", _skill_text())

    def test_license_field_present(self) -> None:
        self.assertIn("license:", _skill_text())


class TestOutputContract(unittest.TestCase):
    def test_badge_format_specified(self) -> None:
        text = _skill_text()
        self.assertIn("CitationHunter v", text)
        self.assertIn("YYYY-MM-DD", text)

    def test_required_output_sections_present(self) -> None:
        text = _skill_text()
        for section in (
            "Citation Coverage Score",
            "Missing Citations",
            "Weak Citations",
            "Contradictory Evidence",
            "Methodological Gaps",
        ):
            self.assertIn(section, text, f"SKILL.md missing required output section: {section}")

    def test_score_range_is_zero_to_ten(self) -> None:
        self.assertIn("0-10", _skill_text())

    def test_raw_urls_forbidden_rule_documented(self) -> None:
        self.assertIn("Raw URLs are forbidden", _skill_text())

    def test_inline_link_format_documented(self) -> None:
        self.assertIn("[name](url)", _skill_text())

    def test_methodology_footer_specified(self) -> None:
        self.assertIn("**Methodology:**", _skill_text())

    def test_no_trailing_references_block_rule(self) -> None:
        self.assertIn("No trailing", _skill_text())


class TestScoringWeights(unittest.TestCase):
    def test_four_scoring_factors_present(self) -> None:
        text = _skill_text()
        for factor in ("Citation sufficiency", "Citation freshness", "Citation relevance", "Contradiction acknowledgment"):
            self.assertIn(factor, text, f"Scoring factor missing: {factor}")

    def test_weights_sum_to_100(self) -> None:
        text = _skill_text()
        weights = re.findall(r"(\d+)%", text)
        scoring_weights = [int(w) for w in weights if int(w) in (40, 25, 20, 15)]
        self.assertEqual(100, sum(scoring_weights), f"Scoring weights should sum to 100, got {sum(scoring_weights)}")


class TestSearchStrategy(unittest.TestCase):
    def test_primary_sources_documented(self) -> None:
        text = _skill_text()
        for source in ("Semantic Scholar", "arXiv", "CrossRef", "OpenAlex"):
            self.assertIn(source, text, f"SKILL.md missing source: {source}")

    def test_api_endpoints_present(self) -> None:
        text = _skill_text()
        self.assertIn("api.semanticscholar.org", text)
        self.assertIn("export.arxiv.org", text)
        self.assertIn("api.crossref.org", text)
        self.assertIn("api.openalex.org", text)

    def test_arxiv_uses_https_not_http(self) -> None:
        text = _skill_text()
        self.assertNotIn("http://export.arxiv.org", text, "arXiv API must use https:// — http:// returns a 301 with empty body")
        self.assertIn("https://export.arxiv.org", text)

    def test_no_authentication_required(self) -> None:
        self.assertIn("no authentication needed", _skill_text().lower())

    def test_input_types_documented(self) -> None:
        text = _skill_text()
        for input_type in ("arXiv link", "paper title", "PDF"):
            self.assertIn(input_type, text, f"SKILL.md missing input type: {input_type}")

    def test_fallback_to_websearch_documented(self) -> None:
        self.assertIn("WebSearch", _skill_text())


class TestHooksPresent(unittest.TestCase):
    def test_hooks_json_exists(self) -> None:
        self.assertTrue((ROOT / "hooks" / "hooks.json").exists())

    def test_check_config_script_exists(self) -> None:
        self.assertTrue((ROOT / "hooks" / "scripts" / "check-config.sh").exists())

    def test_check_config_script_is_executable(self) -> None:
        script = ROOT / "hooks" / "scripts" / "check-config.sh"
        self.assertTrue(os.access(script, os.X_OK), "check-config.sh is not executable")


if __name__ == "__main__":
    unittest.main()
