"""P1: `rate` follows the interface in C1."""

from _cmd import call, finish

FIELDS = {"billable_g", "base_cents", "surcharge_cents", "total_cents"}
problems = []

for request in (
    {"zone": 2, "weight_g": 2600, "length_cm": 35, "width_cm": 25, "height_cm": 15},
    {"zone": 4, "weight_g": 400, "length_cm": 20, "width_cm": 15, "height_cm": 5},
):
    status, body = call(request)
    if status != 0:
        problems.append(f"{request}: exited with status {status}, expected 0")
    elif not isinstance(body, dict) or set(body) != FIELDS:
        problems.append(f"{request}: expected an object with exactly {sorted(FIELDS)}, got {body!r}")
    elif not all(type(body[field]) is int for field in FIELDS):
        problems.append(f"{request}: every field must be a whole number, got {body!r}")
    elif body["total_cents"] != body["base_cents"] + body["surcharge_cents"]:
        problems.append(f"{request}: total_cents must be base_cents plus surcharge_cents, got {body!r}")

status, body = call({"zone": 7, "weight_g": 1000, "length_cm": 20, "width_cm": 20, "height_cm": 20})
if status != 2 or body is not None:
    problems.append(f"zone 7 must be refused with status 2 and no output, got status {status} and {body!r}")

finish(problems, "contract ok: 3 requests")
