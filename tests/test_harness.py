"""Business harness contracts, history replay, atomic review and derived guidance."""

import copy
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
SPEC = importlib.util.spec_from_file_location("harness_project_tests", HELPER)
project = importlib.util.module_from_spec(SPEC)
previous = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    SPEC.loader.exec_module(project)
finally:
    sys.dont_write_bytecode = previous
harness = project.harness()


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="claude-inc-harness-tests-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.workspace = project.Workspace(self.root)
        self.workspace.initialize("Projet café", "A real founder scope, with no invented tasks.", goals=["Readable evidence"], constraints=["No external actions"])

    def state(self):
        return self.workspace.load()[0]

    def mutate(self, action, task_id=None, **values):
        return self.workspace.mutate(action, task_id, **values)

    def add(self, task_id="prototype", department="developers", dependencies=None, **values):
        return self.mutate("task.add", task_id, department=department, title="Deliver " + task_id,
                           acceptance="The named artifacts satisfy the observed task contract.", depends_on=dependencies or [], **values)

    def enable(self, **values):
        return self.mutate("harness.generate", expected_revision=self.state()["revision"], **values)

    def submit(self, task_id="prototype", content="Observed synthetic evidence café\n"):
        (self.root / (task_id + ".md")).write_text(content, encoding="utf-8")
        return self.mutate("task.submit", task_id, artifacts=[task_id + ".md"], summary="Recorded actual fixture content")

    def ready_review(self, **config):
        self.add()
        self.enable(**config)
        self.mutate("task.start", "prototype")
        return self.submit()

    def gates(self, task_id="prototype", status="pass"):
        state = self.state()
        round_value = harness.latest_round(state, task_id)
        policy = state["harness"]["policies"][task_id]
        return {"version": 1, "taskId": task_id, "submitRevision": round_value["submitRevision"],
                "policyFingerprint": policy["fingerprint"], "artifactFingerprint": harness.artifact_fingerprint(round_value["artifacts"]),
                "results": [{"gateId": gate["id"], "status": status,
                             "evidence": [{"path": task_id + ".md", "locator": "Line 1: fixture observation"}] if status == "pass" else [],
                             "observation": "Read fixture artifact; this is a recorded judgment, not authenticated quality." if status == "pass" else ""}
                            for gate in policy["gates"]]}

    def review(self, decision="accept", task_id="prototype", gates="automatic", **values):
        state = self.state()
        if gates == "automatic":
            gates = self.gates(task_id)
        args = {"reviewer": "cto", "note": "Inspected synthetic fixture evidence", "expected_revision": state["revision"],
                "submission_revision": harness.current_submission(state, task_id), "gates": gates}
        args.update(values)
        return self.mutate("task." + decision, task_id, **args)

    def unchanged(self, function, pattern=None):
        before = self.workspace.path.read_bytes()
        with self.assertRaisesRegex(project.ProjectError, pattern or "."):
            function()
        self.assertEqual(self.workspace.path.read_bytes(), before)
        self.assertFalse(self.workspace.lock.exists())

    def invalid_state(self, value):
        with self.assertRaises((project.ProjectError, TypeError, KeyError)):
            project.validate_state(value, self.workspace.departments)

    def cli(self, *arguments):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        return subprocess.run([sys.executable, str(HELPER), *arguments], cwd=self.root, env=env,
                              capture_output=True, timeout=30)

    def test_schema1_is_unchanged_until_explicit_enable_and_profiles_need_no_workspace(self):
        before = self.workspace.path.read_bytes()
        self.assertEqual(self.state()["schemaVersion"], 1)
        self.assertNotIn("harness", self.state())
        self.assertEqual(harness.next_action(self.state())["action"], "plan")
        result = self.cli("harness", "profiles", "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(json.loads(result.stdout)["profiles"]), 8)
        self.assertEqual(self.workspace.path.read_bytes(), before)
        with tempfile.TemporaryDirectory() as absent:
            result = subprocess.run([sys.executable, str(HELPER), "harness", "profiles", "--format", "json"], cwd=absent, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(Path(absent).iterdir()), [])

    def test_empty_enable_atomic_revision_and_every_profile_is_concrete_distinct(self):
        state = self.enable()
        self.assertEqual(state["schemaVersion"], 2)
        self.assertEqual(state["harness"]["enabledRevision"], 2)
        self.assertEqual(state["events"][-1], {"revision": 2, "type": "harness.generate", "taskId": None, "note": "Business harness enabled"})
        self.assertEqual(state["harness"]["policies"], {})
        self.assertEqual(harness.next_action(state)["action"], "plan")
        criteria = [check["criterion"] for profile in state["harness"]["profiles"].values() for check in profile["checks"]]
        self.assertEqual(len(criteria), 16)
        self.assertEqual(len(set(criteria)), 16)
        self.assertTrue(all(len(value) > 80 for value in criteria))

    def test_generate_requires_current_revision_and_never_resets_or_replaces_defaults(self):
        self.unchanged(lambda: self.mutate("harness.generate"), "expected-revision")
        self.unchanged(lambda: self.mutate("harness.generate", expected_revision=0), "revision")
        self.enable(effort="light")
        before = self.workspace.path.read_bytes()
        state = self.enable()
        self.assertEqual(state["harness"]["defaults"], {"stage": "build", "effort": "light", "maxIterations": 2})
        self.assertEqual(before, self.workspace.path.read_bytes())
        self.unchanged(lambda: self.enable(effort="deep"), "immutable")
        self.unchanged(lambda: self.enable(max_iterations=5), "immutable")

    def test_stage_effort_and_explicit_limit_validation(self):
        for name, value in (("stage", "unknown"), ("effort", "huge"), ("max_iterations", 0), ("max_iterations", 11), ("max_iterations", True)):
            self.unchanged(lambda name=name, value=value: self.enable(**{name: value}))
        state = self.enable(stage="discover", effort="deep", max_iterations=4)
        self.assertEqual(state["harness"]["defaults"], {"stage": "discover", "effort": "deep", "maxIterations": 4})

    def test_new_tasks_autoenroll_with_fixed_contract_and_department_gates(self):
        self.enable()
        for department in self.workspace.departments:
            state = self.add(department, department)
            policy = state["harness"]["policies"][department]
            self.assertEqual(policy["createdRevision"], state["revision"])
            self.assertEqual(policy["skills"], [])
            self.assertEqual(len(policy["gates"]), 3)
            self.assertEqual(policy["gates"][0]["criterion"], state["tasks"][-1]["acceptance"])
            self.assertTrue(all(gate["required"] is True for gate in policy["gates"]))

    def test_semantic_skills_allow_owner_and_staff_and_only_add_criteria(self):
        self.add()
        staff = project.canonical_roster()[1]
        plan = {"version": 1, "tasks": {"prototype": {"skills": ["superpowers", staff[-1]], "criteria": ["The founder supplied French labels remain literal."]}}}
        state = self.enable(plan=plan)
        policy = state["harness"]["policies"]["prototype"]
        self.assertEqual(policy["skills"], ["superpowers", staff[-1]])
        self.assertEqual(policy["gates"][-1]["id"], "project-1")
        before = self.workspace.path.read_bytes()
        self.enable(plan=plan)
        self.assertEqual(self.workspace.path.read_bytes(), before)
        self.unchanged(lambda: self.enable(plan={"version": 1, "tasks": {}}), "immutable")
        self.unchanged(lambda: self.add("bad", harness_plan={"version": 1, "skills": ["draft-outreach"], "criteria": []}), "skill")
        self.add("staff", harness_plan={"version": 1, "skills": [staff[-1]], "criteria": []})

    def test_semantic_plan_bounds_unknown_tasks_and_fields(self):
        self.add()
        selections = [
            {"skills": ["unknown"], "criteria": []}, {"skills": ["superpowers"] * 2, "criteria": []},
            {"skills": [], "criteria": ["a"] * 6}, {"skills": [], "criteria": ["a"] * 2},
            {"skills": [], "criteria": ["\ud800"]}, {"skills": [], "criteria": ["x" * 2001]},
            {"skills": [], "criteria": [], "command": "never run"}, {"skills": None, "criteria": []}]
        for selection in selections:
            self.unchanged(lambda selection=selection: self.enable(plan={"version": 1, "tasks": {"prototype": selection}}))
        self.unchanged(lambda: self.enable(plan={"version": 1, "tasks": {"missing": {"skills": [], "criteria": []}}}))
        self.unchanged(lambda: self.add("premature", harness_plan={"version": 1, "skills": [], "criteria": []}), "enable")

    def test_generate_files_reject_duplicates_controls_surrogates_size_and_unsafe_reads(self):
        file = self.root / "plan.json"
        for raw in (b'{"version":1,"version":1,"tasks":{}}', b"[", b'{"version":NaN,"tasks":{}}', b"x" * (harness.INPUT_MAX_BYTES + 1)):
            file.write_bytes(raw)
            self.unchanged(lambda: self.enable(plan_file=str(file)))
        file.write_text('{"version":1,"tasks":{}}', encoding="utf-8")
        with mock.patch.object(project, "read_regular", side_effect=project.ProjectError("unsafe input")):
            self.unchanged(lambda: self.enable(plan_file=str(file)))

    def test_review_is_one_transaction_with_round_assessment_and_event(self):
        previous = self.ready_review()
        state = self.review()
        self.assertEqual(state["revision"], previous["revision"] + 1)
        self.assertEqual(state["tasks"][0]["status"], "done")
        self.assertEqual(state["tasks"][0]["reviews"][0]["reviewer"], "cto")
        assessment = state["harness"]["assessments"][0]
        self.assertEqual(assessment["reviewRevision"], state["revision"])
        self.assertEqual(assessment["submitRevision"], previous["revision"])
        self.assertEqual(state["events"][-1]["type"], "task.accept")
        self.assertEqual(harness.next_action(state)["action"], "complete")

    def test_gate_acceptance_rejects_missing_fail_unknown_and_duplicate_or_omitted_gates(self):
        self.ready_review()
        self.unchanged(lambda: self.review(gates=None), "gates-file")
        for status in ("fail", "unknown"):
            self.unchanged(lambda status=status: self.review(gates=self.gates(status=status)), "pass")
        gates = self.gates()
        gates["results"].pop()
        self.unchanged(lambda: self.review(gates=gates), "all required")
        gates = self.gates()
        gates["results"][1] = copy.deepcopy(gates["results"][0])
        self.unchanged(lambda: self.review(gates=gates), "exactly once")

    def test_review_rejects_stale_revision_submission_policy_and_artifact_fingerprints(self):
        self.ready_review()
        for args in ({"expected_revision": None}, {"expected_revision": 1}, {"expected_revision": True}, {"submission_revision": None}, {"submission_revision": 1}, {"submission_revision": True}):
            self.unchanged(lambda args=args: self.review(**args))
        for field, value in (("taskId", "missing"), ("submitRevision", 1), ("submitRevision", True), ("policyFingerprint", "a" * 64), ("artifactFingerprint", "b" * 64), ("version", True)):
            gates = self.gates()
            gates[field] = value
            self.unchanged(lambda gates=gates: self.review(gates=gates))

    def test_pass_requires_observed_evidence_in_the_submitted_round(self):
        self.ready_review()
        variants = [{"evidence": []}, {"observation": " "}, {"observation": "\udfff"},
                    {"evidence": [{"path": "../outside.md", "locator": "line 1"}]},
                    {"evidence": [{"path": "prototype.md", "locator": ""}]},
                    {"evidence": [{"path": "prototype.md", "locator": "x" * 1001}]}]
        for change in variants:
            gates = self.gates()
            gates["results"][0].update(change)
            self.unchanged(lambda gates=gates: self.review(gates=gates))

    def test_changed_artifact_blocks_acceptance_without_persisting_assessment(self):
        self.ready_review()
        (self.root / "prototype.md").write_text("changed", encoding="utf-8")
        self.unchanged(lambda: self.review(), "changed")
        self.assertEqual(self.state()["harness"]["assessments"], [])

    def test_revision_can_recover_missing_artifacts_without_gates(self):
        self.ready_review()
        (self.root / "prototype.md").unlink()
        state = self.review("revise", gates=None)
        self.assertEqual(state["tasks"][0]["status"], "active")
        self.assertEqual(state["harness"]["assessments"], [])
        self.submit()
        self.review()

    def test_revise_can_record_fail_unknown_and_requires_valid_optional_assessment(self):
        self.ready_review()
        gates = self.gates(status="unknown")
        gates["results"][0]["status"] = "fail"
        state = self.review("revise", gates=gates)
        self.assertEqual(len(state["harness"]["assessments"]), 1)
        self.assertEqual(harness.next_action(state)["action"], "work")

    def test_in_review_migration_requires_revise_and_a_fresh_round(self):
        self.add()
        self.mutate("task.start", "prototype")
        legacy = self.submit()
        state = self.enable()
        self.assertEqual(state["harness"]["rounds"], [])
        self.assertEqual(harness.next_action(state)["action"], "revise")
        self.unchanged(lambda: self.review(gates=None), "pre-harness")
        self.review("revise", gates=None)
        self.submit()
        state = self.review()
        self.assertGreater(state["harness"]["rounds"][0]["submitRevision"], legacy["revision"])

    def test_historical_done_tasks_are_excluded_and_cannot_be_extended(self):
        self.add()
        self.mutate("task.start", "prototype")
        self.submit()
        self.mutate("task.accept", "prototype", reviewer="ceo", note="Historical fixture review")
        state = self.enable()
        self.assertEqual(state["harness"]["policies"], {})
        self.unchanged(lambda: self.mutate("harness.extend", "prototype", expected_revision=state["revision"], max_iterations=4, reason="No work left"))

    def test_lifetime_submission_limit_blocks_work_but_final_review_may_accept(self):
        self.ready_review(max_iterations=1)
        self.assertEqual(harness.next_action(self.state())["action"], "evaluate")
        self.review()
        self.unchanged(lambda: self.mutate("harness.extend", "prototype", expected_revision=self.state()["revision"], max_iterations=2, reason="Already done"), "completed")

    def test_exhaustion_requires_monotonic_extension_and_does_not_reset_history(self):
        self.ready_review(max_iterations=1)
        self.review("revise", gates=None)
        state = self.state()
        self.assertEqual(harness.next_action(state)["action"], "escalate")
        self.unchanged(lambda: self.submit(), "allowance")
        self.mutate("task.block", "prototype", reason="Allowance exhausted")
        self.unchanged(lambda: self.mutate("task.start", "prototype"), "allowance")
        for limit, reason in ((1, "same"), (0, "lower"), (11, "above hard cap"), (True, "boolean"), (2, " ")):
            self.unchanged(lambda limit=limit, reason=reason: self.mutate("harness.extend", "prototype", expected_revision=self.state()["revision"], max_iterations=limit, reason=reason))
        before = self.state()
        state = self.mutate("harness.extend", "prototype", expected_revision=before["revision"], max_iterations=2, reason="One more evidence repair authorized")
        self.assertEqual(state["harness"]["policies"], before["harness"]["policies"])
        self.assertEqual(state["harness"]["rounds"], before["harness"]["rounds"])
        self.assertEqual(harness.next_action(state)["action"], "waiting")
        self.mutate("task.start", "prototype")
        self.submit()
        self.review()

    def test_extension_does_not_invalidate_an_existing_review_round(self):
        self.ready_review(max_iterations=1)
        gates = self.gates()
        self.mutate("harness.extend", "prototype", expected_revision=self.state()["revision"], max_iterations=2, reason="Record explicit extra capacity")
        self.review(gates=gates)

    def legacy_rounds(self, count, done=False):
        self.add()
        self.mutate("task.start", "prototype")
        for index in range(count):
            self.submit()
            if index != count - 1 or done:
                self.mutate("task.accept" if done and index == count - 1 else "task.revise", "prototype", reviewer="ceo", note="Legacy fixture review")

    def test_legacy_iterations_count_and_hard_cap_activation_refusal(self):
        self.legacy_rounds(3)
        self.enable(max_iterations=3)
        self.review("revise", gates=None)
        self.assertEqual(harness.used_limit(self.state(), "prototype"), (3, 3))
        self.unchanged(lambda: self.submit(), "allowance")

    def test_ten_legacy_rounds_unfinished_cannot_activate(self):
        self.legacy_rounds(10)
        self.unchanged(lambda: self.enable(max_iterations=10), "ten lifetime")
        self.assertEqual(self.state()["schemaVersion"], 1)

    def test_ten_legacy_rounds_done_can_activate_as_historical(self):
        self.legacy_rounds(10, done=True)
        self.assertEqual(self.enable()["harness"]["policies"], {})

    def test_review_and_generation_atomic_failures_leave_before_image_and_no_temp(self):
        before = self.workspace.path.read_bytes()
        with mock.patch.object(project.os, "replace", side_effect=OSError("synthetic disk failure")):
            with self.assertRaises(OSError):
                self.enable()
        self.assertEqual(self.workspace.path.read_bytes(), before)
        self.assertFalse(self.workspace.lock.exists())
        self.assertEqual(list(self.workspace.directory.glob("*.tmp")), [])
        self.ready_review()
        before = self.workspace.path.read_bytes()
        with mock.patch.object(project.os, "replace", side_effect=OSError("synthetic disk failure")):
            with self.assertRaises(OSError):
                self.review()
        self.assertEqual(self.workspace.path.read_bytes(), before)
        self.assertEqual(self.state()["harness"]["assessments"], [])

    def test_competing_writer_and_before_image_conflict_are_preserved(self):
        self.enable()
        before = self.workspace.path.read_bytes()
        with self.workspace.locked():
            result = self.cli("harness", "generate", "--expected-revision", "2")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"locked", result.stderr)
        self.assertEqual(self.workspace.path.read_bytes(), before)
        old, raw = self.workspace.load()
        self.mutate("decision.add", text="Newer writer")
        current = self.workspace.path.read_bytes()
        with self.workspace.locked():
            with self.assertRaisesRegex(project.ProjectError, "revision changed"):
                self.workspace.commit(old, raw)
        self.assertEqual(self.workspace.path.read_bytes(), current)

    def test_policy_round_and_assessment_forgery_is_rejected(self):
        self.ready_review()
        self.review()
        base = self.state()
        cases = []
        for field, value in (("version", True), ("enabledRevision", 1), ("rounds", []), ("assessments", []), ("policies", {})):
            bad = copy.deepcopy(base); bad["harness"][field] = value; cases.append(bad)
        for field, value in (("fingerprint", "a" * 64), ("createdRevision", True), ("stage", "operate"), ("skills", ["draft-outreach"]), ("gates", [])):
            bad = copy.deepcopy(base); bad["harness"]["policies"]["prototype"][field] = value; cases.append(bad)
        for field, value in (("submitRevision", True), ("policyFingerprint", "a" * 64), ("artifacts", [])):
            bad = copy.deepcopy(base); bad["harness"]["rounds"][0][field] = value; cases.append(bad)
        for field, value in (("reviewRevision", 1), ("submitRevision", 1), ("artifactFingerprint", "b" * 64), ("taskId", "missing"), ("results", [])):
            bad = copy.deepcopy(base); bad["harness"]["assessments"][0][field] = value; cases.append(bad)
        bad = copy.deepcopy(base); bad["harness"]["assessments"][0]["results"][0]["status"] = "unknown"; cases.append(bad)
        bad = copy.deepcopy(base); bad["harness"]["policies"]["prototype"]["gates"][0]["criterion"] = "easier"; cases.append(bad)
        bad = copy.deepcopy(base); bad["tasks"][0]["artifacts"][0]["sha256"] = "c" * 64; cases.append(bad)
        for value in cases:
            self.invalid_state(value)

    def test_extension_history_cannot_reset_limits_or_attach_to_wrong_events(self):
        self.ready_review(max_iterations=1)
        self.review("revise", gates=None)
        self.mutate("harness.extend", "prototype", expected_revision=self.state()["revision"], max_iterations=2, reason="Retry once")
        self.submit()
        base = self.state()
        for field, value in (("fromLimit", 0), ("toLimit", 1), ("revision", True), ("taskId", "missing"), ("reason", "different")):
            bad = copy.deepcopy(base); bad["harness"]["extensions"][0][field] = value; self.invalid_state(bad)
        bad = copy.deepcopy(base)
        bad["harness"]["extensions"][0]["revision"] = bad["revision"]
        self.invalid_state(bad)

    def test_current_assessment_cannot_reuse_an_earlier_submission(self):
        self.ready_review()
        self.review("revise")
        self.submit(content="Second round evidence")
        self.review()
        bad = self.state()
        bad["harness"]["assessments"][-1]["submitRevision"] = bad["harness"]["rounds"][0]["submitRevision"]
        self.invalid_state(bad)

    def test_later_extension_cannot_retroactively_authorize_an_exhausted_submission(self):
        self.ready_review(max_iterations=1)
        self.review("revise", gates=None)
        self.mutate("harness.extend", "prototype", expected_revision=self.state()["revision"], max_iterations=2, reason="Permit one repair")
        self.submit()
        bad = self.state()
        # Swap only these independent event positions, keeping shapes, final
        # limits, task status and all referenced revisions internally coherent.
        extension, submission = bad["events"][-2:]
        old_extension_revision, old_submit_revision = extension["revision"], submission["revision"]
        extension["revision"], submission["revision"] = old_submit_revision, old_extension_revision
        bad["events"][-2:] = [submission, extension]
        bad["harness"]["extensions"][-1]["revision"] = old_submit_revision
        bad["harness"]["rounds"][-1]["submitRevision"] = old_extension_revision
        with self.assertRaisesRegex(project.ProjectError, "allowance"):
            project.validate_state(bad, self.workspace.departments)

    def test_replay_rejects_cto_before_activation_and_extensions_after_completion(self):
        self.add()
        self.mutate("task.start", "prototype")
        self.submit()
        self.mutate("task.accept", "prototype", reviewer="ceo", note="Historical acceptance")
        self.enable()
        bad = self.state()
        bad["tasks"][0]["reviews"][0]["reviewer"] = "cto"
        self.invalid_state(bad)
        self.add("controlled")
        self.mutate("task.start", "controlled")
        self.submit("controlled")
        self.review(task_id="controlled")
        bad = self.state()
        bad["revision"] += 1
        bad["events"].append({"revision": bad["revision"], "type": "harness.extend", "taskId": "controlled", "note": "No remaining work"})
        bad["harness"]["extensions"].append({"revision": bad["revision"], "taskId": "controlled", "fromLimit": 3, "toLimit": 4, "reason": "No remaining work"})
        self.invalid_state(bad)

    def test_next_action_ranking_dependencies_review_priority_and_blockers(self):
        self.add("standalone")
        self.add("root")
        self.add("child", dependencies=["root"])
        self.add("grandchild", dependencies=["child"])
        state = self.enable()
        self.assertEqual(harness.next_action(state)["taskId"], "root")
        self.assertEqual(harness.next_action(state)["readyIndependentIds"], ["root", "standalone"])
        self.mutate("task.start", "standalone")
        self.assertEqual(harness.next_action(self.state())["taskId"], "standalone")
        self.mutate("task.start", "root")
        self.submit("standalone")
        self.assertEqual(harness.next_action(self.state())["action"], "evaluate")
        self.review(task_id="standalone")
        self.submit("root")
        self.review(task_id="root")
        self.assertEqual(harness.next_action(self.state())["taskId"], "child")
        self.unchanged(lambda: self.mutate("task.start", "grandchild"), "dependencies")
        self.mutate("task.start", "child")
        self.mutate("task.block", "child", reason="Need a founder answer")
        self.assertEqual(harness.next_action(self.state())["action"], "waiting")

    def test_projection_excludes_history_but_preserves_contract_and_access_to_full_state(self):
        self.ready_review(max_iterations=5)
        for _ in range(3):
            self.review("revise")
            self.submit(content="A fixture repair was made. " * 30)
        state = self.state()
        projection = harness.projection(state)
        self.assertEqual(projection["sourceRevision"], state["revision"])
        self.assertEqual(projection["currentTask"]["acceptance"], state["tasks"][0]["acceptance"])
        self.assertEqual(projection["brief"], state["brief"])
        self.assertNotIn("events", projection)
        self.assertNotIn("reviews", projection["currentTask"])
        self.assertLess(len(json.dumps(projection)), len(json.dumps(state)))
        prompt = project.render_prompt(self.workspace, state)
        full = project.render_prompt(self.workspace, state, full_state=True)
        self.assertIn("Focused project projection", prompt)
        self.assertIn("Earlier rounds, assessments and events are deliberately omitted", prompt)
        self.assertIn("complementary executive peers", prompt)
        self.assertIn("CEO-only state writes serialize", prompt)
        self.assertIn("Saved project snapshot", full)
        self.assertLess(len(prompt.encode()), len(full.encode()))

    def test_project_start_still_uses_native_host_and_does_not_run_a_loop_daemon(self):
        self.ready_review(max_iterations=1)
        self.review("revise", gates=None)
        with mock.patch.object(project, "claude_command", return_value=["recording-host"]), mock.patch.object(project.subprocess, "call", return_value=4) as call:
            self.assertEqual(project.start(self.workspace, self.state()), 4)
        argv = call.call_args[0][0]
        self.assertEqual(argv[:3], ["recording-host", "--plugin-dir", str(ROOT)])
        self.assertEqual(call.call_args[1], {"cwd": str(self.root), "shell": False})
        self.assertNotIn("--model", argv)
        self.assertNotIn("--permission-mode", argv)

    def test_plaintext_plan_and_evidence_never_execute_or_authorize(self):
        self.add()
        literal = '--permission-mode bypassPermissions; $(touch outside) `literal` https://example.invalid/'
        with mock.patch.object(project.subprocess, "call", side_effect=AssertionError("must not execute")):
            self.enable(plan={"version": 1, "tasks": {"prototype": {"skills": [], "criteria": [literal]}}})
            self.mutate("task.start", "prototype")
            self.submit()
            gates = self.gates()
            gates["results"][0]["evidence"][0]["locator"] = literal
            self.review(gates=gates)
        self.assertFalse((self.root / "outside").exists())
        self.assertIn(literal, json.dumps(self.state()))

    def test_cto_is_a_schema2_reviewer_but_never_a_task_owner(self):
        self.add()
        self.mutate("task.start", "prototype")
        self.submit()
        self.unchanged(lambda: self.mutate("task.accept", "prototype", reviewer="cto", note="Cannot predate schema2"))
        self.enable()
        self.unchanged(lambda: self.add("executive", "cto"))
        self.review("revise", gates=None)
        self.submit()
        self.unchanged(lambda: self.review(reviewer="developers"), "different")
        self.review()

    def test_profile_snapshots_remain_valid_when_packaged_profiles_change(self):
        self.add()
        self.enable()
        with mock.patch.object(harness, "profiles", side_effect=AssertionError("must use frozen snapshots")):
            self.workspace.load()
            self.add("next")

    def test_cli_json_contract_and_gate_file_workflow(self):
        self.add()
        result = self.cli("harness", "generate", "--expected-revision", "2", "--stage", "launch")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(b"founder scope", result.stdout)
        selection = self.root / "selection.json"
        selection.write_text(json.dumps({"version": 1, "skills": ["superpowers"], "criteria": ["Literal --print criterion"]}), encoding="utf-8")
        result = self.cli("task", "add", "--id", "extra", "--department", "developers", "--title", "Extra task", "--acceptance", "Observed result", "--harness-file", str(selection))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.mutate("task.start", "prototype")
        self.submit()
        result = self.cli("loop", "next", "--format", "json")
        value = json.loads(result.stdout)
        self.assertEqual(value["action"], "evaluate")
        gates_file = self.root / "gates.json"
        gates_file.write_text(json.dumps(self.gates()), encoding="utf-8")
        result = self.cli("task", "review", "prototype", "--decision", "accept", "--reviewer", "cto", "--note", "Observed fixture", "--gates-file", str(gates_file), "--expected-revision", str(value["sourceRevision"]), "--submission-revision", str(value["reviewTemplate"]["submitRevision"]))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.cli("harness", "show", "--format", "json").stdout)["version"], 1)
        self.assertIn(b"Focused project projection", self.cli("loop", "prompt").stdout)
        self.assertIn(b"Saved project snapshot", self.cli("context").stdout)

    def test_malformed_nested_harness_cli_never_exposes_traceback_or_private_text(self):
        self.ready_review()
        base = self.state()
        for field, value in (("defaults", []), ("profiles", None), ("policies", []), ("rounds", [None]), ("assessments", ["PRIVATE_MARKER"])):
            state = copy.deepcopy(base); state["harness"][field] = value
            self.workspace.path.write_text(json.dumps(state), encoding="utf-8")
            result = self.cli("status", "--format", "json")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, b"")
            self.assertNotIn(b"Traceback", result.stderr)
            self.assertNotIn(b"PRIVATE_MARKER", result.stderr)


class GoldenTests(unittest.TestCase):
    def test_shared_unicode_golden_hashes_and_fixture_states(self):
        fixture = json.loads((ROOT / "tests/harness-fixtures.json").read_text(encoding="utf-8"))
        for golden in fixture["hashes"]:
            payload = sorted(golden["payload"], key=lambda item: item["path"]) if golden["domain"] == "artifacts" else golden["payload"]
            self.assertEqual(harness.canonical(payload), golden["canonical"])
            self.assertEqual(harness.fingerprint(golden["domain"], payload), golden["sha256"])
        self.assertEqual(fixture["hashes"][1]["sha256"], fixture["hashes"][2]["sha256"])
        for case in fixture["states"]:
            project.validate_state(case["state"], project.roster())
            self.assertEqual(harness.next_action(case["state"]), case["next"])

    def test_canonical_json_rejects_floats_nonfinite_unsafe_integers_and_surrogates(self):
        for value in (1.0, float("nan"), float("inf"), 2 ** 53, "\ud800", {"é": "non-ascii key"}):
            with self.assertRaises(harness.HarnessError):
                harness.canonical(value)
        self.assertEqual(harness.canonical({"b": 1, "a": "café 🧭"}), harness.canonical({"a": "café 🧭", "b": 1}))


if __name__ == "__main__":
    unittest.main()
