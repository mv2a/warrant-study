"""X3 (G3): the sharers pool every item any sharer ordered, and only those, and each pays
an equal part of the pool whatever they ordered, even nothing.

Parts are checked at a 0% tip, where each share is the diner's part of the subtotal
whatever the tip rule: when the pool splits evenly every sharer must pay exactly
pool / sharers, and when it does not, each must pay that amount rounded down or one cent
more. With a tip, whatever the tip rule, equal parts must still mean equal payments, so
the sharers' shares are never more than one cent apart."""

import random

from _cmd import call, finish
from _model import bill, random_bill, round_bill

# (diners, orders, {sharer: exact share}) at a 0% tip, worked out by hand.
HAND = [
    ([("Ines", "share"), ("Galo", "share"), ("Tove", "share")],
     [("Galo", 3000), ("Tove", 600)], {"Ines": 1200, "Galo": 1200, "Tove": 1200}),
    ([("Brix", "share"), ("Hedda", "share")],
     [("Brix", 4400), ("Hedda", 100), ("Brix", 300)], {"Brix": 2400, "Hedda": 2400}),
    ([("Oda", "own"), ("Pim", "share"), ("Rune", "own")],
     [("Oda", 900), ("Pim", 2100), ("Rune", 1000)], {"Pim": 2100}),
    ([("Suvi", "share"), ("Yara", "own"), ("Zeno", "share"), ("Elio", "share")],
     [("Yara", 9000), ("Suvi", 300), ("Elio", 600)], {"Suvi": 300, "Zeno": 300, "Elio": 300}),
    ([("Fumi", "share"), ("Caio", "share"), ("Mirte", "share"), ("Nell", "share"), ("Oda", "share"),
      ("Pim", "share")], [("Mirte", 100)] * 6,
     {"Fumi": 100, "Caio": 100, "Mirte": 100, "Nell": 100, "Oda": 100, "Pim": 100}),
    ([("Tove", "own"), ("Aroha", "share"), ("Björn", "share")], [("Tove", 5000)], {"Aroha": 0, "Björn": 0}),
]

problems = []
count = 0


def sharers_paid(request, label):
    """The shares of the sharers, in listing order, or None after noting a problem."""
    global count
    count += 1
    status, body = call(request)
    shares = body.get("shares") if isinstance(body, dict) else None
    if status != 0 or not isinstance(shares, dict):
        problems.append(f"{label}: expected shares, got {body!r} (status {status})")
        return None
    return {d["name"]: shares.get(d["name"]) for d in request["diners"] if d["pays"] == "share"}


def pool_of(request):
    pays = {d["name"]: d["pays"] for d in request["diners"]}
    return sum(i["price_cents"] for i in request["items"] if pays[i["diner"]] == "share")


for k, (diners, orders, want) in enumerate(HAND, 1):
    paid = sharers_paid(bill(diners, orders, 0), f"bill {k}")
    if paid is not None and paid != want:
        problems.append(f"bill {k}: sharers should pay {want}, got {paid}")

# Untipped bills, evenly and unevenly split pools.
rng = random.Random(4417093)
made = 0
while made < 40:
    request = random_bill(rng, tips=[0])
    n = sum(1 for d in request["diners"] if d["pays"] == "share")
    if n == 0:
        continue
    made += 1
    pool = pool_of(request)
    if made <= 20 and pool % n:
        sharer = next(d["name"] for d in request["diners"] if d["pays"] == "share")
        request["items"].append({"diner": sharer, "price_cents": n - pool % n})
        pool += n - pool % n
    low = pool // n
    paid = sharers_paid(request, f"untipped bill {made}")
    if paid is None:
        continue
    if not all(type(v) is int and low <= v <= low + (1 if pool % n else 0) for v in paid.values()):
        exact = f"{low}" if pool % n == 0 else f"{low} or {low + 1}"
        problems.append(f"untipped bill {made}: the pool of {pool} over {n} sharers means each pays {exact}, got {paid}")

# Tipped bills, some with whole-hundred pools and some with odd cents: equal parts, equal payments.
rng = random.Random(4417094)
tipped = [round_bill(rng, need_share=True) for _ in range(15)]
while len(tipped) < 40:
    request = random_bill(rng)
    if sum(1 for d in request["diners"] if d["pays"] == "share") >= 2 and request["tip_percent"] > 0:
        tipped.append(request)
for k, request in enumerate(tipped, 1):
    paid = sharers_paid(request, f"tipped bill {k}")
    if paid is None:
        continue
    values = list(paid.values())
    if not all(type(v) is int for v in values) or max(values) - min(values) > 1:
        problems.append(f"tipped bill {k}: sharers with equal parts should pay within a cent of each other, got {paid}")

finish(problems, f"sharers ok: {count} bills")
