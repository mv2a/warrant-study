"""H2: own-payers pay for exactly their own items; one who ordered nothing pays nothing."""

import random

from _bills import NAMES, bill, fair_amounts, near, price, shares_of, tip
from _cmd import call, finish

rng = random.Random(4042)
requests = [
    # An own-payer who ordered nothing, listed first, beside sharers with a real pool.
    bill([("Omar", "own"), ("Beth", "share"), ("Yuki", "share")], [("Beth", 1800), ("Yuki", 2601)], 18),
    bill([("Beth", "share"), ("Omar", "own"), ("Carl", "own")], [("Beth", 999), ("Carl", 1500)], 20),
    # An own-payer with many items, and one whose items come between everyone else's.
    bill([("Nia", "own"), ("Hugo", "share"), ("Asha", "own")],
         [("Nia", 150), ("Hugo", 2200), ("Nia", 275), ("Asha", 1330), ("Nia", 999), ("Hugo", 45)], 15),
]
for _ in range(110):
    names = rng.sample(NAMES, rng.randint(3, 8))
    # At least one own-payer with items, one own-payer without, and one sharer with items.
    roles = ["own-items", "own-empty", "share-items"] + [rng.choice(["own-items", "own-empty", "share-items", "share-empty"]) for _ in names[3:]]
    rng.shuffle(roles)
    pays = [(n, r.split("-")[0]) for n, r in zip(names, roles)]
    orders = [(n, price(rng)) for n, r in zip(names, roles) if r.endswith("items") for _ in range(rng.randint(1, 3))]
    rng.shuffle(orders)
    requests.append(bill(pays, orders, tip(rng)))

problems = []
for request in requests:
    status, body = call(request)
    got = shares_of(body)
    if status != 0 or got is None:
        problems.append(f"{[d['name'] for d in request['diners']]}: expected shares, got {body!r} (status {status})")
        continue
    shares, total = got
    fair = fair_amounts(request, total)
    ordered = {i["diner"] for i in request["items"]}
    for d in request["diners"]:
        name = d["name"]
        if d["pays"] != "own":
            continue
        if name not in ordered:
            if shares.get(name) != 0:
                problems.append(f"{name} pays own and ordered nothing, so should pay 0, got {shares.get(name)!r}")
        elif not near(shares.get(name), fair[name]):
            problems.append(f"{name} pays own: fair amount {float(fair[name]):.2f} for their own items, got {shares.get(name)!r}")

finish(problems, f"own-payers ok: {len(requests)} bills")
