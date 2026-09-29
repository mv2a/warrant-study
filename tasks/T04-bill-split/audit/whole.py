"""X5 (C1): every diner gets exactly one share, every share is a whole number of cents,
zero or more, and the shares add up exactly to total_cents.

Generated bills of many shapes, plus bills where rounding each share to the nearest cent
would overshoot the total and push a last diner below zero."""

import random

from _cmd import call, finish
from _model import bill, random_bill

cases = [
    # Three sharers each owe 66 2/3 cents and the own-payer listed last ordered nothing.
    bill([("Galo", "share"), ("Tove", "share"), ("Rune", "share"), ("Yara", "own")], [("Tove", 200)], 0),
    bill([("Nell", "share"), ("Oda", "share"), ("Pim", "share"), ("Brix", "share"), ("Ines", "own")],
         [("Nell", 7), ("Oda", 1)], 12),
    bill([("Suvi", "own")], [("Suvi", 1)], 0),
    bill([("Suvi", "own")], [("Suvi", 1)], 100),
    bill([("Ngozi", "share"), ("Aroha ", "own"), ("李雷", "share"), ("Zoë", "share")],
         [("Aroha ", 999), ("Zoë", 1001), ("李雷", 2)], 17),
    bill([(f"Seat {k:02d}", "share" if k % 3 else "own") for k in range(40)],
         [(f"Seat {(k * 7) % 40:02d}", 37 + (k * 131) % 2900) for k in range(160)], 19),
    bill([(f"Seat {k:02d}", "share") for k in range(29)], [("Seat 28", 1000)], 0),
]

rng = random.Random(6153307)
for _ in range(90):
    cases.append(random_bill(rng))
for _ in range(20):
    cases.append(random_bill(rng, max_diners=12, max_items=30, max_price=500))
for _ in range(10):
    cases.append(random_bill(rng, max_diners=4, max_items=3, max_price=9))

problems = []
for k, request in enumerate(cases, 1):
    names = [d["name"] for d in request["diners"]]
    status, body = call(request)
    shares = body.get("shares") if isinstance(body, dict) else None
    total = body.get("total_cents") if isinstance(body, dict) else None
    if status != 0 or not isinstance(shares, dict):
        problems.append(f"bill {k}: expected shares, got {body!r} (status {status})")
    elif sorted(shares) != sorted(names):
        problems.append(f"bill {k}: expected exactly one share for each of {names}, got {sorted(shares)}")
    elif not all(type(v) is int and v >= 0 for v in shares.values()):
        bad = {n: v for n, v in shares.items() if not (type(v) is int and v >= 0)}
        problems.append(f"bill {k}: shares must be whole cents, zero or more, got {bad}")
    elif sum(shares.values()) != total:
        problems.append(f"bill {k}: shares add up to {sum(shares.values())}, total_cents is {total!r}")

finish(problems, f"whole shares ok: {len(cases)} bills")
