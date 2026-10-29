#!/usr/bin/env python3
"""Checks for this repository's own skill files. Standard library only."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKILLS = {
    "video-production": "Use when the user wants a video made or edited",
    "ffmpeg-tools": "Use when running local FFmpeg",
    "music-and-beats": "Use when choosing music",
    "review-and-qc": "Use when checking a rendered cut",
}

# The skills stay generic. Credits live in the README, not in a skill.
FORBIDDEN = (
    "kajisho5",
    "ashebytes",
    "brendan",
    "Director video",
    "ffmpeg-skill",
    "npx ",
)


class SkillFileTests(unittest.TestCase):
    def test_each_skill_has_frontmatter_and_a_matching_name(self):
        for name, description_start in SKILLS.items():
            path = ROOT / "skills" / name / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), name)
            front, _, body = text.split("---", 2)
            # split leaves the leading '---\n' in front when the file starts with it
            self.assertIn(f"name: {name}", text.split("---", 2)[1])
            description = text.split("---", 2)[1]
            self.assertIn("description:", description)
            self.assertIn(description_start, description)
            self.assertGreater(len(body.strip()), 200, name)
            for needle in FORBIDDEN:
                self.assertNotIn(needle, text, f"{name} contains {needle!r}")

    def test_script_paths_named_by_the_skills_exist(self):
        blob = "\n".join(
            (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            for name in SKILLS
        )
        paths = set(re.findall(r"`((?:scripts|references|templates)/[^`\s]+)`", blob))
        self.assertTrue(paths, "skills should name repository paths in backticks")
        for rel in sorted(paths):
            rel = rel.split("#", 1)[0]
            if rel.endswith("/"):
                continue
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_gotcha_anchors_used_by_the_skills_exist(self):
        gotchas = (ROOT / "references" / "gotchas.md").read_text(encoding="utf-8")
        headings = []
        for heading in re.findall(r"(?m)^#+ (.+)$", gotchas):
            slug = "".join(ch for ch in heading.lower().replace(" ", "-") if ch.isalnum() or ch == "-")
            headings.append(slug)
        blob = "\n".join(
            (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            for name in SKILLS
        )
        for anchor in re.findall(r"references/gotchas\.md#([a-z0-9-]+)", blob):
            self.assertIn(anchor, headings, anchor)

    def test_removed_upstream_packaging_is_gone(self):
        for rel in (
            "SKILL.md",
            "AGENTS.md",
            "package.json",
            "bin/install.js",
            ".claude",
            "evals",
            "demos",
            "docs",
        ):
            self.assertFalse((ROOT / rel).exists(), rel)

    def test_notice_carries_the_upstream_mit_licence(self):
        notice = (ROOT / "NOTICE").read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2026 kajisho5", notice)
        self.assertIn("Permission is hereby granted, free of charge", notice)
        self.assertIn("https://github.com/kajisho5/ffmpeg-skill", notice)
        for rel in ("scripts/", "templates/", "mcp/server.py", "references/gotchas.md"):
            self.assertIn(rel, notice)

    def test_readme_credits_several_creators(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Inspiration and credits", readme)
        self.assertIn("https://github.com/kajisho5/ffmpeg-skill", readme)
        self.assertIn("https://x.com/ashebytes/status/2115215620279263329", readme)
        self.assertIn("Director video bot template", readme)
        self.assertIn("and many other creators whose posts and guides shaped this workflow.", readme)
        self.assertNotIn("adapted from kajisho5", readme.lower())
        self.assertNotIn("fork", readme.lower())
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2026 Brendan Jarvis", license_text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
