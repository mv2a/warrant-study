"""X8 (S1): 1000000 cents at 600 basis points for 12 months, exactly as the intent states it."""

from _cmd import finish
from _scenario import row_field, run

# The same loan as S1, with the fields in another order and spread over lines.
body, problems = run('{\n  "months": 12,\n  "annual_rate_bp": 600,\n  "principal_cents": 1000000\n}\n')
if body:
    rows = body["rows"]
    facts = [
        ("regular payment", body.get("payment_cents"), 86067),
        ("number of payments (the 12th is the last)", len(rows), 12),
        ("month 1 payment", row_field(rows, 0, "payment_cents"), 86067),
        ("month 1 interest", row_field(rows, 0, "interest_cents"), 5000),
        ("month 1 principal", row_field(rows, 0, "principal_cents"), 81067),
        ("balance after month 1", row_field(rows, 0, "balance_cents"), 918933),
        ("month number of the last payment", row_field(rows, -1, "month"), 12),
        ("last payment", row_field(rows, -1, "payment_cents"), 86059),
        ("balance after the last payment", row_field(rows, -1, "balance_cents"), 0),
        ("total interest", body.get("total_interest_cents"), 32796),
    ]
    problems += [f"S1: {what} should be {wanted}, got {got!r}" for what, got, wanted in facts if got != wanted]

finish(problems, "S1 ok")
