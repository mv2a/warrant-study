"""X9 (S2): 100000 cents at 0 basis points for 7 months, exactly as the intent states it."""

from _cmd import finish
from _scenario import row_field, run

body, problems = run('{"annual_rate_bp":0,"months":7,"principal_cents":100000}')
if body:
    rows = body["rows"]
    facts = [
        ("regular payment", body.get("payment_cents"), 14286),
        ("number of payments (the 7th is the last)", len(rows), 7),
        ("payments", [row_field(rows, k, "payment_cents") for k in range(len(rows))], [14286] * 6 + [14284]),
        ("interest each month", [row_field(rows, k, "interest_cents") for k in range(len(rows))], [0] * 7),
        ("month number of the last payment", row_field(rows, -1, "month"), 7),
        ("balance after the last payment", row_field(rows, -1, "balance_cents"), 0),
        ("total interest", body.get("total_interest_cents"), 0),
    ]
    problems += [f"S2: {what} should be {wanted}, got {got!r}"[:300] for what, got, wanted in facts if got != wanted]

finish(problems, "S2 ok")
