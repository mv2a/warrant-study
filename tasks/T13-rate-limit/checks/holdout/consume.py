"""H5: accept with at least one whole token, take exactly one; a rejection takes nothing (G4)."""

import random

from _cmd import call, finish
from _model import A, R, compare

rng = random.Random(1305)
problems = []
cases = 0

# Rates where a token takes a whole number of milliseconds.
for rate in (1, 2, 4, 5, 8, 10, 25, 125, 200, 1000):
    token = 1000 // rate
    for burst in (1, 2, 5):
        empty = [("h", 0)] * burst
        # Retrying every millisecond: accepted exactly when each token is due, rejected in between.
        hammer = empty + [("h", t) for t in range(1, 3 * token + 1)]
        expected = [A] * burst + [A if t % token == 0 else R for t in range(1, 3 * token + 1)]
        compare(call, burst, rate, hammer, f"rate {rate}, burst {burst}, retrying every ms", problems, expected)
        # Waiting: accepted at the same times.
        wait = empty + [("h", k * token) for k in (1, 2, 3)]
        compare(call, burst, rate, wait, f"rate {rate}, burst {burst}, waiting", problems, [A] * (burst + 3))
        # One millisecond early is too early; then on time works.
        early = empty + [("h", token - 1), ("h", token)]
        compare(call, burst, rate, early, f"rate {rate}, burst {burst}, 1 ms early", problems, [A] * burst + [R, A])
        cases += 3

# Accepting takes exactly one token: a full bucket of 5 serves 5 at one instant, one at a time.
compare(call, 5, 1, [("f", 0), ("f", 0), ("f", 0), ("f", 0), ("f", 0), ("f", 0), ("f", 999), ("f", 1000), ("f", 1000)],
        "a bucket of 5 at one instant", problems, [A, A, A, A, A, R, R, A, R])
cases += 1

# Generated retry-heavy single-client logs.
RATES = [1, 3, 6, 9, 40, 125, 333, 999, 1000, 1700]
for n in range(50):
    burst, rate = rng.randint(1, 3), rng.choice(RATES)
    token = max(1, 1000 // rate)
    t, log = 0, []
    for _ in range(rng.randint(20, 80)):
        t += rng.choice([0, 0, 1, 1, 2, rng.randint(1, token), rng.randint(token, 2 * token)])
        log.extend([("u", t)] * rng.choice([1, 1, 1, 2, 4]))
    compare(call, burst, rate, log, f"generated log {n + 1} (burst {burst}, rate {rate})", problems)
    cases += 1

finish(problems, f"consume ok: {cases} logs")
