"""Real native launcher transport, with an inert Bash recorder and no model."""

import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.name == "nt", "Windows native launcher")
class NativeLauncherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="claude-inc-native-transport-")
        cls.sandbox = Path(cls.temporary.name).resolve()
        assert cls.sandbox.parent == Path(tempfile.gettempdir()).resolve()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.work = cls.sandbox / "cwd café 空白 %LITERAL%"
        cls.work.mkdir()
        cls.env = os.environ.copy()
        # Only child processes receive isolated homes; no real installation runs.
        cls.env.update(HOME=str(cls.sandbox), USERPROFILE=str(cls.sandbox))
        cls.env["NATIVE_RECORD"] = cls.sandbox.as_posix()
        git = shutil.which("git")
        candidates = [shutil.which("bash")]
        if git:
            candidates.append(str(Path(git).parent.parent / "bin/bash.exe"))
        cls.bash = None
        for candidate in candidates:
            if candidate and Path(candidate).is_file():
                probe = subprocess.run([candidate, "--version"], capture_output=True, timeout=15,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
                if probe.returncode == 0 and b"GNU bash" in probe.stdout:
                    cls.bash = Path(candidate).resolve()
                    break
        assert cls.bash, "Git Bash is required for native transport regression"
        cls.compiler = Path(os.environ["WINDIR"]) / "Microsoft.NET/Framework64/v4.0.30319/csc.exe"
        if not cls.compiler.is_file():
            cls.compiler = Path(os.environ["WINDIR"]) / "Microsoft.NET/Framework/v4.0.30319/csc.exe"
        assert cls.compiler.is_file(), "The system .NET Framework compiler is required"
        script = cls.sandbox / "inert recorder %NAME%.sh"
        script_body = '''#!/usr/bin/env bash
printf '%s\\0' "$@" > "$NATIVE_RECORD/argv.bin"
pwd -W > "$NATIVE_RECORD/cwd.txt"
line=''
if [ "$NATIVE_READ_STDIN" = yes ]; then IFS= read -r -t 5 line; fi
printf '%s' "$line" > "$NATIVE_RECORD/stdin.txt"
printf 'native stdout\\n'
printf 'native stderr\\n' >&2
exit 37
'''
        with script.open("w", encoding="utf-8", newline="") as stream:
            stream.write(script_body)
        cls.launcher = cls.compile_launcher(cls.bash, script, "company")

    @classmethod
    def compile_launcher(cls, bash, script, name):
        template = (ROOT / "skills/chief-of-staff/scripts/windows_launcher.cs").read_text(encoding="utf-8")
        source = template.replace("__BASH_PATH_BASE64__", base64.b64encode(str(bash).encode()).decode())
        source = source.replace("__COMPANY_PATH_BASE64__", base64.b64encode(str(script).encode()).decode())
        source_path = cls.sandbox / (name + ".cs")
        output = cls.sandbox / (name + ".exe")
        source_path.write_text(source, encoding="utf-8")
        result = subprocess.run([str(cls.compiler), "/nologo", "/target:exe", "/platform:anycpu",
                                 "/optimize+", "/debug-", "/out:" + str(output), str(source_path)],
                                capture_output=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
        assert result.returncode == 0, result.stdout.decode(errors="replace")
        return output

    def assert_transport(self, command, arguments, check_stdin=True):
        env = dict(self.env, NATIVE_READ_STDIN="yes" if check_stdin else "no")
        result = subprocess.run(command, cwd=self.work, env=env,
                                input="stdin café & literal\n".encode("utf-8") if check_stdin else b"",
                                capture_output=True, timeout=30,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        self.assertEqual(result.returncode, 37, result.stderr)
        self.assertEqual(result.stdout.strip(), b"native stdout")
        self.assertEqual(result.stderr.strip(), b"native stderr")
        recorded = (self.sandbox / "argv.bin").read_bytes().decode("utf-8").split("\0")
        self.assertEqual(recorded[-1], "")
        self.assertEqual(recorded[:-1], arguments)
        self.assertEqual(Path((self.sandbox / "cwd.txt").read_text(encoding="utf-8").strip()).resolve(), self.work)
        self.assertEqual((self.sandbox / "stdin.txt").read_bytes(),
                         "stdin café & literal".encode("utf-8") if check_stdin else b"")

    @staticmethod
    def literal_arguments():
        return ["", "café 空白", '"Camille & associés"', "&", "%NAME%", "!bang!", "^caret",
                "$(not-a-command)", "`literal`", "line one\nline two", "C:\\end\\",
                "two\\\\", 'backslashes\\\\"quote', '"', " ", "--plain"]

    def test_real_bash_preserves_every_native_argument_and_inherits_process_contract(self):
        arguments = self.literal_arguments()
        self.assert_transport([str(self.launcher), *arguments], arguments)

    def test_powershell_7_ordinary_native_call_preserves_literal_arguments(self):
        shell = shutil.which("pwsh.exe")
        self.assertIsNotNone(shell, "PowerShell 7 is required for the caller regression")
        major = subprocess.check_output([shell, "-NoLogo", "-NoProfile", "-Command", "$PSVersionTable.PSVersion.Major"])
        self.assertGreaterEqual(int(major.strip()), 7)
        arguments = self.literal_arguments()
        request = self.sandbox / "arguments.json"
        request.write_text(json.dumps({"arguments": arguments}, ensure_ascii=False), encoding="utf-8")
        driver = self.sandbox / "invoke.ps1"
        driver.write_text('''$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$request = Get-Content -LiteralPath $env:NATIVE_REQUEST -Raw -Encoding UTF8 | ConvertFrom-Json
$arguments = @($request.arguments | ForEach-Object { [string]$_ })
& $env:NATIVE_LAUNCHER @arguments
exit $LASTEXITCODE
''', encoding="utf-8")
        self.env.update(NATIVE_REQUEST=str(request), NATIVE_LAUNCHER=str(self.launcher))
        # PowerShell owns its input pipeline; the direct-native test checks
        # inherited stdin separately, without a caller consuming that stream.
        self.assert_transport([shell, "-NoLogo", "-NoProfile", "-NonInteractive", "-File", str(driver)],
                              arguments, check_stdin=False)

    def test_missing_bash_returns_bounded_actionable_error(self):
        launcher = self.compile_launcher(self.sandbox / "absent-bash.exe", self.sandbox / "unused.sh", "missing")
        result = subprocess.run([str(launcher), "private synthetic text"], capture_output=True, encoding="utf-8",
                                timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("reinstall the company launcher", result.stderr)
        self.assertNotIn("private synthetic text", result.stderr)
        self.assertLess(len(result.stderr), 200)

    def test_temporary_parent_normalization_preserves_roots_without_filesystem_access(self):
        # Extract only the pure function. Do not run the installer or create any
        # file at these synthetic drive/UNC roots.
        shell = shutil.which("pwsh.exe") or shutil.which("powershell.exe")
        driver = self.sandbox / "check-parent.ps1"
        driver.write_text(r'''$ErrorActionPreference = 'Stop'
$tokens = $null; $errors = $null
$ast = [Management.Automation.Language.Parser]::ParseFile($env:NATIVE_INSTALLER, [ref]$tokens, [ref]$errors)
if ($errors.Count) { throw 'Installer syntax error' }
$definition = $ast.Find({ param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Get-LauncherBuildParent' }, $true)
if (-not $definition) { throw 'Missing pure parent normalization function' }
. ([scriptblock]::Create($definition.Extent.Text))
foreach ($example in @('C:\', 'C:/', 'C:\temp with spaces\', '\\server\share\', '\\server\share\temp\')) {
    $actual = Get-LauncherBuildParent $example
    $expected = [IO.Path]::GetDirectoryName([IO.Path]::GetFullPath((Join-Path $actual 'synthetic-child')))
    if ($actual -cne $expected) { throw "Cleanup parent mismatch: $example" }
}
if ((Get-LauncherBuildParent 'C:\') -cne 'C:\') { throw 'Drive root separator was lost' }
''', encoding="utf-8")
        env = dict(self.env, NATIVE_INSTALLER=str(ROOT / "install.ps1"))
        result = subprocess.run([shell, "-NoLogo", "-NoProfile", "-NonInteractive", "-File", str(driver)],
                                env=env, capture_output=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))


if __name__ == "__main__":
    unittest.main()
