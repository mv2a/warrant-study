"""H2: a group that can sit together gets the frontmost row with room and the lowest-numbered block in it."""

import random

from _cmd import call, finish
from _theatre import random_request, replay, response_ok, together_block

problems = []

# Hand-made cases: (name, request, {group id: expected seats}).
CASES = [
    ("the example in the intent", {"rows": [8], "blocked": ["A3", "A4"], "groups": [{"id": "a", "size": 3}]},
     {"a": ["A5", "A6", "A7"]}),
    ("a front row that is too short is passed over", {"rows": [3, 8, 8], "groups": [{"id": "a", "size": 4}]},
     {"a": ["B1", "B2", "B3", "B4"]}),
    ("the frontmost row wins over a row that fits more snugly",
     {"rows": [8, 3], "groups": [{"id": "a", "size": 3}, {"id": "b", "size": 3}]},
     {"a": ["A1", "A2", "A3"], "b": ["A4", "A5", "A6"]}),
    ("blocked seats break a block, and later groups go back to the front",
     {"rows": [6, 6], "blocked": ["A3"], "groups": [{"id": "g", "size": 4}, {"id": "h", "size": 3}, {"id": "i", "size": 2}]},
     {"g": ["B1", "B2", "B3", "B4"], "h": ["A4", "A5", "A6"], "i": ["A1", "A2"]}),
    ("a row with enough scattered seats is not a block",
     {"rows": [7, 4], "blocked": ["A2", "A4", "A6"], "groups": [{"id": "a", "size": 4}]},
     {"a": ["B1", "B2", "B3", "B4"]}),
    ("the lowest-numbered block wins within a row",
     {"rows": [10], "blocked": ["A4"], "groups": [{"id": "a", "size": 3}, {"id": "b", "size": 2}, {"id": "c", "size": 1}]},
     {"a": ["A1", "A2", "A3"], "b": ["A5", "A6"], "c": ["A7"]}),
    ("the lowest block that fits, not the first gap",
     {"rows": [9], "blocked": ["A3", "A6"], "groups": [{"id": "a", "size": 3}]},
     {"a": ["A7", "A8", "A9"]}),
    ("a group of one takes the first free seat",
     {"rows": [3, 3], "blocked": ["A1"], "groups": [{"id": "a", "size": 1}]}, {"a": ["A2"]}),
    ("a group exactly as wide as a row fills it",
     {"rows": [4, 4], "groups": [{"id": "a", "size": 4}, {"id": "b", "size": 4}]},
     {"a": ["A1", "A2", "A3", "A4"], "b": ["B1", "B2", "B3", "B4"]}),
    ("a full 50-seat row",
     {"rows": [50], "groups": [{"id": "a", "size": 50}]}, {"a": [f"A{n}" for n in range(1, 51)]}),
    ("a splittable group still sits together when it can",
     {"rows": [5, 5], "blocked": ["A2"], "groups": [{"id": "a", "size": 3, "may_split": True}]},
     {"a": ["A3", "A4", "A5"]}),
    ("rows further back are used when all front rows are too full",
     {"rows": [4, 4, 4, 4], "blocked": ["A2", "B3", "C2"], "groups": [{"id": "a", "size": 3}]},
     {"a": ["D1", "D2", "D3"]}),
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
            problems.append(f"{label}: group {gid} expected {seats}, got {got.get(gid)!r}")

# Generated cases: whenever a block exists for a group, the group must get exactly that block.
rng = random.Random(19_0202)
groups_checked = 0
for case in range(60):
    request = random_request(rng, max_rows=6, max_seats=14, max_groups=12, split_rate=0.2, blocked_rate=0.2)
    status, body = call(request)
    why = response_ok(status, body)
    if why:
        problems.append(f"case {case}: {why}")
        continue
    for group, free, (kind, value) in replay(request, body):
        block = together_block(request["rows"], free, group["size"])
        if block is None:
            continue
        groups_checked += 1
        if kind != "seated" or value != block:
            problems.append(f"case {case}: group {group['id']} of {group['size']} should sit at {block}, got {kind} {value!r}")
            break

finish(problems, f"seating together ok: {len(CASES)} hand-made cases, {groups_checked} generated groups")
