"""H5: the seats command follows the interface in C1."""

import json
import random

from _cmd import call, finish
from _theatre import random_request, split_name

problems = []


def shape_problem(request, status, body):
    """The first way this response breaks C1, or None."""
    if status != 0:
        return f"exit status {status}, expected 0"
    if not isinstance(body, dict) or set(body) != {"seated", "refused", "free"}:
        return f"expected an object with exactly seated, refused and free, got {body!r}"
    if type(body["free"]) is not int:
        return f"free must be a whole number, got {body['free']!r}"
    if not isinstance(body["seated"], list) or not isinstance(body["refused"], list):
        return "seated and refused must be lists"
    order = {g["id"]: i for i, g in enumerate(request["groups"])}
    for entry in body["seated"]:
        if not isinstance(entry, dict) or set(entry) != {"id", "seats"}:
            return f"a seated entry must hold exactly id and seats, got {entry!r}"
        if entry["id"] not in order or not isinstance(entry["seats"], list):
            return f"a seated entry must name a booked group and list its seats, got {entry!r}"
        parts = [split_name(seat) for seat in entry["seats"]]
        if None in parts:
            return f"seat names must look like B7, got {entry['seats']!r}"
        if parts != sorted(parts):
            return f"seats must be listed row A first and by number, got {entry['seats']!r}"
    for entry in body["refused"]:
        if not isinstance(entry, dict) or set(entry) != {"id", "reason"}:
            return f"a refused entry must hold exactly id and reason, got {entry!r}"
        if entry["id"] not in order or entry["reason"] not in ("not_enough_seats", "not_together"):
            return f"a refused entry must name a booked group and a known reason, got {entry!r}"
    for name in ("seated", "refused"):
        positions = [order[e["id"]] for e in body[name]]
        if positions != sorted(positions):
            return f"{name} must follow booking order, got {[e['id'] for e in body[name]]}"
    return None


rng = random.Random(19_0505)
requests = [random_request(rng, max_rows=6, max_seats=15, max_groups=10, split_rate=0.4) for _ in range(30)]
requests.append({"rows": [3], "groups": [{"id": "Hansen family", "size": 2}, {"id": "Łukasz & co", "size": 1}]})
for request in requests:
    status, body = call(request)
    why = shape_problem(request, status, body)
    if why:
        problems.append(f"{json.dumps(request)[:80]}...: {why}")

# Fields the interface does not name are ignored, and may_split defaults to false.
base = {"rows": [4, 3], "blocked": ["A2"], "groups": [{"id": "a", "size": 3}, {"id": "b", "size": 3, "may_split": True}, {"id": "c", "size": 2}]}
status, plain = call(base)
extra = {**base, "show": "The Seagull", "night": 3, "groups": [{**g, "note": "aisle please", "paid": True} for g in base["groups"]]}
status2, with_extra = call(extra)
if status2 != 0 or with_extra != plain:
    problems.append(f"extra fields must be ignored: expected {plain!r}, got status {status2} and {with_extra!r}")
explicit = {**base, "groups": [{**g, "may_split": g.get("may_split", False)} for g in base["groups"]]}
status3, with_false = call(explicit)
if status3 != 0 or with_false != plain:
    problems.append(f"leaving out may_split must mean false: expected {plain!r}, got {with_false!r}")

# No groups at all, and every group refused: still exit status 0 with the full shape.
request = {"rows": [5, 5], "blocked": ["B5"], "groups": []}
status, body = call(request)
why = shape_problem(request, status, body)
if why or body["seated"] or body["refused"]:
    problems.append(f"no groups: expected status 0 and empty seated and refused lists, got status {status} and {body!r}")
request = {"rows": [2], "groups": [{"id": "a", "size": 3}, {"id": "b", "size": 4, "may_split": True}]}
status, body = call(request)
why = shape_problem(request, status, body)
if why or body["seated"] or [e["id"] for e in body["refused"]] != ["a", "b"]:
    problems.append(f"all groups refused: expected status 0 with both groups in refused, got status {status} and {body!r}")

# A refused request exits with status 2 and writes nothing to standard output.
for label, raw in [
    ("text that is not JSON", "two seats please"),
    ("a group of size 0", '{"rows": [4], "groups": [{"id": "a", "size": 0}]}'),
    ("missing rows", '{"groups": []}'),
    ("a blocked seat that does not exist", '{"rows": [4], "groups": [], "blocked": ["A9"]}'),
]:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{label}: expected status 2 and no output, got status {status} and {body!r}")

finish(problems, f"interface ok: {len(requests)} requests, 4 special cases, 4 refused requests")
