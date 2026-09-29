"""H2: at rates above zero the regular payment is the exact level payment rounded up to the cent (G1)."""

import random

from _cmd import call, finish
from _model import MAX_MONTHS, MAX_PRINCIPAL, MAX_RATE, exact_payment, payment, random_loan

rng = random.Random(8082)
cases = [
    (1, 1, 1), (1, MAX_RATE, MAX_MONTHS), (MAX_PRINCIPAL, MAX_RATE, MAX_MONTHS), (MAX_PRINCIPAL, 1, MAX_MONTHS),
    (MAX_PRINCIPAL, 1, 1), (MAX_PRINCIPAL, MAX_RATE, 1), (1, 1, MAX_MONTHS), (100, 600, 2), (99, 1200, 480),
    (1000000, 600, 12), (700000, 500, 24),
]

# Loans whose exact payment is already a whole number of cents: rounding up must leave it alone.
whole = []
for months in (1, 2, 3, 4):
    for rate in (1, 100, 120, 240, 600, 1200, 2400, 3000, 4800, 5000):
        denominator = (exact_payment(1, rate, months)).denominator
        for multiple in (1, 3, 7):
            if denominator * multiple <= MAX_PRINCIPAL:
                whole.append((denominator * multiple, rate, months))
cases += whole

while len(cases) < 220:
    loan = random_loan(rng, allow_zero=False)
    cases.append((loan["principal_cents"], loan["annual_rate_bp"], loan["months"]))

problems = []
for principal, rate, months in cases:
    expected = payment(principal, rate, months)
    status, body = call({"principal_cents": principal, "annual_rate_bp": rate, "months": months})
    got = body.get("payment_cents") if isinstance(body, dict) else None
    if status != 0 or got != expected:
        exact = exact_payment(principal, rate, months)
        shown = f"about {float(exact):.6f}" if exact.denominator != 1 else f"{exact} exactly"
        problems.append(f"{principal} cents at {rate} bp for {months} months: exact payment {shown}, "
                        f"expected {expected}, got {got!r} (status {status})")

assert len(whole) >= 80 and all(exact_payment(*case).denominator == 1 for case in whole), "check setup"
finish(problems, f"payments ok: {len(cases)} loans, {len(whole)} with a whole-cent exact payment")
