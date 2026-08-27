#!/usr/bin/env python3
"""Claude, Inc.: the company's compliance officer.

Runs on every push and pull request: verifies that the org chart, the employees'
job descriptions, the CLI roster and the docs all agree with each other.
A PR that breaks the org fails CI.

Usage: python3 scripts/validate.py
"""
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

STAFF = {"chief-of-staff", "token-accountant"}
EXPECTED_EMPLOYEES = 50
EXPECTED_DEPARTMENTS = 8
EXPECTED_EMPLOYEES_PER_DEPARTMENT = 6
EXPECTED_VERSION = "1.1.0"
REQUIRED_SECTIONS = ["When to use", "Workflow", "Output format", "Quality bar", "Example"]
ALLOWED_SKILL_KEYS = {"name", "description", "allowed-tools", "license", "metadata", "model"}
ALLOWED_AGENT_KEYS = {"name", "description", "tools", "model", "color"}

errors, warnings = [], []
err = errors.append
warn = warnings.append


def bash_works():
    """True only if bash can actually execute.

    Windows ships a bash.exe stub for WSL that exists on PATH but fails when no
    distribution is installed, so probing the binary matters more than finding it.
    """
    if bash_works.cache is None:
        bash_works.cache = False
        if shutil.which("bash"):
            try:
                probe = subprocess.run(["bash", "-c", "exit 0"], capture_output=True, timeout=10)
                bash_works.cache = probe.returncode == 0
            except (OSError, subprocess.SubprocessError):
                bash_works.cache = False
    return bash_works.cache


bash_works.cache = None


def frontmatter(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text
    fm = {}
    for key in re.findall(r"^([A-Za-z-]+):", m.group(1), re.M):
        val = re.search(rf"^{key}:\s*(.+?)\s*$", m.group(1), re.M | re.S)
        fm[key] = val.group(1).strip().strip("\"'") if val else ""
    return fm, text[m.end():]


def check_employees(skills):
    for slug in skills:
        path = f"skills/{slug}/SKILL.md"
        if not os.path.exists(path):
            err(f"{slug}: SKILL.md missing")
            continue
        fm, body = frontmatter(path)
        if fm is None:
            err(f"{slug}: no YAML frontmatter")
            continue
        if not re.match(r"^[a-z0-9-]{1,64}$", slug):
            err(f"{slug}: invalid slug (lowercase, digits and hyphens only)")
        if fm.get("name") != slug:
            err(f"{slug}: frontmatter name '{fm.get('name')}' != directory name")
        desc = fm.get("description", "")
        if not desc:
            err(f"{slug}: missing description")
        elif len(desc) > 1024:
            err(f"{slug}: description is {len(desc)} chars (max 1024)")
        elif not re.search(r"\bUse (when|for)\b|\bTrigger\b|Utilise", desc, re.I):
            warn(f"{slug}: description has no trigger phrase ('Use when ...')")
        for extra in set(fm) - ALLOWED_SKILL_KEYS:
            warn(f"{slug}: non-standard frontmatter key '{extra}'")
        for section in REQUIRED_SECTIONS:
            if not re.search(rf"^##+ .*{re.escape(section)}", body, re.M | re.I):
                err(f"{slug}: missing '## {section}' section")


def check_departments(agents):
    for name in agents:
        fm, _ = frontmatter(f"agents/{name}.md")
        if fm is None:
            err(f"agent {name}: no YAML frontmatter")
            continue
        if fm.get("name") != name:
            err(f"agent {name}: frontmatter name != file name")
        if not fm.get("description"):
            err(f"agent {name}: missing description")
        elif len(fm["description"]) > 1024:
            err(f"agent {name}: description is {len(fm['description'])} chars (max 1024)")
        for extra in set(fm) - ALLOWED_AGENT_KEYS:
            warn(f"agent {name}: non-standard frontmatter key '{extra}'")


def check_roster(cli, skills, agents):
    """The CLI is the single source of truth for who works where."""
    depts = re.search(r"^DEPTS=\(([^)]+)\)", cli, re.M)
    if not depts:
        err("bin/company: DEPTS array not found")
        return
    cli_depts = depts.group(1).split()
    if len(cli_depts) != EXPECTED_DEPARTMENTS:
        err(f"bin/company has {len(cli_depts)} departments, expected {EXPECTED_DEPARTMENTS}")
    if sorted(cli_depts) != agents:
        err(f"bin/company DEPTS {sorted(cli_depts)} != agents/ {agents}")
    seen = {}
    for dept in cli_depts:
        m = re.search(rf"^\s*{re.escape(dept)}\)\s+echo \"([^\"]+)\"", cli, re.M)
        if not m:
            err(f"bin/company: skills_of() has no entry for '{dept}'")
            continue
        staffed = m.group(1).split()
        if len(staffed) != EXPECTED_EMPLOYEES_PER_DEPARTMENT:
            err(f"{dept}: {len(staffed)} employees, expected {EXPECTED_EMPLOYEES_PER_DEPARTMENT}")
        if f'echo "{dept}"' not in cli:
            err(f"bin/company: dept_of() cannot resolve '{dept}'")
        if not os.path.exists(f"agents/{dept}.md"):
            err(f"agents/{dept}.md missing for department '{dept}'")
            continue
        agent_text = open(f"agents/{dept}.md", encoding="utf-8").read()
        for slug in staffed:
            if slug not in skills:
                err(f"bin/company staffs '{slug}' in {dept}, but skills/{slug}/ does not exist")
            if slug in seen:
                err(f"'{slug}' is staffed in both {seen[slug]} and {dept}")
            seen[slug] = dept
            if slug not in agent_text:
                err(f"agents/{dept}.md never mentions its employee '{slug}'")
    for slug in skills:
        if slug not in seen and slug not in STAFF:
            err(f"skills/{slug}/ belongs to no department (add it to bin/company and its agent)")
    expected_staffed = EXPECTED_DEPARTMENTS * EXPECTED_EMPLOYEES_PER_DEPARTMENT
    if len(seen) != expected_staffed:
        err(f"bin/company staffs {len(seen)} employees, expected {expected_staffed}")


def check_docs(skills, agents):
    readme = open("README.md", encoding="utf-8").read()
    for slug in skills:
        if f"`{slug}`" not in readme:
            err(f"README.md does not list employee '{slug}'")
    links = re.findall(r"\]\((?!https?:|#)([^)]+)\)", readme) + re.findall(r'src="(?!https?:)([^"]+)"', readme)
    for link in links:
        if not os.path.exists(link.split("#")[0]):
            err(f"README.md: broken relative link -> {link}")
    manual = open("CLAUDE.md", encoding="utf-8").read()
    for dept in agents:
        if f"`{dept}`" not in manual:
            err(f"CLAUDE.md routing table is missing '{dept}'")
    for slug in STAFF & set(skills):
        if slug not in manual:
            warn(f"CLAUDE.md does not mention staff hire '{slug}'")
    for cmd in sorted(os.listdir("commands")):
        text = open(f"commands/{cmd}", encoding="utf-8").read()
        if not text.startswith("---"):
            err(f"commands/{cmd}: missing frontmatter")
        if "$ARGUMENTS" not in text:
            warn(f"commands/{cmd}: no $ARGUMENTS placeholder")


def check_packaging(cli):
    try:
        plugin = json.load(open(".claude-plugin/plugin.json"))
        market = json.load(open(".claude-plugin/marketplace.json"))
    except (json.JSONDecodeError, OSError) as exc:
        err(f"invalid plugin manifest: {exc}")
        return
    plugin_version = plugin.get("version")
    market_version = market.get("metadata", {}).get("version")
    if plugin_version != EXPECTED_VERSION:
        err(f"plugin.json version {plugin_version!r} != required {EXPECTED_VERSION}")
    if market_version != EXPECTED_VERSION:
        err(f"marketplace.json version {market_version!r} != required {EXPECTED_VERSION}")
    if plugin_version != market_version:
        err("plugin.json and marketplace.json versions disagree")
    cli_version = re.search(r'^VERSION="([^"]+)"', cli, re.M)
    if not cli_version:
        err("bin/company VERSION not found")
    elif cli_version.group(1) != EXPECTED_VERSION:
        err(f"bin/company VERSION {cli_version.group(1)!r} != required {EXPECTED_VERSION}")


def check_powershell_installer():
    script = "install.ps1"
    if not os.path.exists(script):
        err(f"{script}: missing")
        return
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if not shell:
        warn(f"{script}: PowerShell unavailable, syntax check skipped (Windows CI is authoritative)")
        return
    parser = (
        "$tokens = $null; $errors = $null; "
        "[void][System.Management.Automation.Language.Parser]::ParseFile("
        "(Resolve-Path 'install.ps1'), [ref]$tokens, [ref]$errors); "
        "if ($errors.Count -gt 0) { $errors | ForEach-Object { Write-Error $_ }; exit 1 }"
    )
    proc = subprocess.run(
        [shell, "-NoProfile", "-NonInteractive", "-Command", parser],
        capture_output=True, text=True
    )
    if proc.returncode:
        detail = proc.stderr.strip() or proc.stdout.strip()
        err(f"{script}: PowerShell syntax error\n{detail}")


def check_scripts():
    for script in ["bin/company", "install.sh", "scripts/validate.py"]:
        if script.endswith(".py"):
            if subprocess.run([sys.executable, "-c", f"compile(open('{script}').read(), '{script}', 'exec')"],
                              capture_output=True).returncode:
                err(f"{script}: syntax error")
        elif bash_works():
            proc = subprocess.run(["bash", "-n", script], capture_output=True, text=True)
            if proc.returncode:
                err(f"{script}: bash syntax error\n{proc.stderr.strip()}")
        else:
            warn(f"{script}: no working bash here, syntax check skipped (CI is authoritative)")
        if b"\r\n" in open(script, "rb").read():
            err(f"{script}: CRLF line endings would break execution (see .gitattributes)")
        mode = subprocess.run(["git", "ls-files", "-s", script], capture_output=True, text=True).stdout.split()
        if mode and mode[0] != "100755":
            err(f"{script}: not executable in git (fix: git update-index --chmod=+x {script})")
    check_powershell_installer()
    if os.name == "nt":
        warn("running on Windows: shell checks are advisory here, CI is authoritative")
    if os.path.exists("assets/org-chart.svg"):
        import xml.dom.minidom
        try:
            xml.dom.minidom.parse("assets/org-chart.svg")
        except Exception as exc:
            err(f"assets/org-chart.svg: invalid XML ({exc})")


def main():
    skills = sorted(d for d in os.listdir("skills") if os.path.isdir(f"skills/{d}"))
    agents = sorted(f[:-3] for f in os.listdir("agents") if f.endswith(".md"))
    cli = open("bin/company", encoding="utf-8").read()

    if len(skills) != EXPECTED_EMPLOYEES:
        err(f"skills/ has {len(skills)} employees, expected {EXPECTED_EMPLOYEES}")
    if len(agents) != EXPECTED_DEPARTMENTS:
        err(f"agents/ has {len(agents)} departments, expected {EXPECTED_DEPARTMENTS}")
    missing_staff = STAFF - set(skills)
    if missing_staff:
        err(f"executive staff missing from skills/: {sorted(missing_staff)}")

    check_employees(skills)
    check_departments(agents)
    check_roster(cli, skills, agents)
    check_docs(skills, agents)
    check_packaging(cli)
    check_scripts()

    staff = len(STAFF & set(skills))
    print(f"Claude, Inc.: {len(skills)} employees across {len(agents)} departments "
          f"({len(skills) - staff} staffed + {staff} executive staff)")
    ci = os.getenv("GITHUB_ACTIONS")
    for w in warnings:
        print(f"::warning::{w}" if ci else f"  warning: {w}")
    for e in errors:
        print(f"::error::{e}" if ci else f"  ERROR: {e}")
    if errors:
        print(f"\nFAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"\nAll checks passed ({len(warnings)} warning(s)). The company is in order.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
