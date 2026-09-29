"""X3 (G3): volumes convert with the exact US definitions of ml, l, m3, floz, pt, qt and gal."""

import itertools

from _audit import VOLUME, check_conversions, expected, finish

# Worked out by hand from G3 (1 gal = 3785.411784 ml, 1 qt = 1/4 gal, 1 pt = 1/8 gal, 1 floz = 1/128 gal).
LITERAL = [
    ("1", "gal", "ml", 6, "3785.411784"),
    ("1", "gal", "l", 9, "3.785411784"),
    ("1", "gal", "m3", 12, "0.003785411784"),
    ("1", "gal", "qt", 0, "4"),
    ("1", "gal", "floz", 0, "128"),
    ("1", "qt", "pt", 0, "2"),
    ("1", "pt", "floz", 0, "16"),
    ("1", "qt", "floz", 0, "32"),
    ("1", "qt", "ml", 6, "946.352946"),
    ("1", "pt", "ml", 6, "473.176473"),
    ("1", "floz", "ml", 10, "29.5735295625"),
    ("2.5", "l", "ml", 0, "2500"),
    ("1", "m3", "l", 0, "1000"),
    ("1", "m3", "ml", 0, "1000000"),
    ("1", "ml", "l", 3, "0.001"),
    ("1", "l", "gal", 12, "0.264172052358"),
    ("1", "m3", "gal", 6, "264.172052"),
    ("1", "ml", "floz", 12, "0.033814022702"),
    ("1", "l", "floz", 6, "33.814023"),
    ("1", "l", "pt", 6, "2.113376"),
    ("1", "l", "qt", 6, "1.056688"),
    ("1", "floz", "gal", 12, "0.007812500000"),
    ("3", "floz", "pt", 4, "0.1875"),
]

# Every ordered pair of volume units, twice: 1 unit at 12 places, and another amount at 0 to 12 places.
AMOUNTS = ["12.5", "0.0625", "330", "2.75", "946", "0.00017", "55555"]
MATRIX = []
for i, (a, b) in enumerate(itertools.product(VOLUME, repeat=2)):
    MATRIX.append(("1", a, b, 12, expected("1", a, b, 12)))
    value, places = AMOUNTS[i % len(AMOUNTS)], (i * 7 + 3) % 13
    MATRIX.append((value, a, b, places, expected(value, a, b, places)))

problems = check_conversions(LITERAL + MATRIX)
finish(problems, f"volumes ok: {len(LITERAL)} hand-worked conversions and {len(MATRIX)} across all 49 unit pairs")
