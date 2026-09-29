"""X6 (C3): every unit converts to every unit of its kind, including itself; unknown units and
units of two different kinds are refused."""

import itertools

from _audit import DIMENSION, KINDS, check_conversions, expected, finish, refused, request

problems = []

# Every unit converts to itself, unchanged, and to every other unit of the same kind.
same = [("8.125", u, u, 3, "8.125") for u in DIMENSION] + [("0.0625", u, u, 12, "0.062500000000") for u in DIMENSION]
for table in KINDS.values():
    for a, b in itertools.product(table, repeat=2):
        same.append(("3", a, b, 6, expected("3", a, b, 6)))
problems += check_conversions(same)

# Unit symbols are case-sensitive and must be written exactly: near misses are unknown units.
UNKNOWN = [
    "KG", "Kg", "kG", "lbs", "gallon", "gallons", "MM", "Mm", "M", "CM", "Cm", "KM", "Km", "IN", "In",
    "FT", "Ft", "YD", "MI", "Mi", "MG", "G", "T", "OZ", "Oz", "LB", "Lb", "ST", "ML", "mL", "L", "M3",
    "FLOZ", "flOz", "fl oz", "fl_oz", "fl.oz", "PT", "QT", "GAL", "Gal", "m^3", "m³", "cm3", "cc",
    "dl", "cl", "dm", "nm", "um", "µm", "metre", "meter", "meters", "inch", "inches", "foot", "feet",
    "mile", "miles", "yard", "gram", "grams", "kilogram", "pound", "pounds", "ounce", "stone", "tonne",
    "ton", "tons", "litre", "liter", "pint", "quart", "ton_us", "imp_gal", "", " ", " m", "m ", "kg.",
    "in.", "ft.", "mm2", "C", "K", "s", "null", "0", "__class__", "k", "м",
]
PARTNER = {"length": "m", "mass": "kg", "volume": "l"}
bad_units = []
for i, unit in enumerate(UNKNOWN):
    known = list(PARTNER.values())[i % 3]
    bad_units.append(request("1", unit, known, 2))
    bad_units.append(request("1", known, unit, 2))
problems += refused(bad_units)

# Units of two different kinds, in every order and combination, are refused: all 322 pairs.
cross = []
for (k1, t1), (k2, t2) in itertools.permutations(KINDS.items(), 2):
    for a, b in itertools.product(t1, t2):
        cross.append(request("1", a, b, 2))
problems += refused(cross)

finish(problems, f"units ok: {len(same)} same-kind conversions, {len(bad_units)} unknown units, {len(cross)} cross-kind pairs refused")
