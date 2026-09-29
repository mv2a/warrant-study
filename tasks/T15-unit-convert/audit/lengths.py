"""X1 (G1): lengths convert with the exact definitions of mm, cm, m, km, in, ft, yd and mi."""

import itertools

from _audit import LENGTH, check_conversions, expected, finish

# Worked out by hand from G1 (1 in = 25.4 mm, 1 ft = 12 in, 1 yd = 3 ft, 1 mi = 5280 ft).
LITERAL = [
    ("1", "mi", "ft", 0, "5280"),
    ("1", "mi", "yd", 0, "1760"),
    ("1", "mi", "in", 0, "63360"),
    ("1", "mi", "m", 3, "1609.344"),
    ("1", "mi", "km", 6, "1.609344"),
    ("1", "mi", "mm", 0, "1609344"),
    ("1", "in", "mm", 1, "25.4"),
    ("1", "in", "cm", 2, "2.54"),
    ("1", "ft", "mm", 1, "304.8"),
    ("1", "yd", "m", 4, "0.9144"),
    ("1", "yd", "ft", 0, "3"),
    ("1", "ft", "in", 0, "12"),
    ("1", "m", "cm", 0, "100"),
    ("1", "km", "mm", 0, "1000000"),
    ("1", "cm", "mm", 0, "10"),
    ("1", "mm", "m", 3, "0.001"),
    ("1", "km", "mi", 12, "0.621371192237"),
    ("1", "m", "in", 12, "39.370078740157"),
    ("1", "m", "ft", 12, "3.280839895013"),
    ("1", "m", "yd", 12, "1.093613298338"),
    ("1", "in", "ft", 12, "0.083333333333"),
    ("2", "in", "ft", 12, "0.166666666667"),
    ("1", "ft", "mi", 12, "0.000189393939"),
    ("1", "in", "yd", 12, "0.027777777778"),
    ("1", "mm", "in", 12, "0.039370078740"),
    ("1", "cm", "in", 12, "0.393700787402"),
    ("5", "km", "mi", 4, "3.1069"),
    ("26.2", "mi", "km", 3, "42.165"),
    ("100", "yd", "m", 2, "91.44"),
    ("6", "ft", "cm", 2, "182.88"),
]

# Every ordered pair of length units, twice: 1 unit at 12 places, and another amount at 0 to 12 places.
AMOUNTS = ["4321.5", "0.07", "250", "19.125", "8", "0.0003", "77777"]
MATRIX = []
for i, (a, b) in enumerate(itertools.product(LENGTH, repeat=2)):
    MATRIX.append(("1", a, b, 12, expected("1", a, b, 12)))
    value, places = AMOUNTS[i % len(AMOUNTS)], i % 13
    MATRIX.append((value, a, b, places, expected(value, a, b, places)))

problems = check_conversions(LITERAL + MATRIX)
finish(problems, f"lengths ok: {len(LITERAL)} hand-worked conversions and {len(MATRIX)} across all 64 unit pairs")
