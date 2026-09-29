"""H1: groups are handled in booking order; later groups never change earlier results; refused groups take nothing."""

import random

from _cmd import call, finish
from _theatre import random_request, response_ok

problems = []


def outcome(body, group_id):
    for entry in body.get("seated", []):
        if isinstance(entry, dict) and entry.get("id") == group_id:
            return "seated"
    for entry in body.get("refused", []):
        if isinstance(entry, dict) and entry.get("id") == group_id:
            return "refused"
    return "missing"


# Hand-made cases: (name, request, {group id: "seated" or "refused"}).
CASES = [
    ("an earlier small group keeps its seats before a later big one",
     {"rows": [5], "groups": [{"id": "small", "size": 2}, {"id": "big", "size": 4}]},
     {"small": "seated", "big": "refused"}),
    ("a group refused for lack of seats leaves room for a later one",
     {"rows": [4], "groups": [{"id": "a", "size": 3}, {"id": "b", "size": 2}, {"id": "c", "size": 1}]},
     {"a": "seated", "b": "refused", "c": "seated"}),
    ("a group refused for not fitting together leaves room for a later one",
     {"rows": [3, 3], "blocked": ["A2"], "groups": [{"id": "x", "size": 3}, {"id": "y", "size": 2}, {"id": "z", "size": 1}]},
     {"x": "seated", "y": "refused", "z": "seated"}),
    ("the first bookings are served first even when a later group is larger",
     {"rows": [6], "groups": [{"id": "p", "size": 1}, {"id": "q", "size": 1}, {"id": "r", "size": 5}, {"id": "s", "size": 4}]},
     {"p": "seated", "q": "seated", "r": "refused", "s": "seated"}),
    ("a splittable group booked first is served before a later group that would fit exactly",
     {"rows": [2, 2], "blocked": ["A1", "B2"], "groups": [{"id": "m", "size": 2, "may_split": True}, {"id": "n", "size": 1}]},
     {"m": "seated", "n": "refused"}),
]
for label, request, expected in CASES:
    status, body = call(request)
    why = response_ok(status, body)
    if why:
        problems.append(f"{label}: {why}")
        continue
    got = {gid: outcome(body, gid) for gid in expected}
    if got != expected:
        problems.append(f"{label}: expected {expected}, got {got}")

# The first seat of a one-seat group booked first must not move when big groups follow.
status, body = call({"rows": [6], "groups": [{"id": "a", "size": 1}, {"id": "b", "size": 4}]})
alone_status, alone = call({"rows": [6], "groups": [{"id": "a", "size": 1}]})
if response_ok(status, body) or response_ok(alone_status, alone) or body["seated"][:1] != alone["seated"][:1]:
    problems.append(f"a later group changed an earlier group's seats: {body!r} versus {alone!r}")

# Generated cases: a prefix of the bookings gets exactly the matching prefix of the results,
# and removing a refused group changes nothing else.
rng = random.Random(19_0101)
checked = 0
for case in range(40):
    request = random_request(rng, max_groups=8, split_rate=0.3)
    status, full = call(request)
    why = response_ok(status, full)
    if why:
        problems.append(f"case {case}: {why}")
        continue
    ids = [g["id"] for g in request["groups"]]
    lengths = sorted(set(rng.randint(1, len(ids)) for _ in range(3)))
    for k in lengths:
        if k == len(ids):
            continue
        keep = set(ids[:k])
        status, part = call({**request, "groups": request["groups"][:k]})
        checked += 1
        if response_ok(status, part):
            problems.append(f"case {case} first {k} groups: {response_ok(status, part)}")
            continue
        want = ([e for e in full["seated"] if e.get("id") in keep], [e for e in full["refused"] if e.get("id") in keep])
        if (part["seated"], part["refused"]) != want:
            problems.append(f"case {case}: the first {k} groups got different results when later groups were added")
    for entry in [e for e in full["refused"] if isinstance(e, dict)][:2]:
        gone = entry.get("id")
        status, without = call({**request, "groups": [g for g in request["groups"] if g["id"] != gone]})
        checked += 1
        if response_ok(status, without):
            problems.append(f"case {case} without {gone}: {response_ok(status, without)}")
            continue
        want = {**full, "refused": [e for e in full["refused"] if e is not entry]}
        if without != want:
            problems.append(f"case {case}: removing refused group {gone} changed other results")

finish(problems, f"booking order ok: {len(CASES) + 1} hand-made cases, 40 generated cases, {checked} variations")
