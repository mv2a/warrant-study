"""H4: everyone tips at the same rate on their own part of the subtotal."""

import random

from _bills import NAMES, bill, fair_amounts, near, price, random_bill, shares_of
from _cmd import call, finish

rng = random.Random(4044)
requests = [
    # Very unequal parts and a large tip: the tip must follow each diner's part.
    bill([("Zara", "own"), ("Omar", "own")], [("Zara", 100), ("Omar", 9900)], 100),
    bill([("Zara", "own"), ("Omar", "own"), ("Beth", "own")], [("Zara", 500), ("Omar", 1500), ("Beth", 8000)], 20),
    bill([("Yuki", "share"), ("Carl", "share"), ("Nia", "own")], [("Yuki", 300), ("Nia", 12000)], 50),
    bill([("Hugo", "own"), ("Asha", "share"), ("Theo", "share"), ("Mei", "share")],
         [("Hugo", 45), ("Asha", 6000), ("Theo", 3000)], 25),
    # No tip: everyone pays their part.
    bill([("Rui", "own"), ("Dana", "own"), ("Ilse", "share"), ("Kofi", "share")],
         [("Rui", 1234), ("Dana", 5678), ("Ilse", 910), ("Kofi", 1112)], 0),
]
for _ in range(90):
    request = random_bill(rng, diners=(2, 9), tip_percent=rng.choice([5, 15, 18, 20, 25, 33, 50, 75, 100]))
    # Make one diner's order far bigger than the rest.
    big = rng.choice(request["items"])
    big["price_cents"] += rng.randint(10000, 80000)
    requests.append(request)

problems = []
for request in requests:
    status, body = call(request)
    got = shares_of(body)
    if status != 0 or got is None:
        problems.append(f"{[d['name'] for d in request['diners']]}: expected shares, got {body!r} (status {status})")
        continue
    shares, total = got
    fair = fair_amounts(request, total)
    wrong = {n: (round(float(f), 2), shares.get(n)) for n, f in fair.items() if not near(shares.get(n), f)}
    if wrong:
        problems.append(f"at {request['tip_percent']}% tip, fair amount and share differ by a cent or more: {wrong}")

finish(problems, f"tip rate ok: {len(requests)} bills")
