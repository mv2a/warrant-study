"""X12 (G2, G3, G4): generated single-client logs get exactly the token-bucket model's decisions.

The model: full at the first request, min(burst, k + rate x elapsed / 1000) afterwards,
accept at one whole token or more and take exactly one, reject below that and take nothing.
Rates and gaps are chosen so every amount is a whole or binary fraction of a token, so a
failure here is about the bucket model, not about rounding (C2 has its own check).
"""

import random

from _cmd import finish
from _model import check_log

problems = []
rng = random.Random(90417)

# rate x gap / 1000 is a binary fraction when the rate is a power of two and the gap a
# multiple of 125 ms, or when the rate is a multiple of 125 and the gap any whole millisecond.
POW2 = [1, 2, 4, 8, 16, 32]
MULT125 = [125, 250, 375, 500, 625, 875, 1000, 2000, 3000]
count = 0
for n in range(45):
    burst = rng.choice([1, 1, 2, 3, 4, 5, 8, 13])
    if n % 2:
        rate = rng.choice(POW2)
        unit = 125
        span = max(1, 16 // rate)  # up to about two tokens per gap
    else:
        rate = rng.choice(MULT125)
        unit = 1
        span = max(1, 2000 // rate)
    t = rng.choice([0, 125 * rng.randint(1, 4000), 1_790_000_000_000])
    log = []
    for _ in range(rng.randint(25, 90)):
        roll = rng.random()
        if roll < 0.35:
            gap = 0  # another request at the same instant
        elif roll < 0.9:
            gap = unit * rng.randint(1, span * 2)
        else:
            gap = unit * rng.randint(span * 4, span * 400)  # a long quiet spell that overflows the bucket
        t += gap
        log.append(("m", t))
    count += 1
    check_log(f"generated log {n + 1} (burst {burst}, rate {rate}, {len(log)} requests)", burst, rate, log, problems)

finish(problems, f"model ok: {count} generated logs")
