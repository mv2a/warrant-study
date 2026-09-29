"""H4: conversions are exact however long the input and however many places (C1)."""

import random

from _cmd import call, finish
from _units import KIND, UNITS, converted, exact, expected, is_half

KNOWN = [
    ("123456789.123456789", "ft", "m", 12, "37629629.324829629287"),
    ("98765432109876543210", "mi", "mm", 0, "158947555573437155555754240"),
    ("0.000000000001", "km", "mm", 12, "0.000001000000"),
    ("1", "floz", "ml", 10, "29.5735295625"),
    ("1", "oz", "g", 12, "28.349523125000"),
    ("0.1", "gal", "floz", 12, "12.800000000000"),
    ("3", "floz", "l", 11, "0.08872058869"),
    ("99999999999.999999999", "lb", "kg", 12, "45359236999.999999999546"),
    ("7", "ml", "gal", 12, "0.001849204367"),
]
rng = random.Random(1504)
cases = list(KNOWN)
while len(cases) < len(KNOWN) + 60:
    source = rng.choice(UNITS)
    target = rng.choice([unit for unit in UNITS if KIND[unit] == KIND[source]])
    whole = str(rng.randint(1, 10 ** rng.randint(1, 18)))
    fraction = "".join(rng.choice("0123456789") for _ in range(rng.randint(1, 14)))
    value = f"{whole}.{fraction}"
    places = rng.randint(6, 12)
    if is_half(exact(value, source, target), places):
        continue  # exact halves belong to the rounding check (C2)
    cases.append((value, source, target, places, expected(value, source, target, places)))

# Amounts thousands of digits long. Python refuses by default to convert more than 4300
# digits between text and int, so each shape below trips a different shortcut: a huge whole
# number, a huge fraction part, a result that outgrows the limit though the amount does
# not, and two parts that are each under the limit but are over it once joined.
long_rng = random.Random(150415)


def run_of_digits(count):
    return str(long_rng.randint(1, 9)) + "".join(long_rng.choice("0123456789") for _ in range(count - 1))


LONG_SHAPES = [
    (lambda: run_of_digits(4800), "yd", "km", 12),
    (lambda: "2." + run_of_digits(4450), "oz", "kg", 12),
    (lambda: run_of_digits(4298), "m3", "floz", 6),
    (lambda: run_of_digits(2600) + "." + run_of_digits(2600), "in", "mi", 10),
]
for make, source, target, places in LONG_SHAPES:
    while True:
        value = make()
        if not is_half(exact(value, source, target), places):
            break
    cases.append((value, source, target, places, expected(value, source, target, places)))


def shown(text):
    text = str(text)
    return text if len(text) <= 40 else f"{text[:16]}...{text[-8:]} ({len(text)} characters)"


problems = []
for value, source, target, places, want in cases:
    status, got, _ = converted(call, value, source, target, places)
    if status != 0 or got != want:
        problems.append(f"{shown(value)} {source} to {target} at {places} places: expected {shown(want)}, got {shown(got)} (status {status})")

finish(problems, f"exactness ok: {len(cases)} long or high-precision conversions")
