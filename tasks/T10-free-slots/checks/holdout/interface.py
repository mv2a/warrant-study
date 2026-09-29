"""H8 (C5): the slots command reads one JSON object and writes one, with the stated fields and exit statuses."""

import json
import os
import random
import subprocess

from _cmd import PATH, call, finish
from _oracle import random_request

problems = []
cases = 0


def shape_problem(body):
    if not isinstance(body, dict) or set(body) != {"slots"}:
        return f"expected an object whose only field is slots, got {body!r}"
    slots = body["slots"]
    if not isinstance(slots, list):
        return f"slots must be a list, got {slots!r}"
    for slot in slots:
        if not (isinstance(slot, list) and len(slot) == 2 and all(type(t) is int for t in slot)):
            return f"each slot must be a [start, end] pair of whole numbers, got {slot!r}"
    return None


# Valid requests: exit status 0 and exactly one field, slots, holding [start, end] pairs of whole numbers.
rng = random.Random(8080)
requests = [
    {"workday": [540, 1020], "min_length": 30, "quorum": 1, "busy": [[[600, 660]]]},
    {"workday": [540, 1020], "min_length": 600, "quorum": 1, "busy": [[]]},
    {"workday": [0, 1440], "min_length": 1, "quorum": 1, "busy": [[[0, 1440]]]},
    {"workday": [540, 1020], "min_length": 30, "quorum": 2, "busy": [[[600, 660]], [[630, 700]], []]},
] + [random_request(rng) for _ in range(24)]
for request in requests:
    status, body = call(request)
    cases += 1
    problem = "exited with status %s, expected 0" % status if status != 0 else shape_problem(body)
    if problem:
        problems.append(f"{json.dumps(request)[:80]}: {problem}")

# Other fields are ignored, and the order of the fields does not matter.
base = {"workday": [540, 1020], "min_length": 30, "quorum": 2, "busy": [[[600, 660]], [[630, 700]]]}
expected = [[540, 600], [700, 1020]]
for label, raw in [
    ("extra fields", json.dumps({**base, "room": "blue", "timezone": "UTC", "slots": [[0, 1]], "attendees": 7})),
    ("fields in another order", json.dumps({"busy": base["busy"], "quorum": 2, "min_length": 30, "workday": [540, 1020]})),
    ("pretty-printed input", json.dumps(base, indent=2)),
]:
    status, body = call(raw=raw)
    cases += 1
    if status != 0 or body != {"slots": expected}:
        problems.append(f"{label}: expected {{'slots': {expected}}}, got {body!r} (status {status})")

# Refusals: exit status 2, nothing on standard output, a reason on standard error.
for label, raw in [
    ("not JSON", "tuesday"),
    ("a missing field", json.dumps({"workday": [540, 1020], "quorum": 1, "busy": [[]]})),
    ("a reversed interval", json.dumps({"workday": [540, 1020], "min_length": 30, "quorum": 1, "busy": [[[700, 600]]]})),
    ("a min_length of zero", json.dumps({"workday": [540, 1020], "min_length": 0, "quorum": 1, "busy": [[]]})),
    ("a quorum larger than the group", json.dumps({"workday": [540, 1020], "min_length": 30, "quorum": 3, "busy": [[], []]})),
]:
    cases += 1
    if not os.access(PATH, os.X_OK):
        problems.append("the workspace has no executable named slots")
        break
    try:
        done = subprocess.run([PATH], input=raw, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        problems.append(f"{label}: timed out")
        continue
    if done.returncode != 2:
        problems.append(f"{label}: a refusal must exit with status 2, got {done.returncode}")
    if done.stdout.strip():
        problems.append(f"{label}: a refusal must write nothing to standard output, got {done.stdout.strip()[:60]!r}")
    if not done.stderr.strip():
        problems.append(f"{label}: a refusal must give a reason on standard error")

finish(problems, f"interface ok: {cases} requests")
