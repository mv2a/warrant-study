"""H9: the scenarios in the intent, checked in full."""

from _cmd import call, finish

problems = []
for scenario, request, expected in [
    ("S1", {"value": "12", "from": "ft", "to": "m", "places": 3}, {"value": "3.658", "unit": "m", "dimension": "length"}),
    ("S2", {"value": "2.5", "from": "lb", "to": "kg", "places": 4}, {"value": "1.1340", "unit": "kg", "dimension": "mass"}),
]:
    for attempt in range(2):
        status, body = call(request)
        if status != 0 or body != expected:
            problems.append(f"{scenario} (run {attempt + 1}): expected status 0 and {expected}, got status {status} and {body!r}")

for attempt in range(2):
    status, body = call({"value": "3", "from": "kg", "to": "l", "places": 2})
    if status != 2 or body is not None:
        problems.append(f"S3 (run {attempt + 1}): expected status 2 and nothing on standard output, got status {status} and {body!r}")

finish(problems, "scenarios ok: S1, S2 and S3, each run twice")
