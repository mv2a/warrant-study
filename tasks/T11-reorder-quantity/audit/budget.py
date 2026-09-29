"""X7 (G3): one product buys the most whole packs, up to the packs it wants, that the budget pays for in full, never more."""

from _cmd import call, finish
from _model import by_sku, needing, short

problems = []
sent = []


def expect(label, product, budget, quantity):
    sent.append(label)
    status, body = call({"budget_cents": budget, "products": [product]})
    got = by_sku(body, "quantity")
    if status != 0 or got is None or got.get(product["sku"], 0) != quantity:
        problems.append(f"{label}, budget {budget}: expected quantity {quantity}, got status {status} and {short(body, 110)}")


# Wants 3 packs of 10 units at 25 cents a unit: a pack costs 250.
three = needing("BG-3x10", 30, pack_size=10, unit_cost_cents=25)
for budget, quantity in [(0, 0), (1, 0), (249, 0), (250, 10), (251, 10), (499, 10), (500, 20), (749, 20),
                         (750, 30), (751, 30), (100000, 30), (10 ** 12, 30)]:
    expect("3 packs of 10 at 25c", three, budget, quantity)

# Whole packs, not loose units: packs of 6 at 100 cents cost 600 each.
six = needing("BG-2x6", 12, pack_size=6, unit_cost_cents=100)
for budget, quantity in [(1000, 6), (599, 0), (1199, 6), (1200, 12), (5000, 12)]:
    expect("2 packs of 6 at 100c", six, budget, quantity)

# Packs of one at a high unit cost.
loose = needing("BG-5x1", 5, pack_size=1, unit_cost_cents=999)
for budget, quantity in [(998, 0), (999, 1), (1998, 2), (4994, 4), (4995, 5), (4996, 5)]:
    expect("5 packs of 1 at 999c", loose, budget, quantity)

# A product that wants nothing buys nothing, whatever the budget.
for budget in (0, 5, 10 ** 9):
    expect("needs nothing", needing("BG-none", -4, pack_size=10, unit_cost_cents=1), budget, 0)

# Many packs, budget in between.
many = needing("BG-40x25", 1000, pack_size=25, unit_cost_cents=3)   # 40 packs of 75 cents
for budget, quantity in [(74, 0), (75, 25), (2999, 975), (3000, 1000), (1234, 400)]:
    expect("40 packs of 25 at 3c", many, budget, quantity)

finish(problems, f"single-product budgets ok: {len(sent)} requests")
