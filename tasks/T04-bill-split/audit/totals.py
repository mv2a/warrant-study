"""X1 (G1): subtotal is the sum of the prices, the tip is tip_percent percent of it to the
nearest cent with an exact half cent rounded up, and the total is subtotal plus tip.
Only subtotal_cents, tip_cents and total_cents are checked here."""

import random

from _cmd import call, finish
from _model import bill, cut, random_bill, subtotal, tip, NAMES

# (diners, orders, tip_percent, subtotal, tip), each tip worked out by hand from G1.
HAND = [
    ([("Oda", "own")], [("Oda", 50)], 1, 50, 1),                       # 0.5 -> 1, not 0
    ([("Oda", "own")], [("Oda", 250)], 1, 250, 3),                     # 2.5 -> 3, not 2
    ([("Oda", "own")], [("Oda", 49)], 1, 49, 0),                       # 0.49 -> 0
    ([("Oda", "own")], [("Oda", 51)], 1, 51, 1),                       # 0.51 -> 1
    ([("Brix", "share"), ("Nell", "share")], [("Brix", 1000), ("Nell", 225)], 10, 1225, 123),  # 122.5
    ([("Brix", "share"), ("Nell", "own")], [("Nell", 1221)], 10, 1221, 122),                   # 122.1
    ([("Brix", "own"), ("Nell", "own")], [("Brix", 1000), ("Nell", 229)], 10, 1229, 123),      # 122.9
    ([("Tove", "own")], [("Tove", 1)], 50, 1, 1),                      # 0.5 -> 1
    ([("Tove", "own")], [("Tove", 1)], 49, 1, 0),                      # 0.49 -> 0
    ([("Tove", "own")], [("Tove", 1)], 99, 1, 1),                      # 0.99 -> 1
    ([("Tove", "own")], [("Tove", 1)], 100, 1, 1),
    ([("Tove", "own")], [("Tove", 1)], 0, 1, 0),
    ([("Ines", "share"), ("Galo", "share"), ("Pim", "own")],
     [("Ines", 3333), ("Galo", 3333), ("Pim", 3334)], 15, 10000, 1500),
    ([("Rune", "own"), ("Suvi", "share")], [("Rune", 999), ("Suvi", 1), ("Rune", 250)], 100, 1250, 1250),
    ([("Zeno", "share"), ("Elio", "share"), ("Hedda", "share")],
     [("Zeno", 7), ("Elio", 7), ("Hedda", 7)], 50, 21, 11),            # 10.5 -> 11
    ([("Fumi", "own")], [("Fumi", 150)], 3, 150, 5),                   # 4.5 -> 5, not 4
    ([("Fumi", "own")], [("Fumi", 350)], 7, 350, 25),                  # 24.5 -> 25, not 24
    ([("Caio", "own"), ("Mirte", "share")], [("Caio", 2000), ("Mirte", 50)], 1, 2050, 21),  # 20.5
    ([("Caio", "own")], [("Caio", 1005)], 1, 1005, 10),                # 10.05 -> 10
    ([("Caio", "own")], [("Caio", 105)], 10, 105, 11),                 # 10.5 -> 11, not 10
    ([("Ngozi", "own"), ("Aroha", "share")],
     [("Ngozi" if k % 2 else "Aroha", 1) for k in range(40)], 13, 40, 5),  # forty 1-cent items
    ([("Björn", "own")], [("Björn", 9999), ("Björn", 9999), ("Björn", 2)], 33, 20000, 6600),
    ([("Björn", "own")], [("Björn", 1515)], 33, 1515, 500),            # 499.95 -> 500
    ([("Björn", "own")], [("Björn", 3)], 17, 3, 1),                    # 0.51 -> 1
    ([("Björn", "own")], [("Björn", 3)], 16, 3, 0),                    # 0.48 -> 0
    ([("Björn", "own")], [("Björn", 101)], 50, 101, 51),               # 50.5 -> 51
    ([("Björn", "own")], [("Björn", 97)], 50, 97, 49),                 # 48.5 -> 49, not 48
    ([("Yara", "share"), ("Zoë", "own")], [("Zoë", 4001), ("Yara", 4000)], 25, 8001, 2000),  # 2000.25
]

cases = [(bill(d, o, t), s, x) for d, o, t, s, x in HAND]

rng = random.Random(5528193)
for _ in range(45):
    request = random_bill(rng)
    s = subtotal(request)
    cases.append((request, s, tip(s, request["tip_percent"])))

# Bills whose tip is exactly a half cent more than a whole number of cents.
rng = random.Random(5528194)
while len(cases) < len(HAND) + 45 + 25:
    tip_percent = rng.randint(1, 100)
    s = rng.randint(1, 60000)
    if s * tip_percent % 100 != 50:
        continue
    names = rng.sample(NAMES, rng.randint(1, 4))
    diners = [(n, rng.choice(["own", "share"])) for n in names]
    orders = [(rng.choice(names), c) for c in cut(rng, s, rng.randint(1, 5))]
    cases.append((bill(diners, orders, tip_percent), s, (s * tip_percent + 50) // 100))

problems = []
for request, s, t in cases:
    status, body = call(request)
    want = {"subtotal_cents": s, "tip_cents": t, "total_cents": s + t}
    got = {k: body.get(k) for k in want} if isinstance(body, dict) else body
    if status != 0 or got != want:
        problems.append(f"{len(request['items'])} items, tip {request['tip_percent']}%: "
                        f"expected {want}, got {got!r} (status {status})")

finish(problems, f"totals ok: {len(cases)} bills")
