#!/usr/bin/env python3
"""Generate the public company directory from the canonical registry and manuals."""

import argparse
from html import escape
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


def company_dataset(root=ROOT):
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
    executives = []
    assigned_staff = set()
    for slug in ("cto", "caio"):
        charter = (root / f"agents/{slug}.md").read_text(encoding="utf-8").replace("\r\n", "\n")
        name, role = heading(charter)
        scope = re.search(r"^(You[ ,].*?)(?:\n\n|\Z)", charter, re.M | re.S)
        skills = re.findall(r"^\| `([a-z0-9-]+)` \|", section(charter, "Your team"), re.M)
        if not scope or len(skills) != 4 or len(set(skills)) != 4 or not set(skills) <= {item["id"] for item in staff} or assigned_staff.intersection(skills):
            raise ValueError(f"{slug.upper()} charter must describe four distinct registered staff manuals")
        assigned_staff.update(skills)
        executives.append({"id": slug, "name": name, "role": role,
                           "scope": " ".join(scope.group(1).split()), "skills": skills})
    return {"schemaVersion": 1, "source": "alebgl77/claude-inc", "departments": departments, "staff": staff,
            "executive": executives[0], "executives": executives,
            "missionIds": [item["id"] for item in company["catalog"]["missions"]]}


def generate(root=ROOT):
    return serialize_dataset(company_dataset(root))


def serialize_dataset(dataset):
    data = json.dumps(dataset, ensure_ascii=True, separators=(",", ":"))
    data = data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return ("// Generated by scripts/build_company.py; do not edit.\nwindow.CLAUDE_INC_COMPANY = " + data + ";\n").encode("ascii")


def organization_svg(dataset, detailed=True):
    """Keep both public organization diagrams tied to the canonical directory."""
    width, height = (1440, 1110) if detailed else (1200, 630)
    total = sum(len(d["skills"]) for d in dataset["departments"]) + len(dataset["staff"])
    description = f"Peer CEO, CTO and CAIO executives support nine departments, six employee manuals each and ten staff manuals: {total} operating manuals."
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">',
             '<!-- Generated by scripts/build_company.py; do not edit. -->', '<title id="title">Claude, Inc. organization map</title>',
             f'<desc id="description">{escape(description)}</desc>',
             '<style>text{font-family:Trebuchet MS,Segoe UI,sans-serif;fill:#25271f}.muted{fill:#626458}.accent{fill:#b9462c}.label{font-family:Consolas,monospace;font-size:12px}.rule{fill:none;stroke:#b9b5a7}.card{fill:#ede9df;stroke:#d4d0c3}</style>',
             f'<rect width="{width}" height="{height}" fill="#f6f3eb"/>']

    def text(x, y, value, size=16, css="", anchor="start"):
        lines.append(f'<text x="{x}" y="{y}" font-size="{size}" class="{css}" text-anchor="{anchor}">{escape(value)}</text>')

    text(40, 43, "claude, inc.", 28)
    text(width - 40, 40, f"9 DEPARTMENTS / {total} OPERATING MANUALS", 12, "label muted", "end")
    text(width // 2, 83, "YOU / FOUNDER — DIRECTION AND AUTHORITY", 12, "label muted", "middle")
    top, gap, margin = 111, 20, 40
    card_width = (width - margin * 2 - gap * 2) // 3
    leader_labels = [("CEO", "Business direction & priorities"), ("CTO", "Technology, security & evaluation"), ("CAIO", "AI workflows, handoffs & adoption")]
    for i, (name, purpose) in enumerate(leader_labels):
        x = margin + i * (card_width + gap)
        lines.append(f'<rect x="{x}" y="{top}" width="{card_width}" height="76" class="card"/>')
        text(x + 18, top + 29, name, 12, "label accent")
        text(x + 88, top + 29, "PEER EXECUTIVE", 12, "label muted")
        text(x + 18, top + 56, purpose, 15)
    text(width // 2, 215, "DEPARTMENT VPs OWN DELIVERY", 12, "label muted", "middle")
    row_height = 221 if detailed else 99
    for i, department in enumerate(dataset["departments"]):
        x = margin + (i % 3) * (card_width + gap)
        y = 237 + (i // 3) * row_height
        lines.append(f'<rect x="{x}" y="{y}" width="{card_width}" height="{row_height - 14}" class="card"/>')
        text(x + 16, y + 29, department["name"], 20)
        if detailed:
            for index, skill in enumerate(department["skills"]):
                text(x + 16, y + 58 + index * 25, skill["id"], 13, "muted skill")
        else:
            text(x + 16, y + 57, "6 SPECIALIST MANUALS", 12, "label muted")
    if detailed:
        for i, (name, skills) in enumerate([
            ("COMPANY STAFF", [s["id"] for s in dataset["staff"] if not any(s["id"] in e["skills"] for e in dataset["executives"])]),
            *[(e["name"] + " OFFICE", e["skills"]) for e in dataset["executives"]],
        ]):
            x = margin + i * (card_width + gap)
            text(x, 928, name, 12, "label accent")
            for index, skill in enumerate(skills):
                text(x, 955 + index * 25, skill, 14, "muted skill")
    text(margin, height - 27, "54 department manuals + 10 staff manuals. One shared company.", 14, "muted")
    lines.append('</svg>')
    return ("\n".join(lines) + "\n").encode("utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--check", action="store_true", help="fail on stale data; write nothing")
    args = parser.parse_args(argv)
    try:
        dataset = company_dataset()
        diagram = organization_svg(dataset)
        outputs = {"studio/company-data.js": serialize_dataset(dataset), "studio/org-chart.svg": diagram,
                   "assets/org-chart.svg": diagram, "studio/company-preview.svg": organization_svg(dataset, detailed=False)}
        stale = [name for name, generated in outputs.items() if not (ROOT / name).is_file() or (ROOT / name).read_bytes() != generated]
        if args.check and stale:
            print(f"{', '.join(stale)} is stale; run python scripts/build_company.py", file=sys.stderr)
            return 1
        for name, generated in outputs.items():
            if not args.check:
                (ROOT / name).parent.mkdir(parents=True, exist_ok=True)
                (ROOT / name).write_bytes(generated)
            print(f"{name} is up to date" if args.check else f"Generated {name}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"build_company: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if sys.version_info < (3, 9):
        sys.exit("build_company requires Python 3.9 or newer")
    sys.exit(main())
