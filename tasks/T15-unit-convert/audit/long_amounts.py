"""X12 (C1): amounts with hundreds or thousands of digits still convert exactly.

C1 says the answer must be right however many digits the input has. The longest amount here
has more digits than Python's default limit for converting text to int (4300), so it fails any
implementation that parses the amount with int() or Fraction() under that default.
"""

import random

from _audit import check_conversions, expected, finish

rng = random.Random(84126037)


def digits(n):
    return str(rng.randint(1, 9)) + "".join(rng.choice("0123456789") for _ in range(n - 1))


def frac(n):
    return "".join(rng.choice("0123456789") for _ in range(n))


AMOUNTS = [
    (digits(120), "km", "m", 0),
    (digits(300) + "." + frac(300), "in", "yd", 12),
    ("0." + "0" * 500 + "5", "t", "mg", 12),
    (digits(1000), "lb", "oz", 0),
    (digits(40) + "." + frac(1500), "floz", "l", 12),
    (digits(4400), "m", "mm", 0),
    (digits(4500) + "." + frac(20), "gal", "ml", 7),
]
cases = [(v, a, b, p, expected(v, a, b, p)) for v, a, b, p in AMOUNTS]
problems = check_conversions(cases, workers=4)
finish(problems, f"long amounts ok: {len(cases)} amounts of up to {max(len(v) for v, *_ in AMOUNTS)} characters")
