"""X1 (C5): the command's interface: request fields, answer shape, exit statuses, refusals."""

import json
import os
import subprocess
import sys

from _cmd import PATH, finish


def run_raw(text):
    """Returns (exit status, raw stdout, raw stderr)."""
    if not os.access(PATH, os.X_OK):
        sys.exit("the workspace has no executable named slots")
    try:
        done = subprocess.run([PATH], input=text, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        return 124, "", ""
    return done.returncode, done.stdout, done.stderr


problems = []
answered = []


def answer(text, label):
    """Check one valid request's answer shape; return its slots or None."""
    answered.append(label)
    status, out, _ = run_raw(text)
    if status != 0:
        problems.append(f"{label}: exited with status {status}, expected 0")
        return None
    try:
        body = json.loads(out)
    except json.JSONDecodeError:
        problems.append(f"{label}: standard output is not one JSON value: {out[:80]!r}")
        return None
    if not isinstance(body, dict) or set(body) != {"slots"}:
        problems.append(f"{label}: expected an object whose only field is slots, got {str(body)[:80]}")
        return None
    slots = body["slots"]
    if not isinstance(slots, list) or not all(
        isinstance(slot, list) and len(slot) == 2 and all(type(t) is int for t in slot) for slot in slots
    ):
        problems.append(f"{label}: slots must be a list of [start, end] pairs of whole numbers, got {str(slots)[:80]}")
        return None
    return slots


# Answers have exactly one field, slots, holding [start, end] pairs of whole numbers,
# including when the list is likely empty or likely holds the whole day. Which slots are
# right is for the other checks; this one looks only at the form of the answer.
BASE = {"workday": [600, 1080], "min_length": 20, "quorum": 2, "busy": [[[660, 700]], [[690, 750], [900, 915]], [[720, 800]]]}
SHAPES = [
    ("a request with free slots", BASE),
    ("a request with no long-enough slot", {"workday": [600, 1080], "min_length": 400, "quorum": 1, "busy": [[[700, 760]]]}),
    ("a request with the whole day free", {"workday": [0, 1440], "min_length": 1440, "quorum": 2, "busy": [[], []]}),
    ("a request with the day fully booked", {"workday": [300, 500], "min_length": 1, "quorum": 1, "busy": [[[250, 550]]]}),
    ("a request with a quorum of one", {"workday": [300, 500], "min_length": 1, "quorum": 1, "busy": [[[250, 550]], [[350, 420]]]}),
]
base_slots = None
for label, request in SHAPES:
    got = answer(json.dumps(request), label)
    if request is BASE:
        base_slots = got

# Other request fields are ignored, even ones named like the answer or like real fields.
EXTRA = dict(BASE)
EXTRA.update({
    "room": "Harbour",
    "slots": [[0, 1440]],
    "timezone": "UTC",
    "notes": None,
    "attendees": ["ana", "bo"],
    "min_len": 999,
    "Quorum": 1,
    "workdays": [[0, 10]],
    "options": {"min_length": 500, "busy": []},
})
if base_slots is not None:
    got = answer(json.dumps(EXTRA), "a request with nine extra fields")
    if got is not None and got != base_slots:
        problems.append(f"extra fields changed the answer: {got} instead of {base_slots}")

    # Layout of the JSON text and the order of its fields do not matter.
    reordered = {"busy": BASE["busy"], "quorum": BASE["quorum"], "min_length": BASE["min_length"], "workday": BASE["workday"]}
    for label, text in [
        ("pretty-printed request", json.dumps(BASE, indent=4)),
        ("reordered fields", json.dumps(reordered)),
        ("surrounding blank lines", "\n\n  " + json.dumps(BASE) + "  \n\n"),
        ("compact JSON (no extra whitespace)", json.dumps(BASE, separators=(",", ":"))),
        ("a trailing newline", json.dumps(BASE) + "\n"),
    ]:
        got = answer(text, label)
        if got is not None and got != base_slots:
            problems.append(f"{label}: got {got} instead of {base_slots}")

# A refused request exits 2, writes nothing at all to standard output and gives a reason on
# standard error. Whether a request is refused at all is C4 (X11): an invalid request that
# gets an answer is not judged here.
REFUSED = [
    ("text that isn't JSON", "free slots please"),
    ("a JSON list", json.dumps([BASE])),
    ("no min_length", json.dumps({"workday": [600, 1080], "quorum": 1, "busy": [[]]})),
    ("no busy", json.dumps({"workday": [600, 1080], "min_length": 20, "quorum": 1})),
    ("no quorum", json.dumps({"workday": [600, 1080], "min_length": 20, "busy": [[]]})),
    ("a reversed busy interval", json.dumps({"workday": [600, 1080], "min_length": 20, "quorum": 1, "busy": [[[760, 700]]]})),
    ("min_length 0", json.dumps({"workday": [600, 1080], "min_length": 0, "quorum": 1, "busy": [[]]})),
    ("a workday past 1440", json.dumps({"workday": [600, 1500], "min_length": 20, "quorum": 1, "busy": [[]]})),
    ("a quorum of three for two people", json.dumps({"workday": [600, 1080], "min_length": 20, "quorum": 3, "busy": [[], []]})),
]
refused = 0
for label, text in REFUSED:
    status, out, err = run_raw(text)
    if status == 0:
        try:
            answered_anyway = isinstance(json.loads(out), dict)
        except json.JSONDecodeError:
            answered_anyway = False
        if answered_anyway:
            continue
    refused += 1
    if status != 2:
        problems.append(f"refusal, {label}: exited with status {status}, expected 2")
    if out != "":
        problems.append(f"refusal, {label}: wrote {out[:60]!r} to standard output, expected nothing")
    if not err.strip():
        problems.append(f"refusal, {label}: gave no reason on standard error")

finish(problems, f"interface ok: {len(answered)} answers and {refused} refusals")
