"""Shared helpers for the audit checks: an independent model of intent.md and a runner.

The model below is written from intent.md alone, in exact integer and fraction arithmetic.
"""

import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from math import floor

from _cmd import PATH, call

DAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
WEEKEND = ("fri", "sat")
FIELDS = ("room_cents", "discount_cents", "tax_cents", "total_cents")
TAX_PER_NIGHT = 275
TAXED_NIGHTS = 10


def nights_of(check_in, nights):
    """G1: each night is named by the weekday it begins on, wrapping through the weeks."""
    start = DAYS.index(check_in)
    return [DAYS[(start + i) % 7] for i in range(nights)]


def surcharge(rate):
    """C2: 25% of the nightly rate, to the nearest cent, an exact half cent rounded up."""
    return floor(Fraction(rate * 25, 100) + Fraction(1, 2))


def night_price(day, rate):
    return rate + surcharge(rate) if day in WEEKEND else rate


def discount_percent(nights):
    """G2: 10% for 7 to 13 nights, 15% for 14 or more, nothing below 7."""
    if nights >= 14:
        return 15
    if nights >= 7:
        return 10
    return 0


def discount_of(room, nights):
    """C2: the discount is rounded down to a whole cent."""
    return floor(Fraction(room * discount_percent(nights), 100))


def tax_of(nights):
    """G3: $2.75 for each of the first 10 nights only."""
    return TAX_PER_NIGHT * min(nights, TAXED_NIGHTS)


def refused(check_in, nights):
    """G4: a stay that includes a Saturday night must be at least 3 nights long."""
    return "sat" in nights_of(check_in, nights) and nights < 3


def price(check_in, nights, rate):
    room = sum(night_price(day, rate) for day in nights_of(check_in, nights))
    discount = discount_of(room, nights)
    tax = tax_of(nights)
    return {"room_cents": room, "discount_cents": discount, "tax_cents": tax,
            "total_cents": room - discount + tax}


def request(check_in, nights, rate):
    return {"check_in": check_in, "nights": nights, "rate_cents": rate}


def call_all(requests, raw=False):
    """Run many requests in parallel; results come back in the same order."""
    with ThreadPoolExecutor(max_workers=8) as pool:
        if raw:
            return list(pool.map(lambda text: call(raw=text), requests))
        return list(pool.map(call, requests))


def run_bytes(data, timeout=10, env=None):
    """Send raw bytes; return (exit status, stdout text, stderr text) without parsing."""
    if not os.access(PATH, os.X_OK):
        raise SystemExit("the workspace has no executable named stay")
    try:
        done = subprocess.run([PATH], input=data, capture_output=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return 124, "", ""
    return (done.returncode, done.stdout.decode("utf-8", "replace"),
            done.stderr.decode("utf-8", "replace"))


def posix_locale_env():
    """The environment with the locale fixed to POSIX "C". How a Python program decodes
    bytes that are not UTF-8 on standard input depends on the locale (strict under a UTF-8
    locale such as en_US.UTF-8, surrogateescape under "C"), so a check that sends such bytes
    must fix the locale or its verdict would change from host to host."""
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONIOENCODING", "PYTHONUTF8")}
    env["LC_ALL"] = "C"
    return env


def run_full(req, timeout=10):
    return run_bytes(json.dumps(req).encode(), timeout)


def is_amounts(body):
    """True when body is an object with exactly the four fields, each a JSON integer."""
    return (isinstance(body, dict) and set(body) == set(FIELDS)
            and all(type(body[f]) is int for f in FIELDS))


def is_number(value):
    return type(value) in (int, float)


def priced(body):
    """True when the output carries a price (any object with a total); used to tell pricing from refusal."""
    return isinstance(body, dict) and "total_cents" in body


def amount_problems(body, want):
    """The four amounts that differ from want (the exact field set and JSON types are checked by X5)."""
    if not isinstance(body, dict):
        return {"output": body}
    wrong = {f: body.get(f) for f in FIELDS if not is_number(body.get(f)) or body.get(f) != want[f]}
    return wrong or None


def show(req):
    return json.dumps(req, separators=(",", ":"))
