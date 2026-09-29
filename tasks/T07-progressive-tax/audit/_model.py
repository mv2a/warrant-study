"""Audit (X) helpers: an independent model of intent.md, and a strict raw runner.

Written from intent.md alone. Every amount is an integer number of cents, and the exact
tax is kept in hundredths of a cent, so no floating point is used anywhere.
"""

import json
import os
import subprocess
import sys

from _cmd import PATH, call

FIELDS = ("income_cents", "allowance_cents", "taxable_cents",
          "tax_before_credit_cents", "credit_cents", "tax_cents")
STANDARD_ALLOWANCE = 1_200_000      # G2: 12,000.00
TAPER_FROM = 8_000_000              # G2: the allowance shrinks for income above 80,000.00
TAPER_END = 14_000_000              # G2: zero for incomes of 140,000.00 and above
CREDIT_PER_DEPENDENT = 45_000       # G3: 450.00
# G1: (lower edge, upper edge or None, rate in percent), edges in cents of taxable income
BANDS = ((0, 1_000_000, 5), (1_000_000, 4_000_000, 15),
         (4_000_000, 10_000_000, 25), (10_000_000, None, 38))


def reduction_exact(income):
    """G2 reduction as a (numerator, 5) fraction of cents; 0 at or below 80,000.00."""
    return max(0, income - TAPER_FROM)


def allowance(income):
    """G2 with C1: the reduction is rounded up to a whole cent; never below zero."""
    over = reduction_exact(income)
    reduction = -(-over // 5)
    return max(0, STANDARD_ALLOWANCE - reduction)


def allowance_either_rounding(income):
    """G2 alone: the allowances allowed if the fractional reduction were rounded either way."""
    over = reduction_exact(income)
    return {max(0, STANDARD_ALLOWANCE - over // 5), max(0, STANDARD_ALLOWANCE - (-(-over // 5)))}


def band_hundredths(taxable):
    """G1: the exact tax before credit on a taxable income, in hundredths of a cent."""
    total = 0
    for low, high, rate in BANDS:
        top = taxable if high is None else min(taxable, high)
        if top > low:
            total += (top - low) * rate
    return total


def half_up(hundredths):
    """C1: nearest whole cent, an exact half cent rounded up (amounts here are never negative)."""
    return (hundredths + 50) // 100


def either_cent(hundredths):
    """The whole cents just below and just above an exact amount (one value when exact)."""
    return {hundredths // 100, -(-hundredths // 100)}


def near_band_tax(before, hundredths):
    """Whether a reported tax before credit is close enough to the exact band tax for C1 to
    judge its rounding: within a cent, or, for amounts far beyond ordinary incomes, within
    one part in 10**14 (room for the inexact arithmetic C1 forbids, not for a band error).
    A figure further off is a band error, which is G1's business and is not judged here."""
    return abs(before * 100 - hundredths) <= max(100, hundredths // 10 ** 14)


def expected(income, dependents):
    """The full response the intent requires for a valid request."""
    allow = allowance(income)
    taxable = max(0, income - allow)
    before = half_up(band_hundredths(taxable))
    credit = min(CREDIT_PER_DEPENDENT * dependents, before)
    return {"income_cents": income, "allowance_cents": allow, "taxable_cents": taxable,
            "tax_before_credit_cents": before, "credit_cents": credit, "tax_cents": before - credit}


def short(value, width=90):
    text = value if isinstance(value, str) else json.dumps(value)
    return text if len(text) <= width else text[:width - 3] + "..."


def taxed(request, raw=None, needed=FIELDS):
    """Send one request that must be taxed. Returns (body, None) or (None, problem).

    Only the figures a check reads (`needed`) must be present as JSON integers: the exact
    shape of the response is C4's business, checked by X1, so a stray extra field or a
    missing unused one does not count against the promise another check is about."""
    status, body = call(request, raw=raw)
    label = short(raw if raw is not None else request)
    if status != 0:
        return None, f"{label}: exit status {status}, expected 0 (output {short(repr(body), 60)})"
    if not isinstance(body, dict):
        return None, f"{label}: expected one JSON object, got {short(repr(body), 100)}"
    wrong = [f for f in needed if type(body.get(f)) is not int]
    if wrong:
        return None, f"{label}: {wrong} must be JSON integers, got {short(repr(body), 100)}"
    return body, None


def looks_taxed(out):
    """Whether standard output carries a tax response (an object with any tax figure)."""
    try:
        body = json.loads(out)
    except ValueError:
        return False
    return isinstance(body, dict) and any(field in body for field in FIELDS[1:])


def run_raw(text, timeout=10):
    """Send raw text on stdin. Returns (exit status, exact standard output text)."""
    if not os.access(PATH, os.X_OK):
        sys.exit("the workspace has no executable named tax")
    try:
        done = subprocess.run([PATH], input=text, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, ""
    return done.returncode, done.stdout


def table_error(problems, message):
    """A hand-computed table value disagrees with the model: the audit itself is wrong."""
    problems.append(f"AUDIT TABLE ERROR (not the command's fault): {message}")
