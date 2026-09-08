"""Canonical Markdown sections must preserve examples without inventing content."""

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("company_builder", ROOT / "scripts/build_company.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class CompanyBuilderTests(unittest.TestCase):
    def test_internal_headings_and_closing_fences_are_preserved(self):
        for opening, closing in [("```markdown", "```"), ("````markdown", "`````"), ("~~~text", "~~~~")]:
            with self.subTest(opening=opening):
                example = opening + "\n## Inner heading\nLiteral content\n" + closing
                source = "# Manual\n\n## Output format\n\n" + example + "\n\n## Quality bar\nSHOULD NOT APPEAR\n"
                self.assertEqual(builder.section(source, "Output format"), example)

    def test_shorter_or_different_fences_cannot_end_an_example(self):
        example = "````\n## Included\n```\n## Still included\n~~~~\nMore text\n````"
        self.assertEqual(builder.section("## Output format\n" + example + "\n## End\nexcluded", "Output format"), example)

    def test_headings_inside_earlier_fences_cannot_start_the_section(self):
        source = "~~~\n## Output format\nFalse section\n~~~\n## Output format\nActual section\n# New document\nExcluded"
        self.assertEqual(builder.section(source, "Output format"), "Actual section")

    def test_indentation_line_endings_and_nested_headings_stay_canonical(self):
        example = "   ~~~ text\r\n## Nested\r\n  Literal spacing  \r\n   ~~~\r\n\r\n### Detail\r\nBody"
        self.assertEqual(builder.section("## Output format ###\r\n\r\n" + example + "\r\n\r\n## Next\r\nExcluded", "Output format"), example)

    def test_missing_empty_unclosed_and_oversized_sections_fail(self):
        for source in ["# No section", "## Output format\n\n## Next\n", "## Output format\n```\nbody", "## Output format\n" + "é" * 25001]:
            with self.subTest(source=source[:30]):
                with self.assertRaises(ValueError):
                    builder.section(source, "Output format")

    def test_all_fifty_examples_have_source_body_and_sales_qa_keep_the_whole_block(self):
        generated = builder.generate().decode("ascii")
        data = json.loads(generated.split("window.CLAUDE_INC_COMPANY = ", 1)[1].removesuffix(";\n"))
        employees = [skill for department in data["departments"] for skill in department["skills"]] + data["staff"]
        self.assertEqual(len(employees), 50)
        for employee in employees:
            with self.subTest(employee=employee["id"]):
                output = employee["output"]
                self.assertTrue(any(character.isalnum() for character in output), "example has no body")
                source = (ROOT / "skills" / employee["id"] / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn(output, source)
        selected = next(department["skills"] for department in data["departments"] if department["id"] == "sales")
        selected += [employee for employee in employees if employee["id"] == "webapp-testing"]
        for employee in selected:
            source = (ROOT / "skills" / employee["id"] / "SKILL.md").read_text(encoding="utf-8")
            expected = source.split("\n## Output format\n", 1)[1].split("\n## Quality bar\n", 1)[0].strip("\r\n")
            self.assertEqual(employee["output"], expected, employee["id"])
            self.assertIn("\n## ", employee["output"])
            self.assertTrue(employee["output"].endswith("```"), employee["id"])


if __name__ == "__main__":
    unittest.main()
