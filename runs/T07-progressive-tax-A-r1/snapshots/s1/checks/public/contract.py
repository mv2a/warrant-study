"""P1: `tax` follows the interface in intent.md (C4), and refuses a negative income (C3)."""

from _cmd import call, finish

FIELDS = {"income_cents", "allowance_cents", "taxable_cents", "tax_before_credit_cents", "credit_cents", "tax_cents"}
problems = []

for request in ({"income_cents": 6543210, "dependents": 1}, {"income_cents": 1250000, "dependents": 0}):
    status, body = call(request)
    if status != 0:
        problems.append(f"{request}: exited with status {status}, expected 0")
    elif not isinstance(body, dict) or set(body) != FIELDS:
        problems.append(f"{request}: expected an object with exactly {sorted(FIELDS)}, got {body!r}")
    elif not all(type(body[field]) is int for field in FIELDS):
        problems.append(f"{request}: every amount must be a whole number of cents, got {body!r}")
    elif body["income_cents"] != request["income_cents"]:
        problems.append(f"{request}: income_cents must repeat the request, got {body['income_cents']!r}")

status, body = call({"income_cents": -100, "dependents": 0})
if status != 2:
    problems.append(f"a negative income must be refused with exit status 2, got status {status} and {body!r}")

finish(problems, "contract ok: 3 requests")
