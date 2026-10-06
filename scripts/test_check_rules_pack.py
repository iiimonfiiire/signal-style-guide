import unittest

from check_rules_pack import GUIDE, PACK, check

GUIDE_TEXT = """# Guide

* **Last revision:** 6 Oct 2026

## 1. Voice

- **Directness** – Be blunt.

## 2. Types

### Release notes

Text.
"""

PACK_TEXT = """[guide]
id = "t"
version = "2026-10-06"

[[rules]]
id = "a"
section = "1. Voice > Directness"
summary = "x"

[[content_types.release_note.requirements]]
id = "b"
section = "2. Types > Release notes"
summary = "x"
"""


class CheckRulesPack(unittest.TestCase):
    def test_valid_pack(self):
        self.assertEqual(check(GUIDE_TEXT, PACK_TEXT), [])

    def test_unknown_section(self):
        problems = check(GUIDE_TEXT, PACK_TEXT.replace("1. Voice > Directness", "1. Voice > Humor"))
        self.assertTrue(any("Humor" in p for p in problems))
        problems = check(GUIDE_TEXT, PACK_TEXT.replace("2. Types > Release notes", "9. Missing"))
        self.assertTrue(any("9. Missing" in p for p in problems))

    def test_version_drift(self):
        problems = check(GUIDE_TEXT, PACK_TEXT.replace("2026-10-06", "2026-09-23"))
        self.assertTrue(any("version" in p for p in problems))

    def test_author_line(self):
        problems = check(GUIDE_TEXT, PACK_TEXT.replace('id = "t"', 'id = "t"\nauthor = "Someone"'))
        self.assertTrue(any("author" in p for p in problems))

    def test_duplicate_ids_and_bad_severity(self):
        dup = PACK_TEXT + '\n[[rules]]\nid = "a"\nsection = "1. Voice"\nsummary = "y"\nseverity = "fatal"\n'
        problems = check(GUIDE_TEXT, dup)
        self.assertTrue(any("duplicate" in p for p in problems))
        self.assertTrue(any("severity" in p for p in problems))

    def test_repository_pack(self):
        self.assertEqual(check(GUIDE.read_text(encoding="utf-8"), PACK.read_text(encoding="utf-8")), [])


if __name__ == "__main__":
    unittest.main()
