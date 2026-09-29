"""X2 (G2): an own-payer is charged for exactly their own items and nobody else's, and an
own-payer who ordered nothing pays nothing.

Parts are checked at a 0% tip, where each share is the diner's part of the subtotal
whatever the tip rule, and the pool divides evenly among the sharers, so no leftover
cents arise: an own-payer's share must be exactly the sum of their own items. Bills with
tips and odd cents elsewhere at the table check that an own-payer who ordered nothing
still pays 0."""

import random

from _cmd import call, finish
from _model import bill, random_bill, NAMES

# (diners, orders, tip_percent, {own-payer: exact share}), worked out by hand.
HAND = [
    ([("Brix", "own"), ("Oda", "own"), ("Pim", "own")],
     [("Brix", 1200), ("Oda", 800), ("Brix", 400), ("Pim", 1600)], 0, {"Brix": 1600, "Oda": 800, "Pim": 1600}),
    ([("Tove", "own"), ("Galo", "own")], [("Galo", 2500)], 20, {"Tove": 0}),
    ([("Suvi", "share"), ("Rune", "own"), ("Yara", "share")],
     [("Suvi", 5000), ("Rune", 700), ("Yara", 1000), ("Suvi", 1000)], 0, {"Rune": 700}),
    ([("Aroha", "own"), ("Björn", "share"), ("Ines", "share")],
     [("Björn", 300), ("Aroha", 450), ("Ines", 300), ("Aroha", 250), ("Björn", 400)], 0, {"Aroha": 700}),
    ([("Galo", "own"), ("Nell", "share"), ("Oda", "share"), ("Pim", "own")],
     [("Galo", 1500), ("Nell", 2000), ("Pim", 300), ("Oda", 400)], 0, {"Galo": 1500, "Pim": 300}),
    ([("Hedda", "share"), ("Caio", "own"), ("Mirte", "own")],
     [("Hedda", 9900), ("Mirte", 100)], 0, {"Caio": 0, "Mirte": 100}),
    ([("Hedda", "share"), ("Caio", "own"), ("Mirte", "own")],
     [("Hedda", 9900), ("Mirte", 100)], 100, {"Caio": 0}),
    ([("Elio", "own")], [("Elio", 1), ("Elio", 2), ("Elio", 3)], 0, {"Elio": 6}),
    ([("Suvi", "own"), ("Yara", "share")], [("Yara", 4000), ("Suvi", 1)], 0, {"Suvi": 1}),
]


def untipped_bill(rng):
    """A random 0%-tip bill with at least one own-payer and a pool that splits evenly."""
    names = rng.sample(NAMES, rng.randint(2, 7))
    diners = [(n, rng.choice(["own", "share"])) for n in names]
    if all(p == "share" for _, p in diners):
        diners[-1] = (diners[-1][0], "own")
    owners = [n for n, p in diners if p == "own"]
    sharers = [n for n, p in diners if p == "share"]
    orders = [(n, rng.randint(1, 9999)) for n in owners for _ in range(rng.choice([0, 1, 1, 2, 3]))]
    if sharers:
        orders += [(rng.choice(sharers), rng.randint(1, 9999)) for _ in range(rng.randint(0, 5))]
        pool = sum(c for n, c in orders if n in sharers)
        if pool % len(sharers) or pool == 0:
            orders.append((rng.choice(sharers), len(sharers) - pool % len(sharers)))
    if not orders:
        orders.append((owners[0], rng.randint(1, 9999)))
    rng.shuffle(orders)
    want = {n: sum(c for m, c in orders if m == n) for n in owners}
    return bill(diners, orders, 0), want


problems = []
count = 0


def check(request, want, label):
    global count
    count += 1
    status, body = call(request)
    shares = body.get("shares") if isinstance(body, dict) else None
    if status != 0 or not isinstance(shares, dict):
        problems.append(f"{label}: expected shares, got {body!r} (status {status})")
        return
    for name, cents in want.items():
        if shares.get(name) != cents:
            problems.append(f"{label}: own-payer {name} should pay {cents}, got {shares.get(name)!r}")


for k, (diners, orders, tip_percent, want) in enumerate(HAND, 1):
    check(bill(diners, orders, tip_percent), want, f"bill {k}")

rng = random.Random(7310041)
for k in range(40):
    request, want = untipped_bill(rng)
    check(request, want, f"untipped bill {k + 1}")

# An own-payer with no items, slipped into bills whose other amounts have odd cents.
rng = random.Random(7310042)
for k in range(20):
    request = random_bill(rng, max_diners=6)
    request["diners"].insert(rng.randint(0, len(request["diners"])), {"name": "Quiet", "pays": "own"})
    check(request, {"Quiet": 0}, f"bill with an idle own-payer {k + 1}")

finish(problems, f"own-payers ok: {count} bills")
