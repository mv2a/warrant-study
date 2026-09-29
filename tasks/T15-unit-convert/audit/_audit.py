"""Shared helpers for the audit checks (X).

The oracle here is written from intent.md alone: every unit is an exact Fraction built
from the definitions in G1 to G3, and rounding is done once, half up, as C1 and C2 say.
"""

import json
import math
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction as F

import _cmd
from _cmd import call, finish  # noqa: F401  (re-exported for the check scripts)

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)  # the oracle must handle amounts of any length

# G1: lengths, in millimetres.
_IN = F(254, 10)
_FT = 12 * _IN
LENGTH = {
    "mm": F(1), "cm": F(10), "m": F(1000), "km": F(1000) * 1000,
    "in": _IN, "ft": _FT, "yd": 3 * _FT, "mi": 5280 * _FT,
}
# G2: masses, in milligrams.
_G = F(1000)
_LB = F(45359237, 100000) * _G  # 453.59237 g
MASS = {
    "mg": F(1), "g": _G, "kg": 1000 * _G, "t": 1000 * 1000 * _G,
    "lb": _LB, "oz": _LB / 16, "st": 14 * _LB,
}
# G3: volumes (US liquid), in millilitres.
_GAL = F(3785411784, 1000000)  # 3785.411784 ml
VOLUME = {
    "ml": F(1), "l": F(1000), "m3": F(1000) * 1000,
    "gal": _GAL, "qt": _GAL / 4, "pt": _GAL / 8, "floz": _GAL / 128,
}
KINDS = {"length": LENGTH, "mass": MASS, "volume": VOLUME}
DIMENSION = {unit: kind for kind, table in KINDS.items() for unit in table}
SIZE = {unit: size for table in KINDS.values() for unit, size in table.items()}
UNITS = list(SIZE)


def amount(text):
    """The exact value of a well-formed amount string such as "007.50"."""
    whole, _, frac = text.partition(".")
    return F(int(whole + frac), 10 ** len(frac))


def rounded(x, places):
    """x (a non-negative Fraction) rounded once, half up, written as C2 requires."""
    n = math.floor(x * 10 ** places + F(1, 2))
    digits = str(n)
    if places == 0:
        return digits
    digits = digits.rjust(places + 1, "0")
    return digits[:-places] + "." + digits[-places:]


def exact(value, source, target):
    return amount(value) * SIZE[source] / SIZE[target]


def expected(value, source, target, places):
    return rounded(exact(value, source, target), places)


def decimal_text(x):
    """Write a terminating non-negative Fraction as a plain decimal string, exactly."""
    k = 0
    while (x * 10 ** k).denominator != 1:
        k += 1
        if k > 400:
            raise ValueError(f"{x} does not terminate")
    return rounded(x, k)


def frac_digits(x):
    """How many digits a terminating Fraction needs after the point."""
    k = 0
    while (x * 10 ** k).denominator != 1:
        k += 1
    return k


def tie(rng, source, target, places):
    """A terminating amount whose exact conversion lies exactly halfway between two
    neighbouring multiples of 10**-places. Returns (amount, exact result)."""
    ratio = SIZE[target] / SIZE[source]  # amount = result * ratio
    odd = ratio.denominator
    while odd % 2 == 0:
        odd //= 2
    while odd % 5 == 0:
        odd //= 5
    m = rng.randint(0, 10 ** rng.randint(0, 6))
    result = F(odd * (2 * m + 1), 2 * 10 ** places)  # an odd number of half-steps
    return result * ratio, result


def well_formed(text, places):
    """C2's shape: ASCII digits, one leading 0 at most, exactly `places` digits after a point."""
    if not isinstance(text, str):
        return False
    pattern = r"(0|[1-9][0-9]*)" + (r"\.[0-9]{%d}" % places if places else "")
    return re.fullmatch(pattern, text, flags=re.ASCII) is not None


def request(value, source, target, places):
    return {"value": value, "from": source, "to": target, "places": places}


def _one(item):
    if isinstance(item, str):
        return call(raw=item)
    return call(item)


def run_all(items, workers=8):
    """Call the command once per item (a request dict, or raw text) and keep the order."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(_one, items))


def raw_run(text, timeout=10):
    """Run the command on raw stdin text. Returns (exit status, stdout exactly as written)."""
    if not os.access(_cmd.PATH, os.X_OK):
        sys.exit(f"the workspace has no executable named {_cmd.COMMAND}")
    try:
        done = subprocess.run([_cmd.PATH], input=text, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, None
    except OSError as error:
        return 126, f"could not run the command: {error}"
    return done.returncode, done.stdout


def raw_run_all(texts, workers=8):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(raw_run, texts))


def short(obj, limit=90):
    text = repr(obj)
    return text if len(text) <= limit else text[: limit - 3] + "..."


def check_conversions(cases, workers=8):
    """cases: (value, from, to, places, wanted value string). Returns a list of problems."""
    problems = []
    results = run_all([request(v, a, b, p) for v, a, b, p, _ in cases], workers)
    for (value, source, target, places, want), (status, body) in zip(cases, results):
        wanted = {"value": want, "unit": target, "dimension": DIMENSION[target]}
        if status != 0 or body != wanted:
            problems.append(
                f"{short(value, 40)} {source} to {target} at {places} places: expected {short(want, 40)}, "
                f"got status {status} and {short(body, 80)}"
            )
    return problems


def refused(items, workers=8):
    """Each item must be refused: exit status 2 and nothing on standard output."""
    problems = []
    for item, (status, body) in zip(items, run_all(items, workers)):
        if status != 2 or body is not None:
            problems.append(f"{short(item, 90)} must be refused (status 2, no output), got status {status} and {short(body, 60)}")
    return problems


__all__ = [
    "F", "LENGTH", "MASS", "VOLUME", "KINDS", "DIMENSION", "SIZE", "UNITS", "amount", "rounded",
    "exact", "expected", "decimal_text", "frac_digits", "tie", "well_formed", "request", "run_all", "raw_run",
    "raw_run_all", "short", "check_conversions", "refused", "call", "finish", "json",
]
