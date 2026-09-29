"""Shared audit helpers, written from intent.md alone.

An oracle for the promises, a runner that sends many requests to the workspace's `rate`
command in parallel (results come back in input order), and one judge per kind of promise.

The study counts every promise that a failing X check covers as broken, so each check
judges only what the promises it covers decide:

- C1, the interface: an answer with status 0 must be exactly one JSON object with the four
  JSON-integer fields and total_cents = base_cents + surcharge_cents; an answer with status 2
  must write nothing at all on standard output; any other status breaks C1. Whether a request
  should have been priced is decided by the other promises, not by C1.
- G1 to G4 and S1 to S3: the named response fields have the values the intent gives. Field
  types and layout are C1's business, so 1500 and 1500.0 are the same value here. A parcel
  that sits exactly on a carrying limit and is refused is left to C2. G2 and G3 are judged on
  parcels billed on their actual weight that are not oversize; G1 judges billable_g and that a parcel billed on its
  dimensional weight pays what a parcel of that actual weight pays.
- C2, C3 and S4: priced means status 0 with a JSON object; refused means status 2 and no
  price. What a refusal writes is C1's business.
"""

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from _cmd import COMMAND, PATH, finish

FIELDS = ("billable_g", "base_cents", "surcharge_cents", "total_cents")
REFUSED = None  # the oracle's answer for a request the intent says must be refused

BRACKETS = (500, 1000, 2000, 5000, 10000)
TABLE = {  # zone: the five bracket prices, then the price per started kg over 10,000 g
    1: (450, 540, 690, 920, 1350, 85),
    2: (520, 630, 810, 1090, 1600, 105),
    3: (610, 740, 960, 1310, 1930, 130),
    4: (780, 950, 1240, 1700, 2520, 175),
}
SURCHARGE = 1500
MAX_BILLABLE, MAX_SIDE, MAX_LENGTH_GIRTH = 30000, 150, 300
OVERSIZE_SIDE, OVERSIZE_LENGTH_GIRTH = 100, 220


# ---- the oracle -------------------------------------------------------------------------

def parcel(zone, weight, length, width, height, **extra):
    request = {"zone": zone, "weight_g": weight, "length_cm": length, "width_cm": width, "height_cm": height}
    request.update(extra)
    return request


def sides_of(request):
    return request["length_cm"], request["width_cm"], request["height_cm"]


def dim_weight(length, width, height):
    """G1: length x width x height / 5, rounded up to a whole gram."""
    return -(-(length * width * height) // 5)


def billable(weight, length, width, height):
    return max(weight, dim_weight(length, width, height))


def length_and_girth(length, width, height):
    """G4: the length is the longest side; the girth is twice the sum of the other two."""
    a, b, c = sorted((length, width, height))
    return c, 2 * (a + b)


def base_price(zone, grams):
    row = TABLE[zone]
    for limit, price in zip(BRACKETS, row):
        if grams <= limit:
            return price
    return row[4] + row[5] * -(-(grams - 10000) // 1000)


def is_oversize(length, width, height):
    longest, girth = length_and_girth(length, width, height)
    return longest > OVERSIZE_SIDE or longest + girth > OVERSIZE_LENGTH_GIRTH


def carriable(request):
    """C2: within all three carrying limits (a parcel exactly at a limit is carried)."""
    sides = sides_of(request)
    longest, girth = length_and_girth(*sides)
    return billable(request["weight_g"], *sides) <= MAX_BILLABLE and longest <= MAX_SIDE and longest + girth <= MAX_LENGTH_GIRTH


def at_limit(request):
    """C2: carried, but exactly on at least one carrying limit."""
    sides = sides_of(request)
    longest, girth = length_and_girth(*sides)
    return carriable(request) and (
        billable(request["weight_g"], *sides) == MAX_BILLABLE or longest == MAX_SIDE or longest + girth == MAX_LENGTH_GIRTH)


def actual_wins(request):
    """The actual weight is more than 1 g above volume / 5, so the billable weight is the actual
    weight however the dimensional weight is rounded. The pricing checks (G2, G3) use
    only such parcels, so that a G1 mistake cannot fail them; that a parcel is charged on its
    dimensional weight when that is greater is G1's business."""
    length, width, height = sides_of(request)
    return 5 * request["weight_g"] > length * width * height + 5  # weight > volume / 5 + 1


def _volume_fits_sides(volume):
    """Whether some three whole sides of at most MAX_SIDE cm have exactly this volume."""
    return any(volume % (a * b) == 0 and volume // (a * b) <= MAX_SIDE
               for a in range(1, MAX_SIDE + 1) for b in range(1, MAX_SIDE + 1))


# How G1 rounds never decides C2. Rounding volume / 5 up or down gives a different answer to
# "over 30,000 g?" only for a volume of 150,001 to 150,004 cm3, and each of those has a prime
# factor over 150 (150,001 is prime, 150,002 = 2 x 179 x 419, 150,003 = 63 x 2381,
# 150,004 = 4 x 37,501), so a parcel of that volume always has a side over 150 cm and is
# refused whatever the rounding. The C2 checks therefore judge every parcel, including light
# ones exactly at 150,000 cm3 (a dimensional weight of exactly 30,000 g, which is carried).
assert not any(_volume_fits_sides(v) for v in range(5 * MAX_BILLABLE + 1, 5 * MAX_BILLABLE + 5))


def expected(request):
    """The answer the intent requires for a well-formed request: a dict, or REFUSED."""
    if not carriable(request):
        return REFUSED
    zone, weight, sides = request["zone"], request["weight_g"], sides_of(request)
    grams = billable(weight, *sides)
    base = base_price(zone, grams)
    surcharge = SURCHARGE if is_oversize(*sides) else 0
    return {"billable_g": grams, "base_cents": base, "surcharge_cents": surcharge, "total_cents": base + surcharge}


# ---- running the command ----------------------------------------------------------------

def run_raw(text, timeout=10):
    """Send raw text on stdin. Returns (exit status, stdout, stderr), unstripped."""
    try:
        done = subprocess.run([PATH], input=text, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, "", "timed out"
    return done.returncode, done.stdout, done.stderr


def as_text(request):
    return request if isinstance(request, str) else json.dumps(request)


def run_many(requests, workers=8):
    """Send each request (a dict, or raw text) and return the results in the same order."""
    if not os.access(PATH, os.X_OK):
        sys.exit(f"the workspace has no executable named {COMMAND}")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(run_raw, [as_text(r) for r in requests]))


def parse(out):
    """The JSON value on standard output, or None when there is none."""
    try:
        return json.loads(out)
    except ValueError:
        return None


def number(body, field):
    """A numeric response field's value, or None (true/false and text are not numbers)."""
    value = body.get(field) if isinstance(body, dict) else None
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def shown(result):
    status, out, _ = result
    return f"status {status} and {out[:120]!r}"


def is_price(result):
    status, out, _ = result
    return status == 0 and isinstance(parse(out), dict)


def is_refusal(result):
    status, out, _ = result
    body = parse(out)
    return status == 2 and not (isinstance(body, dict) and "total_cents" in body)


# ---- judges: each takes a result and returns a problem, or None -----------------------------

def interface(must_price=False):
    """C1. With must_price, the request is one the intent prices, so a refusal is also wrong."""
    def judge(result):
        status, out, _ = result
        if status == 2:
            if must_price:
                return f"expected a price with status 0, got {shown(result)}"
            if out != "":
                return f"a refusal (status 2) must write nothing at all on standard output, got {out[:120]!r}"
            return None
        if status != 0:
            return f"C1 allows only status 0 (priced) or 2 (refused), got {shown(result)}"
        body = parse(out)
        if not isinstance(body, dict):
            return f"a priced answer must be one JSON object on standard output, got {out[:120]!r}"
        if set(body) != set(FIELDS):
            return f"expected exactly the fields {list(FIELDS)}, got {body!r}"
        if not all(type(body[field]) is int for field in FIELDS):
            return f"every field must be a JSON integer, got {body!r}"
        if body["total_cents"] != body["base_cents"] + body["surcharge_cents"]:
            return f"total_cents must be base_cents plus surcharge_cents, got {body!r}"
        return None
    return judge


def values(request, want):
    """G1 to G3, S1 to S3: the answer is a price whose named fields have these values."""
    def judge(result):
        if not is_price(result):
            if result[0] == 2 and at_limit(request):
                return None  # whether a parcel exactly on a carrying limit is priced is C2's business
            return f"expected a price with {want}, got {shown(result)}"
        body = parse(result[1])
        if any(number(body, field) != value for field, value in want.items()):
            return f"expected {want}, got {body}"
        return None
    return judge


def surcharge(request, want):
    """G4: the surcharge is `want` and it comes on top of the base price."""
    def judge(result):
        if not is_price(result):
            if result[0] == 2 and at_limit(request):
                return None
            return f"expected a price with surcharge_cents {want}, got {shown(result)}"
        body = parse(result[1])
        base, extra, total = (number(body, f) for f in ("base_cents", "surcharge_cents", "total_cents"))
        if extra != want:
            return f"expected surcharge_cents {want}, got {body}"
        if base is None or total != base + want:
            return f"expected total_cents = base_cents + {want}, got {body}"
        return None
    return judge


def priced(result):
    """C2, C3 controls: the request is priced (status 0 with a JSON object)."""
    return None if is_price(result) else f"expected a price (status 0), got {shown(result)}"


def refused(result):
    """C2, C3, S4: the request is refused (status 2) and not priced."""
    return None if is_refusal(result) else f"expected a refusal (status 2, no price), got {shown(result)}"


def check(cases, summary):
    """cases: list of (label, request dict or raw text, judge). Exits 0 or 1."""
    results = run_many([c[1] for c in cases])
    problems = []
    for (label, _, judge), result in zip(cases, results):
        problem = judge(result)
        if problem:
            problems.append(f"{label}: {problem}")
    finish(problems, f"{summary}: {len(cases)} requests")
