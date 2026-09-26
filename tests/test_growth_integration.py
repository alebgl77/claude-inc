"""Saved-roster compatibility and Growth/CAIO boundaries, without migration."""

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "skills/chief-of-staff/scripts/project.py"
SPEC = importlib.util.spec_from_file_location("growth_project_tests", HELPER)
project = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(project)
harness = project.harness()


class SavedRosterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="company-growth-compat-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.workspace = project.Workspace(self.root)
        self.workspace.initialize("Saved project", "Preserve the actual company history")
        self.current = list(self.workspace.departments)
        self.legacy = self.current[:-1]

    def state(self):
        return self.workspace.load()[0]

    def save(self, state):
        project.validate_state(state, self.workspace.departments)
        # Deliberately retain distinct whitespace to detect implicit rewrites.
        self.workspace.path.write_bytes((json.dumps(state, indent=3) + "\n\n").encode("utf-8"))

    def legacy_state(self, schema):
        if schema == 2:
            fixture = json.loads((ROOT / "tests/harness-fixtures.json").read_text(encoding="utf-8"))
            return copy.deepcopy(fixture["states"][0]["state"])
        state = self.state()
        state["departments"] = self.legacy
        state["activeDepartments"] = ["marketing"]
        return state

    def unchanged_failure(self, callback, message=None):
        before = self.workspace.path.read_bytes()
        with self.assertRaisesRegex(project.ProjectError, message or "."):
            callback()
        self.assertEqual(self.workspace.path.read_bytes(), before)
        self.assertFalse(self.workspace.lock.exists())
        self.assertEqual(list(self.workspace.directory.glob("*.tmp")), [])

    def add(self, department="marketing", task_id="new-work"):
        return self.workspace.mutate("task.add", task_id, department=department, title="A bounded deliverable",
                                     acceptance="The submitted file contains the observed evidence", depends_on=[])

    def submit(self, task_id):
        (self.root / "evidence.md").write_text("Observed synthetic evidence\n", encoding="utf-8")
        return self.workspace.mutate("task.submit", task_id, artifacts=["evidence.md"], summary="Read the synthetic evidence")

    def accept(self, task_id, reviewer="ceo"):
        state = self.state()
        values = {"reviewer": reviewer, "note": "Reviewed the recorded artifact"}
        if state["schemaVersion"] == 2:
            round_value = harness.latest_round(state, task_id)
            policy = state["harness"]["policies"][task_id]
            values.update(expected_revision=state["revision"], submission_revision=round_value["submitRevision"],
                          gates={"version": 1, "taskId": task_id, "submitRevision": round_value["submitRevision"],
                                 "policyFingerprint": policy["fingerprint"],
                                 "artifactFingerprint": harness.artifact_fingerprint(round_value["artifacts"]),
                                 "results": [{"gateId": gate["id"], "status": "pass", "observation": "Read the synthetic evidence",
                                              "evidence": [{"path": "evidence.md", "locator": "Line 1"}]} for gate in policy["gates"]]})
        return self.workspace.mutate("task.accept", task_id, **values)

    def test_legacy_read_only_surfaces_and_native_start_preserve_exact_bytes(self):
        for schema in (1, 2):
            with self.subTest(schema=schema):
                state = self.legacy_state(schema)
                self.save(state)
                before = self.workspace.path.read_bytes()
                loaded, raw = self.workspace.load()
                self.assertEqual(raw, before)
                prompt = project.render_prompt(self.workspace, loaded)
                self.assertNotIn(str(ROOT / "agents/growth.md").replace("\\", "\\\\"), prompt)
                self.assertIn("historical eight-department workspace", prompt)
                for args in (("status", "--format", "json"), ("context",), ("prompt",), ("loop", "next", "--format", "json")):
                    result = subprocess.run([sys.executable, "-B", str(HELPER), *args], cwd=self.root,
                                            env=dict(os.environ, PYTHONIOENCODING="utf-8"), capture_output=True, timeout=30)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(self.workspace.path.read_bytes(), before)
                with mock.patch.object(project, "claude_command", return_value=["native-host"]), mock.patch.object(project.subprocess, "call", return_value=0) as launch:
                    self.assertEqual(project.start(self.workspace, loaded), 0)
                    self.assertFalse(launch.call_args.kwargs["shell"])
                    self.assertNotIn("--model", launch.call_args.args[0])
                self.assertEqual(self.workspace.path.read_bytes(), before)

    def test_legacy_lifecycle_preserves_roster_profiles_and_prior_history(self):
        for schema in (1, 2):
            with self.subTest(schema=schema):
                old = self.legacy_state(schema)
                self.save(old)
                self.add()
                self.workspace.mutate("task.start", "new-work")
                self.submit("new-work")
                self.accept("new-work")
                state = self.state()
                self.assertEqual(state["departments"], self.legacy)
                self.assertEqual(state["tasks"][-1]["status"], "done")
                self.assertEqual(state["events"][:len(old["events"])], old["events"])
                if schema == 2:
                    self.assertEqual(state["harness"]["profiles"], old["harness"]["profiles"])
                    for task_id, policy in old["harness"]["policies"].items():
                        self.assertEqual(state["harness"]["policies"][task_id], policy)
                    self.assertEqual(state["harness"]["rounds"][:len(old["harness"]["rounds"])], old["harness"]["rounds"])

    def test_legacy_enable_selects_eight_profiles_from_one_packaged_digest(self):
        self.save(self.legacy_state(1))
        self.add()
        old = self.state()
        state = self.workspace.mutate("harness.generate", expected_revision=old["revision"])
        profiles = state["harness"]["profiles"]
        self.assertEqual(list(profiles), self.legacy)
        digest = hashlib.sha256((ROOT / harness.PROFILE_PATH).read_bytes()).hexdigest()
        self.assertEqual({value["source"]["sha256"] for value in profiles.values()}, {digest})
        self.assertEqual(state["events"][:-1], old["events"])
        self.assertEqual(state["tasks"], old["tasks"])
        before = self.workspace.path.read_bytes()
        self.workspace.mutate("harness.generate", expected_revision=state["revision"])
        self.assertEqual(self.workspace.path.read_bytes(), before)

    def test_legacy_growth_assignment_and_caio_assignment_or_review_are_atomic_rejections(self):
        for schema in (1, 2):
            with self.subTest(schema=schema):
                self.save(self.legacy_state(schema))
                self.unchanged_failure(lambda: self.add("growth"), "new project workspace")
                self.unchanged_failure(lambda: self.add("caio"))
                self.add()
                self.workspace.mutate("task.start", "new-work")
                self.submit("new-work")
                self.unchanged_failure(lambda: self.accept("new-work", "caio"))
                self.unchanged_failure(lambda: self.accept("new-work", "growth"))

    def test_exact_supported_rosters_reject_permutations_duplicates_and_partial_lists(self):
        state = self.state()
        for saved in (self.current, self.legacy):
            valid = copy.deepcopy(state)
            valid["departments"] = saved
            valid["activeDepartments"] = ["marketing"]
            project.validate_state(valid, self.workspace.departments)
        invalid = [self.current[::-1], self.legacy[::-1], self.current[:-2], self.current + ["growth"],
                   self.legacy + ["caio"], ["designers", *self.current[1:]], self.current[1:]]
        for departments in invalid:
            with self.subTest(departments=departments):
                value = copy.deepcopy(state)
                value["departments"] = departments
                with self.assertRaises(project.ProjectError):
                    project.validate_state(value, self.workspace.departments)
                self.workspace.path.write_text(json.dumps(value), encoding="utf-8")
                self.unchanged_failure(lambda: self.workspace.mutate("decision.add", text="Must not write"))

    def test_legacy_tasks_active_departments_and_reviewers_cannot_escape_saved_roster(self):
        state = self.legacy_state(2)
        for field in ("active", "owner", "reviewer"):
            value = copy.deepcopy(state)
            if field == "active":
                value["activeDepartments"].append("growth")
            elif field == "owner":
                value["tasks"][0]["department"] = "growth"
            else:
                fixture = json.loads((ROOT / "tests/harness-fixtures.json").read_text(encoding="utf-8"))
                value = copy.deepcopy(fixture["states"][2]["state"])
                value["tasks"][0]["reviews"][-1]["reviewer"] = "growth"
            with self.subTest(field=field), self.assertRaises(project.ProjectError):
                project.validate_state(value, self.workspace.departments)

    def test_new_growth_lifecycle_and_caio_staff_are_available_without_reviewer_authority(self):
        self.assertEqual(self.state()["departments"], self.current)
        self.assertEqual(self.current[-1], "growth")
        self.add("growth", "growth-test")
        self.workspace.mutate("harness.generate", expected_revision=self.state()["revision"],
                              plan={"version": 1, "tasks": {"growth-test": {"skills": ["growth-experiments", "agent-reliability"], "criteria": []}}})
        self.workspace.mutate("task.start", "growth-test")
        self.submit("growth-test")
        self.unchanged_failure(lambda: self.accept("growth-test", "caio"))
        state = self.accept("growth-test", "sales")
        self.assertEqual(state["tasks"][0]["status"], "done")
        self.assertEqual(len(state["harness"]["profiles"]), 9)
        self.assertIn("business-signal-and-qualification", [gate["id"] for gate in state["harness"]["policies"]["growth-test"]["gates"]])

    def test_profiles_command_always_reports_packaged_nine_for_legacy_workspace(self):
        self.save(self.legacy_state(1))
        before = self.workspace.path.read_bytes()
        result = subprocess.run([sys.executable, "-B", str(HELPER), "harness", "profiles", "--format", "json"],
                                cwd=self.root, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(set(json.loads(result.stdout)["profiles"]), set(self.current))
        self.assertEqual(self.workspace.path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
