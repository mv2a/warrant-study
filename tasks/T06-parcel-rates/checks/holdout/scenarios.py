"""H8 (S1 to S4): the four example parcels in the intent, response for response."""

from _cmd import call, finish
from _model import refused

PRICED = [
    ("S1", {"zone": 1, "weight_g": 1500, "length_cm": 30, "width_cm": 20, "height_cm": 10},
     {"billable_g": 1500, "base_cents": 690, "surcharge_cents": 0, "total_cents": 690}),
    ("S2", {"zone": 3, "weight_g": 800, "length_cm": 50, "width_cm": 40, "height_cm": 30},
     {"billable_g": 12000, "base_cents": 2190, "surcharge_cents": 0, "total_cents": 2190}),
    ("S3", {"zone": 4, "weight_g": 3500, "length_cm": 20, "width_cm": 110, "height_cm": 15},
     {"billable_g": 6600, "base_cents": 2520, "surcharge_cents": 1500, "total_cents": 4020}),
]
S4 = {"zone": 1, "weight_g": 3000, "length_cm": 20, "width_cm": 10, "height_cm": 155}
problems = []
for _ in range(2):  # the same request gets the same answer every time
    for name, request, expected in PRICED:
        status, body = call(request)
        if status != 0 or body != expected:
            problems.append(f"{name}: expected status 0 and {expected}, got status {status} and {body!r}")
    status, body = call(S4)
    if not refused(status, body):
        problems.append(f"S4: expected a refusal with status 2, got status {status} and {body!r}")

finish(problems, "scenarios ok: S1 to S4, twice each")
