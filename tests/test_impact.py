"""Evidence freshness: superseded inputs, project-file drift, early cutoff and read-only reporting."""

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
spec = importlib.util.spec_from_file_location("company_project_impact_tests", HELPER)
project = importlib.util.module_from_spec(spec)
previous = sys.dont_write_bytecode
try:
    sys.dont_write_bytecode = True
    spec.loader.exec_module(project)
finally:
    sys.dont_write_bytecode = previous


class ImpactTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        # macOS /var is a system symlink; choose the physical project root.
        self.directory = Path(self.temp.name).resolve()
        self.workspace = project.Workspace(self.directory)
        self.workspace.initialize("Founder project", "Change one decision and see what it touches")

    def state(self):
        return self.workspace.load()[0]

    def add(self, task_id, department="marketing", deps=None):
        self.workspace.mutate("task.add", task_id, department=department, title="Deliver " + task_id,
                              acceptance="Named artifact reviewed against its inputs", depends_on=deps or [])

    def submit(self, task_id, content, path=None):
        path = path or task_id + ".md"
        (self.directory / path).write_text(content, encoding="utf-8", newline="\n")
        self.workspace.mutate("task.submit", task_id, artifacts=[path], summary="Checks actually run")

    def accept(self, task_id):
        self.workspace.mutate("task.accept", task_id, reviewer="ceo", note="Inspected files and observed checks")

    def deliver(self, task_id, department="marketing", deps=None, content=None, path=None):
        self.add(task_id, department, deps)
        self.workspace.mutate("task.start", task_id)
        self.submit(task_id, content or "Deliverable " + task_id, path)
        self.accept(task_id)

    def report(self, *what_if):
        return project.freshness(self.workspace, self.state(), what_if)

    def evidence(self, *what_if):
        return {task["id"]: task["evidence"] for task in self.report(*what_if)["tasks"]}

    def company(self):
        """price -> offer -> page, price -> terms, and an unrelated brand task."""
        self.deliver("price", "finance", content="Price: 19")
        self.deliver("offer", "marketing", ["price"])
        self.deliver("page", "designers", ["offer"])
        self.deliver("terms", "legal", ["price"])
        self.deliver("brand", "designers")

    def cli(self, *args):
        return subprocess.run([sys.executable, str(HELPER), *args], cwd=self.directory, capture_output=True, timeout=30)

    def test_accepted_work_is_fresh_and_the_report_writes_nothing(self):
        self.company()
        before = {str(path.relative_to(self.directory)): path.read_bytes() for path in self.directory.rglob("*") if path.is_file()}
        sources = {str(path): path.stat().st_mtime_ns for path in HELPER.parent.rglob("*")}
        report = self.report()
        self.assertEqual(set(self.evidence().values()), {"fresh"})
        self.assertFalse(report["attention"])
        self.assertEqual((report["waves"], report["paths"]), ([], []))
        self.assertEqual(report["summary"], {"accepted": {"fresh": 5}, "open": {}, "paths": {"tracked": 5, "current": 5}})
        for args in (("impact",), ("impact", "--format", "json"), ("impact", "--check"), ("impact", "--what-if", "price")):
            result = self.cli(*args)
            self.assertEqual((result.returncode, result.stderr), (0, b""), result)
        self.assertEqual(before, {str(path.relative_to(self.directory)): path.read_bytes() for path in self.directory.rglob("*") if path.is_file()})
        self.assertEqual(sources, {str(path): path.stat().st_mtime_ns for path in HELPER.parent.rglob("*")})
        self.assertFalse(self.workspace.lock.exists())

    def test_changed_or_missing_accepted_file_is_reported_with_its_consumers(self):
        self.company()
        (self.directory / "price.md").write_text("Price: 29", encoding="utf-8")
        self.assertEqual(self.evidence(), {"price": "drifted", "offer": "at-risk", "terms": "at-risk", "page": "conditional", "brand": "fresh"})
        report = self.report()
        self.assertTrue(report["attention"])
        self.assertEqual(report["waves"], [["price"], ["offer", "terms"], ["page"]])
        self.assertEqual(report["paths"], [{"path": "price.md", "owner": "price", "acceptedRevision": 5, "versions": 1, "disk": "changed"}])
        self.assertEqual(next(task for task in report["tasks"] if task["id"] == "offer")["reasons"],
                         [{"role": "input", "path": "price.md", "change": "changed", "from": "price"}])
        check = self.cli("impact", "--check")
        self.assertEqual(check.returncode, 2)
        self.assertIn(b"price.md (accepted from price at revision 5): changed", check.stdout)
        (self.directory / "price.md").unlink()
        self.assertEqual(self.report()["paths"][0]["disk"], "missing")
        self.assertEqual(self.evidence()["offer"], "at-risk")

    def test_a_superseding_task_makes_consumers_stale_until_they_are_recertified(self):
        self.company()
        self.deliver("price-2", "finance", content="Price: 29", path="price.md")
        self.assertEqual(self.evidence(), {"price": "superseded", "offer": "stale", "terms": "stale", "page": "conditional",
                                           "brand": "fresh", "price-2": "fresh"})
        report = self.report()
        self.assertEqual(report["waves"], [["offer", "terms"], ["page"]])
        self.assertEqual(next(task for task in report["tasks"] if task["id"] == "offer")["reasons"],
                         [{"role": "input", "path": "price.md", "change": "superseded", "from": "price", "by": "price-2"}])
        self.assertEqual(report["paths"][0]["versions"], 2)
        self.deliver("offer-2", "marketing", ["price-2"], content="Offer at the new price", path="offer.md")
        self.assertEqual(self.evidence()["page"], "stale")
        self.deliver("terms-2", "legal", ["price-2"], content="Terms at the new price", path="terms.md")
        self.deliver("page-2", "designers", ["offer-2"], content="Page at the new price", path="page.md")
        final = self.evidence()
        self.assertEqual({task for task, value in final.items() if value == "superseded"}, {"price", "offer", "terms", "page"})
        self.assertEqual({value for value in final.values()}, {"fresh", "superseded"})
        self.assertFalse(self.report()["attention"])

    def test_identical_bytes_keep_downstream_work_fresh(self):
        self.company()
        self.deliver("price-2", "finance", content="Price: 29", path="price.md")
        # The offer does not quote the price: its reviewer confirms the unchanged file.
        self.deliver("offer-2", "marketing", ["price-2"], content="Deliverable offer", path="offer.md")
        evidence = self.evidence()
        self.assertEqual((evidence["offer"], evidence["offer-2"], evidence["page"], evidence["terms"]), ("superseded", "fresh", "fresh", "stale"))
        self.assertEqual(self.report()["waves"], [["terms"]])

    def test_consumed_version_is_the_one_current_when_the_task_last_became_active(self):
        self.deliver("price", "finance", content="Price: 19")
        self.add("offer", "marketing", ["price"])
        self.add("deck", "sales", ["price"])
        self.add("faq", "marketing", ["price"])
        self.workspace.mutate("task.start", "deck")
        self.workspace.mutate("task.start", "faq")
        self.submit("faq", "Answers at the old price")
        self.deliver("price-2", "finance", content="Price: 29", path="price.md")
        # A planned task consumes the current version; in-flight work started on the old one.
        self.assertEqual(self.evidence(), {"price": "superseded", "offer": "fresh", "deck": "stale", "faq": "stale", "price-2": "fresh"})
        self.assertEqual(self.report()["summary"]["open"], {"stale": 2, "fresh": 1})
        self.workspace.mutate("task.revise", "faq", reviewer="ceo", note="Rework against the new price")
        self.submit("faq", "Answers at the new price")
        self.accept("faq")
        self.workspace.mutate("task.start", "offer")
        self.submit("offer", "Offer at the new price")
        self.accept("offer")
        self.submit("deck", "Deck still quoting the old price")
        self.accept("deck")
        self.assertEqual(self.evidence(), {"price": "superseded", "offer": "fresh", "deck": "stale", "faq": "fresh", "price-2": "fresh"})

    def test_a_task_that_resubmits_its_dependency_path_is_not_stale_from_its_own_version(self):
        self.deliver("draft", "developers", content="First version", path="app.md")
        self.deliver("reader", "marketing", ["draft"])
        self.deliver("polish", "developers", ["draft"], content="Second version", path="app.md")
        self.assertEqual(self.evidence(), {"draft": "superseded", "reader": "stale", "polish": "fresh"})

    def test_superseding_work_that_depends_on_its_own_consumer_terminates(self):
        self.deliver("price", "finance", content="Price: 19")
        self.deliver("economics", "finance", ["price"])
        self.deliver("page", "designers", ["economics"])
        self.deliver("price-2", "finance", ["economics"], content="Price: 29", path="price.md")
        self.assertEqual(self.evidence(), {"price": "superseded", "economics": "stale", "page": "conditional", "price-2": "conditional"})
        self.assertEqual(self.report()["waves"], [["economics"], ["page", "price-2"]])

    def test_unreviewed_submission_is_pending_not_an_unexplained_change(self):
        self.company()
        self.add("price-2", "finance")
        self.workspace.mutate("task.start", "price-2")
        self.submit("price-2", "Price: 29", path="price.md")
        report = self.report()
        self.assertEqual(report["paths"][0]["disk"], "pending")
        self.assertEqual(next(task for task in report["tasks"] if task["id"] == "offer")["reasons"],
                         [{"role": "input", "path": "price.md", "change": "pending", "from": "price", "by": "price-2"}])
        self.assertIn("has an unreviewed submission in price-2", project.impact_call("render", report))

    def test_what_if_is_hypothetical_validated_and_never_changes_the_project(self):
        self.company()
        before = self.workspace.path.read_bytes()
        self.assertEqual(self.evidence("price"), {"price": "what-if", "offer": "at-risk", "terms": "at-risk", "page": "conditional", "brand": "fresh"})
        report = self.report("price", "price")
        self.assertEqual((report["whatIf"], report["waves"]), (["price"], [["offer", "terms"], ["page"]]))
        self.assertEqual(report["summary"]["paths"], {"tracked": 5, "current": 4, "what-if": 1})
        self.assertIn("What if price changed?", project.impact_call("render", report))
        self.deliver("price-2", "finance", content="Price: 29", path="price.md")
        before = self.workspace.path.read_bytes()
        for args in (("--what-if", "missing"), ("--what-if", "price"), ("--check", "--what-if", "price-2")):
            result = self.cli("impact", *args)
            self.assertEqual(result.returncode, 1)
            self.assertNotIn(b"Traceback", result.stderr)
        self.add("idea", "sales")
        with self.assertRaises(project.ProjectError):
            self.report("idea")
        self.assertEqual(json.loads(self.cli("impact", "--what-if=price-2", "--format", "json").stdout)["whatIf"], ["price-2"])
        self.assertNotEqual(self.workspace.path.read_bytes(), before)  # only the explicit task.add above changed the state

    def test_unsafe_or_oversized_reads_stay_visible_without_failing(self):
        self.company()
        with mock.patch.object(project, "IMPACT_MAX_BYTES", 12):
            report = self.report()
        self.assertEqual(report["summary"]["paths"]["unchecked"], 4)
        self.assertFalse(report["attention"])
        self.assertEqual({task["evidence"] for task in report["tasks"]}, {"fresh"})
        state = self.state()
        with mock.patch.object(project, "ARTIFACT_MAX_BYTES", 4):
            self.assertEqual({path["disk"] for path in project.freshness(self.workspace, state)["paths"]}, {"changed"})
        target = self.directory / "price.md"
        outside = self.directory / "elsewhere.md"
        outside.write_text("Price: 19", encoding="utf-8")
        target.unlink()
        try:
            os.symlink(outside, target)
        except (OSError, NotImplementedError):
            self.skipTest("symbolic links are unavailable")
        self.assertEqual(self.report()["paths"][0]["disk"], "unreadable")
        self.assertEqual(self.evidence()["offer"], "at-risk")

    def test_resume_prompt_carries_the_computed_freshness(self):
        self.company()
        clean = project.render_prompt(self.workspace, self.state())
        self.assertIn("## Evidence freshness", clean)
        self.assertIn('"attention": false', clean)
        self.assertIn("refresh it with `impact --format json`", clean)
        self.assertNotIn("compare its SHA-256", clean)
        self.deliver("price-2", "finance", content="Price: 29", path="price.md")
        prompt = project.render_prompt(self.workspace, self.state())
        view = json.loads(prompt.split("## Evidence freshness", 1)[1].split("\n\n", 2)[2].split("\n\n## ", 1)[0])
        self.assertEqual((view["attention"], view["recertifyFirst"], view["omitted"]), (True, ["offer", "terms"], 0))
        self.assertEqual([task["id"] for task in view["affected"]], ["offer", "page", "terms"])
        bounded = project.impact_call("brief", self.report(), 1)
        self.assertEqual((len(bounded["affected"]), bounded["omitted"]), (1, 2))

    def test_harness_projects_and_installed_cli_report_the_same_way(self):
        self.company()
        self.workspace.mutate("harness.generate", expected_revision=self.state()["revision"], stage="build", effort="light")
        (self.directory / "price.md").write_text("Price: 29", encoding="utf-8")
        report = json.loads(self.cli("impact", "--format", "json").stdout)
        self.assertEqual((report["version"], report["sourceRevision"], report["attention"]), (1, self.state()["revision"], True))
        self.assertEqual(report, json.loads(json.dumps(self.report())))
        self.assertIn("## Evidence freshness", self.cli("loop", "prompt").stdout.decode("utf-8"))
        text = self.cli("impact").stdout.decode("utf-8")
        self.assertIn("## Recertify first", text)
        self.assertIn("It cannot see undeclared reuse", text)
        if os.name != "nt":
            wrapped = subprocess.run(["bash", str(ROOT / "bin/company"), "project", "impact", "--check"], cwd=self.directory, capture_output=True, timeout=30)
            self.assertEqual((wrapped.returncode, wrapped.stderr), (2, b""))


if __name__ == "__main__":
    unittest.main()
