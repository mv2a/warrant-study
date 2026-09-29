"""H3: only groups with may_split true are split, only as a last resort, and they take the first free seats in seating order."""

import random

from _cmd import call, finish
from _theatre import first_free, random_request, replay, response_ok, split_name, together_block

problems = []

# Hand-made cases: (name, request, {group id: expected seats, or None when it must not be seated}).
CASES = [
    ("a splittable group that can sit together is not split",
     {"rows": [4, 4], "blocked": ["A2"], "groups": [{"id": "a", "size": 3, "may_split": True}]},
     {"a": ["B1", "B2", "B3"]}),
    ("a split takes the first free seats, row A first",
     {"rows": [3, 3, 3], "blocked": ["A2", "B2", "C2"], "groups": [{"id": "a", "size": 4, "may_split": True}]},
     {"a": ["A1", "A3", "B1", "B3"]}),
    ("a split takes seats in order, not the biggest gaps first",
     {"rows": [2, 5], "blocked": ["A2", "B3"], "groups": [{"id": "a", "size": 4, "may_split": True}]},
     {"a": ["A1", "B1", "B2", "B4"]}),
    ("a split across three rows",
     {"rows": [3, 3, 3], "groups": [{"id": "a", "size": 2}, {"id": "b", "size": 2}, {"id": "c", "size": 2},
                                    {"id": "d", "size": 3, "may_split": True}]},
     {"d": ["A3", "B3", "C3"]}),
    ("a split that uses the very last free seats",
     {"rows": [2, 2], "blocked": ["A1", "B2"], "groups": [{"id": "a", "size": 2, "may_split": True}]},
     {"a": ["A2", "B1"]}),
    ("a split skips blocked seats and seats sold earlier",
     {"rows": [5, 4], "blocked": ["A1", "B2"],
      "groups": [{"id": "a", "size": 3}, {"id": "b", "size": 3, "may_split": True}]},
     {"b": ["A5", "B1", "B3"]}),
    ("a group without may_split is never split",
     {"rows": [3, 3, 3], "blocked": ["A2", "B2", "C2"], "groups": [{"id": "a", "size": 4}]}, {"a": None}),
    ("a group with may_split false is never split",
     {"rows": [3, 3, 3], "blocked": ["A2", "B2", "C2"], "groups": [{"id": "a", "size": 4, "may_split": False}]},
     {"a": None}),
]
for label, request, expected in CASES:
    status, body = call(request)
    why = response_ok(status, body)
    if why:
        problems.append(f"{label}: {why}")
        continue
    got = {e.get("id"): e.get("seats") for e in body["seated"] if isinstance(e, dict)}
    for gid, seats in expected.items():
        if got.get(gid) != seats:
            problems.append(f"{label}: group {gid} expected {seats if seats else 'no seats'}, got {got.get(gid)!r}")


def one_block(seats):
    parts = [split_name(s) for s in seats]
    if None in parts or len({r for r, _ in parts}) != 1:
        return False
    numbers = [n for _, n in parts]
    return numbers == list(range(numbers[0], numbers[0] + len(numbers)))


# Generated cases: replay each response and check every group against G3.
rng = random.Random(19_0303)
split_seen = 0
for case in range(60):
    request = random_request(rng, max_rows=5, max_seats=10, max_groups=12, split_rate=0.5, blocked_rate=0.25, max_size=8)
    status, body = call(request)
    why = response_ok(status, body)
    if why:
        problems.append(f"case {case}: {why}")
        continue
    for group, free, (kind, value) in replay(request, body):
        size, may_split = group["size"], group.get("may_split") is True
        block = together_block(request["rows"], free, size)
        if kind == "seated" and not isinstance(value, list):
            problems.append(f"case {case}: group {group['id']} has unreadable seats {value!r}")
            break
        if kind == "seated" and not may_split and not one_block(value):
            problems.append(f"case {case}: group {group['id']} may not split but got {value}")
            break
        if kind == "seated" and block is not None and not one_block(value):
            problems.append(f"case {case}: group {group['id']} could sit together but was split: {value}")
            break
        if may_split and block is None and len(free) >= size:
            split_seen += 1
            want = first_free(request["rows"], free, size)
            if kind != "seated" or value != want:
                problems.append(f"case {case}: splittable group {group['id']} should get {want}, got {kind} {value!r}")
                break

if split_seen < 20:
    problems.append(f"only {split_seen} generated groups needed splitting; the generator should give at least 20")
finish(problems, f"splitting ok: {len(CASES)} hand-made cases, {split_seen} generated splits")
