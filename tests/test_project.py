"""Persistent company lifecycle, storage safety, CLI and native host acceptance."""

import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "skills/chief-of-staff/scripts/project.py"
spec = importlib.util.spec_from_file_location("company_project", HELPER)
project = importlib.util.module_from_spec(spec)
previous = sys.dont_write_bytecode
try:
    sys.dont_write_bytecode = True
    spec.loader.exec_module(project)
finally:
    sys.dont_write_bytecode = previous


def run_cli(cwd, *args, executable=None, env=None):
    command = executable or [sys.executable, str(HELPER)]
    if os.name == "nt" and executable and Path(command[0]).name == "bash.exe":
        env = dict(os.environ if env is None else env)
        git_root = Path(command[0]).parent.parent
        env["PATH"] = str(git_root / "usr/bin") + os.pathsep + str(git_root / "bin") + os.pathsep + env.get("PATH", "")
    return subprocess.run([*command, *args], cwd=cwd, env=env, capture_output=True, timeout=30)


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        # macOS /var is a system symlink; choose the physical project root.
        self.directory = Path(self.temp.name).resolve()
        self.workspace = project.Workspace(self.directory)
        self.workspace.initialize("Founder project", "Build an arbitrary company project", "marketing", ["Useful result"], ["Local only"])

    def state(self):
        return self.workspace.load()[0]

    def add(self, task_id="offer", department="marketing", deps=None):
        return self.workspace.mutate("task.add", task_id, department=department, title="Deliver " + task_id,
                                     acceptance="Named artifact reviewed against the founder's requirements", depends_on=deps or [])

    def submit(self, task_id="offer", content="Observed evidence", path=None):
        path = path or task_id + ".md"
        (self.directory / path).write_text(content, encoding="utf-8")
        return self.workspace.mutate("task.submit", task_id, artifacts=[path], summary="Checks actually run")

    def accept(self, task_id="offer", reviewer="ceo"):
        return self.workspace.mutate("task.accept", task_id, reviewer=reviewer, note="Inspected files and observed checks")

    def unchanged_failure(self, callback):
        before = self.workspace.path.read_bytes()
        with self.assertRaises(project.ProjectError):
            callback()
        self.assertEqual(self.workspace.path.read_bytes(), before)
        self.assertFalse(self.workspace.lock.exists())
        self.assertEqual(list(self.workspace.directory.glob("*.tmp")), [])

    def test_complete_workflow_spans_three_departments_and_bench(self):
        self.add("offer", "marketing")
        self.add("cost", "finance", ["offer"])
        self.add("prototype", "developers", ["cost"])
        for task_id, reviewer in (("offer", "sales"), ("cost", "ceo"), ("prototype", "designers")):
            self.workspace.mutate("task.start", task_id)
            self.submit(task_id)
            self.accept(task_id, reviewer)
        self.workspace.mutate("decision.add", text="Founder retained pricing approval")
        state = self.state()
        self.assertEqual([t["status"] for t in state["tasks"]], ["done"] * 3)
        self.assertEqual(state["activeDepartments"], ["marketing"])
        self.assertEqual(len(state["departments"]), 8)
        self.assertEqual(state["revision"], len(state["events"]))
        self.assertEqual(state["decisions"][0]["text"], "Founder retained pricing approval")

    def test_init_all_departments_no_recipe_tasks_and_no_profile_access(self):
        other = self.directory / "other"
        other.mkdir()
        (other / ".claude").mkdir()
        profile = other / ".claude/company-team.md"
        profile.write_text("SECRET PROFILE BODY\nmalformed", encoding="utf-8")
        workspace = project.Workspace(other)
        workspace.initialize("New", "Founder scope")
        state, _ = workspace.load()
        self.assertEqual(state["activeDepartments"], list(workspace.departments))
        self.assertEqual(state["tasks"], [])
        self.assertNotIn("SECRET PROFILE", project.render_prompt(workspace, state))
        self.assertEqual(profile.read_text(encoding="utf-8"), "SECRET PROFILE BODY\nmalformed")

    def test_duplicate_id_and_missing_dependency_rejected(self):
        self.add()
        self.unchanged_failure(lambda: self.add())
        self.unchanged_failure(lambda: self.add("other", deps=["missing"]))
        self.unchanged_failure(lambda: self.add("cycle", deps=["cycle"]))
        self.unchanged_failure(lambda: self.add("aliases", "dev"))

    def test_dependency_blocking_duplicate_claim_and_done_is_terminal(self):
        self.add()
        self.add("cost", "finance", ["offer"])
        self.unchanged_failure(lambda: self.workspace.mutate("task.start", "cost"))
        self.workspace.mutate("task.start", "offer")
        self.unchanged_failure(lambda: self.workspace.mutate("task.start", "offer"))
        self.submit()
        self.unchanged_failure(lambda: self.workspace.mutate("task.start", "cost"))
        self.accept()
        self.workspace.mutate("task.start", "cost")
        self.unchanged_failure(lambda: self.workspace.mutate("task.start", "offer"))
        self.unchanged_failure(lambda: self.workspace.mutate("task.revise", "offer", reviewer="ceo", note="reopen"))

    def test_block_resume_and_revision_request(self):
        self.add()
        self.unchanged_failure(lambda: self.workspace.mutate("task.block", "offer", reason="waiting"))
        self.workspace.mutate("task.start", "offer")
        self.workspace.mutate("task.block", "offer", reason="Founder input missing")
        self.assertEqual(self.state()["tasks"][0]["blockedReason"], "Founder input missing")
        self.workspace.mutate("task.start", "offer")
        self.assertIsNone(self.state()["tasks"][0]["blockedReason"])
        self.submit()
        self.workspace.mutate("task.revise", "offer", reviewer="sales", note="Correct the evidence")
        self.assertEqual(self.state()["tasks"][0]["status"], "active")
        self.submit(content="Corrected actual evidence")
        self.accept()
        self.assertEqual([r["decision"] for r in self.state()["tasks"][0]["reviews"]], ["revise", "accept"])
        self.assertIn("Founder input missing", [e["note"] for e in self.state()["events"]])

    def test_reviewer_separation_and_lifecycle(self):
        self.add()
        self.unchanged_failure(lambda: self.accept())
        self.unchanged_failure(lambda: self.submit())
        self.workspace.mutate("task.start", "offer")
        self.submit()
        self.unchanged_failure(lambda: self.accept(reviewer="marketing"))
        self.unchanged_failure(lambda: self.accept(reviewer="unknown"))
        self.accept(reviewer="legal")

    def test_stale_or_missing_artifact_cannot_be_accepted(self):
        self.add()
        self.workspace.mutate("task.start", "offer")
        self.submit()
        (self.directory / "offer.md").write_text("Changed after submission", encoding="utf-8")
        self.unchanged_failure(lambda: self.accept())
        (self.directory / "offer.md").unlink()
        self.unchanged_failure(lambda: self.accept())
        self.assertEqual(self.state()["tasks"][0]["status"], "review")

    def test_artifact_paths_presence_duplicates_sizes_and_regular_files(self):
        self.add()
        self.workspace.mutate("task.start", "offer")
        (self.directory / "folder").mkdir()
        (self.directory / "ok.md").write_text("valid", encoding="utf-8")
        cases = [[], ["missing.md"], ["folder"], ["../outside.md"], [str(self.directory / "ok.md")],
                 ["C:outside.md"], ["file:stream"], ["folder/../ok.md"], ["folder\\ok.md"],
                 ["ok.md", "ok.md"], [".claude/company/project.json"], [".CLAUDE/Company/project.json"], ["NUL"]]
        for paths in cases:
            with self.subTest(paths=paths):
                self.unchanged_failure(lambda: self.workspace.mutate("task.submit", "offer", artifacts=paths, summary="evidence"))
        with mock.patch.object(project, "ARTIFACT_MAX_BYTES", 2):
            self.unchanged_failure(lambda: self.workspace.mutate("task.submit", "offer", artifacts=["ok.md"], summary="evidence"))

    def symlink(self, target, path, directory=False):
        try:
            path.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation is unavailable to this host")

    def test_symlink_artifact_and_ancestor_rejected(self):
        self.add()
        self.workspace.mutate("task.start", "offer")
        real = self.directory / "real.md"
        real.write_text("real", encoding="utf-8")
        self.symlink(real, self.directory / "linked.md")
        self.unchanged_failure(lambda: self.workspace.mutate("task.submit", "offer", artifacts=["linked.md"], summary="evidence"))
        real_dir = self.directory / "real"
        real_dir.mkdir()
        (real_dir / "file.md").write_text("real", encoding="utf-8")
        self.symlink(real_dir, self.directory / "linked", True)
        self.unchanged_failure(lambda: self.workspace.mutate("task.submit", "offer", artifacts=["linked/file.md"], summary="evidence"))

    def test_symlink_state_ancestor_never_reads_or_writes_foreign_files(self):
        other = self.directory / "new"
        other.mkdir()
        self.symlink(self.directory / ".claude", other / ".claude", True)
        before = self.workspace.path.read_bytes()
        workspace = project.Workspace(other)
        with self.assertRaises(project.ProjectError):
            workspace.initialize("unsafe", "scope")
        with self.assertRaises(project.ProjectError):
            workspace.load()
        self.assertEqual(self.workspace.path.read_bytes(), before)

    def test_windows_reparse_detection_without_link_privileges(self):
        fake = mock.Mock(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
        self.assertTrue(project.is_link(fake))

    def test_init_refuses_overwrite(self):
        self.unchanged_failure(lambda: self.workspace.initialize("replacement", "private replacement"))

    def test_lock_conflict_preserves_exact_state_and_foreign_lock(self):
        before = self.workspace.path.read_bytes()
        self.workspace.lock.write_bytes(b"another writer")
        with self.assertRaisesRegex(project.ProjectError, "locked"):
            self.add()
        self.assertEqual(self.workspace.path.read_bytes(), before)
        self.assertEqual(self.workspace.lock.read_bytes(), b"another writer")
        # Snapshot reads do not claim or remove even a preexisting lock.
        self.assertEqual(self.state()["revision"], 1)

    def test_atomic_replace_failure_cleans_temp_and_lock(self):
        before = self.workspace.path.read_bytes()
        with mock.patch.object(project.os, "replace", side_effect=OSError("no space")):
            with self.assertRaises(OSError):
                self.add()
        self.assertEqual(self.workspace.path.read_bytes(), before)
        self.assertFalse(self.workspace.lock.exists())
        self.assertEqual(list(self.workspace.directory.glob("*.tmp")), [])

    def test_revision_conflict_preserves_newer_writer(self):
        state, before = self.workspace.load()
        self.workspace.mutate("decision.add", text="A different writer committed")
        current = self.workspace.path.read_bytes()
        with self.workspace.locked():
            with self.assertRaisesRegex(project.ProjectError, "revision changed"):
                self.workspace.commit(state, before)
        self.assertEqual(self.workspace.path.read_bytes(), current)

    def test_private_state_and_no_partial_files(self):
        if os.name != "nt":
            self.assertEqual(stat.S_IMODE(self.workspace.path.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(self.workspace.directory.stat().st_mode), 0o700)
        self.assertEqual([p.name for p in self.workspace.directory.iterdir()], ["project.json"])

    def test_malformed_oversized_unknown_schema_status_and_dependencies_fail(self):
        base = self.state()
        self.add()
        task_state = self.state()
        cases = [b"{", b"[]", b'{"schemaVersion":1,"schemaVersion":1}', b"x" * (project.STATE_MAX_BYTES + 1)]
        for field, value in (("schemaVersion", 2), ("schemaVersion", True), ("revision", -1), ("name", " "),
                             ("brief", "x" * 8001), ("goals", ["x"] * 33), ("events", []), ("departments", [])):
            corrupt = copy.deepcopy(base)
            corrupt[field] = value
            cases.append(json.dumps(corrupt).encode())
        for field, value in (("status", "mystery"), ("dependsOn", ["missing"]), ("department", "dev"), ("status", "done"),
                             ("artifacts", [{"path": "../escape", "size": 1, "sha256": "a" * 64}])):
            corrupt = copy.deepcopy(task_state)
            corrupt["tasks"][0][field] = value
            cases.append(json.dumps(corrupt).encode())
        for payload in cases:
            with self.subTest(payload=payload[:50]):
                self.workspace.path.write_bytes(payload)
                with self.assertRaises(project.ProjectError):
                    self.workspace.load()
                self.assertEqual(self.workspace.path.read_bytes(), payload)

    def test_state_and_event_history_cannot_diverge(self):
        self.add()
        state = self.state()
        state["tasks"][0]["status"] = "active"
        with self.assertRaisesRegex(project.ProjectError, "history"):
            project.validate_state(state, self.workspace.departments)
        state = self.state()
        state["events"][1]["type"] = "task.accept"
        with self.assertRaises(project.ProjectError):
            project.validate_state(state, self.workspace.departments)

    def test_malformed_nested_types_have_safe_cli_errors(self):
        self.add()
        self.workspace.mutate("task.start", "offer")
        self.submit()
        self.accept()
        base = self.state()
        cases = [("task", "department", []), ("task", "status", {}), ("task", "dependsOn", [None]),
                 ("review", "decision", []), ("review", "reviewer", {}), ("artifact", "path", []),
                 ("artifact", "sha256", {}), ("event", "type", []), ("event", "taskId", {})]
        for location, field, value in cases:
            with self.subTest(location=location, field=field):
                state = copy.deepcopy(base)
                targets = {"task": state["tasks"][0], "review": state["tasks"][0]["reviews"][0],
                           "artifact": state["tasks"][0]["artifacts"][0], "event": state["events"][-1]}
                targets[location][field] = value
                self.workspace.path.write_text(json.dumps(state), encoding="utf-8")
                with self.assertRaises(project.ProjectError):
                    self.workspace.load()
                result = run_cli(self.directory, "status", "--format", "json")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, b"")
                self.assertNotIn(b"Traceback", result.stderr)

    def test_symlink_state_file_and_corrupt_context_fail_closed(self):
        other = self.directory / "state-copy.json"
        other.write_bytes(self.workspace.path.read_bytes())
        original = other.read_bytes()
        self.workspace.path.unlink()
        self.symlink(other, self.workspace.path)
        result = run_cli(self.directory, "context")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"")
        with self.assertRaises(project.ProjectError):
            self.workspace.mutate("decision.add", text="must not write")
        self.assertEqual(other.read_bytes(), original)

    def test_two_processes_lock_conflict_fails_fast(self):
        before = self.workspace.path.read_bytes()
        with self.workspace.locked():
            result = run_cli(self.directory, "decision", "add", "--text", "competing process")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"locked", result.stderr)
            self.assertTrue(self.workspace.lock.exists())
        self.assertEqual(before, self.workspace.path.read_bytes())

    def test_file_replacement_during_open_is_rejected(self):
        path = self.directory / "observed.md"
        path.write_bytes(b"observed")
        original_open = project.os.open
        def raced_open(filename, flags, *args, **kwargs):
            if Path(filename) == path:
                replacement = self.directory / "replacement.md"
                replacement.write_bytes(b"replaced")
                os.replace(replacement, path)
            return original_open(filename, flags, *args, **kwargs)
        with mock.patch.object(project.os, "open", side_effect=raced_open):
            with self.assertRaisesRegex(project.ProjectError, "changed"):
                project.read_regular(path, 100)

    def test_input_limits_and_slug(self):
        for bad in ("bad id", "--flag", "a" * 81):
            self.unchanged_failure(lambda: self.add(bad))
        self.unchanged_failure(lambda: self.workspace.mutate("decision.add", text="secret\x00value"))
        self.unchanged_failure(lambda: self.workspace.mutate("decision.add", text="x" * 8001))
        with mock.patch.object(project, "MAX_TASKS", 0):
            self.unchanged_failure(lambda: self.add())
        with mock.patch.object(project, "MAX_EVENTS", 1):
            self.unchanged_failure(lambda: self.add())

    def test_prompt_has_actual_state_absolute_sources_and_execution_contract(self):
        self.add()
        self.workspace.mutate("decision.add", text="Keep all eight departments available")
        prompt = project.render_prompt(self.workspace, self.state())
        self.assertIn(json.dumps(str(ROOT / "agents/developers.md")), prompt)
        self.assertIn('"id": "offer"', prompt)
        self.assertIn("Keep all eight departments available", prompt)
        self.assertIn("Create explicit tasks BEFORE delegating", prompt)
        self.assertIn("CEO alone serializes", prompt)
        self.assertIn("NOT authenticated", prompt)
        self.assertNotIn("----- EMPLOYEE MANUAL", prompt)

    def test_mocked_native_host_plugin_cwd_argument_boundaries_and_no_override(self):
        self.workspace.mutate("decision.add", text='--permission-mode bypassPermissions; $(touch escaped) café')
        with mock.patch.object(project, "claude_command", return_value=["claude-test"]), mock.patch.object(project.subprocess, "call", return_value=7) as launch:
            result = project.start(self.workspace, self.state())
        self.assertEqual(result, 7)
        args, kwargs = launch.call_args
        self.assertEqual(args[0][:3], ["claude-test", "--plugin-dir", str(ROOT)])
        self.assertEqual(len(args[0]), 4)
        self.assertLess(len(args[0][-1].encode("utf-16-le")), 16000)
        self.assertIn('"prompt"', args[0][-1])
        self.assertNotIn("--permission-mode", args[0][-1])
        self.assertEqual(kwargs, {"cwd": str(self.directory), "shell": False})

    def test_missing_engine_is_actionable_and_does_not_emit_private_context(self):
        with mock.patch.object(project.shutil, "which", return_value=None):
            with self.assertRaisesRegex(project.ProjectError, "company project prompt"):
                project.claude_command()

    def test_native_windows_shell_shim_is_never_evaluated(self):
        with mock.patch.object(project.os, "name", "nt"), mock.patch.object(project.shutil, "which", return_value="C:/missing/claude.cmd"):
            # Path selects the host path class; patch it to remain portable on POSIX.
            with mock.patch.object(project, "Path", type(self.directory)):
                with self.assertRaisesRegex(project.ProjectError, "native Claude Code"):
                    project.claude_command()

    def test_native_windows_npm_shim_launches_node_with_exact_safe_arguments(self):
        install = self.directory / "npm & $(literal) café"
        script = install / "node_modules/@anthropic-ai/claude-code/cli.js"
        script.parent.mkdir(parents=True)
        script.write_text("// Test fixture; never executed", encoding="utf-8")
        shim = install / "claude.cmd"
        shim.write_text("@echo This batch file must never run", encoding="utf-8")
        node = install / "node runtime/node.exe"
        state = self.state()
        original_environment = dict(os.environ)
        locations = {"claude": str(shim), "node.exe": str(node)}
        with mock.patch.object(project.os, "name", "nt"), mock.patch.object(project, "Path", type(self.directory)), \
                mock.patch.object(project.shutil, "which", side_effect=locations.get) as lookup, \
                mock.patch.object(project.subprocess, "call", return_value=0) as launch:
            self.assertEqual(project.start(self.workspace, state), 0)
        self.assertEqual(lookup.call_args_list, [mock.call("claude"), mock.call("node.exe")])
        arguments, options = launch.call_args
        argv = arguments[0]
        self.assertEqual(argv[:-1], [str(node), str(script), "--plugin-dir", str(ROOT)])
        self.assertEqual(len(argv), 5)
        self.assertNotIn(str(shim), argv)
        self.assertEqual(options, {"cwd": str(self.directory), "shell": False})
        bootstrap = json.loads(argv[-1].split("\n", 1)[1])
        self.assertEqual(bootstrap, {"cwd": str(self.directory),
                                    "argv": [sys.executable, str(HELPER), "prompt"],
                                    "validatedRevisionAtLaunch": state["revision"]})
        self.assertNotIn("--model", argv[-1])
        self.assertNotIn("--permission-mode", argv[-1])
        self.assertNotIn("--dangerously-skip-permissions", argv[-1])
        self.assertEqual(dict(os.environ), original_environment)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name).resolve()

    def run_ok(self, *args, executable=None):
        result = run_cli(self.directory, *args, executable=executable)
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))
        return result.stdout.decode("utf-8")

    def test_full_cli_workflow_unicode_flags_shell_text_and_cross_cwd(self):
        brief = '--print café 東京 🧭 — "quotes" $() `literal` & | ;\nsecond line'
        self.run_ok("init", "--name", "--print", "--brief", brief, "--goal", "-p", "--constraint", "--flag")
        self.run_ok("task", "add", "--id", "offer", "--department", "marketing", "--title", "--print", "--acceptance", "--flag")
        self.run_ok("task", "start", "offer")
        (self.directory / "résultat.md").write_text("file evidence", encoding="utf-8")
        self.run_ok("task", "submit", "offer", "--artifact", "résultat.md", "--summary", "$() ; & literal")
        self.run_ok("task", "review", "offer", "--decision", "revise", "--reviewer", "sales", "--note", "--print")
        self.run_ok("task", "submit", "offer", "--artifact", "résultat.md", "--summary", "revised")
        self.run_ok("task", "review", "offer", "--decision", "accept", "--reviewer", "ceo", "--note", "inspected")
        self.run_ok("decision", "add", "--text", "--decision")
        state = json.loads(self.run_ok("status", "--format", "json"))
        self.assertEqual(state["brief"], brief)
        self.assertEqual(state["name"], "--print")
        self.assertEqual(state["goals"], ["-p"])
        self.assertEqual(state["constraints"], ["--flag"])
        self.assertEqual(state["tasks"][0]["status"], "done")
        self.assertEqual(state["decisions"][0]["text"], "--decision")

    def test_brief_file_and_strict_readonly_context(self):
        self.assertEqual(self.run_ok("context"), "")
        self.assertEqual(list(self.directory.iterdir()), [])
        (self.directory / ".claude").mkdir()
        self.assertEqual(self.run_ok("context"), "")
        (self.directory / ".claude/company").mkdir()
        self.assertNotEqual(run_cli(self.directory, "context").returncode, 0)
        (self.directory / "brief.md").write_text("Arbitrary founder café", encoding="utf-8")
        self.run_ok("init", "--name", "File brief", "--brief-file", "brief.md")
        before = {str(p.relative_to(self.directory)): p.read_bytes() for p in self.directory.rglob("*") if p.is_file()}
        source_before = {str(p): p.stat().st_mtime_ns for p in HELPER.parent.rglob("*")}
        self.assertIn("Arbitrary founder café", self.run_ok("context"))
        self.run_ok("status")
        self.run_ok("prompt")
        after = {str(p.relative_to(self.directory)): p.read_bytes() for p in self.directory.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(source_before, {str(p): p.stat().st_mtime_ns for p in HELPER.parent.rglob("*")})
        (self.directory / ".claude/company/project.json").write_bytes(b"corrupt SECRET")
        result = run_cli(self.directory, "context")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"")
        self.assertNotIn(b"SECRET", result.stderr)
        self.assertNotIn(b"Traceback", result.stderr)

    def test_prompt_strict_absent_and_invalid_cli_does_not_echo_input(self):
        self.assertNotEqual(run_cli(self.directory, "prompt").returncode, 0)
        result = run_cli(self.directory, "init", "--secret-private-data")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(b"secret-private-data", result.stderr)

    def test_canonical_bridge_preserves_profile_validation_and_uses_project_context(self):
        command = (ROOT / "commands/company.md").read_text(encoding="utf-8")
        self.assertIn('"${CLAUDE_PLUGIN_ROOT}/bin/company" profile-context', command)
        self.assertIn('"${CLAUDE_PLUGIN_ROOT}/bin/company" project context', command)
        self.assertIn("Do not switch helpers after a failure", command)
        self.assertIn("profile body", command)
        self.assertIn("CEO serializes all state mutations", command)

    def test_cli_lock_conflict_no_mutation_and_no_traceback(self):
        self.run_ok("init", "--name", "Project", "--brief", "Private scope")
        state = self.directory / ".claude/company/project.json"
        before = state.read_bytes()
        (state.parent / ".project.lock").write_text("live writer", encoding="utf-8")
        result = run_cli(self.directory, "decision", "add", "--text", "SECRET")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(before, state.read_bytes())
        self.assertNotIn(b"SECRET", result.stderr)
        self.assertNotIn(b"Traceback", result.stderr)

    def bash(self):
        candidate = shutil.which("bash")
        if not candidate and os.name == "nt":
            installed = Path("C:/Program Files/Git/bin/bash.exe")
            if installed.exists():
                candidate = str(installed)
        if not candidate:
            self.skipTest("Bash unavailable; Python CLI remains fully covered")
        return [candidate, str(ROOT / "bin/company")]

    def test_bash_forwards_exact_project_arguments_and_legacy_brief_root(self):
        command = self.bash()
        self.run_ok("project", "init", "--name", "Shell project", "--brief", "--print", "--goal", "-p", executable=command)
        state = json.loads(self.run_ok("project", "status", "--format", "json", executable=command))
        self.assertEqual(state["brief"], "--print")
        self.assertEqual(state["goals"], ["-p"])
        output = self.run_ok("brief", "Founder scope", "--print", executable=command)
        self.assertIn("literal absolute path", output)
        self.assertIn("claude-inc", output)
        self.assertIn("never the founder's current working directory", output)


if __name__ == "__main__":
    unittest.main()
