"""Exact unit table and expected results, written from intent.md (G1 to G3, C2)."""

import sys
from fractions import Fraction

# C1 allows amounts of any length, so these expected results must not stop at Python's
# default cap on how many digits int() and str() will convert (4300 since Python 3.11).
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

INCH = Fraction(254, 10)  # millimetres
POUND = Fraction(45359237, 100)  # milligrams
GALLON = Fraction(3785411784, 1000000)  # millilitres

KINDS = {
    "length": {"mm": 1, "cm": 10, "m": 1000, "km": 10**6,
               "in": INCH, "ft": 12 * INCH, "yd": 36 * INCH, "mi": 63360 * INCH},
    "mass": {"mg": 1, "g": 1000, "kg": 10**6, "t": 10**9,
             "lb": POUND, "oz": POUND / 16, "st": 14 * POUND},
    "volume": {"ml": 1, "l": 1000, "m3": 10**6,
               "gal": GALLON, "qt": GALLON / 4, "pt": GALLON / 8, "floz": GALLON / 128},
}
SIZE = {unit: Fraction(size) for units in KINDS.values() for unit, size in units.items()}
KIND = {unit: kind for kind, units in KINDS.items() for unit in units}
UNITS = list(SIZE)


def exact(value, source, target):
    return Fraction(value) * SIZE[source] / SIZE[target]


def written(amount, places):
    """The string C2 asks for: `amount` rounded half up to `places` decimals."""
    scaled = amount * 10**places
    whole, remainder = divmod(scaled.numerator, scaled.denominator)
    if 2 * remainder >= scaled.denominator:
        whole += 1
    digits = str(whole)
    if places == 0:
        return digits
    digits = digits.rjust(places + 1, "0")
    return digits[:-places] + "." + digits[-places:]


def expected(value, source, target, places):
    return written(exact(value, source, target), places)


def is_half(amount, places):
    """True when `amount` lies exactly halfway between two results at `places` decimals."""
    scaled = amount * 10**places
    return 2 * (scaled.numerator % scaled.denominator) == scaled.denominator


def decimal_string(amount):
    """Write a non-negative fraction whose denominator divides a power of ten exactly."""
    places = 0
    while (amount * 10**places).denominator != 1:
        places += 1
        if places > 60:
            raise ValueError(f"{amount} has no short decimal form")
    return written(amount, places)


def random_value(rng, int_digits, frac_digits):
    """A request value with up to `int_digits` integer and `frac_digits` fraction digits."""
    whole = str(rng.randint(0, 10 ** rng.randint(1, int_digits) - 1))
    count = rng.randint(0, frac_digits)
    if count == 0:
        return whole
    return whole + "." + "".join(rng.choice("0123456789") for _ in range(count))


def converted(call, value, source, target, places):
    """Run one conversion; return (status, the value field or None, the whole body)."""
    status, body = call({"value": value, "from": source, "to": target, "places": places})
    got = body.get("value") if isinstance(body, dict) else None
    return status, got, body
