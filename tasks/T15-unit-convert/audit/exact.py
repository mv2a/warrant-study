"""X4 (C1): conversions are exact and rounded once, at the end, for long amounts and every places value."""

import random

from _audit import (F, KINDS, check_conversions, decimal_text, expected, finish, frac_digits, rounded, tie)

# Cases where binary floating point, a 28-digit decimal context, or rounding along the way
# (first to some fixed precision, then to `places`) gives the wrong answer.
HAND = [
    ("9007199254740993", "m", "mm", 0),                    # 2**53 + 1: floats lose the last digit
    ("123456789", "mi", "mm", 12),                        # a 15-digit integer shown with 12 places
    ("3", "ft", "in", 12),                                # exactly 36, not 35.99999999999999
    ("0.3", "yd", "ft", 12),
    ("0.1", "ft", "in", 12),
    ("1.4999999999999999999", "m", "m", 0),               # "1"; rounding to 12 places first gives 2
    ("0.4999999999999999", "km", "km", 0),
    ("1.4999999999999999999", "yd", "ft", 0),             # 4.4999999999999999997 ft is "4"
    ("0.49999999999999999999", "floz", "floz", 0),
    ("2.4999999999999999999999999", "gal", "qt", 1),      # 9.9999999999999999999999996 is "10.0"
    ("12345678901234567890.123456789012345", "g", "kg", 12),
    ("98765432109876543210", "lb", "g", 5),
    ("0.000000000000000000000001", "t", "mg", 12),
    ("99999999999999999999.9999999999995", "mm", "mm", 12),  # halfway in the 13th place, with a long carry
    ("1", "floz", "ml", 12),
    ("7", "mi", "in", 12),
    ("0.000000000000000000000000000000000000001", "m3", "floz", 12),
    ("31415926535897932384626433832795028841971", "in", "mi", 12),
    ("2.718281828459045235360287471352662497757", "st", "oz", 12),
    ("1000000000000000000000000000000.000000000000000000000000000001", "kg", "lb", 12),
]
cases = [(v, a, b, p, expected(v, a, b, p)) for v, a, b, p in HAND]

# Generated amounts with up to 30 digits before the point and 25 after, over random
# pairs of the same kind and every places value from 0 to 12.
rng = random.Random(15150929)
tables = [list(t) for t in KINDS.values()]


def digits(n):
    return "".join(rng.choice("0123456789") for _ in range(n))


for i in range(169):
    units = rng.choice(tables)
    source, target = rng.choice(units), rng.choice(units)
    whole = "0" if rng.random() < 0.2 else str(rng.randint(1, 9)) + digits(rng.randint(0, 29))
    frac = digits(rng.randint(1, 25)) if rng.random() < 0.8 else ""
    value = whole + ("." + frac if frac else "")
    places = i % 13
    cases.append((value, source, target, places, expected(value, source, target, places)))

# Amounts a hair below and a hair above an exact halfway result: the answer depends on
# digits far beyond any fixed working precision.
rng2 = random.Random(60417151)
for i in range(65):
    units = rng2.choice(tables)
    source, target = rng2.choice(units), rng2.choice(units)
    places = (i * 3) % 13
    amount, result = tie(rng2, source, target, places)
    step = F(1, 10 ** (max(frac_digits(amount), places) + 14))
    for nudged in (amount - step, amount + step):
        if nudged <= 0:
            continue
        value = decimal_text(nudged)
        want = expected(value, source, target, places)
        # Sanity check of the oracle itself: below the halfway point rounds down, above rounds up.
        low = rounded(result - F(1, 2 * 10 ** places), places)
        assert want == (low if nudged < amount else rounded(result, places)), (value, source, target, places)
        assert rounded(result, places) != low, (value, source, target, places)
        cases.append((value, source, target, places, want))

problems = check_conversions(cases)
finish(problems, f"exact ok: {len(HAND)} precision traps, 169 long random amounts, {len(cases) - len(HAND) - 169} amounts just off halfway")
