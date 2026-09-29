"""H12: generated multi-client logs match an exact token-bucket model (G1-G4, C2)."""

import random

from _cmd import call, finish
from _model import compare

rng = random.Random(1312)
POOL = ["api", "API", "web", "batch", "b", "mobile ", "x"]
RATES = [1, 2, 3, 7, 10, 33, 100, 250, 999, 1000, 1001, 5000]
problems = []
for n in range(120):
    names = rng.sample(POOL, rng.randint(1, 5))
    burst, rate = rng.randint(1, 6), rng.choice(RATES)
    token = max(1, 1000 // rate)
    t, log = rng.choice([0, 0, 3, 10 ** 6]), []
    for _ in range(rng.randint(5, 100)):
        t += rng.choice([0, 0, 1, rng.randint(1, token), rng.randint(token, 5 * token), rng.randint(0, 20 * token)])
        log.extend([(rng.choice(names), t)] * rng.choice([1, 1, 1, 2, 3]))
    compare(call, burst, rate, log, f"generated log {n + 1} (burst {burst}, rate {rate})", problems)

finish(problems, "model ok: 120 generated logs")
