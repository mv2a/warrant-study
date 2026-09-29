"""Audit oracle for the loan schedule, written from intent.md alone with exact arithmetic.

Nothing here reads the workspace; the check scripts compare the command's output with it.
"""

from fractions import Fraction

RATE_SCALE = 120000  # i = annual_rate_bp / 120000


def ceil_div(a, b):
    return -(-a // b)


def exact_level(principal, rate_bp, months):
    """G1's level payment P*i / (1 - (1+i)^-n) as an exact fraction of cents (rate above 0)."""
    i = Fraction(rate_bp, RATE_SCALE)
    growth = (1 + i) ** months
    return principal * i * growth / (growth - 1)


def regular_payment(principal, rate_bp, months):
    """G1 (rate > 0): level payment rounded up to a whole cent. G4 (rate 0): P / n rounded up."""
    if rate_bp == 0:
        return ceil_div(principal, months)
    x = exact_level(principal, rate_bp, months)
    return ceil_div(x.numerator, x.denominator)


def interest_on(balance, rate_bp):
    """G2: balance * i rounded to the nearest cent, an exact half cent rounded up."""
    # floor(balance * rate_bp / 120000 + 1/2), in integers
    return (2 * balance * rate_bp + RATE_SCALE) // (2 * RATE_SCALE)


def schedule(principal, rate_bp, months):
    """The whole response the intent promises, as a dict shaped like the command's output."""
    pay = regular_payment(principal, rate_bp, months)
    rows = []
    balance = principal
    for month in range(1, months + 1):
        interest = interest_on(balance, rate_bp)
        if balance + interest <= pay or month == months:
            rows.append({"month": month, "payment_cents": balance + interest, "interest_cents": interest,
                         "principal_cents": balance, "balance_cents": 0})
            break
        rows.append({"month": month, "payment_cents": pay, "interest_cents": interest,
                     "principal_cents": pay - interest, "balance_cents": balance - (pay - interest)})
        balance -= pay - interest
    return {"payment_cents": pay, "total_interest_cents": sum(r["interest_cents"] for r in rows), "rows": rows}


def req(principal, rate_bp, months):
    return {"principal_cents": principal, "annual_rate_bp": rate_bp, "months": months}


def is_whole(value):
    return type(value) is int


def well_formed(body):
    """True when body has the C1 shape: exact fields, whole numbers, rows numbered 1, 2, 3, ..."""
    if not isinstance(body, dict) or set(body) != {"payment_cents", "total_interest_cents", "rows"}:
        return False
    if not is_whole(body["payment_cents"]) or not is_whole(body["total_interest_cents"]):
        return False
    rows = body["rows"]
    if not isinstance(rows, list) or not rows:
        return False
    keys = {"month", "payment_cents", "interest_cents", "principal_cents", "balance_cents"}
    for number, row in enumerate(rows, start=1):
        if not isinstance(row, dict) or set(row) != keys or not all(is_whole(row[k]) for k in keys):
            return False
        if row["month"] != number:
            return False
    return True
