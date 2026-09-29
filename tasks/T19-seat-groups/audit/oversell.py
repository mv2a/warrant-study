"""C2: seats are never oversold. For each request, every sold seat exists, is not blocked
and goes to one group only; each seated group has exactly `size` seats; and `free` is the
number of seats neither blocked nor sold. Also checks `free` exactly on requests where no
seat can be sold."""

import random

from _audit import answers, brief, call_all, name, parse, seats_of
from _cmd import finish

REQUESTS = [
    {"rows": [4, 4], "blocked": ["A2", "A3", "B1", "B4"], "groups": [
        {"id": "Aoki", "size": 2}, {"id": "Bell", "size": 2, "may_split": True}, {"id": "Cobb", "size": 1, "may_split": True}]},
    {"rows": [2, 9, 1], "groups": [
        {"id": "Finn", "size": 9}, {"id": "Gale", "size": 3, "may_split": True}, {"id": "Hux", "size": 1}]},
    {"rows": [3], "blocked": ["A1", "A3"], "groups": [
        {"id": "Ives", "size": 2, "may_split": True}, {"id": "Jory", "size": 1}, {"id": "Kemp", "size": 1, "may_split": True}]},
    {"rows": [6, 1, 6], "blocked": ["B1", "A6", "C1"], "groups": [
        {"id": "Lark", "size": 6, "may_split": True}, {"id": "Moe", "size": 5, "may_split": True}, {"id": "Nye", "size": 2}]},
    {"rows": [10, 10], "blocked": ["A10", "B10"], "groups": [
        {"id": "Ode", "size": 9}, {"id": "Pym", "size": 9}, {"id": "Quay", "size": 2, "may_split": True}]},
]

# A full theatre, generated with a fixed seed: many groups, some blocked seats.
rng = random.Random(31337)
rows = [50] * 26
blocked = sorted({name(*rng.choice(seats_of(rows))) for _ in range(60)})
groups = []
for i in range(320):
    group = {"id": f"party-{i:03d}", "size": rng.choice([1, 2, 2, 3, 3, 4, 4, 5, 6, 8, 12, 30, 55])}
    if rng.random() < 0.5:
        group["may_split"] = True
    groups.append(group)
REQUESTS.append({"rows": rows, "blocked": blocked, "groups": groups})

# `free` when no seat can be sold: no groups, or only groups larger than the free seats.
EXACT = [
    ({"rows": [7, 7, 7], "blocked": ["B4", "C1", "C7"], "groups": []}, 18),
    ({"rows": [5, 5], "groups": [{"id": "Dean", "size": 11, "may_split": True}, {"id": "Ezra", "size": 12}]}, 10),
    ({"rows": [1] * 26, "blocked": ["M1"], "groups": [{"id": "Gus", "size": 26}, {"id": "Hana", "size": 26, "may_split": True}]}, 25),
    ({"rows": [50] * 26, "groups": [], "blocked": ["A1", "Z50"]}, 1298),
]

problems = []
for request, (status, body) in zip(REQUESTS, call_all(REQUESTS)):
    got = answers(body) if status == 0 else None
    if got is None:
        problems.append(f"status {status} or unreadable response for a valid request | {brief(request)}")
        continue
    exist = set(seats_of(request["rows"]))
    block = {parse(s) for s in request.get("blocked", [])}
    sizes = {g["id"]: g["size"] for g in request["groups"]}
    sold, bad, seen = set(), [], set()
    for entry in body["seated"]:
        gid, names = entry["id"], entry["seats"]
        if gid in seen:
            bad.append(f"{gid} is seated more than once")
        seen.add(gid)
        if gid not in sizes:
            bad.append(f"seats sold to unknown group {gid!r}")
        elif len(names) != sizes[gid]:
            bad.append(f"{gid} has size {sizes[gid]} but got {len(names)} seats")
        for seat_name in names:
            seat = parse(seat_name)
            if seat not in exist:
                bad.append(f"{gid} got {seat_name!r}, which is not a seat of this theatre")
            elif seat in block:
                bad.append(f"{gid} got blocked seat {seat_name}")
            elif seat in sold:
                bad.append(f"{seat_name} sold twice")
            else:
                sold.add(seat)
    free = len(exist) - len(block) - len(sold)
    if type(body.get("free")) is not int or body["free"] != free:
        bad.append(f"free is {body.get('free')!r}, but {free} seats are neither blocked nor sold")
    if bad:
        problems.append("; ".join(bad[:3]) + f" | {brief(request)}")

for (request, free), (status, body) in zip(EXACT, call_all([r for r, _ in EXACT])):
    value = body.get("free") if isinstance(body, dict) else None
    if status != 0 or type(value) is not int or value != free:
        problems.append(f"expected status 0 and free {free}, got status {status} and free {value!r} | {brief(request)}")

finish(problems, f"no overselling: {len(REQUESTS) + len(EXACT)} requests")
