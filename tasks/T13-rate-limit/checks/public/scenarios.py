"""P2: the example logs S1, S2 and S3 from the intent."""

from _cmd import call, finish

A, R = "accept", "reject"
SCENARIOS = [
    ("S1", 3, 2, [("alice", t) for t in (0, 0, 0, 0, 499, 500, 1000, 1000)],
     [A, A, A, R, R, A, A, R], {"alice": {"accepted": 5, "rejected": 3}}),
    ("S2", 1, 1, [("a", 0), ("b", 0), ("a", 0), ("b", 600), ("a", 1000), ("b", 1000)],
     [A, A, R, R, A, A], {"a": {"accepted": 2, "rejected": 1}, "b": {"accepted": 2, "rejected": 1}}),
    ("S3", 2, 1, [("carol", t) for t in (0, 0, 0, 60000, 60000, 60000)],
     [A, A, R, A, A, R], {"carol": {"accepted": 4, "rejected": 2}}),
]
problems = []
for name, burst, rate, log, decisions, clients in SCENARIOS:
    request = {"burst": burst, "rate": rate, "requests": [{"client": c, "at": t} for c, t in log]}
    status, body = call(request)
    expected = {"decisions": decisions, "clients": clients}
    if status != 0 or body != expected:
        problems.append(f"{name}: expected status 0 and {expected}, got status {status} and {body!r}")

finish(problems, f"scenarios ok: {len(SCENARIOS)} logs")
