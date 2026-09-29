"""P2: the judged scenarios S1, S2 and S3 in the intent."""

from _cmd import call, finish

SCENARIOS = [
    ("S1", {"password": "Bell-Book-77", "username": "rebel", "banned": ["books"]},
     {"ok": True, "violations": []}),
    ("S2", {"password": "maria.silva2024", "username": "MSILVA", "banned": ["2024"]},
     {"ok": False, "violations": ["banned", "username"]}),
    ("S3", {"password": "kim111", "username": "kim", "banned": ["11"]},
     {"ok": False, "violations": ["banned", "classes", "repeat", "too_short"]}),
]
problems = []
for sid, request, expected in SCENARIOS:
    status, body = call(request)
    if status != 0 or body != expected:
        problems.append(f"{sid}: expected status 0 and {expected}, got status {status} and {body!r}")

finish(problems, f"scenarios ok: {len(SCENARIOS)}")
