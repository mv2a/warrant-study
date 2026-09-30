"""P1: `schedule` follows the interface in C1, and refuses two invalid requests."""

from _cmd import call, call_exact, finish

TOP = {"payment_cents", "total_interest_cents", "rows"}
ROW = {"month", "payment_cents", "interest_cents", "principal_cents", "balance_cents"}
problems = []

for request in (
    {"principal_cents": 250000, "annual_rate_bp": 1999, "months": 36},
    {"principal_cents": 5000, "annual_rate_bp": 0, "months": 3},
    {"principal_cents": 99, "annual_rate_bp": 450, "months": 1},
):
    status, body = call(request)
    if status != 0:
        problems.append(f"{request}: exited with status {status}, expected 0")
    elif not isinstance(body, dict) or set(body) != TOP:
        problems.append(f"{request}: expected an object with exactly {sorted(TOP)}, got {body!r}"[:300])
    elif type(body["payment_cents"]) is not int or type(body["total_interest_cents"]) is not int:
        problems.append(f"{request}: payment_cents and total_interest_cents must be whole numbers")
    elif not isinstance(body["rows"], list) or not body["rows"]:
        problems.append(f"{request}: rows must be a non-empty list, got {body['rows']!r}"[:300])
    else:
        for number, row in enumerate(body["rows"], start=1):
            if not isinstance(row, dict) or set(row) != ROW:
                problems.append(f"{request}: row {number} must have exactly {sorted(ROW)}, got {row!r}")
                break
            if not all(type(row[field]) is int for field in ROW):
                problems.append(f"{request}: row {number} must hold whole numbers only, got {row!r}")
                break
            if row["month"] != number:
                problems.append(f"{request}: row {number} has month {row['month']!r}; months count 1, 2, 3, ...")
                break

for name, request in (
    ("a request for 0 months", {"principal_cents": 100000, "annual_rate_bp": 500, "months": 0}),
    ("a request with no rate", {"principal_cents": 100000, "months": 12}),
):
    status, out = call_exact(request)
    if status != 2 or out != "":
        problems.append(f"{name} must be refused with status 2 and nothing on standard output, "
                        f"got status {status} and {out!r}"[:300])

finish(problems, "contract ok: 3 loans, 2 refusals")
