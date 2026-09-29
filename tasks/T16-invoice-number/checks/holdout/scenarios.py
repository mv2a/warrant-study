"""H9: the example requests written in the intent, run twice each."""

from _cmd import call, finish

SCENARIOS = [
    ("S1", {"branch": "lisbon", "year": 2026, "previous": "LIS-2026-00041"}, 0, {"number": "LIS-2026-00042", "sequence": 42}),
    ("S2", {"branch": "porto", "year": 2027, "previous": "OPO-2026-01873"}, 0, {"number": "OPO-2027-00001", "sequence": 1}),
    ("S3", {"branch": "faro", "year": 2026, "previous": None}, 0, {"number": "FAO-2026-00001", "sequence": 1}),
    ("S4", {"branch": "braga", "year": 2026, "previous": "LIS-2026-00041"}, 2, None),
]
problems = []
for scenario, request, expected_status, expected in SCENARIOS:
    for attempt in (1, 2):
        status, body = call(request)
        if status != expected_status or body != expected:
            problems.append(f"{scenario} (run {attempt}): expected {expected!r} with status {expected_status}, got {body!r} (status {status})")

finish(problems, "scenarios ok: S1, S2, S3, S4, twice each")
