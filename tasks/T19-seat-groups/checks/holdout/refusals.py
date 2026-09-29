"""H4: groups that cannot be seated are refused whole, with not_enough_seats or not_together as G4 says."""

import random

from _cmd import call, finish
from _theatre import random_request, replay, response_ok, together_block

problems = []

# Hand-made cases: (name, request, {group id: expected reason}, number of groups that must be seated).
CASES = [
    ("too few seats left, group may not split",
     {"rows": [4, 4], "groups": [{"id": "a", "size": 3}, {"id": "b", "size": 3}, {"id": "c", "size": 3}]},
     {"c": "not_enough_seats"}, 2),
    ("too few seats left, group may split",
     {"rows": [4, 4], "groups": [{"id": "a", "size": 3}, {"id": "b", "size": 3}, {"id": "c", "size": 3, "may_split": True}]},
     {"c": "not_enough_seats"}, 2),
    ("enough seats, none side by side",
     {"rows": [5, 5], "blocked": ["A3", "B3"], "groups": [{"id": "a", "size": 3}]},
     {"a": "not_together"}, 0),
    ("exactly as many free seats as members, but apart",
     {"rows": [3, 3], "blocked": ["A2"], "groups": [{"id": "x", "size": 3}, {"id": "y", "size": 2}]},
     {"y": "not_together"}, 1),
    ("one seat short, group may split",
     {"rows": [3, 3], "blocked": ["A2"], "groups": [{"id": "x", "size": 3}, {"id": "y", "size": 3, "may_split": True}]},
     {"y": "not_enough_seats"}, 1),
    ("a group bigger than the theatre",
     {"rows": [3], "groups": [{"id": "a", "size": 10}, {"id": "b", "size": 10, "may_split": True}]},
     {"a": "not_enough_seats", "b": "not_enough_seats"}, 0),
    ("every seat blocked",
     {"rows": [2], "blocked": ["A1", "A2"], "groups": [{"id": "a", "size": 1}]},
     {"a": "not_enough_seats"}, 0),
    ("a very large group",
     {"rows": [50] * 26, "groups": [{"id": "a", "size": 10 ** 12, "may_split": True}]},
     {"a": "not_enough_seats"}, 0),
    ("a group wider than any row, not splittable, with seats to spare",
     {"rows": [4, 4, 4], "groups": [{"id": "a", "size": 5}]},
     {"a": "not_together"}, 0),
]
for label, request, expected, seated_count in CASES:
    status, body = call(request)
    why = response_ok(status, body)
    if why:
        problems.append(f"{label}: {why}")
        continue
    got = {e.get("id"): e.get("reason") for e in body["refused"] if isinstance(e, dict)}
    for gid, reason in expected.items():
        if got.get(gid) != reason:
            problems.append(f"{label}: group {gid} expected refusal {reason!r}, got {got.get(gid)!r}")
    if len(body["seated"]) != seated_count:
        problems.append(f"{label}: expected {seated_count} seated groups, got {body['seated']!r}")

# A refused group is not partly seated: nobody from it holds a seat, and the next group finds all seats free.
status, body = call({"rows": [3], "groups": [{"id": "big", "size": 5, "may_split": True}, {"id": "next", "size": 3}]})
if response_ok(status, body) or body["seated"] != [{"id": "next", "seats": ["A1", "A2", "A3"]}]:
    problems.append(f"a refused group must hold no seats: got {body!r}")

# Generated cases: every group appears once, and every refusal and its reason follow G4.
rng = random.Random(19_0404)
refusals = 0
for case in range(60):
    request = random_request(rng, max_rows=4, max_seats=9, max_groups=12, split_rate=0.3, blocked_rate=0.2, max_size=9)
    status, body = call(request)
    why = response_ok(status, body)
    if why:
        problems.append(f"case {case}: {why}")
        continue
    listed = [e.get("id") for e in body["seated"] + body["refused"] if isinstance(e, dict)]
    ids = [g["id"] for g in request["groups"]]
    if sorted(listed) != sorted(ids):
        problems.append(f"case {case}: every group must appear exactly once in seated or refused, got {listed}")
        continue
    for group, free, (kind, value) in replay(request, body):
        size = group["size"]
        if kind == "seated":
            if not isinstance(value, list) or len(value) != size:
                problems.append(f"case {case}: group {group['id']} of {size} was partly seated: {value!r}")
                break
            continue
        refusals += 1
        if len(free) < size:
            want = "not_enough_seats"
        elif group.get("may_split") is True or together_block(request["rows"], free, size):
            want = None  # this group could have been seated
        else:
            want = "not_together"
        if value != want:
            what = f"reason {want!r}" if want else "to be seated"
            problems.append(f"case {case}: group {group['id']} of {size} with {len(free)} seats free expected {what}, got refusal {value!r}")
            break

if refusals < 60:
    problems.append(f"only {refusals} generated refusals; the generator should give at least 60")
finish(problems, f"refusals ok: {len(CASES) + 1} hand-made cases, {refusals} generated refusals")
