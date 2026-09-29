"""X2 (G2): masses convert with the exact definitions of mg, g, kg, t, oz, lb and st."""

import itertools

from _audit import MASS, check_conversions, expected, finish

# Worked out by hand from G2 (1 lb = 453.59237 g, 1 oz = 1/16 lb, 1 st = 14 lb, 1 t = 1000 kg).
LITERAL = [
    ("1", "lb", "g", 5, "453.59237"),
    ("1", "lb", "kg", 8, "0.45359237"),
    ("1", "lb", "mg", 2, "453592.37"),
    ("1", "lb", "oz", 0, "16"),
    ("1", "st", "lb", 0, "14"),
    ("1", "st", "oz", 0, "224"),
    ("1", "st", "kg", 8, "6.35029318"),
    ("1", "oz", "g", 9, "28.349523125"),
    ("1", "oz", "mg", 6, "28349.523125"),
    ("1", "oz", "lb", 4, "0.0625"),
    ("1", "t", "kg", 0, "1000"),
    ("1", "t", "mg", 0, "1000000000"),
    ("1", "g", "mg", 0, "1000"),
    ("1", "mg", "g", 3, "0.001"),
    ("1", "kg", "lb", 12, "2.204622621849"),
    ("1", "g", "oz", 12, "0.035273961950"),
    ("1", "kg", "st", 12, "0.157473044418"),
    ("1", "t", "lb", 6, "2204.622622"),
    ("10", "st", "kg", 3, "63.503"),
    ("100", "g", "oz", 4, "3.5274"),
    ("1", "st", "t", 12, "0.006350293180"),
]

# Every ordered pair of mass units, twice: 1 unit at 12 places, and another amount at 0 to 12 places.
AMOUNTS = ["3.75", "0.009", "1250", "64.0625", "11", "0.00042", "90001"]
MATRIX = []
for i, (a, b) in enumerate(itertools.product(MASS, repeat=2)):
    MATRIX.append(("1", a, b, 12, expected("1", a, b, 12)))
    value, places = AMOUNTS[i % len(AMOUNTS)], (i * 5) % 13
    MATRIX.append((value, a, b, places, expected(value, a, b, places)))

problems = check_conversions(LITERAL + MATRIX)
finish(problems, f"masses ok: {len(LITERAL)} hand-worked conversions and {len(MATRIX)} across all 49 unit pairs")
