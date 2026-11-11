"""The company's share of Claude Code's per-turn skill listing stays inside its budget."""

import importlib.util
import os
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_validator():
    spec = importlib.util.spec_from_file_location("company_validate", ROOT / "scripts/validate.py")
    module = importlib.util.module_from_spec(spec)
    previous, directory = sys.dont_write_bytecode, os.getcwd()
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
        os.chdir(directory)
    return module


validate = load_validator()


class ListingBudgetTests(unittest.TestCase):
    def descriptions(self):
        result = {}
        for manual in sorted((ROOT / "skills").glob("*/SKILL.md")):
            result[manual.parent.name] = re.search(r"^description:[ \t]*(.*)$", manual.read_text(encoding="utf-8"), re.M).group(1).strip()
        return result

    def test_every_manual_fits_the_documented_default_listing(self):
        descriptions = self.descriptions()
        total, problems = validate.listing_problems(descriptions)
        self.assertEqual(problems, [])
        self.assertEqual(len(descriptions), 64)
        self.assertLessEqual(total, validate.SKILL_LISTING_BUDGET)
        self.assertLess(validate.SKILL_LISTING_BUDGET, validate.SKILL_LISTING_DEFAULT)
        self.assertEqual(total, sum(len("claude-inc:" + slug) + len(text) + 5 for slug, text in descriptions.items()))
        for slug, text in descriptions.items():
            self.assertRegex(text, r"\bUse (when|for)\b", slug)
            self.assertLessEqual(len(text), validate.SKILL_DESCRIPTION_MAX, slug)

    def test_example_requests_live_in_the_manual_body(self):
        for manual in sorted((ROOT / "skills").glob("*/SKILL.md")):
            body = manual.read_text(encoding="utf-8").split("\n## When to use\n", 1)[1].split("\n## ", 1)[0]
            self.assertEqual(body.count("\n- Typical requests: "), 1, manual.parent.name)

    def test_gate_reports_an_overgrown_or_unsafe_listing(self):
        descriptions = self.descriptions()
        grown = dict(descriptions, **{"new-hire": "Use for " + "x" * 200})
        total, problems = validate.listing_problems(grown)
        self.assertGreater(total, validate.SKILL_LISTING_BUDGET)
        self.assertEqual(len(problems), 2)
        self.assertIn("new-hire: description is 208 chars (max 100)", problems[0])
        self.assertIn("over the 7200-char company budget", problems[1])
        for unsafe in ('"Quoted. Use for x."', "Tools: a and b. Use for x.", "Notes #1. Use for x.", "[list] Use for x."):
            self.assertEqual(validate.listing_problems({"sample": unsafe})[1],
                             ["sample: description must be a plain YAML scalar (no quotes, ': ' or ' #')"])
        self.assertEqual(validate.listing_problems({"sample": "Books costs. Use for budgets."}), (len("claude-inc:sample") + 29 + 5, []))


if __name__ == "__main__":
    unittest.main()
