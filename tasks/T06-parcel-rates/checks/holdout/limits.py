"""H6 (C2): parcels over the weight, side or length-plus-girth limit are refused; parcels at a limit are priced."""

import random

from _cmd import call, finish
from _model import carriable, orders, parcel, priced, refused

rng = random.Random(6060)
ACCEPTED = [
    ("30,000 g actual weight", [parcel(1, 30000, (1, 1, 1))]),
    ("30,000 g dimensional weight", [parcel(2, 1, s) for s in orders((100, 50, 30))]),
    ("a 150 cm side", [parcel(3, 2000, s) for s in orders((150, 10, 10))]),
    ("length plus girth of 300 cm", [parcel(4, 2000, s) for s in orders((150, 70, 5))]),
    ("length plus girth of 300 cm", [parcel(1, 2000, s) for s in orders((120, 85, 5))]),
]
REFUSED = [
    ("30,001 g actual weight", [parcel(1, 30001, (1, 1, 1))]),
    ("a very heavy parcel", [parcel(2, 10**9, (20, 20, 20))]),
    ("30,005 g dimensional weight, 1 g actual", [parcel(3, 1, s) for s in orders((76, 47, 42))]),
    ("36,000 g dimensional weight, 5,000 g actual", [parcel(4, 5000, s) for s in orders((100, 60, 30))]),
    ("a 151 cm side", [parcel(1, 2000, s) for s in orders((151, 10, 10))]),
    ("a 400 cm side", [parcel(2, 100, (400, 1, 1))]),
    ("length plus girth of 301 cm", [parcel(3, 2000, s) for s in orders((121, 85, 5))]),
    ("length plus girth of 304 cm", [parcel(4, 2000, s) for s in orders((150, 76, 1))]),
]
cases = [(name, p, True) for name, group in ACCEPTED for p in group]
cases += [(name, p, False) for name, group in REFUSED for p in group]
for _ in range(80):  # a spread of parcels on both sides of every limit
    sides = [rng.randint(1, 160), rng.randint(1, 110), rng.randint(1, 60)]
    rng.shuffle(sides)
    p = parcel(rng.randint(1, 4), rng.randint(1, 34000), sides)
    cases.append(("a generated parcel", p, carriable(p)))

problems = []
for name, p, accept in cases:
    status, body = call(p)
    if accept and not priced(status, body):
        problems.append(f"{name} {p}: must be priced, got status {status} and {body!r}")
    if not accept and not refused(status, body):
        problems.append(f"{name} {p}: must be refused with status 2, got status {status} and {body!r}")

accepted = sum(1 for _, _, a in cases if a)
finish(problems, f"limits ok: {accepted} parcels priced and {len(cases) - accepted} refused")
