"""X10 (S3): 700000 cents at 500 basis points for 24 months, exactly as the intent states it."""

from _cmd import finish
from _scenario import row_field, run

body, problems = run('  {"principal_cents" : 700000 , "months" : 24 , "annual_rate_bp" : 500}\t\n')
if body:
    rows = body["rows"]
    facts = [
        ("regular payment", body.get("payment_cents"), 30710),
        ("number of payments (the 24th is the last)", len(rows), 24),
        ("month 1 payment", row_field(rows, 0, "payment_cents"), 30710),
        ("month 1 interest", row_field(rows, 0, "interest_cents"), 2917),
        ("month 1 principal", row_field(rows, 0, "principal_cents"), 27793),
        ("month number of the last payment", row_field(rows, -1, "month"), 24),
        ("last payment", row_field(rows, -1, "payment_cents"), 30714),
        ("last-month interest", row_field(rows, -1, "interest_cents"), 127),
        ("balance after the last payment", row_field(rows, -1, "balance_cents"), 0),
        ("total interest", body.get("total_interest_cents"), 37044),
    ]
    problems += [f"S3: {what} should be {wanted}, got {got!r}" for what, got, wanted in facts if got != wanted]
    last, regular = row_field(rows, -1, "payment_cents"), body.get("payment_cents")
    if type(last) is int and type(regular) is int and not last > regular:
        problems.append(f"S3: the last payment {last} should be more than the regular payment {regular}")

finish(problems, "S3 ok")
