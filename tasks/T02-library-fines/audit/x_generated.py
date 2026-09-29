"""X14 (G1, G2, G3, G4, C2): generated requests match the intent's arithmetic exactly (fixed seed)."""

import random

from _audit import TYPES, expected, finish, item, succeed

rng = random.Random(61803399)
problems = []

ROUNDS = 120
for n in range(ROUNDS):
    size = rng.choice([0, 1, 1, 2, 3, 4, 5, 8, 15])
    items = []
    for k in range(size):
        due = rng.randint(0, 2000)
        # Lateness drawn to land often near the grace and cap boundaries, sometimes early.
        late = rng.choice([
            rng.randint(-60, 0), rng.randint(0, 5), rng.randint(6, 12),
            rng.randint(8, 13), rng.randint(20, 26), rng.randint(32, 38), rng.randint(39, 3000),
        ])
        items.append(item(f"G{n}.{k}", rng.choice(TYPES), due, max(0, due + late)))
    request = {"items": items}
    succeed(problems, f"round {n} ({size} items)", request, want=expected(request))

finish(problems, f"generated ok: {ROUNDS} requests (seed 61803399)")
