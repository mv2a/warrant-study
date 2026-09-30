"""P2: the example requests written in the intent."""

from _cmd import call, finish

SCENARIOS = [
    ("S1", {"branch": "lisbon", "year": 2026, "previous": "LIS-2026-00041"}, {"number": "LIS-2026-00042", "sequence": 42}),
    ("S2", {"branch": "porto", "year": 2027, "previous": "OPO-2026-01873"}, {"number": "OPO-2027-00001", "sequence": 1}),
    ("S3", {"branch": "faro", "year": 2026, "previous": None}, {"number": "FAO-2026-00001", "sequence": 1}),
]
problems = []
for scenario, request, expected in SCENARIOS:
    status, body = call(request)
    if status != 0 or body != expected:
        problems.append(f"{scenario}: expected {expected} with status 0, got {body!r} (status {status})")

status, body = call({"branch": "braga", "year": 2026, "previous": "LIS-2026-00041"})
if status != 2 or body is not None:
    problems.append(f"S4: expected a refusal (status 2, no output), got status {status} and {body!r}")

finish(problems, "scenarios ok: S1, S2, S3, S4")
