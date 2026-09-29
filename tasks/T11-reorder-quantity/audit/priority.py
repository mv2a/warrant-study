"""X10 (G4): a smaller priority number is always funded first, whatever the request order, prices and spacing of the numbers."""

from _cmd import finish
from _order import check_order, one_pack

# (label, [(sku, priority, pack size, pack price)])
CASES = [
    ("priorities listed in reverse", [("RV-a", 3, 4, 360), ("RV-b", 2, 90, 360), ("RV-c", 1, 1, 360)]),
    ("non-consecutive priorities", [("NC-a", 40, 4, 360), ("NC-b", 7, 90, 360), ("NC-c", 250, 1, 360), ("NC-d", 3, 36, 360)]),
    ("priorities compared as numbers, not text",
     [("NT-a", 10, 12, 360), ("NT-b", 9, 5, 360), ("NT-c", 2, 4, 360), ("NT-d", 11, 90, 360), ("NT-e", 100, 1, 360)]),
    ("large priority numbers", [("LG-a", 1000000, 4, 360), ("LG-b", 999999, 1, 360), ("LG-c", 1000001, 36, 360), ("LG-d", 5, 12, 360)]),
    ("priority 1 listed last of six",
     [("L6-a", 6, 4, 360), ("L6-b", 5, 90, 360), ("L6-c", 4, 1, 360), ("L6-d", 3, 36, 360), ("L6-e", 2, 12, 360), ("L6-f", 1, 5, 360)]),
    ("the urgent product is the dearest", [("DP-a", 2, 4, 400), ("DP-b", 1, 3, 1500), ("DP-c", 3, 10, 250)]),
    ("the urgent product is the cheapest, listed last", [("CP-a", 8, 6, 1200), ("CP-b", 5, 2, 900), ("CP-c", 1, 1, 7)]),
    ("the least urgent product is listed first and is the cheapest",
     [("LU-a", 30, 1, 100), ("LU-b", 20, 2, 600), ("LU-c", 10, 1, 150), ("LU-d", 25, 5, 2000)]),
]
problems = []
for label, spec in CASES:
    products = [one_pack(sku, priority, pack_size=size, price=cost) for sku, priority, size, cost in spec]
    check_order(label, products, problems)

finish(problems, f"priority order ok: {len(CASES)} requests at every budget step")
