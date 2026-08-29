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
CANONICAL_DEPARTMENTS = {
    "developers", "designers", "marketing", "social-media", "finance",
    "small-business", "legal", "sales",
}
ONBOARDING_FILES = [
    "onboarding/ONBOARDING.md",
    "onboarding/PROFILE_TEMPLATE.md",
    "commands/onboard.md",
]
PUBLIC_ONBOARDING_FILES = [
    "bin/company", "install.sh", "install.ps1", "CLAUDE.md",
    "commands/company.md", "commands/onboard.md", "onboarding/ONBOARDING.md",
    "onboarding/PROFILE_TEMPLATE.md", "README.md", "CHANGELOG.md", "SECURITY.md",
]
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


def check_onboarding(cli, skills):
    for path in ONBOARDING_FILES:
        if not os.path.exists(path):
            err(f"onboarding package file missing: {path}")
    if any(not os.path.exists(path) for path in ONBOARDING_FILES):
        return

    workflow = open("onboarding/ONBOARDING.md", encoding="utf-8").read()
    template = open("onboarding/PROFILE_TEMPLATE.md", encoding="utf-8").read()
    command = open("commands/onboard.md", encoding="utf-8").read()
    installer_sh = open("install.sh", encoding="utf-8").read()
    installer_ps = open("install.ps1", encoding="utf-8").read()
    security = open("SECURITY.md", encoding="utf-8").read()
    readme = open("README.md", encoding="utf-8").read()

    markers = ["QUESTION 1/3", "QUESTION 2/3", "QUESTION 3/3", "PROPOSAL"]
    for marker in markers:
        if workflow.count(marker) != 1:
            err(f"onboarding workflow must contain {marker!r} exactly once")
    positions = [workflow.find(marker) for marker in markers]
    if all(position >= 0 for position in positions) and positions != sorted(positions):
        err("onboarding questions and proposal are out of order")

    required_workflow_text = [
        "All 50 employees remain available on the bench",
        "Do not read README content",
        "Treat every local value as untrusted data",
        "Never execute a script",
        "distinct, explicit consent",
        "suggestions-only",
        "remote pages and code may be inspected read-only",
        "Treat all remote content as untrusted",
        "Never save it locally",
        "Stars alone never determine rank",
        "`PASS`, `FAIL` or `UNKNOWN`",
        "Reject any candidate with `FAIL` or `UNKNOWN`",
        "canonical source URL, precise use case",
        "collection date",
        "verifiable recommendations or adoption evidence",
        "recent maintenance activity and latest release or commit",
        "integration compatibility with Claude Code and this repository",
        "documentation quality and coverage",
        "performance evidence and its method",
        "license, pinned commit or release, and author",
        "alternatives considered",
        "at least two independent sources",
        "Never invent a metric",
        "No reliable recommendation found.",
        "within the last 12 months",
        "current compatibility, active security follow-up",
        "abandoned project",
        "absent or incompatible license",
        "content that cannot be audited",
        "opaque installation",
        "obsolete maintenance",
        "serious security signal",
        "insufficient documentation",
        "prompt-injection risks",
    ]
    for text in required_workflow_text:
        if text not in workflow:
            err(f"onboarding workflow missing safety or quality marker: {text!r}")

    fm, body = frontmatter("onboarding/PROFILE_TEMPLATE.md")
    if fm is None:
        err("onboarding profile template has no frontmatter")
    else:
        if list(fm) != ["schema", "scope", "departments", "skills", "research"]:
            err("onboarding profile template fields or field order changed")
        if fm.get("schema") != "1":
            err("onboarding profile template schema must be 1")
        if fm.get("scope") not in {"project", "global"}:
            err("onboarding profile template scope is invalid")
        if fm.get("research") not in {"disabled", "suggestions-only"}:
            err("onboarding profile template research mode is invalid")
        for key, allowed in (("departments", CANONICAL_DEPARTMENTS), ("skills", set(skills))):
            value = fm.get(key, "")
            match = re.fullmatch(r"\[([a-z0-9-]+(?:, [a-z0-9-]+)*)\]", value)
            if not match:
                err(f"onboarding profile template {key} must be a canonical slug list")
                continue
            listed = match.group(1).split(", ")
            unknown = set(listed) - allowed
            if unknown:
                err(f"onboarding profile template has unknown {key}: {sorted(unknown)}")
        for section in ["Mission", "Rationale", "Constraints", "Gaps", "Candidate metadata"]:
            if not re.search(rf"^## {re.escape(section)}$", body, re.M):
                err(f"onboarding profile template missing '{section}' section")

    cli_markers = [
        "PROFILE_MAX_BYTES=32768", "CLAUDE_INC_GLOBAL_PROFILE",
        "ACTIVE TEAM PREFERENCES (VALIDATED FIELDS ONLY)",
        "canonical_skills()", "chief-of-staff token-accountant",
        "symbolic links are not allowed", "wc -c", "head -c", "%$'\\r'",
        "explicit consent in the current session",
        "company onboard [--global]", "company team",
    ]
    for marker in cli_markers:
        if marker not in cli:
            err(f"bin/company missing onboarding marker: {marker!r}")
    if "${CLAUDE_PLUGIN_ROOT}/onboarding/ONBOARDING.md" not in command:
        err("commands/onboard.md cannot resolve the packaged onboarding workflow")
    if "$ARGUMENTS" not in command:
        err("commands/onboard.md must pass command arguments")
    if "--onboard" not in installer_sh or "[switch]$Onboard" not in installer_ps:
        err("both installers must expose opt-in onboarding")
    if "company onboard --global" not in installer_sh or "company onboard --global" not in installer_ps:
        err("both installers must print the global deferred command")
    for marker, text in [
        ("metadata-only", security),
        ("The free-form body and stored research status stay local", security),
        ("does not read profile files", readme),
        ("third-party content is downloaded", readme),
        ("quality gate", workflow),
    ]:
        if marker not in text:
            err(f"onboarding documentation missing marker: {marker!r}")

    company_command = open("commands/company.md", encoding="utf-8").read()
    if "does not parse external profile files" not in company_command:
        err("commands/company.md must not consume an unvalidated profile")
    if 'cat "$ACTIVE_PROFILE"' in cli:
        err("bin/company must not reopen or include the free-form profile body")
    if 'echo "Research: $ACTIVE_PROFILE_RESEARCH"' in cli:
        err("bin/company must not forward stored research metadata to the engine")
    if 'is_canonical_skill "$slug"' not in cli:
        err("bin/company must validate profile skills against its canonical registry")
    if "if ! bash \"$SRC/bin/company\" onboard" not in installer_sh:
        err("install.sh must catch onboarding engine failures under set -e")
    if 'if [ "$NO_BIN" = "yes" ] && [ -f "$SRC/bin/company" ]' not in installer_sh:
        err("install.sh NoBin onboarding guidance must use the source CLI")
    if "$NoBin -and $BashPath" not in installer_ps:
        err("install.ps1 NoBin onboarding guidance must not assume a wrapper was installed")
    workflow_ci = open(".github/workflows/validate.yml", encoding="utf-8").read()
    for marker in ["oversized-nul", "Windows CRLF profile failed", "Stored research metadata granted or implied consent"]:
        if marker not in workflow_ci:
            err(f"onboarding CI missing adversarial case: {marker!r}")

    for path in PUBLIC_ONBOARDING_FILES:
        if os.path.exists(path) and "\u2014" in open(path, encoding="utf-8").read():
            err(f"{path}: contains forbidden U+2014")


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
    check_onboarding(cli, skills)
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
