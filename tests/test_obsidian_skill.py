from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "obsidian" / "SKILL.md"


class ObsidianSkillTests(unittest.TestCase):
    def test_obsidian_skill_documents_web_clipper_workflow(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("name: obsidian", content)
        self.assertIn("/obsidian", content)
        self.assertIn("bb-browser", content)
        self.assertIn("Obsidian Web Clipper", content)
        self.assertIn("/Users/saaaaa/Obsidian-Template/raw/articles", content)
        self.assertIn("raw/articles", content)
        self.assertIn("Obsidian-Template", content)
        self.assertIn("obsidian://", content)
        self.assertIn("system `open` command", content)
        self.assertIn("Keep the returned `Tab ID`", content)
        self.assertIn("do not trust a sparse accessibility snapshot", content)
        self.assertIn("#source", content)
        self.assertIn("chrome.tabs.update", content)
        self.assertIn("stale panel", content)
        self.assertIn("/json/list", content)
        self.assertIn("side-panel.html?context=iframe", content)
        self.assertIn("manual-obsidian-clipper", content)
        self.assertIn("do not claim success", content)
        self.assertIn("Obsidian URL:", content)
        self.assertIn("still open the exact URI", content)
        self.assertIn("Do not replace or \"fix\" the URI", content)
        self.assertIn("target source and expected article/post body", content)
        self.assertIn("clipboard troubleshooting text", content)
        self.assertIn("logged-in browser state", content)
        self.assertIn("Do not post, like, reply, follow", content)
        self.assertIn("Do not use unauthenticated fetch/curl", content)


if __name__ == "__main__":
    unittest.main()
