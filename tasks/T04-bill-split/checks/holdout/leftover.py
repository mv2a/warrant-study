"""H6: leftover cents go to the largest fractional parts, ties to the diner listed earlier."""

import random

from _bills import bill, expected_shares, random_bill, shares_of
from _cmd import call, finish

rng = random.Random(4046)
requests = [
    # Equal fractional parts, names not in alphabetical order: the earlier-listed diner wins.
    bill([("Zara", "share"), ("Beth", "share"), ("Mei", "share")], [("Beth", 1000)], 0),
    bill([("Zara", "share"), ("Beth", "share"), ("Mei", "share")], [("Mei", 1001)], 0),
    bill([("Yuki", "own"), ("Carl", "own"), ("Asha", "own")], [("Yuki", 1), ("Carl", 1), ("Asha", 1)], 50),
    # The largest fractional part belongs to the diner listed last.
    bill([("Nia", "own"), ("Hugo", "own"), ("Theo", "own")], [("Nia", 100), ("Hugo", 100), ("Theo", 107)], 15),
    # An own-payer whose fair amount is already whole never gets a leftover cent.
    bill([("Omar", "own"), ("Rui", "share"), ("Dana", "share"), ("Pia", "share")],
         [("Omar", 1000), ("Rui", 1000)], 0),
    # No leftover at all.
    bill([("Ilse", "own"), ("Kofi", "own")], [("Ilse", 1500), ("Kofi", 2500)], 20),
]
requests += [random_bill(rng, diners=(2, 10)) for _ in range(150)]
requests += [random_bill(rng, diners=(3, 10), share=0.8, empty=0.4) for _ in range(50)]

problems = []
for request in requests:
    status, body = call(request)
    got = shares_of(body)
    if status != 0 or got is None:
        problems.append(f"{[d['name'] for d in request['diners']]}: expected shares, got {body!r} (status {status})")
        continue
    shares, total = got
    want = expected_shares(request, total)
    if shares != want:
        diff = {n: (want[n], shares.get(n)) for n in want if shares.get(n) != want[n]}
        problems.append(f"{[d['name'] for d in request['diners']]} total {total}: expected, got {diff}")

finish(problems, f"leftover cents ok: {len(requests)} bills")
