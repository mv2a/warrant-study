"""H5: results are rounded half up and written exactly as C2 describes."""

import random
import re
from fractions import Fraction

from _cmd import call, finish
from _units import SIZE, converted, decimal_string, expected

# Pairs whose ratio is a power of ten, so any decimal result can be reached exactly.
DECIMAL_PAIRS = [("mm", "cm"), ("mm", "m"), ("cm", "m"), ("m", "km"), ("mg", "g"), ("g", "kg"),
                 ("kg", "t"), ("ml", "l"), ("l", "m3"), ("km", "m"), ("t", "g"), ("m", "m"), ("l", "l")]

KNOWN = [
    ("5", "mm", "cm", 0, "1"),
    ("125", "mm", "m", 2, "0.13"),
    ("2.5", "m", "m", 0, "3"),
    ("0.5", "g", "g", 0, "1"),
    ("0.05", "m", "m", 1, "0.1"),
    ("0.75", "in", "mm", 1, "19.1"),
    ("1", "oz", "g", 8, "28.34952313"),
    ("1", "floz", "ml", 9, "29.573529563"),
    ("1", "floz", "l", 12, "0.029573529563"),
    ("0.4", "mm", "cm", 0, "0"),
    ("0", "m", "cm", 3, "0.000"),
    ("7", "m", "km", 2, "0.01"),
    ("4", "mm", "km", 5, "0.00000"),
    ("1", "km", "mm", 0, "1000000"),
    ("1", "kg", "g", 6, "1000.000000"),
    ("12345678901234567890", "t", "mg", 0, "12345678901234567890000000000"),
    ("007.50", "m", "cm", 1, "750.0"),
    ("2.5", "lb", "kg", 4, "1.1340"),
    ("1", "mi", "m", 0, "1609"),
]


def shape(places):
    return re.compile(r"(0|[1-9][0-9]*)" + (r"\.[0-9]{%d}" % places if places else ""))


rng = random.Random(1505)
cases = list(KNOWN)
for _ in range(70):
    source, target = rng.choice(DECIMAL_PAIRS)
    places = rng.randint(0, 12)
    ending = rng.choice(["5", "5", "5", "49", "51"])
    digits = str(rng.randint(0, 10 ** rng.randint(1, 8))) + ending
    result = Fraction(int(digits), 10 ** (places + len(ending)))
    value = decimal_string(result * SIZE[target] / SIZE[source])
    cases.append((value, source, target, places, expected(value, source, target, places)))

problems = []
for value, source, target, places, want in cases:
    status, got, _ = converted(call, value, source, target, places)
    if status != 0 or got != want:
        problems.append(f"{value} {source} to {target} at {places} places: expected {want!r}, got {got!r} (status {status})")
    elif not shape(places).fullmatch(got):
        problems.append(f"{value} {source} to {target} at {places} places: {got!r} is not written as C2 describes")

finish(problems, f"rounding ok: {len(cases)} conversions, most of them exact halves")
