#!/usr/bin/env python3
"""Claude, Inc. — the company's compliance officer.

Runs on every push and pull request: verifies that the org chart, the employees'
job descriptions, the CLI roster and the docs all agree with each other.
A PR that breaks the org fails CI.

Usage: python3 scripts/validate.py
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

STAFF = {"chief-of-staff", "token-accountant"}
REQUIRED_SECTIONS = ["When to use", "Workflow", "Output format", "Quality bar", "Example"]
ALLOWED_SKILL_KEYS = {"name", "description", "allowed-tools", "license", "metadata", "model"}
ALLOWED_AGENT_KEYS = {"name", "description", "tools", "model", "color"}

errors, warnings = [], []
err = errors.append
warn = warnings.append


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
    if sorted(cli_depts) != agents:
        err(f"bin/company DEPTS {sorted(cli_depts)} != agents/ {agents}")
    seen = {}
    for dept in cli_depts:
        m = re.search(rf"^\s*{re.escape(dept)}\)\s+echo \"([^\"]+)\"", cli, re.M)
        if not m:
            err(f"bin/company: skills_of() has no entry for '{dept}'")
            continue
        staffed = m.group(1).split()
        if len(staffed) != 6:
            warn(f"{dept}: {len(staffed)} employees (the company standard is 6)")
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
    if plugin.get("version") != market.get("metadata", {}).get("version"):
        err("plugin.json and marketplace.json versions disagree")
    cli_version = re.search(r'^VERSION="([^"]+)"', cli, re.M)
    if cli_version and cli_version.group(1) != plugin.get("version"):
        err(f"bin/company VERSION {cli_version.group(1)} != plugin.json {plugin.get('version')}")


def check_scripts():
    for script in ["bin/company", "install.sh", "scripts/validate.py"]:
        if script.endswith(".py"):
            if subprocess.run([sys.executable, "-c", f"compile(open('{script}').read(), '{script}', 'exec')"],
                              capture_output=True).returncode:
                err(f"{script}: syntax error")
        elif subprocess.run(["bash", "-n", script], capture_output=True).returncode:
            err(f"{script}: bash syntax error")
        if b"\r\n" in open(script, "rb").read():
            err(f"{script}: CRLF line endings would break execution (see .gitattributes)")
        mode = subprocess.run(["git", "ls-files", "-s", script], capture_output=True, text=True).stdout.split()
        if mode and mode[0] != "100755":
            err(f"{script}: not executable in git (fix: git update-index --chmod=+x {script})")
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

    check_employees(skills)
    check_departments(agents)
    check_roster(cli, skills, agents)
    check_docs(skills, agents)
    check_packaging(cli)
    check_scripts()

    staff = len(STAFF & set(skills))
    print(f"Claude, Inc. — {len(skills)} employees across {len(agents)} departments "
          f"({len(skills) - staff} staffed + {staff} executive staff)")
    ci = os.getenv("GITHUB_ACTIONS")
    for w in warnings:
        print(f"::warning::{w}" if ci else f"  warning: {w}")
    for e in errors:
        print(f"::error::{e}" if ci else f"  ERROR: {e}")
    if errors:
        print(f"\nFAILED — {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"\nAll checks passed ({len(warnings)} warning(s)). The company is in order.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
