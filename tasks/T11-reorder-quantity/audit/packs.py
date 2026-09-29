"""X5 (G2): units wanted are the units needed rounded up to the next whole pack, exact multiples unchanged, nothing for no need."""

from _cmd import call, finish
from _model import by_sku, needing, short

# (units needed, pack size, units wanted)
CASES = [
    (0, 12, 0), (-5, 12, 0), (-1, 1, 0), (0, 1, 0),
    (1, 12, 12), (11, 12, 12), (12, 12, 12), (13, 12, 24), (23, 12, 24), (24, 12, 24), (25, 12, 36),
    (7, 1, 7), (1, 1, 1),
    (3, 500, 500), (499, 500, 500), (500, 500, 500), (501, 500, 1000),
    (69, 7, 70), (70, 7, 70), (71, 7, 77), (140, 7, 140),
    (2, 2, 2), (3, 2, 4), (1, 2, 2),
    (10 ** 12 + 1, 1000, 10 ** 12 + 1000), (10 ** 12, 1000, 10 ** 12), (10 ** 12 - 1, 1000, 10 ** 12),
]
products = [needing(f"PK-{i:02d}", need, pack_size=pack, unit_cost_cents=1, priority=1 + i)
            for i, (need, pack, _) in enumerate(CASES)]

problems = []
status, body = call({"budget_cents": 10 ** 13, "products": products})
got = by_sku(body, "wanted")
if status != 0 or got is None:
    finish([f"expected status 0 and a plan, got status {status} and {short(body)}"], "")
for p, (need, pack, want) in zip(products, CASES):
    if got.get(p["sku"], 0) != want:
        problems.append(f"{p['sku']}: {need} needed in packs of {pack}, expected wanted={want}, got {got.get(p['sku'], 0)!r}")

# A few of the same boundaries alone in their request.
for need, pack, want in [(0, 12, 0), (12, 12, 12), (13, 12, 24), (1, 12, 12)]:
    status, body = call({"budget_cents": 10 ** 6, "products": [needing("PK-solo", need, pack_size=pack)]})
    got = by_sku(body, "wanted")
    if status != 0 or got is None or got.get("PK-solo", 0) != want:
        problems.append(f"alone, {need} needed in packs of {pack}: expected wanted={want}, got status {status} and {short(body, 100)}")

finish(problems, f"packs ok: {len(products)} products and 4 single-product requests")
