"""X11 (G4): products with the same priority are funded in request order, not by sku, price or size."""

from _cmd import finish
from _order import check_order, one_pack

# (label, [(sku, priority, pack size, pack price)])
CASES = [
    ("two tied products, the later sku sorting first", [("ZZ-9", 1, 60, 360), ("AA-1", 1, 1, 360)]),
    ("three tied products", [("M-3", 4, 8, 360), ("M-1", 4, 360, 360), ("M-2", 4, 3, 360)]),
    ("ties interleaved with other priorities",
     [("IL-a", 5, 60, 360), ("IL-b", 2, 1, 360), ("IL-c", 5, 8, 360), ("IL-d", 2, 360, 360), ("IL-e", 1, 3, 360)]),
    ("a tie at a large priority after a smaller one",
     [("TL-z", 70, 20, 360), ("TL-y", 70, 60, 360), ("TL-x", 69, 1, 360), ("TL-w", 70, 8, 360)]),
    ("everything tied", [("ET-%s" % c, 3, size, 360) for c, size in zip("qwerty", [60, 1, 8, 360, 3, 20])]),
    ("the dearer tied product listed first", [("TP-X", 2, 7, 700), ("TP-Y", 2, 3, 300)]),
    ("the cheaper tied product listed first", [("TQ-X", 1, 2, 400), ("TQ-Y", 1, 5, 900)]),
    ("the bigger pack tied and listed second", [("TS-X", 6, 1, 50), ("TS-Y", 6, 500, 500), ("TS-Z", 6, 10, 50)]),
    ("a tie after a more urgent product", [("TR-A", 8, 10, 600), ("TR-B", 8, 10, 600), ("TR-C", 3, 1, 700)]),
]
problems = []
for label, spec in CASES:
    products = [one_pack(sku, priority, pack_size=size, price=cost) for sku, priority, size, cost in spec]
    check_order(label, products, problems)

finish(problems, f"ties ok: {len(CASES)} requests at every budget step")
