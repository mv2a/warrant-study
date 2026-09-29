"""X12 (G4): 45 generated requests (seed 23459) with shuffled, tied and widely spaced priorities and varied prices fund products in (priority, request position) order."""

import random

from _cmd import finish
from _order import PACK_SIZES, check_order, one_pack

rng = random.Random(23459)
POOLS = [[1, 2, 3], [1, 1, 2], [4, 9, 10, 11, 100], [2, 3, 5, 8, 13, 21], [7], [1, 50, 50, 999999]]

problems = []
steps = 0
for n in range(45):
    pool = rng.choice(POOLS)
    size = rng.randint(3, 9)
    products = []
    for i in range(size):
        pack = rng.choice(PACK_SIZES)
        products.append(one_pack(f"G4-{n:02d}-{rng.randint(10, 99)}{i}", rng.choice(pool), pack_size=pack,
                                 price=pack * rng.choice([1, 2, 3, 5, 7, 11, 40])))
    ks = sorted({0, rng.randint(1, size - 1), rng.randint(1, size - 1), size})
    steps += len(ks)
    check_order(f"request {n} (priorities {[p['priority'] for p in products]})", products, problems, ks)

finish(problems, f"generated priority order ok: {steps} requests")
