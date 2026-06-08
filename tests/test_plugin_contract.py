import json
import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "citationhunter"

_VERSION_RE = re.compile(
    r'''^version:\s*(?:"([^"]+)"|'([^']+)'|(\S+))\s*$''',
    re.MULTILINE,
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _skill_version() -> str:
    text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    match = _VERSION_RE.search(text)
    if not match:
        raise AssertionError("SKILL.md version frontmatter not found")
    return match.group(1) or match.group(2) or match.group(3)


class TestVersionConsistency(unittest.TestCase):
    def test_versions_match_across_manifests(self) -> None:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        version = pyproject["project"]["version"]

        self.assertEqual(version, _skill_version(), "SKILL.md version differs from pyproject.toml")
        self.assertEqual(version, _json(ROOT / ".claude-plugin" / "plugin.json")["version"])
        self.assertEqual(version, _json(ROOT / "gemini-extension.json")["version"])

        marketplace = _json(ROOT / ".claude-plugin" / "marketplace.json")
        plugins = marketplace.get("plugins") or []
        self.assertEqual(1, len(plugins))
        self.assertEqual(version, plugins[0]["version"])


class TestClaudePluginJson(unittest.TestCase):
    def test_required_fields_present(self) -> None:
        plugin = _json(ROOT / ".claude-plugin" / "plugin.json")
        for field in ("name", "version", "description", "license", "repository", "homepage"):
            self.assertIn(field, plugin, f"plugin.json missing field: {field}")

    def test_name_matches_skill(self) -> None:
        plugin = _json(ROOT / ".claude-plugin" / "plugin.json")
        self.assertEqual("citationhunter", plugin["name"])

    def test_license_is_mit(self) -> None:
        plugin = _json(ROOT / ".claude-plugin" / "plugin.json")
        self.assertEqual("MIT", plugin["license"])


class TestClaudeMarketplaceJson(unittest.TestCase):
    def test_required_schema_shape(self) -> None:
        marketplace = _json(ROOT / ".claude-plugin" / "marketplace.json")
        self.assertIn("metadata", marketplace)
        self.assertIn("description", marketplace["metadata"])
        self.assertIn("plugins", marketplace)
        self.assertEqual(1, len(marketplace["plugins"]))

    def test_no_top_level_description(self) -> None:
        marketplace = _json(ROOT / ".claude-plugin" / "marketplace.json")
        self.assertNotIn("description", marketplace, "description belongs under metadata, not top-level")

    def test_plugin_entry_has_required_fields(self) -> None:
        plugin = _json(ROOT / ".claude-plugin" / "marketplace.json")["plugins"][0]
        for field in ("name", "version", "description", "source", "category", "homepage"):
            self.assertIn(field, plugin, f"marketplace.json plugins[0] missing field: {field}")


class TestAgentsMarketplaceJson(unittest.TestCase):
    def test_required_fields_present(self) -> None:
        agents = _json(ROOT / ".agents" / "plugins" / "marketplace.json")
        self.assertIn("plugins", agents)
        self.assertEqual(1, len(agents["plugins"]))
        plugin = agents["plugins"][0]
        self.assertIn("name", plugin)
        self.assertIn("source", plugin)

    def test_authentication_is_none(self) -> None:
        plugin = _json(ROOT / ".agents" / "plugins" / "marketplace.json")["plugins"][0]
        auth = plugin.get("policy", {}).get("authentication")
        self.assertEqual("NONE", auth, "CitationHunter needs no auth — policy.authentication should be NONE")


class TestGeminiExtensionJson(unittest.TestCase):
    def test_required_fields_present(self) -> None:
        ext = _json(ROOT / "gemini-extension.json")
        for field in ("name", "version", "description"):
            self.assertIn(field, ext, f"gemini-extension.json missing field: {field}")

    def test_settings_is_empty_list(self) -> None:
        ext = _json(ROOT / "gemini-extension.json")
        self.assertEqual([], ext.get("settings"), "CitationHunter needs no API keys — settings should be []")


if __name__ == "__main__":
    unittest.main()
