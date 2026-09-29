"""H6: token counts are exact, never rounded (C2)."""

import math
import random

from _cmd import call, finish
from _model import A, R, compare

rng = random.Random(1306)
problems = []
cases = 0

# The examples in the intent.
compare(call, 1, 3, [("x", 0), ("x", 333)], "rate 3, asking at 333 ms", problems, [A, R])
compare(call, 1, 3, [("x", 0), ("x", 334)], "rate 3, asking at 334 ms", problems, [A, A])
compare(call, 1, 3, [("x", 0), ("x", 333), ("x", 334)], "rate 3, asking at 333 and 334 ms", problems, [A, R, A])
compare(call, 1, 10, [("x", t) for t in range(0, 101, 10)], "rate 10, asking every 10 ms", problems, [A] + [R] * 9 + [A])
compare(call, 4, 10, [("x", 0)] * 4 + [("x", t) for t in range(10, 101, 10)], "rate 10, burst 4, asking every 10 ms",
        problems, [A] * 4 + [R] * 9 + [A])
cases += 5

# A token due on an exact millisecond is available then, and not one millisecond before.
for rate in (3, 6, 7, 8, 9, 12, 16, 30, 40, 64, 125, 300, 625, 999):
    tokens = rate // math.gcd(rate, 1000)  # the fewest tokens that fall due on a whole millisecond
    due = tokens * 1000 // rate
    burst = tokens + 1
    empty = [("e", 0)] * burst
    compare(call, burst, rate, empty + [("e", due)] * (tokens + 1), f"rate {rate}: {tokens} tokens at {due} ms",
            problems, [A] * burst + [A] * tokens + [R])
    compare(call, burst, rate, empty + [("e", due - 1)] * tokens, f"rate {rate}: {tokens} tokens at {due - 1} ms",
            problems, [A] * burst + [A] * (tokens - 1) + [R])
    cases += 2

# Long runs of small steps, where rounding errors would pile up.
for rate in (3, 6, 7, 9, 10, 11, 13, 17, 30, 70, 100, 300, 333, 700, 999, 1001, 3333):
    for step in (1, 3, 7, 10):
        burst = 1 + (rate + step) % 3
        log = [("z", 0)] * burst + [("z", t) for t in range(step, 3001, step)]
        compare(call, burst, rate, log, f"rate {rate}, burst {burst}, every {step} ms", problems)
        cases += 1

# Generated single-client logs with awkward rates and small gaps.
RATES = [3, 7, 9, 10, 11, 30, 70, 99, 100, 101, 300, 333, 999, 3001]
for n in range(80):
    burst, rate = rng.randint(1, 3), rng.choice(RATES)
    t, log = rng.choice([0, 1, 777]), []
    for _ in range(rng.randint(30, 120)):
        t += rng.choice([0, 1, 1, 2, 3, 7, 10, 30, 33, 100, 333])
        log.append(("m", t))
    compare(call, burst, rate, log, f"generated log {n + 1} (burst {burst}, rate {rate})", problems)
    cases += 1

finish(problems, f"exact ok: {cases} logs")
