"""X2 (G1): for a yearly rate above zero, the regular payment is the exact level payment
P*i / (1 - (1+i)^-n) rounded up to the next whole cent, and left alone when it is already whole."""

import random

from _batch import call_all
from _cmd import finish
from _loan import exact_level, regular_payment, req

# Loans whose exact level payment is already a whole number of cents: rounding up must not add a cent.
WHOLE = [
    (120000, 1, 1), (48, 5000, 1), (30000, 4, 1), (1000000000, 600, 1), (360000, 1, 1),
    (800020000, 6, 2), (2352, 5000, 2), (450015000, 8, 2),
    (733594375, 192, 3), (649080600, 200, 3), (86448, 5000, 3),
    (988343875, 960, 4), (839865720, 1000, 4), (406040100, 1200, 4), (2824752, 5000, 4),
    (538248040, 3000, 5), (178590752, 3750, 5), (86544048, 5000, 5),
]
# Exact level payment a hair above a whole cent (must round up) or a hair below (must not overshoot).
NEAR = [
    (625665274, 4593, 12), (767996825, 3904, 480), (714768288, 3040, 84), (344967367, 4267, 60),
    (922861367, 3238, 480), (501543912, 4118, 180), (801886738, 345, 300), (941136967, 4025, 18),
    (483854, 4593, 12), (2059981, 4070, 48), (255383, 4025, 18), (6034590, 345, 300),
    (198620134, 4070, 48), (188023087, 4025, 18), (752858497, 4025, 18), (28753861, 463, 6),
    (295156767, 463, 6), (804492644, 463, 6), (97972871, 345, 300), (186558375, 4823, 12),
    (90235123, 4823, 12),
]
# Edges of the allowed ranges.
EDGES = [
    (1, 1, 1), (1, 5000, 1), (1, 1, 480), (1, 5000, 480), (2, 1, 480), (1000000000, 1, 1),
    (1000000000, 5000, 1), (1000000000, 1, 480), (1000000000, 5000, 480), (999999999, 4999, 479),
    (1000000000, 2500, 240), (7, 3, 2),
]

rng = random.Random(31337)
GENERATED = []
for _ in range(45):
    size = rng.choice([(1, 5000), (5000, 5000000), (5000000, 1000000000)])
    GENERATED.append((rng.randint(*size), rng.randint(1, 5000), rng.choice([rng.randint(1, 36), rng.randint(1, 480)])))

cases = WHOLE + NEAR + EDGES + GENERATED
problems = []
for (p, bp, n), (status, body) in zip(cases, call_all([req(*c) for c in cases])):
    wanted = regular_payment(p, bp, n)
    got = body.get("payment_cents") if isinstance(body, dict) else None
    if status != 0 or got != wanted:
        exact = exact_level(p, bp, n)
        problems.append(f"{req(p, bp, n)}: expected payment_cents {wanted} (exact level {float(exact):.9f}), "
                        f"got status {status} and {got!r}")

finish(problems, f"level payment ok: {len(cases)} loans ({len(WHOLE)} already whole, {len(NEAR)} within a "
                 f"millionth of a cent of whole)")
