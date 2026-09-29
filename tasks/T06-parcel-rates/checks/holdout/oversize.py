"""H4 (G4): oversize parcels pay 1500 cents on top of the base price, whatever order the sides are given in."""

import random

from _cmd import call, finish
from _model import orders, parcel, random_parcel, surcharge

rng = random.Random(6040)
SHAPES = [  # sides in cm, and whether the parcel is oversize
    ((100, 10, 10), False),  # longest side exactly 100 cm
    ((101, 10, 10), True),   # longest side 101 cm
    ((150, 5, 5), True),     # long and thin
    ((101, 5, 5), True),     # long and thin, length plus girth only 121 cm
    ((100, 30, 30), False),  # length plus girth exactly 220 cm
    ((98, 31, 30), False),   # length plus girth 220 cm
    ((99, 31, 30), True),    # length plus girth 221 cm
    ((60, 40, 40), False),   # length plus girth 220 cm with no long side
    ((61, 40, 40), True),    # length plus girth 221 cm with no long side
    ((90, 20, 10), False),   # comfortably normal
    ((70, 55, 1), False),    # flat, length plus girth 182 cm
    ((150, 70, 5), True),    # at the carrying limits
]
cases = [
    (parcel(1 + i % 4, 1000, order), 1500 if oversize else 0)
    for i, (sides, oversize) in enumerate(SHAPES)
    for order in orders(sides)
]
cases += [(p, surcharge(p)) for p in (random_parcel(rng) for _ in range(60))]
problems = []
for p, want in cases:
    status, body = call(p)
    if status != 0 or not isinstance(body, dict):
        problems.append(f"{p}: expected a price, got status {status} and {body!r}")
        continue
    got, base, total = body.get("surcharge_cents"), body.get("base_cents"), body.get("total_cents")
    if got != want:
        problems.append(f"{p}: expected surcharge_cents {want}, got {got!r}")
    elif not isinstance(base, int) or total != base + want:
        problems.append(f"{p}: expected total_cents {base!r} + {want}, got {total!r}")

finish(problems, f"oversize surcharge ok: {len(cases)} parcels")
