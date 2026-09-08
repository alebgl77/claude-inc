#!/usr/bin/env python3
"""Generate the public company directory from the canonical registry and manuals."""

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def section(markdown, title):
    """Extract a level-two section without treating fenced examples as headings."""
    body = []
    found = False
    fence = None
    for line in markdown.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        if fence:
            if found:
                body.append(line)
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(fence[1]) + r",}[ \t]*", content):
                fence = None
            continue
        opening = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", content)
        if opening and not (opening.group(1)[0] == "`" and "`" in opening.group(2)):
            fence = (opening.group(1)[0], len(opening.group(1)))
            if found:
                body.append(line)
            continue
        heading_match = re.fullmatch(r" {0,3}(#{1,2})[ \t]+(.+?)[ \t]*", content)
        if heading_match:
            heading_title = re.sub(r"[ \t]+#+[ \t]*$", "", heading_match.group(2))
            if found:
                break
            if heading_match.group(1) == "##" and heading_title == title:
                found = True
            continue
        if found:
            body.append(line)
    if not found:
        raise ValueError(f"canonical manual is missing {title!r}")
    if fence:
        raise ValueError(f"canonical section {title!r} has an unclosed code fence")
    result = "".join(body).strip("\r\n")
    if not result.strip() or len(result.encode("utf-8")) > 50000:
        raise ValueError(f"canonical section {title!r} is empty or exceeds 50000 UTF-8 bytes")
    return result


def heading(markdown):
    match = re.search(r"^# (.+)$", markdown, re.M)
    if not match:
        raise ValueError("canonical manual is missing its heading")
    return match.group(1).strip().split(" — ", 1)


def generate(root=ROOT):
    spec = importlib.util.spec_from_file_location("company_mission", root / "skills/chief-of-staff/scripts/mission.py")
    mission = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(mission)
    finally:
        sys.dont_write_bytecode = previous
    company = mission.load_company(root)
    departments = []
    for slug, employees in company["roster"].items():
        charter = company["charters"][slug].replace("\r\n", "\n")
        name, lead = heading(charter)
        # The role paragraph starts with "You". Do not let a greedy heading
        # match consume the document or mistake a legal note for its purpose.
        scope_match = re.search(r"^You (.*?)(?:\n\n|\Z)", charter, re.M | re.S)
        if not scope_match:
            raise ValueError(f"{slug}: missing canonical department purpose")
        scope = "You " + scope_match.group(1)
        rows = {}
        for row in section(charter, "Your team").splitlines():
            cells = [cell.strip() for cell in row.split("|")]
            if len(cells) != 5:
                continue
            employee = re.search(r"`([a-z0-9-]+)`", cells[1])
            if employee and employee.group(1) in employees:
                rows[employee.group(1)] = (cells[2], cells[3])
        if set(rows) != set(employees):
            raise ValueError(f"{slug}: charter must describe all six registered employees")
        skills = []
        for employee in employees:
            manual = company["manuals"][employee].replace("\r\n", "\n")
            skills.append({"id": employee, "name": heading(manual)[0], "role": rows[employee][0],
                           "scope": rows[employee][1], "output": section(manual, "Output format")})
        departments.append({"id": slug, "name": name, "lead": lead, "scope": " ".join(scope.split()), "skills": skills})
    assigned = {skill for employees in company["roster"].values() for skill in employees}
    staff = []
    for slug, manual in company["manuals"].items():
        if slug in assigned:
            continue
        name, role = heading(manual)
        reporting = re.search(r"^\*Staff (?:position|skill) (.+)\*$", manual, re.M)
        scope = section(manual, "When to use").splitlines()[0].removeprefix("- ")
        staff.append({"id": slug, "name": name, "role": role, "scope": scope,
                      "reporting": reporting.group(1).strip() if reporting else "Company staff",
                      "output": section(manual, "Output format")})
    cto = (root / "agents/cto.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    cto_name, cto_role = heading(cto)
    cto_scope = re.search(r"^You (.*?)(?:\n\n|\Z)", cto, re.M | re.S)
    cto_skills = re.findall(r"^\| `([a-z0-9-]+)` \|", section(cto, "Your team"), re.M)
    if not cto_scope or len(cto_skills) != 4 or len(set(cto_skills)) != 4 or not set(cto_skills) <= {item["id"] for item in staff}:
        raise ValueError("CTO charter must describe four registered staff manuals")
    executive = {"id": "cto", "name": cto_name, "role": cto_role,
                 "scope": " ".join(("You " + cto_scope.group(1)).split()), "skills": cto_skills}
    dataset = {"schemaVersion": 1, "source": "alebgl77/claude-inc", "departments": departments, "staff": staff, "executive": executive,
               "missionIds": [item["id"] for item in company["catalog"]["missions"]]}
    data = json.dumps(dataset, ensure_ascii=True, separators=(",", ":"))
    data = data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return ("// Generated by scripts/build_company.py; do not edit.\nwindow.CLAUDE_INC_COMPANY = " + data + ";\n").encode("ascii")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--check", action="store_true", help="fail on stale data; write nothing")
    args = parser.parse_args(argv)
    try:
        generated = generate()
        target = ROOT / "studio/company-data.js"
        if args.check:
            if not target.is_file() or target.read_bytes() != generated:
                print("studio/company-data.js is stale; run python scripts/build_company.py", file=sys.stderr)
                return 1
            print("studio/company-data.js is up to date")
        else:
            target.write_bytes(generated)
            print("Generated studio/company-data.js")
        return 0
    except (OSError, ValueError) as exc:
        print(f"build_company: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if sys.version_info < (3, 9):
        sys.exit("build_company requires Python 3.9 or newer")
    sys.exit(main())
