"""Bounded business review policies and derived loop guidance; no execution adapter."""

import copy
import hashlib
import json
import re
import unicodedata

PROFILE_PATH = "skills/chief-of-staff/references/harness-profiles.json"
INPUT_MAX_BYTES = 256 * 1024
STAGES = ("discover", "build", "launch", "operate")
EFFORTS = {"light": 2, "balanced": 3, "deep": 5}
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


class HarnessError(ValueError):
    pass


def fail(message):
    raise HarnessError(message)


def keys(value, names, label):
    if not isinstance(value, dict) or set(value) != set(names.split()):
        fail("invalid " + label + " fields")


def text(value, label="harness text", maximum=8000, empty=False):
    if not isinstance(value, str) or (not empty and not value.strip()):
        fail(label + " must be non-empty text")
    try:
        if len(value.encode("utf-8")) > maximum:
            fail(label + " exceeds its UTF-8 byte limit")
    except UnicodeError:
        fail(label + " must be valid UTF-8")
    if any(unicodedata.category(c) == "Cc" and c not in "\t\r\n" for c in value):
        fail(label + " contains unsupported controls")
    return value


def sequence(value, maximum, label):
    if not isinstance(value, list) or len(value) > maximum:
        fail("invalid or oversized " + label)
    return value


def integer(value, low, high, label):
    if type(value) is not int or not low <= value <= high:
        fail("invalid " + label)
    return value


def digest(value):
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        fail("invalid harness fingerprint")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail("duplicate harness JSON field")
        result[key] = value
    return result


def read_json(path, read_regular):
    try:
        return json.loads(read_regular(path, INPUT_MAX_BYTES).decode("utf-8"), object_pairs_hook=unique_object,
                          parse_constant=lambda _: fail("non-finite harness JSON number"))
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        fail("harness input must be bounded valid UTF-8 JSON")


def canonical(value):
    def check(item):
        if item is None or type(item) is bool:
            return
        if type(item) is int:
            integer(item, -(2 ** 53 - 1), 2 ** 53 - 1, "canonical integer")
        elif isinstance(item, str):
            text(item, empty=True)
        elif isinstance(item, list):
            for child in item:
                check(child)
        elif isinstance(item, dict):
            for key, child in item.items():
                if not isinstance(key, str) or not key.isascii():
                    fail("canonical object keys must be ASCII")
                check(child)
        else:
            fail("canonical JSON does not support this value")
    check(value)
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)


def fingerprint(domain, payload):
    return hashlib.sha256(("claude-inc/harness-" + domain + "/v1\n" + canonical(payload)).encode("ascii")).hexdigest()


def policy_payload(task, policy):
    return {"task": {key: task[key] for key in ("id", "department", "title", "acceptance", "dependsOn")},
            **{key: policy[key] for key in ("stage", "effort", "skills", "gates")}}


def artifact_fingerprint(artifacts):
    # Python's Unicode codepoint ordering is the public cross-language contract.
    return fingerprint("artifacts", sorted(artifacts, key=lambda item: item["path"]))


def profiles(root, departments, read_regular):
    path = root / PROFILE_PATH
    raw = read_regular(path, INPUT_MAX_BYTES)
    try:
        document = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        fail("invalid packaged harness profiles")
    keys(document, "version profiles", "profile document")
    integer(document["version"], 1, 1, "profile version")
    if not isinstance(document["profiles"], dict) or set(document["profiles"]) != set(departments):
        fail("profile departments do not match the canonical roster")
    result = {}
    for department, profile in document["profiles"].items():
        keys(profile, "checks", "packaged profile")
        result[department] = {"source": {"path": PROFILE_PATH, "sha256": hashlib.sha256(raw).hexdigest()},
                              "checks": copy.deepcopy(profile["checks"])}
    validate_profiles(result, departments)
    return result


def validate_profiles(value, departments):
    if not isinstance(value, dict) or set(value) != set(departments):
        fail("invalid harness profile departments")
    criteria = set()
    hashes = set()
    for profile in value.values():
        keys(profile, "source checks", "profile snapshot")
        keys(profile["source"], "path sha256", "profile source")
        if profile["source"]["path"] != PROFILE_PATH:
            fail("unknown packaged profile source")
        digest(profile["source"]["sha256"])
        hashes.add(profile["source"]["sha256"])
        if len(sequence(profile["checks"], 2, "business checks")) != 2:
            fail("each business profile requires two checks")
        ids = set()
        for check in profile["checks"]:
            keys(check, "id criterion", "business check")
            if not isinstance(check["id"], str) or not SLUG.fullmatch(check["id"]) or len(check["id"]) > 80 or check["id"] in ids:
                fail("invalid or duplicate business check id")
            ids.add(check["id"])
            text(check["criterion"], "business criterion", 2000)
            if check["criterion"] in criteria:
                fail("business criteria must be distinct")
            criteria.add(check["criterion"])
    if len(hashes) != 1:
        fail("profile source snapshots disagree")


def defaults(stage=None, effort=None, maximum=None, existing=None):
    old = existing or {"stage": "build", "effort": "balanced", "maxIterations": 3}
    stage = old["stage"] if stage is None else stage
    effort = old["effort"] if effort is None else effort
    if stage not in STAGES or effort not in EFFORTS:
        fail("unknown harness stage or effort")
    limit = (old["maxIterations"] if existing or effort == old["effort"] else EFFORTS[effort]) if maximum is None else maximum
    return {"stage": stage, "effort": effort, "maxIterations": integer(limit, 1, 10, "iteration limit")}


def semantic(value, department, departments, staff):
    if value is None:
        return {"skills": [], "criteria": []}
    keys(value, "version skills criteria", "semantic task plan")
    integer(value["version"], 1, 1, "semantic plan version")
    skills = sequence(value["skills"], 32, "selected skills")
    allowed = set(departments[department]) | set(staff)
    for skill in skills:
        if not isinstance(skill, str) or skill not in allowed:
            fail("selected skill does not belong to the task department or executive staff")
    if len(set(skills)) != len(skills):
        fail("duplicate selected skill")
    for criterion in sequence(value["criteria"], 5, "project criteria"):
        text(criterion, "project criterion", 2000)
    if len(set(value["criteria"])) != len(value["criteria"]):
        fail("duplicate project criterion")
    return {"skills": list(skills), "criteria": list(value["criteria"])}


def make_policy(task, harness, revision, selection, departments, staff):
    selection = semantic(selection, task["department"], departments, staff)
    gates = [{"id": "contract", "criterion": task["acceptance"], "source": "contract", "required": True}]
    gates += [{"id": "business-" + check["id"], "criterion": check["criterion"], "source": "profile", "required": True}
              for check in harness["profiles"][task["department"]]["checks"]]
    gates += [{"id": "project-" + str(index), "criterion": criterion, "source": "project", "required": True}
              for index, criterion in enumerate(selection["criteria"], 1)]
    policy = {"createdRevision": revision, "stage": harness["defaults"]["stage"], "effort": harness["defaults"]["effort"],
              "skills": selection["skills"], "gates": gates}
    policy["fingerprint"] = fingerprint("policy", policy_payload(task, policy))
    return policy


def plan_selections(plan, allowed, tasks, departments, staff):
    if plan is None:
        return {}
    keys(plan, "version tasks", "harness plan")
    integer(plan["version"], 1, 1, "harness plan version")
    if not isinstance(plan["tasks"], dict) or not set(plan["tasks"]).issubset(allowed):
        fail("harness plan references an ineligible task")
    for task_id, selection in plan["tasks"].items():
        keys(selection, "skills criteria", "task selection")
        semantic({"version": 1, **selection}, tasks[task_id]["department"], departments, staff)
    return {task_id: {"version": 1, **selection} for task_id, selection in plan["tasks"].items()}


def generate(state, revision, root, departments, staff, read_regular, stage=None, effort=None, maximum=None, plan=None):
    tasks = {task["id"]: task for task in state["tasks"]}
    if state["schemaVersion"] == 2:
        h = state["harness"]
        config = defaults(stage, effort, maximum, h["defaults"])
        allowed = {task_id for task_id, policy in h["policies"].items() if policy["createdRevision"] == h["enabledRevision"]}
        selections = plan_selections(plan, allowed, tasks, departments, staff)
        if config != h["defaults"]:
            fail("harness defaults are immutable; an existing harness cannot be regenerated with different settings")
        if plan is not None:
            for task_id in allowed:
                if make_policy(tasks[task_id], h, h["enabledRevision"], selections.get(task_id), departments, staff) != h["policies"][task_id]:
                    fail("harness policies are immutable; regenerate cannot replace task gates")
        return False
    h = {"version": 1, "enabledRevision": revision, "defaults": defaults(stage, effort, maximum),
         "profiles": profiles(root, departments, read_regular), "policies": {}, "rounds": [], "assessments": [], "extensions": []}
    eligible = {task_id for task_id, task in tasks.items() if task["status"] != "done"}
    if any(used_limit(state, task_id)[0] >= 10 for task_id in eligible):
        fail("unfinished task already has ten lifetime submissions; finish its existing schema-1 work before enabling the harness. History cannot be reset")
    selections = plan_selections(plan, eligible, tasks, departments, staff)
    for task_id in tasks:
        if task_id in eligible:
            h["policies"][task_id] = make_policy(tasks[task_id], h, revision, selections.get(task_id), departments, staff)
    state["schemaVersion"], state["harness"] = 2, h
    return True


def used_limit(state, task_id, before_revision=None):
    boundary = state["revision"] + 1 if before_revision is None else before_revision
    used = sum(event["type"] == "task.submit" and event["taskId"] == task_id and event["revision"] < boundary for event in state["events"])
    limit = None
    if state["schemaVersion"] == 2 and task_id in state["harness"]["policies"]:
        limit = state["harness"]["defaults"]["maxIterations"]
        for extension in state["harness"]["extensions"]:
            if extension["taskId"] == task_id and extension["revision"] < boundary:
                limit = extension["toLimit"]
    return used, limit


def require_available(state, task_id):
    used, limit = used_limit(state, task_id)
    if limit is not None and used >= limit:
        fail("task submission allowance exhausted; escalate and record an explicit extension before further work")


def current_submission(state, task_id, before_revision=None):
    boundary = state["revision"] + 1 if before_revision is None else before_revision
    return max((event["revision"] for event in state["events"] if event["taskId"] == task_id and event["type"] == "task.submit" and event["revision"] < boundary), default=0)


def latest_round(state, task_id, before_revision=None):
    submission = current_submission(state, task_id, before_revision)
    return next((item for item in state["harness"]["rounds"] if item["taskId"] == task_id and item["submitRevision"] == submission), None)


def validate_results(results, policy, artifacts):
    sequence(results, 8, "gate results")
    expected = {gate["id"] for gate in policy["gates"]}
    seen = set()
    paths = {item["path"] for item in artifacts}
    for result in results:
        keys(result, "gateId status evidence observation", "gate result")
        gate_id, status = result["gateId"], result["status"]
        if not isinstance(gate_id, str) or gate_id not in expected or gate_id in seen or status not in ("pass", "fail", "unknown"):
            fail("gate results must name each required gate exactly once with pass, fail or unknown")
        seen.add(gate_id)
        for evidence in sequence(result["evidence"], 16, "gate evidence"):
            keys(evidence, "path locator", "gate evidence")
            if not isinstance(evidence["path"], str) or evidence["path"] not in paths:
                fail("gate evidence must reference an artifact in this submitted round")
            text(evidence["locator"], "evidence locator", 1000)
        text(result["observation"], "gate observation", empty=status != "pass")
        if status == "pass" and not result["evidence"]:
            fail("a passed gate requires recorded artifact evidence and an observation")
    if seen != expected:
        fail("gate results must cover all required gates exactly once")


def record_review(state, task, revision, decision, submission_revision, gate_file):
    policy = state["harness"]["policies"].get(task["id"])
    if policy is None:
        return
    current = current_submission(state, task["id"])
    if type(submission_revision) is not int or submission_revision != current:
        fail("review requires the current --submission-revision")
    round_value = latest_round(state, task["id"])
    if round_value is None:
        if decision == "accept" or gate_file is not None:
            fail("pre-harness submission must be revised and freshly submitted before gated review")
        return
    if gate_file is None:
        if decision == "accept":
            fail("accepting a harness task requires --gates-file with all required gates passed")
        return
    keys(gate_file, "version taskId submitRevision policyFingerprint artifactFingerprint results", "gate assessment file")
    integer(gate_file["version"], 1, 1, "assessment file version")
    if (gate_file["taskId"] != task["id"] or type(gate_file["submitRevision"]) is not int or gate_file["submitRevision"] != current
            or gate_file["policyFingerprint"] != policy["fingerprint"] or gate_file["artifactFingerprint"] != artifact_fingerprint(round_value["artifacts"])):
        fail("assessment targets a stale submission, policy or artifact fingerprint")
    validate_results(gate_file["results"], policy, round_value["artifacts"])
    if decision == "accept" and any(result["status"] != "pass" for result in gate_file["results"]):
        fail("all required gates must pass before acceptance; fail or unknown requires revision")
    state["harness"]["assessments"].append({"taskId": task["id"], "reviewRevision": revision, "submitRevision": current,
        "policyFingerprint": policy["fingerprint"], "artifactFingerprint": gate_file["artifactFingerprint"], "results": copy.deepcopy(gate_file["results"])})


def extend(state, task_id, revision, maximum, reason):
    if state["schemaVersion"] != 2 or task_id not in state["harness"]["policies"]:
        fail("an extension requires an enrolled harness task")
    if next(task for task in state["tasks"] if task["id"] == task_id)["status"] == "done":
        fail("completed tasks have no remaining work to extend")
    _, old = used_limit(state, task_id)
    integer(maximum, old + 1, 10, "strictly increasing iteration limit")
    text(reason, "extension reason")
    state["harness"]["extensions"].append({"taskId": task_id, "revision": revision, "fromLimit": old, "toLimit": maximum, "reason": reason})


def validate(state, departments, staff, artifact_records):
    h = state["harness"]
    keys(h, "version enabledRevision defaults profiles policies rounds assessments extensions", "harness")
    integer(h["version"], 1, 1, "harness version")
    enabled = integer(h["enabledRevision"], 2, state["revision"], "harness enabled revision")
    keys(h["defaults"], "stage effort maxIterations", "harness defaults")
    if defaults(h["defaults"]["stage"], h["defaults"]["effort"], h["defaults"]["maxIterations"]) != h["defaults"]:
        fail("invalid harness defaults")
    validate_profiles(h["profiles"], departments)
    events = state["events"]
    generated = [e for e in events if e["type"] == "harness.generate"]
    if len(generated) != 1 or generated[0]["revision"] != enabled or generated[0]["taskId"] is not None:
        fail("harness activation does not match event history")
    tasks = {task["id"]: task for task in state["tasks"]}
    add_revisions = {e["taskId"]: e["revision"] for e in events if e["type"] == "task.add"}
    old_done = {e["taskId"] for e in events if e["type"] == "task.accept" and e["revision"] < enabled}
    if any(review["reviewer"] == "cto" and review["revision"] < enabled for task in tasks.values() for review in task["reviews"]):
        fail("CTO review cannot predate schema-2 activation")
    legacy_submissions = {task_id: sum(event["type"] == "task.submit" and event["taskId"] == task_id and event["revision"] < enabled for event in events)
                          for task_id in tasks}
    if any(count >= 10 and task_id not in old_done for task_id, count in legacy_submissions.items()):
        fail("harness activation cannot enroll an unfinished task with ten lifetime submissions")
    eligible = set(tasks) - old_done
    if not isinstance(h["policies"], dict) or set(h["policies"]) != eligible:
        fail("harness policies must enroll every unfinished or new task, excluding historical acceptance")
    for task_id, policy in h["policies"].items():
        keys(policy, "createdRevision stage effort skills gates fingerprint", "task policy")
        expected_revision = max(enabled, add_revisions[task_id])
        integer(policy["createdRevision"], expected_revision, expected_revision, "policy creation revision")
        gates = sequence(policy["gates"], 8, "policy gates")
        if len(gates) < 3:
            fail("policy cannot remove required baseline gates")
        for gate in gates:
            keys(gate, "id criterion source required", "gate")
            if gate["required"] is not True:
                fail("all policy gates are required")
            text(gate["criterion"], "gate criterion")
        selection = {"version": 1, "skills": policy["skills"], "criteria": [gate["criterion"] for gate in gates[3:]]}
        expected = make_policy(tasks[task_id], h, expected_revision, selection, departments, staff)
        if policy != expected:
            fail("policy baseline, selection or fingerprint is inconsistent")
    extension_events = [e for e in events if e["type"] == "harness.extend"]
    extensions = sequence(h["extensions"], 2048, "harness extensions")
    if len(extensions) != len(extension_events):
        fail("extensions do not match event history")
    limits = {task_id: h["defaults"]["maxIterations"] for task_id in eligible}
    for extension, event in zip(extensions, extension_events):
        keys(extension, "taskId revision fromLimit toLimit reason", "extension")
        task_id = extension["taskId"]
        if not isinstance(task_id, str) or task_id not in eligible or event["taskId"] != task_id or event["revision"] != extension["revision"] or extension["revision"] <= h["policies"][task_id]["createdRevision"]:
            fail("extension targets an invalid task or revision")
        if any(item["type"] == "task.accept" and item["taskId"] == task_id and item["revision"] < extension["revision"] for item in events):
            fail("extension cannot follow completed task acceptance")
        integer(extension["revision"], enabled + 1, state["revision"], "extension revision")
        integer(extension["fromLimit"], limits[task_id], limits[task_id], "prior iteration limit")
        integer(extension["toLimit"], limits[task_id] + 1, 10, "extended iteration limit")
        text(extension["reason"], "extension reason")
        if event["note"] != extension["reason"]:
            fail("extension reason differs from its event")
        limits[task_id] = extension["toLimit"]
    rounds = sequence(h["rounds"], 2048, "submission rounds")
    submissions = [e for e in events if e["type"] == "task.submit" and e["revision"] > enabled]
    if len(rounds) != len(submissions):
        fail("submission rounds must match post-activation submissions exactly")
    round_map = {}
    for round_value, event in zip(rounds, submissions):
        keys(round_value, "taskId submitRevision policyFingerprint artifacts", "submission round")
        task_id = round_value["taskId"]
        if not isinstance(task_id, str) or task_id not in eligible or event["taskId"] != task_id or type(round_value["submitRevision"]) is not int or event["revision"] != round_value["submitRevision"]:
            fail("submission round does not match its event")
        if round_value["policyFingerprint"] != h["policies"][task_id]["fingerprint"]:
            fail("submission policy fingerprint changed")
        artifact_records(round_value["artifacts"])
        if not round_value["artifacts"]:
            fail("submission round requires artifacts")
        round_map[event["revision"]] = round_value
    for task_id in eligible:
        current = latest_round(state, task_id)
        if current is not None and current["artifacts"] != tasks[task_id]["artifacts"]:
            fail("current task artifacts differ from its last submission round")
    assessments = sequence(h["assessments"], 2048, "assessments")
    assessment_map = {}
    previous = 0
    for assessment in assessments:
        keys(assessment, "taskId reviewRevision submitRevision policyFingerprint artifactFingerprint results", "assessment")
        revision = integer(assessment["reviewRevision"], previous + 1, state["revision"], "assessment revision")
        previous = revision
        task_id = assessment["taskId"]
        if not isinstance(task_id, str) or task_id not in eligible:
            fail("assessment targets an unknown policy task")
        event = events[revision - 1]
        submission = integer(assessment["submitRevision"], enabled + 1, revision - 1, "assessed submission revision")
        round_value = round_map.get(submission)
        if (event["taskId"] != task_id or event["type"] not in {"task.accept", "task.revise"}
                or current_submission(state, task_id, revision) != submission or round_value is None or round_value["taskId"] != task_id):
            fail("assessment is not attached to the current submission's review")
        policy = h["policies"][task_id]
        if assessment["policyFingerprint"] != policy["fingerprint"] or assessment["artifactFingerprint"] != artifact_fingerprint(round_value["artifacts"]):
            fail("assessment fingerprint differs from its policy or artifacts")
        validate_results(assessment["results"], policy, round_value["artifacts"])
        if event["type"] == "task.accept" and any(result["status"] != "pass" for result in assessment["results"]):
            fail("accepted task has an unresolved required gate")
        assessment_map[revision] = assessment
    for event in events:
        task_id, revision = event["taskId"], event["revision"]
        if revision <= enabled or task_id not in eligible:
            continue
        if event["type"] in {"task.start", "task.submit"}:
            used, limit = used_limit(state, task_id, revision)
            if used >= limit:
                fail("event history exceeds the task submission allowance")
        if event["type"] == "task.accept" and revision not in assessment_map:
            fail("harness acceptance requires a complete recorded gate assessment")


def next_action(state):
    tasks = state["tasks"]
    by_id = {task["id"]: task for task in tasks}
    policies = state.get("harness", {}).get("policies", {})
    blockers = {task["id"]: [dep for dep in task["dependsOn"] if by_id[dep]["status"] != "done"] for task in tasks}
    def downstream(task_id):
        found = set()
        for task in tasks:
            if task["status"] != "done" and (task_id in task["dependsOn"] or any(dep in found for dep in task["dependsOn"])):
                found.add(task["id"])
        return len(found)
    ranked = sorted(tasks, key=lambda task: -downstream(task["id"]))
    ready = [task["id"] for task in ranked if task["status"] == "planned" and not blockers[task["id"]]
             and (used_limit(state, task["id"])[1] is None or used_limit(state, task["id"])[0] < used_limit(state, task["id"])[1])]
    result = {"sourceRevision": state["revision"], "action": "waiting", "taskId": None, "phase": "waiting",
              "reason": "No eligible work: resolve recorded blockers or unaccepted dependencies.", "used": 0, "limit": None,
              "dependencyBlockers": [], "policyFingerprint": None, "readyIndependentIds": ready, "reviewTemplate": None}
    if state["schemaVersion"] == 1:
        result.update(action="plan", phase="planning", readyIndependentIds=[], reason="Harness is not enabled. Inspect the founder scope and enable it explicitly at the current revision before using harness loops.")
        return result
    if not tasks:
        result.update(action="plan", phase="planning", reason="Create real task contracts from the founder project; no tasks have been invented.")
        return result
    if all(task["status"] == "done" for task in tasks):
        result.update(action="complete", phase="complete", reason="All recorded tasks are accepted; this is historical review state, not proof of delivery or publication.")
        return result
    task = next((item for item in ranked if item["status"] == "review"), None)
    if task is not None:
        current = latest_round(state, task["id"]) if task["id"] in policies else None
        if task["id"] in policies and current is None:
            result.update(action="revise", phase="review", reason="This submission predates harness activation. Revise, then submit a fresh artifact round before acceptance.")
        else:
            result.update(action="evaluate", phase="review", reason="Inspect the submitted artifacts and every required criterion, then record an evidence-backed review.")
            if current:
                result["reviewTemplate"] = {"version": 1, "taskId": task["id"], "submitRevision": current["submitRevision"],
                    "policyFingerprint": policies[task["id"]]["fingerprint"], "artifactFingerprint": artifact_fingerprint(current["artifacts"]),
                    "results": [{"gateId": gate["id"], "status": "unknown", "evidence": [], "observation": ""} for gate in policies[task["id"]]["gates"]]}
    else:
        task = next((item for item in ranked if item["status"] == "active"), None)
        if task is not None:
            result.update(action="work", phase="execution", reason="Continue the active task against its fixed contract; submit actual artifact files when ready.")
        elif ready:
            task = by_id[ready[0]]
            result.update(action="start", phase="execution", reason="Dependencies are accepted; inspect their current artifacts before starting this task.")
        else:
            task = next((item for item in ranked if item["status"] != "done" and item["id"] in policies
                         and used_limit(state, item["id"])[0] >= used_limit(state, item["id"])[1]), None)
        if task is not None:
            used, limit = used_limit(state, task["id"])
            if limit is not None and used >= limit:
                result.update(action="escalate", phase="escalation", reason="The lifetime submission allowance is exhausted. Seek an explicit reasoned extension or stop this work.")
    if task is not None:
        task_id = task["id"]
        used, limit = used_limit(state, task_id)
        result.update(taskId=task_id, used=used, limit=limit, dependencyBlockers=blockers[task_id], policyFingerprint=policies.get(task_id, {}).get("fingerprint"))
    return result


def render_next(state):
    value = next_action(state)
    result = "Next: " + value["action"] + (" " + value["taskId"] if value["taskId"] else "") + "\n" + value["reason"] + "\n"
    policy = state.get("harness", {}).get("policies", {}).get(value["taskId"])
    if policy:
        result += "\nRequired criteria:\n" + "\n".join("- " + gate["id"] + ": " + gate["criterion"] for gate in policy["gates"]) + "\n"
    return result


def projection(state):
    view = next_action(state)
    task = next((task for task in state["tasks"] if task["id"] == view["taskId"]), None)
    current = None if task is None else {key: copy.deepcopy(value) for key, value in task.items() if key != "reviews"}
    if current is not None:
        current["lastReview"] = copy.deepcopy(task["reviews"][-1]) if task["reviews"] else None
    round_value = latest_round(state, task["id"]) if task is not None and task["id"] in state["harness"]["policies"] else None
    assessments = [item for item in state["harness"]["assessments"] if task is not None and item["taskId"] == task["id"]]
    return {"schemaVersion": 2, "sourceRevision": state["revision"],
            **{key: copy.deepcopy(state[key]) for key in ("name", "brief", "goals", "constraints", "activeDepartments", "departments", "decisions")},
            "board": [{key: copy.deepcopy(item[key]) for key in ("id", "department", "status", "dependsOn")} for item in state["tasks"]],
            "currentTask": current, "lastRound": copy.deepcopy(round_value),
            "lastAssessment": copy.deepcopy(assessments[-1]) if assessments else None,
            "dependencyEvidence": [{"taskId": dep["id"], "status": dep["status"], "artifacts": copy.deepcopy(dep["artifacts"])}
                                   for dep in state["tasks"] if task is not None and dep["id"] in task["dependsOn"]]}
