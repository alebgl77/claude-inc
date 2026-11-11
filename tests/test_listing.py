"""The company's share of Claude Code's per-turn skill listing stays inside its budget."""

import importlib.util
import json
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

    def test_every_manual_stays_inside_the_company_listing_cap(self):
        descriptions = self.descriptions()
        total, problems = validate.listing_problems(descriptions)
        self.assertEqual(problems, [])
        self.assertEqual(len(descriptions), 64)
        self.assertLessEqual(total, validate.SKILL_LISTING_BUDGET)
        self.assertEqual(validate.SKILL_LISTING_PREFIX, "orgware:")
        self.assertEqual(total, sum(len("orgware:" + slug) + len(text) + 5 for slug, text in descriptions.items()))
        for slug, text in descriptions.items():
            self.assertRegex(text, r"\bUse (when|for)\b", slug)
            self.assertLessEqual(len(text), validate.SKILL_DESCRIPTION_MAX, slug)

    def test_example_requests_live_in_the_manual_body(self):
        for manual in sorted((ROOT / "skills").glob("*/SKILL.md")):
            body = manual.read_text(encoding="utf-8").split("\n## When to use\n", 1)[1].split("\n## ", 1)[0]
            self.assertEqual(body.count("\n- Typical requests: "), 1, manual.parent.name)

    def test_gate_reports_an_overgrown_or_unsafe_listing(self):
        descriptions = self.descriptions()
        long_text = "Use for " + "x" * 200
        self.assertEqual(validate.listing_problems(dict(descriptions, **{"new-hire": long_text}))[1][0],
                         "new-hire: description is 208 chars (max 100); keep the capability and one 'Use for ...' cue, "
                         "and put example requests under '## When to use'")
        hires = 1 + (validate.SKILL_LISTING_BUDGET - validate.listing_footprint(descriptions)) // 100
        grown = dict(descriptions, **{"hire-%03d" % number: "Use for " + "y" * 92 for number in range(hires)})
        total, problems = validate.listing_problems(grown)
        self.assertGreater(total, validate.SKILL_LISTING_BUDGET)
        self.assertEqual(len(problems), 1)
        self.assertIn("over the 7200-char company budget", problems[0])
        for unsafe in ('"Quoted. Use for x."', "Tools: a and b. Use for x.", "Notes #1. Use for x.", "[list] Use for x."):
            self.assertEqual(validate.listing_problems({"sample": unsafe})[1],
                             ["sample: description must be a plain YAML scalar (no quotes, ': ' or ' #')"])
        self.assertEqual(validate.listing_problems({"sample": "Books costs. Use for budgets."}), (len("orgware:sample") + 29 + 5, []))


class AgentListingTests(unittest.TestCase):
    def descriptions(self):
        return {charter.stem: re.search(r"^description:[ \t]*(.*)$", charter.read_text(encoding="utf-8"), re.M).group(1).strip()
                for charter in sorted((ROOT / "agents").glob("*.md"))}

    def test_every_agent_description_is_a_role_and_one_cue(self):
        descriptions = self.descriptions()
        total, problems = validate.agent_listing_problems(descriptions)
        self.assertEqual(problems, [])
        self.assertEqual(len(descriptions), 12)
        self.assertEqual(total, sum(len(text) for text in descriptions.values()))
        for name, text in descriptions.items():
            self.assertRegex(text, r"\bUse (when|for)\b", name)
            self.assertNotIn('"', text, name)

    def test_gate_reports_a_heavy_or_unsafe_agent_description(self):
        self.assertEqual(validate.agent_listing_problems({"sample": "VP of Everything. Use for " + "x" * 200}),
                         (226, ["agent sample: description is 226 chars (max 180); keep the role and one 'Use for ...' cue, "
                                "and quote example requests on the charter's 'Typical requests:' line"]))
        self.assertEqual(validate.agent_listing_problems({"sample": '"Quoted role. Use for x."'})[1],
                         ["agent sample: description must be a plain YAML scalar (no quotes, ': ' or ' #')"])


class PluginNameTests(unittest.TestCase):
    def test_manifests_use_an_accepted_name_and_migrate_the_former_one(self):
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin["name"], validate.PLUGIN_NAME)
        self.assertEqual([entry["name"] for entry in market["plugins"]], [validate.PLUGIN_NAME])
        self.assertEqual(market["name"], validate.MARKETPLACE_NAME)
        self.assertEqual(market["renames"], {former: validate.PLUGIN_NAME for former in validate.FORMER_PLUGIN_NAMES})
        self.assertIsNone(validate.plugin_name_problem(validate.PLUGIN_NAME))
        self.assertNotIn(validate.PLUGIN_NAME, validate.FORMER_PLUGIN_NAMES)

    def test_naming_rule_matches_the_documented_cases(self):
        reserved = ("claude-inc", "Claude_Inc", "claude--inc", "anthropic-tools", "anthropics-kit", "cc-plugin-notes", "claude", "Anthropic",
                    "claude-code", "claude-mods", "official-claude-tools", "tools-claude-official", "anthropic.official")
        warned = ("mcp-for-claude", "company-by-claude", "kit_for_anthropic")
        accepted = ("orgware", "company", "claudeinc", "cc-company", "official-tools", "inc")
        for name in reserved:
            self.assertEqual(validate.plugin_name_problem(name), "is reserved: it passes as one of Anthropic's own", name)
        for name in warned:
            self.assertEqual(validate.plugin_name_problem(name), "reads as one of Anthropic's own", name)
        for name in accepted:
            self.assertIsNone(validate.plugin_name_problem(name), name)
        for former in validate.FORMER_PLUGIN_NAMES:
            self.assertIsNotNone(validate.plugin_name_problem(former), former)


if __name__ == "__main__":
    unittest.main()
