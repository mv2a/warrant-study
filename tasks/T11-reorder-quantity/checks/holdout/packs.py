"""H2 (G2): the units wanted are the units needed rounded up to whole packs, exact multiples left alone."""

from _cmd import call, finish
from _model import needed, product, random_product, random_skus, rng_for, wanted

BUDGET = 10**12
# (units needed, pack size): need is set through the safety stock alone.
SIMPLE = [(0, 12), (1, 12), (11, 12), (12, 12), (13, 12), (24, 12), (25, 12), (7, 1), (499, 500),
          (500, 500), (501, 500), (1000, 250), (1001, 250), (5, 5), (6, 5), (99, 100), (0, 1)]
problems = []


def wanted_by_sku(products):
    status, body = call({"budget_cents": BUDGET, "products": products})
    if status != 0 or not isinstance(body, dict) or not isinstance(body.get("orders"), list):
        return {}
    return {o.get("sku"): o.get("wanted") for o in body["orders"] if isinstance(o, dict)}


for need, pack in SIMPLE:
    p = product(f"G2-{need}-{pack}", safety_stock=need, pack_size=pack)
    got = wanted_by_sku([p]).get(p["sku"])
    if got != wanted(p):
        problems.append(f"{need} needed in packs of {pack}: expected {wanted(p)} wanted, got {got!r}")

# Needs close to and exactly at multiples of the pack size, reached through stock, demand and lead time.
rng = rng_for(110202)
generated = []
while len(generated) < 60:
    pack = rng.choice([2, 3, 4, 5, 6, 8, 10, 12, 20, 24, 25, 48, 50, 100])
    need = pack * rng.randint(1, 9) + rng.choice([0, 0, 0, -1, 1])
    daily, lead, safety = rng.randint(0, 30), rng.randint(0, 14), rng.randint(0, 40)
    position = daily * lead + safety - need
    if position < 0:
        continue
    on_order = rng.randint(0, position)
    p = product("", position - on_order, on_order, daily, lead, safety, pack)
    assert needed(p) == need
    generated.append(p)
# ...and some wholly random products.
for _ in range(30):
    generated.append(random_product(rng, ""))
skus = random_skus(rng, len(generated))
for p, sku in zip(generated, skus):
    p["sku"] = sku
for start in range(0, len(generated), 15):
    batch = generated[start:start + 15]
    got = wanted_by_sku(batch)
    for p in batch:
        if got.get(p["sku"]) != wanted(p):
            problems.append(f"{needed(p)} needed in packs of {p['pack_size']} ({p}): expected {wanted(p)} wanted, got {got.get(p['sku'])!r}")

finish(problems, f"packs ok: {len(SIMPLE)} simple needs and {len(generated)} generated products")
