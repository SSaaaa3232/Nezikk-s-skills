import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "import_external_skill.py"


def load_module():
    spec = importlib.util.spec_from_file_location("import_external_skill", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ImportExternalSkillTests(unittest.TestCase):
    def test_parses_npx_skills_add_command(self) -> None:
        module = load_module()

        parsed = module.parse_import_args(
            [
                "npx skills add https://github.com/op7418/guizang-ppt-skill "
                "--skill guizang-ppt-skill"
            ]
        )

        self.assertEqual(parsed.repo_url, "https://github.com/op7418/guizang-ppt-skill")
        self.assertEqual(parsed.skill_name, "guizang-ppt-skill")
        self.assertFalse(parsed.replace)
        self.assertFalse(parsed.no_link)

    def test_parses_direct_repo_url_and_skill(self) -> None:
        module = load_module()

        parsed = module.parse_import_args(
            [
                "https://github.com/op7418/guizang-ppt-skill",
                "--skill",
                "guizang-ppt-skill",
                "--no-link",
            ]
        )

        self.assertEqual(parsed.repo_url, "https://github.com/op7418/guizang-ppt-skill")
        self.assertEqual(parsed.skill_name, "guizang-ppt-skill")
        self.assertTrue(parsed.no_link)

    def test_extracts_github_owner_and_repo(self) -> None:
        module = load_module()

        owner, repo = module.parse_github_repo("git@github.com:op7418/guizang-ppt-skill.git")

        self.assertEqual(owner, "op7418")
        self.assertEqual(repo, "guizang-ppt-skill")

    def test_finds_root_skill_when_repo_root_is_skill(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as temp_dir:
            clone_dir = Path(temp_dir)
            (clone_dir / "SKILL.md").write_text(
                "---\nname: guizang-ppt-skill\n---\n\n# PPT\n",
                encoding="utf-8",
            )

            skill_dir = module.find_skill_dir(clone_dir, "guizang-ppt-skill")

        self.assertEqual(skill_dir, clone_dir)

    def test_imports_skill_and_writes_source_metadata_without_linking(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as temp_dir:
            work = Path(temp_dir)
            clone_dir = work / "clone"
            clone_dir.mkdir()
            skill_dir = clone_dir / "guizang-ppt-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nname: guizang-ppt-skill\n---\n\n# PPT\n",
                encoding="utf-8",
            )
            (skill_dir / "assets").mkdir()
            (skill_dir / "assets" / "theme.txt").write_text("theme", encoding="utf-8")

            repo_root = work / "repo"
            repo_root.mkdir()

            result = module.import_from_clone(
                clone_dir=clone_dir,
                repo_root=repo_root,
                repo_url="https://github.com/op7418/guizang-ppt-skill",
                owner="op7418",
                repo_name="guizang-ppt-skill",
                skill_name="guizang-ppt-skill",
                commit="abc1234",
                replace=False,
            )

            imported = repo_root / "external" / "op7418" / "guizang-ppt-skill"
            self.assertEqual(result, imported / "guizang-ppt-skill")
            self.assertTrue((imported / "guizang-ppt-skill" / "SKILL.md").exists())
            self.assertTrue((imported / "guizang-ppt-skill" / "assets" / "theme.txt").exists())
            source = (imported / "SOURCE.md").read_text(encoding="utf-8")
            self.assertIn("Original repository: https://github.com/op7418/guizang-ppt-skill", source)
            self.assertIn("Imported commit: abc1234", source)
            self.assertIn("Local changes: none", source)


if __name__ == "__main__":
    unittest.main()
