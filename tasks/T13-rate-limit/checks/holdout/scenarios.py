"""H9 to H11: the scenarios in the intent, as written and shifted or renamed. Usage: scenarios.py S1|S2|S3"""

import sys

from _cmd import call, finish
from _model import A, R, request

SCENARIOS = {
    "S1": (3, 2, [("alice", t) for t in (0, 0, 0, 0, 499, 500, 1000, 1000)],
           [A, A, A, R, R, A, A, R], {"alice": {"accepted": 5, "rejected": 3}}),
    "S2": (1, 1, [("a", 0), ("b", 0), ("a", 0), ("b", 600), ("a", 1000), ("b", 1000)],
           [A, A, R, R, A, A], {"a": {"accepted": 2, "rejected": 1}, "b": {"accepted": 2, "rejected": 1}}),
    "S3": (2, 1, [("carol", t) for t in (0, 0, 0, 60000, 60000, 60000)],
           [A, A, R, A, A, R], {"carol": {"accepted": 4, "rejected": 2}}),
}
name = sys.argv[1]
burst, rate, log, decisions, clients = SCENARIOS[name]
RENAME = {"alice": "tenant-42", "a": "A1", "b": "zz top", "carol": "Carol"}
variants = [("as written", log, clients)]
for shift in (1, 86_400_000):
    variants.append((f"shifted by {shift} ms", [(c, t + shift) for c, t in log], clients))
variants.append(("with other client names", [(RENAME[c], t) for c, t in log], {RENAME[c]: v for c, v in clients.items()}))

problems = []
for label, entries, counts in variants:
    expected = {"decisions": decisions, "clients": counts}
    status, body = call(request(burst, rate, entries))
    if status != 0 or body != expected:
        problems.append(f"{name} {label}: expected status 0 and {expected}, got status {status} and {body!r}")

finish(problems, f"{name} ok: {len(variants)} variants")
