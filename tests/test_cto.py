"""Canonical executive registry and real CLI prompt-boundary regressions."""

import hashlib
import importlib.util
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CTO_SKILLS = ["cto-advisor", "skill-vetting", "appsec-review", "agent-evaluation"]
STAFF = {"chief-of-staff", "token-accountant", *CTO_SKILLS}
spec = importlib.util.spec_from_file_location("cto_mission", ROOT / "skills/chief-of-staff/scripts/mission.py")
mission = importlib.util.module_from_spec(spec)
previous_bytecode_setting = sys.dont_write_bytecode
try:
    sys.dont_write_bytecode = True
    spec.loader.exec_module(mission)
finally:
    sys.dont_write_bytecode = previous_bytecode_setting


class RegistryTests(unittest.TestCase):
    def test_eight_departments_six_staff_and_one_peer_executive(self):
        roster, staff = mission.parse_roster((ROOT / "bin/company").read_text(encoding="utf-8"))
        self.assertEqual(len(roster), 8)
        self.assertNotIn("cto", roster)
        self.assertTrue(all(len(skills) == 6 for skills in roster.values()))
        self.assertEqual(set(staff), STAFF)
        self.assertEqual(len(staff), 6)
        self.assertEqual({path.stem for path in (ROOT / "agents").glob("*.md")}, set(roster) | {"cto"})
        self.assertEqual(len(list((ROOT / "skills").glob("*/SKILL.md"))), 54)

    def test_malformed_staff_and_executive_registries_are_rejected(self):
        cli = (ROOT / "bin/company").read_text(encoding="utf-8")
        invalid = [
            cli.replace("STAFF=(", "MISSING=(", 1),
            cli.replace("STAFF=(chief-of-staff token-accountant", "STAFF=(chief-of-staff chief-of-staff", 1),
            cli.replace("STAFF=(chief-of-staff", "STAFF=(unknown-skill", 1),
            cli.replace("EXECUTIVES=(cto)", "EXECUTIVES=(developers)"),
            cli.replace("EXECUTIVES=(cto)", "EXECUTIVES=(cto cto)"),
            cli.replace("CTO_SKILLS=(cto-advisor", "CTO_SKILLS=(unknown-skill", 1),
            cli.replace("CTO_SKILLS=(cto-advisor skill-vetting", "CTO_SKILLS=(cto-advisor cto-advisor", 1),
            cli + "\nEXECUTIVES=(cto)\n",
            cli.replace("CTO_SKILLS=(", "CTO_SKILLS=($(touch unsafe) ", 1),
        ]
        for index, value in enumerate(invalid):
            with self.subTest(case=index), self.assertRaises(mission.MissionError):
                mission.parse_roster(value)

    def test_nvidia_reference_and_license_remain_exact_pinned_bytes(self):
        expected = {
            "nvidia-skill-inspector.md": "89ab1550769752ffbad782ee63fee3c345d546bded672adaac5fd03d2941aa84",
            "LICENSE.nvidia": "9f8785b47596b2993a17a3fa8d747ae63126a2c5e80a9e77195a907273d71839",
        }
        for name, digest in expected.items():
            path = ROOT / "skills/skill-vetting/references" / name
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest, name)


class CtoCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        candidates = [shutil.which("bash")]
        if os.name == "nt":
            candidates.insert(0, "C:/Program Files/Git/bin/bash.exe")
        cls.bash = None
        for candidate in candidates:
            if candidate and Path(candidate).is_file():
                try:
                    result = subprocess.run([candidate, "-c", 'export PATH="/usr/bin:/bin:$PATH"; command -v dirname'], capture_output=True, timeout=10)
                    if result.returncode == 0:
                        cls.bash = candidate
                        break
                except (OSError, subprocess.TimeoutExpired):
                    pass
        if cls.bash is None:
            raise unittest.SkipTest("working Bash unavailable; canonical registry tests still run")

    def run_company(self, *args, cwd=ROOT, env=None):
        return subprocess.run([self.bash, "-c", 'export PATH="/usr/bin:/bin:$PATH"; exec bash "$@"',
                               "cto-test", str(ROOT / "bin/company"), *args], cwd=cwd, env=env,
                              capture_output=True, timeout=20)

    def test_cto_print_contains_only_its_four_complete_manuals(self):
        brief = 'Review "quotes", café, $(touch NEVER_EXECUTE) & literal text'
        with tempfile.TemporaryDirectory() as directory:
            sandbox = Path(directory)
            (sandbox / ".claude").mkdir()
            (sandbox / ".claude/company-team.md").write_text("INVALID_PROFILE_SENTINEL", encoding="utf-8")
            env = dict(os.environ, CLAUDE_INC_ENGINE="missing-cto-test-engine")
            result = self.run_company("cto", brief, "--print", cwd=sandbox, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, b"")
            text = result.stdout.decode("utf-8")
            self.assertEqual(re.findall(r"^----- EMPLOYEE: ([a-z-]+) -----$", text, re.M), CTO_SKILLS)
            self.assertIn((ROOT / "agents/cto.md").read_text(encoding="utf-8"), text)
            for slug in CTO_SKILLS:
                self.assertEqual(text.count((ROOT / "skills" / slug / "SKILL.md").read_text(encoding="utf-8")), 1)
            self.assertIn(brief, text)
            self.assertNotIn("INVALID_PROFILE_SENTINEL", text)
            self.assertFalse((sandbox / "NEVER_EXECUTE").exists())

    def test_department_prompts_still_have_exactly_six_manuals(self):
        roster, _ = mission.parse_roster((ROOT / "bin/company").read_text(encoding="utf-8"))
        for department, skills in roster.items():
            with self.subTest(department=department):
                result = self.run_company(department, "Bounded test", "--print")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(re.findall(r"^----- EMPLOYEE: ([a-z0-9-]+) -----$", result.stdout.decode("utf-8"), re.M), skills)

    def test_ceo_brief_loads_cto_charter_without_its_specialist_manuals(self):
        with tempfile.TemporaryDirectory() as directory:
            env = dict(os.environ, CLAUDE_INC_GLOBAL_PROFILE=str(Path(directory) / "missing-profile.md"))
            result = self.run_company("brief", "Plan the work", "--print", cwd=directory, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        text = result.stdout.decode("utf-8")
        self.assertIn((ROOT / "agents/cto.md").read_text(encoding="utf-8"), text)
        self.assertEqual(text.count("----- CEO STAFF:"), 2)
        for slug in CTO_SKILLS:
            self.assertNotIn((ROOT / "skills" / slug / "SKILL.md").read_text(encoding="utf-8"), text)

    def test_cto_uses_existing_engine_path_with_one_literal_prompt(self):
        with tempfile.TemporaryDirectory() as directory:
            sandbox = Path(directory)
            capture = sandbox / "captured-prompt.txt"
            engine = sandbox / "recording-engine"
            engine.write_text('#!/usr/bin/env bash\n[ "$#" -eq 1 ] || exit 91\nprintf "%s" "$1" > "$CTO_TEST_CAPTURE"\n', encoding="utf-8")
            engine.chmod(0o700)
            env = dict(os.environ, CLAUDE_INC_ENGINE=engine.as_posix(), CTO_TEST_CAPTURE=capture.as_posix())
            result = self.run_company("cto", 'A "literal" technical brief & no side effects', cwd=sandbox, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('A "literal" technical brief & no side effects', capture.read_text(encoding="utf-8"))
            self.assertEqual(result.stdout, b"")

    def test_cto_requires_a_task_and_is_documented_in_help_and_roster(self):
        self.assertNotEqual(self.run_company("cto", "--print").returncode, 0)
        for command in ("help", "roster"):
            result = self.run_company(command)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(b"company cto", result.stdout)


if __name__ == "__main__":
    unittest.main()
