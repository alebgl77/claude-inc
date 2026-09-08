#!/usr/bin/env python3
"""Exercise a real isolated install and its platform wrapper; never run a model."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import shlex
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(argv, cwd, env):
    result = subprocess.run(argv, cwd=str(cwd), env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, encoding="utf-8", errors="replace",
                            timeout=120, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    if result.returncode:
        raise AssertionError("Command failed (" + str(result.returncode) + "): " + str(argv[0]) +
                             "\n" + result.stdout[-3000:] + "\n" + result.stderr[-3000:])
    return result.stdout


def recording_host(sandbox, env):
    """A real child executable records launch arguments; it cannot call a model."""
    directory = sandbox / "recording host"
    directory.mkdir()
    record = sandbox / "host-record.json"
    if os.name == "nt":
        compiler = Path(os.environ["WINDIR"]) / "Microsoft.NET/Framework64/v4.0.30319/csc.exe"
        if not compiler.is_file():
            compiler = Path(os.environ["WINDIR"]) / "Microsoft.NET/Framework/v4.0.30319/csc.exe"
        assert compiler.is_file(), "Windows .NET Framework compiler is required for the recording test host"
        executable = directory / "claude.exe"
        source = directory / "RecordingHost.cs"
        source.write_text('''using System;
using System.IO;
using System.Text;
using System.Web.Script.Serialization;
public class RecordingHost {
    public static int Main(string[] args) {
        var value = new { cwd = Environment.CurrentDirectory, argv = args };
        File.WriteAllText(Environment.GetEnvironmentVariable("CLAUDE_INC_SMOKE_RECORD"),
            new JavaScriptSerializer().Serialize(value), new UTF8Encoding(false));
        return 0;
    }
}
''', encoding="utf-8")
        run([str(compiler), "/nologo", "/r:System.Web.Extensions.dll", "/out:" + str(executable), str(source)], sandbox, env)
    else:
        executable = directory / "claude"
        recorder = directory / "record.py"
        recorder.write_text('''import json, os, pathlib, sys
pathlib.Path(os.environ["CLAUDE_INC_SMOKE_RECORD"]).write_text(json.dumps({"cwd": os.getcwd(), "argv": sys.argv[1:]}, ensure_ascii=False), encoding="utf-8")
''', encoding="utf-8")
        executable.write_text("#!/bin/sh\nexec " + shlex.quote(sys.executable) + " " + shlex.quote(str(recorder)) + ' "$@"\n', encoding="utf-8")
        executable.chmod(0o700)
    env["PATH"] = str(directory) + os.pathsep + env.get("PATH", "")
    env["CLAUDE_INC_SMOKE_RECORD"] = str(record)
    env["CLAUDE_INC_SMOKE_HOST"] = str(executable)
    # Fail before the actual helper runs if a login shell changes PATH and would
    # select a real host. This guard does not mock subprocess.call or resolution.
    guard = sandbox / "host safety guard"
    guard.mkdir()
    (guard / "sitecustomize.py").write_text('''import os, pathlib, shutil
selected = shutil.which("claude")
expected = os.environ["CLAUDE_INC_SMOKE_HOST"]
if not selected or pathlib.Path(selected).resolve() != pathlib.Path(expected).resolve():
    os.write(2, b"Recording host is not first on PATH; refusing any launch.\\n")
    os._exit(91)
''', encoding="utf-8")
    env["PYTHONPATH"] = str(guard)
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quote-probe", action="store_true", help="probe literal quotes and ampersand through PowerShell and company.exe")
    args = parser.parse_args(argv)
    with tempfile.TemporaryDirectory(prefix="claude-inc-installed-smoke-") as temporary:
        sandbox = Path(temporary).resolve()
        assert sandbox.parent == Path(tempfile.gettempdir()).resolve()
        home = sandbox / "isolated home"
        project = sandbox / "projet café 空白"
        home.mkdir()
        project.mkdir()
        env = os.environ.copy()
        env.update({"HOME": str(home), "USERPROFILE": str(home), "PYTHONDONTWRITEBYTECODE": "1",
                    "PYTHONIOENCODING": "utf-8", "CLAUDE_INC_ENGINE": "missing-smoke-engine"})
        for key in ("CLAUDE_INC_HOME", "CLAUDE_INC_REPO_URL", "CLAUDE_INC_GLOBAL_PROFILE", "CLAUDE_PLUGIN_ROOT"):
            env.pop(key, None)
        if os.name == "nt":
            shell = shutil.which("pwsh.exe") or shutil.which("powershell.exe")
            assert shell, "PowerShell is required for the installed company.exe smoke test"
            if args.quote_probe:
                major = run([shell, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command",
                             "$PSVersionTable.PSVersion.Major"], ROOT, env).strip()
                assert int(major) >= 7, "The literal native argument regression requires PowerShell 7"
            run([shell, "-NoLogo", "-NoProfile", "-NonInteractive", "-File", str(ROOT / "install.ps1")], ROOT, env)
            wrapper = home / ".local/bin/company.exe"
            assert wrapper.is_file()
            assert not (home / ".local/bin/company.cmd").exists()
            driver = sandbox / "invoke-installed.ps1"
            driver.write_text('''$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding
$request = Get-Content -LiteralPath $env:SMOKE_REQUEST -Raw -Encoding UTF8 | ConvertFrom-Json
$arguments = @($request.arguments | ForEach-Object { [string]$_ })
Set-Location -LiteralPath $env:SMOKE_PROJECT
& $env:SMOKE_WRAPPER @arguments
exit $LASTEXITCODE
''', encoding="utf-8")
            request = sandbox / "arguments.json"
            env.update({"SMOKE_WRAPPER": str(wrapper), "SMOKE_PROJECT": str(project), "SMOKE_REQUEST": str(request)})

            def company(*arguments):
                request.write_text(json.dumps({"arguments": list(arguments)}, ensure_ascii=False), encoding="utf-8")
                return run([shell, "-NoLogo", "-NoProfile", "-NonInteractive", "-File", str(driver)], project, env)
        else:
            run(["bash", str(ROOT / "install.sh")], ROOT, env)
            wrapper = home / ".local/bin/company"
            assert wrapper.is_symlink() and wrapper.resolve() == (ROOT / "bin/company").resolve()

            def company(*arguments):
                return run([str(wrapper), *arguments], project, env)

        assert len(list((home / ".claude/skills").iterdir())) == 54
        assert len(list((home / ".claude/agents").glob("*.md"))) == 9
        assert (home / ".claude/commands/company.md").read_bytes() == (ROOT / "commands/company.md").read_bytes()
        profiles = json.loads(company("project", "harness", "profiles", "--format", "json"))
        assert profiles["version"] == 1 and set(profiles["profiles"]) == {"developers", "designers", "marketing", "social-media", "finance", "small-business", "legal", "sales"}
        assert all(len(profile["checks"]) == 2 for profile in profiles["profiles"].values())
        print("PASS: installed wrapper loads the harness profile catalog with eight departments and two checks each")
        brief = 'Un projet café pour "Camille & associés". Texte littéral, sans exécution.'
        brief_file = project / "brief français.txt"
        brief_file.write_text(brief, encoding="utf-8")
        company("project", "init", "--name", "Projet café", "--brief-file", str(brief_file))
        state = json.loads(company("project", "status", "--format", "json"))
        assert state["brief"] == brief and state["name"] == "Projet café"
        assert state["tasks"] == [] and state["revision"] == 1
        assert not (project / ".claude/company-team.md").exists()
        prompt = company("project", "prompt")
        assert "Saved project snapshot" in prompt and "Projet café" in prompt
        assert str(project).replace("\\", "\\\\") in prompt
        print("PASS: real installed wrapper init/status/prompt preserves Unicode and paths with spaces")

        company("project", "task", "add", "--id", "installed-check", "--department", "developers",
                "--title", "Check the installed lifecycle", "--acceptance", "The fixture file matches its recorded SHA-256")
        company("project", "task", "start", "installed-check")
        artifact = project / "résultat métier.md"
        artifact.write_text("Synthetic installed-helper evidence: café 空白\n", encoding="utf-8")
        company("project", "task", "submit", "installed-check", "--artifact", artifact.name, "--summary", "Fixture file written and read")
        company("project", "task", "review", "installed-check", "--decision", "accept", "--reviewer", "ceo", "--note", "Compared the recorded fixture hash")
        state = json.loads(company("project", "status", "--format", "json"))
        assert state["tasks"][0]["status"] == "done"
        assert state["tasks"][0]["artifacts"][0]["sha256"] == hashlib.sha256(artifact.read_bytes()).hexdigest()
        print("PASS: actual installed helper task add/start/submit/review/status lifecycle")

        record = recording_host(sandbox, env)
        company("project", "start")
        launched = json.loads(record.read_text(encoding="utf-8"))
        assert Path(launched["cwd"]).resolve() == project
        assert len(launched["argv"]) == 3 and launched["argv"][:2] == ["--plugin-dir", str(ROOT)]
        bootstrap = json.loads(launched["argv"][2].split("\n")[-1])
        assert bootstrap["cwd"] == str(project)
        assert bootstrap["argv"][1:] == [str(ROOT / "skills/chief-of-staff/scripts/project.py"), "prompt"]
        assert bootstrap["validatedRevisionAtLaunch"] == state["revision"]
        assert [argument for argument in launched["argv"] if argument.startswith("--")] == ["--plugin-dir"]
        print("PASS: real recording host received project cwd, packaged plugin and resume argv; no permission/model overrides")

        if args.quote_probe:
            if os.name != "nt":
                raise AssertionError("--quote-probe targets the real Windows PowerShell/company.exe handoff")
            quoted = sandbox / "quoted project"
            quoted.mkdir()
            env["SMOKE_PROJECT"] = str(quoted)
            company("project", "init", "--name", "Quote probe", "--brief", brief)
            quoted_state = json.loads(company("project", "status", "--format", "json"))
            assert quoted_state["brief"] == brief, "PowerShell/company.exe changed literal quotes or ampersand: " + repr(quoted_state["brief"])
            print("PASS: real PowerShell/company.exe literal quote and ampersand round-trip")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (AssertionError, OSError, subprocess.TimeoutExpired) as error:
        print("FAIL: installed project smoke: " + str(error), file=sys.stderr)
        sys.exit(1)
