"""H4: tokens flow back continuously at rate per second, with partial progress kept (G3)."""

import random

from _cmd import call, finish
from _model import compare

rng = random.Random(1304)
problems = []
cases = 0

# Empty the bucket at 0 ms, then probe more often than tokens arrive.
for rate in (1, 2, 3, 4, 7, 10, 60, 250, 1000, 1500, 7000):
    for burst in (1, 3):
        token = max(1, 1000 // rate)
        step = max(1, token // 3)
        log = [("r", 0)] * burst + [("r", t) for t in range(step, 4 * token + step + 1, step)]
        compare(call, burst, rate, log, f"rate {rate}, burst {burst}, probing every {step} ms", problems)
        cases += 1

# Generated single-client logs, with gaps measured against the time one token takes.
RATES = [1, 2, 3, 5, 7, 12, 25, 64, 100, 333, 1000, 2500]
for n in range(60):
    burst, rate = rng.randint(1, 4), rng.choice(RATES)
    token = max(1, 1000 // rate)
    t, log = rng.choice([0, 17, 40000]), []
    for _ in range(rng.randint(10, 60)):
        t += rng.choice([0, rng.randint(1, token), rng.randint(1, max(1, token // 4)), rng.randint(token, 3 * token)])
        log.append(("s", t))
    compare(call, burst, rate, log, f"generated log {n + 1} (burst {burst}, rate {rate})", problems)
    cases += 1

finish(problems, f"refill ok: {cases} logs")
