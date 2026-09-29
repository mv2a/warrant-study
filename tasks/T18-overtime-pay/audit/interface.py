"""X: the interface of `pay` (C2).

Valid weeks get exit status 0 and one JSON object with exactly the seven integer fields,
whose minute fields add up to the week's worked minutes. Extra request fields, key order
and whitespace do not change the answer. A refused request exits 2 and writes nothing at
all on standard output.
"""

import json
import subprocess

from _cmd import PATH, call, finish
from _expect import FIELDS, MINUTE_FIELDS

problems = []

VALID = [
    ([0, 0, 0, 0, 0, 0, 0], 100000),
    ([1440, 0, 0, 0, 0, 0, 0], 1),
    ([15, 1440, 0, 725, 1, 0, 999], 4321),
    ([1, 1, 1, 1, 1, 1, 1], 1),
    ([481, 661, 479, 1, 0, 1439, 3], 99999),
    ([1440, 1440, 1440, 1440, 1440, 1440, 1440], 100000),
    ([333, 555, 777, 999, 111, 222, 444], 2718),
    ([0, 0, 0, 0, 0, 0, 1440], 7),
]


def shape_problem(body, worked):
    if not isinstance(body, dict):
        return f"expected one JSON object, got {body!r}"
    if set(body) != set(FIELDS):
        return f"expected exactly the fields {sorted(FIELDS)}, got {sorted(body)}"
    wrong = [field for field in FIELDS if type(body[field]) is not int]
    if wrong:
        return f"fields {wrong} are not integers in {body!r}"
    if sum(body[field] for field in MINUTE_FIELDS) != worked:
        return f"the minute fields must add up to {worked}, got {body!r}"
    return None


answers = {}
for minutes, rate in VALID:
    request = {"minutes": minutes, "rate_cents": rate}
    status, body = call(request)
    problem = "exited with status %s, expected 0" % status if status != 0 else shape_problem(body, sum(minutes))
    if problem:
        problems.append(f"{request}: {problem}")
    else:
        answers[(tuple(minutes), rate)] = body

# Other fields are ignored, whatever their names and values.
EXTRAS = [
    {"employee": "A-17", "week": 39},
    {"total_cents": 1, "regular_minutes": 5000, "overtime_minutes": -3, "double_cents": "x"},
    {"Minutes": "not a list", "RATE_CENTS": -1, "rate": 0, "minute": [1], "rateCents": 1.5},
    {"notes": None, "flags": [True, False], "meta": {"minutes": [0, 0, 0, 0, 0, 0, 0], "rate_cents": 0}},
    {"note": "café ✓ overtime", "history": list(range(300))},
    {"seventh_day": True, "consecutive": 7, "holiday": [1, 2, 3], "multiplier": 3},
]
for index, extra in enumerate(EXTRAS):
    minutes, rate = VALID[(index * 5 + 2) % len(VALID)]
    base = answers.get((tuple(minutes), rate))
    if base is None:
        continue
    request = dict(extra)
    request.update({"minutes": minutes, "rate_cents": rate})
    status, body = call(request)
    if status != 0 or body != base:
        problems.append(f"extra fields {sorted(extra)} changed the answer for {minutes} at {rate}: "
                        f"got {body!r} (status {status}), expected {base!r}")

# Key order, indentation and surrounding whitespace do not matter either.
for minutes, rate in VALID[2:6]:
    base = answers.get((tuple(minutes), rate))
    if base is None:
        continue
    reversed_keys = {"rate_cents": rate, "minutes": minutes}
    for raw in (json.dumps(reversed_keys, indent=2) + "\n",
                "\n  \t" + json.dumps({"minutes": minutes, "rate_cents": rate}, separators=(",", ":")) + "\n\n"):
        status, body = call(raw=raw)
        if status != 0 or body != base:
            problems.append(f"reformatted request {raw!r} got {body!r} (status {status}), expected {base!r}")

# A refused request exits 2 and writes nothing at all on standard output.
REFUSED = [
    "this is not json",
    "{}",
    json.dumps({"minutes": [480, 480], "rate_cents": 1500}),
    json.dumps({"minutes": [480, 0, 0, 0, 0, 0, 0], "rate_cents": 0.5}),
    json.dumps({"minutes": [480, 0, 0, 0, 0, 0, 1441], "rate_cents": 1500}),
    json.dumps([480, 0, 0, 0, 0, 0, 0]),
]
for raw in REFUSED:
    try:
        done = subprocess.run([PATH], input=raw, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        problems.append(f"{raw!r}: timed out")
        continue
    if done.returncode != 2 or done.stdout != "":
        problems.append(f"{raw!r} must exit 2 with nothing on standard output, "
                        f"got status {done.returncode} and {done.stdout[:80]!r}")

finish(problems, f"interface ok: {len(VALID)} weeks, {len(EXTRAS)} with extra fields, "
                 f"8 reformatted, {len(REFUSED)} refused")
