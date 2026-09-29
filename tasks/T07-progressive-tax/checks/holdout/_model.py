"""The rules of intent.md, written out once for the hidden checks. Amounts are in cents."""

import math
from fractions import Fraction

FIELDS = ("income_cents", "allowance_cents", "taxable_cents", "tax_before_credit_cents", "credit_cents", "tax_cents")
STANDARD_ALLOWANCE = 1_200_000
PHASE_OUT_START = 8_000_000
CREDIT_PER_DEPENDENT = 45_000
# (lower edge, upper edge or None, rate) for each band of G1
BANDS = [
    (0, 1_000_000, Fraction(5, 100)),
    (1_000_000, 4_000_000, Fraction(15, 100)),
    (4_000_000, 10_000_000, Fraction(25, 100)),
    (10_000_000, None, Fraction(38, 100)),
]


def exact_band_tax(taxable):
    """G1 before any rounding, as an exact fraction of a cent. A taxable income below zero owes nothing."""
    total = Fraction(0)
    for lower, upper, rate in BANDS:
        top = taxable if upper is None else min(taxable, upper)
        if top > lower:
            total += (top - lower) * rate
    return total


def half_up(value):
    """C1: nearest whole cent, an exact half cent rounded up."""
    return math.floor(value + Fraction(1, 2))


def exact_reduction(income):
    """G2: one fifth of the income above 80,000.00, before rounding."""
    return Fraction(max(0, income - PHASE_OUT_START), 5)


def allowance(income, rounding=math.ceil):
    """G2 with the reduction rounded as C1 says (up), or another way when a check must not depend on C1."""
    return max(0, STANDARD_ALLOWANCE - rounding(exact_reduction(income)))


def expected(income, dependents):
    """The whole response intent.md promises for a valid request."""
    allowed = allowance(income)
    taxable = max(0, income - allowed)
    before = half_up(exact_band_tax(taxable))
    credit = min(CREDIT_PER_DEPENDENT * dependents, before)
    return {
        "income_cents": income,
        "allowance_cents": allowed,
        "taxable_cents": taxable,
        "tax_before_credit_cents": before,
        "credit_cents": credit,
        "tax_cents": before - credit,
    }


def income_for_taxable(target):
    """The smallest income whose taxable income under the rules is at least `target`."""
    low, high = 0, target + STANDARD_ALLOWANCE
    while low < high:
        middle = (low + high) // 2
        if max(0, middle - allowance(middle)) >= target:
            high = middle
        else:
            low = middle + 1
    return low


def whole(value):
    return type(value) is int
