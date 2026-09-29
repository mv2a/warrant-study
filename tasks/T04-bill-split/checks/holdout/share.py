"""H3: sharers pool what they ordered and split it equally."""

import random

from _bills import NAMES, bill, fair_amounts, near, price, shares_of, tip
from _cmd import call, finish

rng = random.Random(4043)
requests = [
    # Four sharers whose pool leaves 3 odd cents; one ordered nothing.
    bill([("Theo", "share"), ("Mei", "share"), ("Rui", "share"), ("Dana", "share")],
         [("Theo", 1001), ("Mei", 1001), ("Rui", 1001)], 0),
    bill([("Theo", "share"), ("Mei", "share"), ("Rui", "share")], [("Rui", 2), ("Theo", 3)], 0),
    # Only own-payers ordered anything: the sharers' pool is empty and they pay nothing.
    bill([("Ilse", "share"), ("Kofi", "own"), ("Pia", "share")], [("Kofi", 2500)], 20),
    # One sharer ordered everything the sharers had.
    bill([("Emil", "share"), ("Wes", "own"), ("Lars", "share"), ("Gia", "share"), ("Finn", "share")],
         [("Emil", 7777), ("Wes", 1234)], 25),
]
for _ in range(100):
    names = rng.sample(NAMES, rng.randint(2, 9))
    sharers = rng.randint(2, min(6, len(names)))
    pays = [(n, "share" if i < sharers else "own") for i, n in enumerate(names)]
    rng.shuffle(pays)
    orders = [(n, price(rng)) for n, _ in pays if rng.random() < 0.75 for _ in range(rng.randint(1, 3))]
    if not any(p == "share" and any(o == n for o, _ in orders) for n, p in pays):
        orders.append((next(n for n, p in pays if p == "share"), price(rng)))
    rng.shuffle(orders)
    requests.append(bill(pays, orders, tip(rng)))

problems = []


def check(request, label=""):
    status, body = call(request)
    got = shares_of(body)
    if status != 0 or got is None:
        problems.append(f"{label}{[d['name'] for d in request['diners']]}: expected shares, got {body!r} (status {status})")
        return None
    shares, total = got
    fair = fair_amounts(request, total)
    sharers = [d["name"] for d in request["diners"] if d["pays"] == "share"]
    paid = [shares.get(n) for n in sharers]
    for n in sharers:
        if not near(shares.get(n), fair[n]):
            problems.append(f"{label}sharer {n}: fair amount {float(fair[n]):.2f} (an equal part of the pool), got {shares.get(n)!r}")
            return shares
    if max(paid) - min(paid) > 1:
        problems.append(f"{label}sharers {sharers} should pay within a cent of each other, got {paid}")
    return shares


for request in requests:
    check(request)

# Moving items between sharers must not change anything: what each sharer ordered doesn't matter.
for request in requests[4:40]:
    before = check(request)
    sharers = [d["name"] for d in request["diners"] if d["pays"] == "share"]
    moved = {**request, "items": [
        {**i, "diner": rng.choice(sharers)} if i["diner"] in sharers else i for i in request["items"]
    ]}
    after = check(moved, "after moving sharers' items: ")
    if before is not None and after is not None and before != after:
        problems.append(f"moving items between sharers changed the shares from {before} to {after}")

finish(problems, f"sharers ok: {len(requests)} bills and 36 with items moved between sharers")
