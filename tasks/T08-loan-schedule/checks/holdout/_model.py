"""What the intent promises, computed with exact fractions, plus the loans the checks try."""

import math
from fractions import Fraction

MAX_PRINCIPAL = 1_000_000_000
MAX_RATE = 5000
MAX_MONTHS = 480
HALF = Fraction(1, 2)
TYPICAL_MONTHS = (1, 2, 3, 6, 12, 18, 24, 36, 48, 60, 84, 120, 180, 240, 300, 360, 480)


def monthly_rate(rate_bp):
    return Fraction(rate_bp, 120000)


def exact_payment(principal, rate_bp, months):
    """The unrounded level payment (G1), or the unrounded P / n for a zero rate (G4)."""
    if rate_bp == 0:
        return Fraction(principal, months)
    i = monthly_rate(rate_bp)
    return principal * i / (1 - (1 + i) ** -months)


def payment(principal, rate_bp, months):
    return math.ceil(exact_payment(principal, rate_bp, months))


def interest(balance, rate_bp):
    """Balance times the monthly rate, to the nearest cent, exact halves rounded up (G2)."""
    return math.floor(balance * monthly_rate(rate_bp) + HALF)


def schedule(principal, rate_bp, months):
    regular = payment(principal, rate_bp, months)
    rows, balance = [], principal
    for month in range(1, months + 1):
        owed = interest(balance, rate_bp)
        if balance + owed <= regular or month == months:
            rows.append({"month": month, "payment_cents": balance + owed, "interest_cents": owed,
                         "principal_cents": balance, "balance_cents": 0})
            break
        balance -= regular - owed
        rows.append({"month": month, "payment_cents": regular, "interest_cents": owed,
                     "principal_cents": regular - owed, "balance_cents": balance})
    return {"payment_cents": regular, "total_interest_cents": sum(r["interest_cents"] for r in rows), "rows": rows}


def random_principal(rng):
    shape = rng.random()
    if shape < 0.15:
        return rng.randint(1, 5000)
    if shape < 0.6:
        return rng.randrange(100, 5_000_001, 100)
    return min(MAX_PRINCIPAL, int(10 ** rng.uniform(0, 9)) + rng.randint(0, 99))


def random_rate(rng, allow_zero=True):
    shape = rng.random()
    if allow_zero and shape < 0.1:
        return 0
    if shape < 0.55:
        return rng.randrange(25, 2501, 25)
    return rng.randint(1, MAX_RATE)


def random_months(rng):
    return rng.choice(TYPICAL_MONTHS) if rng.random() < 0.6 else rng.randint(1, MAX_MONTHS)


def random_loan(rng, allow_zero=True):
    return {
        "principal_cents": random_principal(rng),
        "annual_rate_bp": random_rate(rng, allow_zero),
        "months": random_months(rng),
    }


def is_schedule(body):
    return (
        isinstance(body, dict)
        and isinstance(body.get("rows"), list)
        and len(body["rows"]) > 0
        and all(isinstance(row, dict) for row in body["rows"])
    )
