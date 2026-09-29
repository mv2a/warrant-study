"""X6 (G3): tokens flow back continuously at rate per second, and progress toward the next token is kept.

Every amount here is a whole or binary fraction of a token, so rounding (C2) cannot be the
reason for a failure. Each expected list was worked out by hand and agrees with the model.
"""

from _cmd import finish
from _model import A, R, check_log, replay

problems = []
CASES = [
    # (label, burst, rate, times for one client, decisions worked out by hand)
    ("half a token at 125 ms is kept to 250 ms", 1, 4, [0, 125, 250], [A, R, A]),
    ("a quarter token at a time, rejected three times", 1, 2,
     [0, 125, 250, 375, 500, 625, 750, 875, 1000], [A, R, R, R, A, R, R, R, A]),
    ("half a token left after an accept is kept", 3, 4,
     [0, 0, 0, 375, 500, 750, 875, 1000], [A, A, A, A, A, A, R, A]),
    ("linear refill of 2 tokens in 250 ms, then 1 in 125 ms", 4, 8,
     [0, 0, 0, 0, 250, 250, 250, 375], [A, A, A, A, A, A, R, A]),
    ("slow rate: 1.5 tokens, then 1.0, then 0.75, then 1.0", 2, 1,
     [0, 0, 500, 1500, 2000, 2750, 3000], [A, A, R, A, A, R, A]),
    ("an eighth of a token per millisecond", 2, 125,
     [0, 0, 12, 16, 20, 24, 30, 31, 32], [A, A, A, A, R, A, R, R, A]),
    ("fractions add up over accepts: 1.25 per request", 2, 5,
     [0, 0, 250, 500, 750, 1000, 1000], [A, A, A, A, A, A, A]),
    ("exactly one token accumulated from three pieces", 1, 250,
     [0, 1, 3, 4, 5], [A, R, R, A, R]),
]

for label, burst, rate, times, decisions in CASES:
    log = [("r", t) for t in times]
    want = replay(burst, rate, log)
    if want["decisions"] != decisions:  # guards the hand-worked lists against typing mistakes
        problems.append(f"{label}: the audit's own expectation is inconsistent; fix the check")
        continue
    check_log(label, burst, rate, log, problems, want=want)

finish(problems, f"refill ok: {len(CASES)} logs")
