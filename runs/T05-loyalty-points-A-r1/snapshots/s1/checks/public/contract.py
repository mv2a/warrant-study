"""P1: `points` follows the interface described in C3."""

from _cmd import call, finish

FIELDS = {"eligible_cents", "base_points", "bonus_points", "total_points"}
VALID = [
    {"tier": "standard", "items": [{"category": "books", "price_cents": 1250, "quantity": 1}]},
    {"tier": "silver", "items": [{"category": "toys", "price_cents": 999, "quantity": 2}], "bonus_categories": ["toys"]},
    {"tier": "gold", "items": []},
]
problems = []

for request in VALID:
    status, body = call(request)
    if status != 0:
        problems.append(f"{request}: exited with status {status}, expected 0")
    elif not isinstance(body, dict) or set(body) != FIELDS:
        problems.append(f"{request}: expected an object with exactly {sorted(FIELDS)}, got {body!r}")
    elif not all(type(body[field]) is int for field in FIELDS):
        problems.append(f"{request}: every field must be an integer, got {body!r}")
    elif body["total_points"] != body["base_points"] + body["bonus_points"]:
        problems.append(f"{request}: total_points must be base_points plus bonus_points, got {body!r}")

status, body = call({"tier": "platinum", "items": []})
if status != 2 or body is not None:
    problems.append(f"an unknown tier must be refused with status 2 and no output, got status {status} and {body!r}")

finish(problems, f"contract ok: {len(VALID) + 1} requests")
