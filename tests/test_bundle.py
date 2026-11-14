"""Check that the ADR skills remain usable as one installed bundle."""

from pathlib import Path
import re
import shutil
import tempfile
import unittest
from urllib.parse import unquote, urlsplit


REPOSITORY = Path(__file__).resolve().parents[1]
SKILLS = (
    "adr-workflow",
    "adr-check",
    "adr-writing",
    "adr-review",
    "adr-implementation",
)
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)\s]+)(?:\s+[^)]*)?\)")


def problems_at(skills_root: Path) -> list[str]:
    """Return missing entry points and broken local Markdown references."""
    problems = []
    root = skills_root.resolve()
    for name in SKILLS:
        skill_dir = skills_root / name
        entry = skill_dir / "SKILL.md"
        if not entry.is_file():
            problems.append(f"missing entry: {name}/SKILL.md")
            continue
        text = entry.read_text(encoding="utf-8")
        frontmatter = re.match(r"\A---\s*\n(.*?)\n---(?:\s*\n|$)", text, re.DOTALL)
        if not frontmatter:
            problems.append(f"invalid frontmatter: {name}/SKILL.md")
        elif not re.search(rf"(?m)^name:\s*{re.escape(name)}\s*$", frontmatter.group(1)):
            problems.append(f"wrong skill name: {name}/SKILL.md")
        elif not re.search(r"(?m)^description:\s*\S", frontmatter.group(1)):
            problems.append(f"missing description: {name}/SKILL.md")

        for markdown in skill_dir.rglob("*.md"):
            for raw in LINK.findall(markdown.read_text(encoding="utf-8")):
                parsed = urlsplit(raw)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                target = (markdown.parent / unquote(parsed.path)).resolve()
                if not target.is_relative_to(root) or not target.is_file():
                    problems.append(f"broken link: {markdown.relative_to(skills_root)} -> {raw}")
    return problems


class BundleTest(unittest.TestCase):
    def test_repository_bundle_has_all_entries_and_references(self):
        self.assertEqual([], problems_at(REPOSITORY / "skills"))

    def test_readme_links_resolve(self):
        for name in ("README.md", "README_EN.md"):
            markdown = REPOSITORY / name
            for raw in LINK.findall(markdown.read_text(encoding="utf-8")):
                parsed = urlsplit(raw)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                target = (markdown.parent / unquote(parsed.path)).resolve()
                self.assertTrue(target.is_relative_to(REPOSITORY), raw)
                self.assertTrue(target.is_file(), raw)

    def test_installed_sibling_directories_resolve_references(self):
        with tempfile.TemporaryDirectory(prefix=".adr-skills-test-", dir=REPOSITORY) as directory:
            target = Path(directory) / "skills"
            target.mkdir()
            for name in SKILLS:
                shutil.copytree(REPOSITORY / "skills" / name, target / name)
            self.assertEqual([], problems_at(target))

    def test_missing_cross_skill_reference_is_detected(self):
        with tempfile.TemporaryDirectory(prefix=".adr-skills-test-", dir=REPOSITORY) as directory:
            target = Path(directory) / "skills"
            shutil.copytree(REPOSITORY / "skills", target)
            (target / "adr-review" / "references" / "input-fingerprint.md").unlink()
            self.assertTrue(any("input-fingerprint.md" in problem for problem in problems_at(target)))

    def test_missing_component_is_detected(self):
        with tempfile.TemporaryDirectory(prefix=".adr-skills-test-", dir=REPOSITORY) as directory:
            target = Path(directory) / "skills"
            shutil.copytree(REPOSITORY / "skills", target)
            removed = (target / "adr-check").resolve()
            self.assertTrue(removed.is_relative_to(target.resolve()))
            shutil.rmtree(removed)
            self.assertIn("missing entry: adr-check/SKILL.md", problems_at(target))


if __name__ == "__main__":
    unittest.main()
