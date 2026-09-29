"""H5: one share per diner, whole cents, never negative, adding up exactly to the total."""

import random

from _bills import bill, random_bill
from _cmd import call, finish

rng = random.Random(4045)
requests = [
    bill([("Zara", "share"), ("Omar", "share"), ("Beth", "share")], [("Zara", 100)], 0),
    bill([("Zara", "share"), ("Omar", "share"), ("Beth", "share"), ("Yuki", "share"), ("Carl", "share"),
          ("Nia", "share"), ("Hugo", "share")], [("Nia", 1)], 100),
    bill([("Asha", "own"), ("Theo", "own"), ("Mei", "own")], [("Asha", 1), ("Theo", 1), ("Mei", 1)], 49),
    bill([("Rui", "own"), ("Dana", "share")], [("Rui", 1)], 0),
]
requests += [random_bill(rng, diners=(1, 15)) for _ in range(160)]
requests += [random_bill(rng, diners=(2, 12), share=1.0, empty=0.5) for _ in range(40)]

problems = []
for request in requests:
    names = [d["name"] for d in request["diners"]]
    status, body = call(request)
    shares = body.get("shares") if isinstance(body, dict) else None
    total = body.get("total_cents") if isinstance(body, dict) else None
    if status != 0 or not isinstance(shares, dict):
        problems.append(f"{names}: expected shares, got {body!r} (status {status})")
    elif sorted(shares) != sorted(names):
        problems.append(f"{names}: expected exactly one share per diner, got {sorted(shares)}")
    elif not all(type(v) is int and v >= 0 for v in shares.values()):
        problems.append(f"{names}: every share must be a whole number of cents, zero or more, got {shares}")
    elif sum(shares.values()) != total:
        problems.append(f"{names}: shares add up to {sum(shares.values())}, but total_cents is {total!r}")

finish(problems, f"sums ok: {len(requests)} bills")
