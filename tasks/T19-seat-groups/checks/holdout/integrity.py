"""H6: seats are never oversold, and free counts the seats that are neither blocked nor sold."""

import random

from _cmd import call, finish
from _theatre import all_seats, random_request, response_ok

problems = []


def integrity_problem(request, body):
    seats_in_theatre = set(all_seats(request["rows"]))
    blocked = set(request.get("blocked", []))
    sizes = {g["id"]: g["size"] for g in request["groups"]}
    sold = []
    for entry in body["seated"]:
        seats = entry.get("seats") if isinstance(entry, dict) else None
        if not isinstance(seats, list) or entry.get("id") not in sizes:
            return f"unreadable seated entry {entry!r}"
        if len(seats) != sizes[entry["id"]]:
            return f"group {entry['id']} of {sizes[entry['id']]} got {len(seats)} seats: {seats}"
        for seat in seats:
            if seat not in seats_in_theatre:
                return f"group {entry['id']} got {seat!r}, which is not a seat of this theatre"
            if seat in blocked:
                return f"group {entry['id']} got blocked seat {seat}"
        sold.extend(seats)
    doubled = sorted({seat for seat in sold if sold.count(seat) > 1})
    if doubled:
        return f"seats sold twice: {doubled}"
    expected_free = len(seats_in_theatre) - len(blocked) - len(sold)
    if body.get("free") != expected_free or type(body.get("free")) is not int:
        return f"free should be {expected_free} ({len(seats_in_theatre)} seats, {len(blocked)} blocked, {len(sold)} sold), got {body.get('free')!r}"
    return None


requests = [
    {"rows": [3, 3], "blocked": ["A1", "A2", "A3", "B1", "B2", "B3"], "groups": [{"id": "a", "size": 1}]},
    {"rows": [3, 3], "groups": [{"id": "a", "size": 3}, {"id": "b", "size": 3}, {"id": "c", "size": 1, "may_split": True}]},
    {"rows": [5, 5, 5], "blocked": ["C5", "A1"], "groups": []},
    {"rows": [4], "blocked": ["A4"], "groups": [{"id": "a", "size": 4, "may_split": True}, {"id": "b", "size": 3}]},
    {"rows": [1] * 26, "blocked": ["Z1"], "groups": [{"id": "a", "size": 25, "may_split": True}, {"id": "b", "size": 1}]},
    {"rows": [50] * 26, "blocked": ["M25", "M26"], "groups": [{"id": f"g{i}", "size": 49, "may_split": i % 2 == 0} for i in range(28)]},
]
rng = random.Random(19_0606)
for _ in range(80):
    requests.append(random_request(rng, max_rows=6, max_seats=12, max_groups=14, split_rate=0.4, blocked_rate=0.2, max_size=8))

for number, request in enumerate(requests):
    status, body = call(request)
    why = response_ok(status, body) or integrity_problem(request, body)
    if why:
        problems.append(f"request {number}: {why}")

finish(problems, f"integrity ok: {len(requests)} requests")
