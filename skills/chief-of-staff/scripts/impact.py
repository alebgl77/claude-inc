"""Freshness of accepted evidence from recorded artifact hashes; read-only, no execution adapter."""

UNVERIFIED = ("changed", "missing", "unreadable", "pending", "what-if")
AFFECTED = ("stale", "drifted", "at-risk", "conditional")
ATTENTION = ("stale", "drifted", "at-risk")
ORDER = ("stale", "drifted", "at-risk", "conditional", "fresh", "superseded", "what-if")
LIMITS = ("Freshness follows declared dependencies, recorded SHA-256 values and the event history. It cannot see undeclared reuse, "
          "judge whether a change matters, or show that recertified work is correct. A task is assumed to work from the accepted "
          "versions that were current when it last became active.")


class ImpactError(ValueError):
    pass


def analyse(state, observe, what_if=()):
    """Compare what every task consumed with later accepted versions and with the project files.

    Accepted tasks never change, so the saved state already names each consumed input: the artifacts
    of a task's dependencies, at the versions accepted before the task last became active. A later
    accepted task that submits the same path supersedes that path; identical bytes keep every consumer
    fresh. `observe(path)` returns the current SHA-256 of a project file, or "missing", "unreadable"
    or "unchecked", and is called once per accepted path.
    """
    tasks = {task["id"]: task for task in state["tasks"]}
    accepted, active_since = {}, {}
    for event in state["events"]:
        if event["type"] == "task.accept":
            accepted[event["taskId"]] = event["revision"]
        elif event["type"] in ("task.start", "task.revise"):
            active_since[event["taskId"]] = event["revision"]
    chains = {}
    for task in sorted((item for item in state["tasks"] if item["status"] == "done"), key=lambda item: accepted[item["id"]]):
        for item in task["artifacts"]:
            chains.setdefault(item["path"], []).append((accepted[task["id"]], task["id"], item["sha256"]))
    owner = {path: chain[-1] for path, chain in chains.items()}
    hypothetical = list(dict.fromkeys(what_if))
    for task_id in hypothetical:
        if task_id not in tasks:
            raise ImpactError("what-if names an unknown task")
        if not any(version[1] == task_id for version in owner.values()):
            raise ImpactError("what-if requires an accepted task that still provides the current version of an artifact")
    pending = {(item["path"], item["sha256"]): task["id"] for task in state["tasks"] if task["status"] == "review" for item in task["artifacts"]}
    disk, pending_by = {}, {}
    for path in sorted(chains):
        _, producer, digest = owner[path]
        if producer in hypothetical:
            disk[path] = "what-if"
            continue
        seen = observe(path)
        if seen == digest:
            disk[path] = "current"
        elif seen in ("missing", "unreadable", "unchecked"):
            disk[path] = seen
        elif (path, seen) in pending:
            disk[path], pending_by[path] = "pending", pending[(path, seen)]
        else:
            disk[path] = "changed"

    def unverified(path, role, source=None):
        reason = {"role": role, "path": path, "change": disk[path]}
        if source is not None:
            reason["from"] = source
        if path in pending_by:
            reason["by"] = pending_by[path]
        return reason

    entries, consumers, producers = {}, {}, {}
    for task in state["tasks"]:
        own = [item["path"] for item in task["artifacts"]] if task["status"] == "done" else []
        if own and all(owner[path][1] != task["id"] for path in own):
            entries[task["id"]] = ("superseded", [{"role": "output", "path": path, "change": "superseded", "by": owner[path][1]} for path in own])
            continue
        since = active_since.get(task["id"], state["revision"] + 1)
        reasons = []
        for dependency in task["dependsOn"]:
            if tasks[dependency]["status"] != "done":
                continue
            for item in tasks[dependency]["artifacts"]:
                # Dependencies are accepted before a task can start, so one earlier version always exists.
                _, source, digest = [version for version in chains[item["path"]] if version[0] < since][-1]
                _, producer, current = owner[item["path"]]
                if producer == task["id"]:
                    continue
                consumers.setdefault(producer, set()).add(task["id"])
                producers.setdefault(task["id"], set()).add(producer)
                if current != digest:
                    reasons.append({"role": "input", "path": item["path"], "change": "superseded", "from": source, "by": producer})
                elif disk[item["path"]] in UNVERIFIED:
                    reasons.append(unverified(item["path"], "input", producer))
        reasons += [unverified(path, "output") for path in own if owner[path][1] == task["id"] and disk[path] in UNVERIFIED]
        reasons = [reason for index, reason in enumerate(reasons) if reason not in reasons[:index]]
        if task["id"] in hypothetical:
            evidence = "what-if"
        elif any(reason["change"] == "superseded" for reason in reasons):
            evidence = "stale"
        elif any(reason["role"] == "output" for reason in reasons):
            evidence = "drifted"
        else:
            evidence = "at-risk" if reasons else "fresh"
        entries[task["id"]] = (evidence, reasons)

    # Least fixpoint: work downstream of affected evidence stays conditional until its producers settle.
    frontier = [task_id for task_id, (evidence, _) in entries.items() if evidence in ATTENTION or evidence == "what-if"]
    reached = set(frontier)
    while frontier:
        for consumer in sorted(consumers.get(frontier.pop(), ())):
            if consumer not in reached:
                reached.add(consumer)
                frontier.append(consumer)
                if entries[consumer][0] == "fresh":
                    entries[consumer] = ("conditional", entries[consumer][1])

    # Recertify in dependency order so no task is redone before its affected producers settle.
    waiting = [task["id"] for task in state["tasks"] if task["status"] == "done" and entries[task["id"]][0] in AFFECTED]
    plan = []
    while waiting:
        ready = [task_id for task_id in waiting if not producers.get(task_id, set()).intersection(waiting)]
        if not ready:  # superseding work can depend on its own consumer: release direct evidence first
            ready = [next((task_id for task_id in waiting if entries[task_id][0] in ATTENTION), waiting[0])]
        plan.append(ready)
        waiting = [task_id for task_id in waiting if task_id not in ready]
    waves = {task_id: number for number, wave in enumerate(plan, 1) for task_id in wave}

    result = []
    counts = {"accepted": {}, "open": {}}
    for task in state["tasks"]:
        evidence, reasons = entries[task["id"]]
        group = counts["accepted" if task["status"] == "done" else "open"]
        group[evidence] = group.get(evidence, 0) + 1
        result.append({"id": task["id"], "department": task["department"], "status": task["status"], "evidence": evidence,
                       "wave": waves.get(task["id"]), "reasons": reasons})
    states = {}
    for value in disk.values():
        states[value] = states.get(value, 0) + 1
    return {"version": 1, "sourceRevision": state["revision"], "whatIf": hypothetical,
            "attention": any(evidence in ATTENTION for evidence, _ in entries.values()),
            "summary": {"accepted": {key: counts["accepted"][key] for key in ORDER if key in counts["accepted"]},
                        "open": {key: counts["open"][key] for key in ORDER if key in counts["open"]},
                        "paths": {"tracked": len(chains), **{key: states[key] for key in sorted(states)}}},
            "waves": plan, "tasks": result,
            "paths": [{"path": path, "owner": owner[path][1], "acceptedRevision": owner[path][0], "versions": len(chains[path]), "disk": disk[path]}
                      for path in sorted(chains) if disk[path] != "current" or len(chains[path]) > 1],
            "limits": LIMITS}


def brief(report, maximum=24):
    """A bounded view for the resume prompt: affected work only, with omissions counted."""
    affected = [task for task in report["tasks"] if task["evidence"] in AFFECTED]
    return {"sourceRevision": report["sourceRevision"], "attention": report["attention"], "summary": report["summary"],
            "recertifyFirst": report["waves"][0] if report["waves"] else [],
            "affected": [{**task, "reasons": task["reasons"][:4]} for task in affected[:maximum]], "omitted": max(0, len(affected) - maximum)}


def explain(reason):
    if reason["change"] == "superseded" and reason["role"] == "output":
        return reason["path"] + " now comes from " + reason["by"]
    if reason["change"] == "superseded":
        return "consumed " + reason["path"] + " from " + reason["from"] + "; " + reason["by"] + " has since had a different version accepted"
    subject = reason["path"] + (" from " + reason["from"] if "from" in reason else "")
    detail = {"changed": "differs from its accepted version in the project files", "missing": "is missing from the project files",
              "unreadable": "cannot be read safely", "pending": "has an unreviewed submission" + (" in " + reason["by"] if "by" in reason else ""),
              "what-if": "would change"}[reason["change"]]
    return subject + " " + detail


def render(report):
    tasks = {task["id"]: task for task in report["tasks"]}

    def line(task):
        return "- " + task["id"] + " [" + task["department"] + ", " + task["status"] + "] " + task["evidence"] + ": " + "; ".join(explain(reason) for reason in task["reasons"][:4]) \
            + (" (and " + str(len(task["reasons"]) - 4) + " more)" if len(task["reasons"]) > 4 else "")

    title = "Evidence freshness at revision " + str(report["sourceRevision"])
    if report["whatIf"]:
        title = "What if " + ", ".join(report["whatIf"]) + " changed? Hypothetical view at revision " + str(report["sourceRevision"])
    lines = ["# " + title, ""]
    accepted, open_work = report["summary"]["accepted"], report["summary"]["open"]
    lines += ["Accepted work: " + (", ".join(str(count) + " " + key for key, count in accepted.items()) or "none"),
              "Open work: " + (", ".join(str(count) + " " + key for key, count in open_work.items()) or "none"), ""]
    for number, wave in enumerate(report["waves"], 1):
        direct = [tasks[task_id] for task_id in wave if tasks[task_id]["evidence"] != "conditional"]
        waiting = [task_id for task_id in wave if tasks[task_id]["evidence"] == "conditional"]
        heading = "Wave " + str(number) + (" (directly affected)" if number == 1 else "") if report["whatIf"] else "Recertify first" if number == 1 else "Wave " + str(number)
        lines += ["## " + heading, ""] + [line(task) for task in direct]
        if waiting:
            lines.append("- Recheck only if an upstream recertification changes a file: " + ", ".join(waiting))
        lines.append("")
    active = [task for task in report["tasks"] if task["status"] != "done" and task["evidence"] in AFFECTED]
    if active:
        lines += ["## Open work on affected inputs", ""] + [line(task) if task["reasons"] else "- " + task["id"] + " [" + task["department"] + ", " + task["status"] + "] conditional: an upstream producer is affected" for task in active] + [""]
    drifted = [path for path in report["paths"] if path["disk"] not in ("current", "what-if")]
    if drifted:
        lines += ["## Project files that differ from accepted evidence", ""] + ["- " + path["path"] + " (accepted from " + path["owner"] + " at revision " + str(path["acceptedRevision"]) + "): " + path["disk"] for path in drifted] + [""]
    if not report["waves"] and not active and not drifted:
        lines += ["Every accepted task still matches the latest accepted versions and the project files it declares.", ""]
    lines += ["Recertify with a new task that depends on the current producers and submits the affected path; an unchanged file keeps downstream work fresh.",
              report["limits"]]
    return "\n".join(lines) + "\n"
