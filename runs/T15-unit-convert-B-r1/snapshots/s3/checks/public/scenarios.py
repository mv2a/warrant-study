"""P2: the scenarios written in the intent."""

from _cmd import call, finish

SCENARIOS = [
    ("S1", {"value": "12", "from": "ft", "to": "m", "places": 3}, {"value": "3.658", "unit": "m", "dimension": "length"}),
    ("S2", {"value": "2.5", "from": "lb", "to": "kg", "places": 4}, {"value": "1.1340", "unit": "kg", "dimension": "mass"}),
]
problems = []
for scenario, request, expected in SCENARIOS:
    status, body = call(request)
    if status != 0 or body != expected:
        problems.append(f"{scenario}: expected status 0 and {expected}, got status {status} and {body!r}")

status, body = call({"value": "3", "from": "kg", "to": "l", "places": 2})
if status != 2 or body is not None:
    problems.append(f"S3: expected a refusal (status 2, no output), got status {status} and {body!r}")

finish(problems, "scenarios ok: S1, S2, S3")
