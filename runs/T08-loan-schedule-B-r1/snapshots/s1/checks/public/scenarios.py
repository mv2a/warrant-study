"""P2: the three example loans in the intent (S1, S2, S3) come out exactly as stated."""

from _cmd import call, finish

problems = []


def schedule_for(name, request):
    status, body = call(request)
    if status != 0 or not isinstance(body, dict) or not isinstance(body.get("rows"), list) or not body["rows"]:
        problems.append(f"{name}: expected a schedule, got status {status} and {body!r}"[:300])
        return None
    return body


def expect(name, what, got, wanted):
    if got != wanted:
        problems.append(f"{name}: expected {what} of {wanted}, got {got!r}")


def field(rows, index, key):
    try:
        return rows[index].get(key)
    except (IndexError, AttributeError):
        return None


body = schedule_for("S1", {"principal_cents": 1000000, "annual_rate_bp": 600, "months": 12})
if body:
    rows = body["rows"]
    expect("S1", "a regular payment", body.get("payment_cents"), 86067)
    expect("S1", "12 rows", len(rows), 12)
    expect("S1", "month 1 interest", field(rows, 0, "interest_cents"), 5000)
    expect("S1", "month 1 principal", field(rows, 0, "principal_cents"), 81067)
    expect("S1", "a balance after month 1", field(rows, 0, "balance_cents"), 918933)
    expect("S1", "a last payment", field(rows, -1, "payment_cents"), 86059)
    expect("S1", "a final balance", field(rows, -1, "balance_cents"), 0)
    expect("S1", "total interest", body.get("total_interest_cents"), 32796)

body = schedule_for("S2", {"principal_cents": 100000, "annual_rate_bp": 0, "months": 7})
if body:
    rows = body["rows"]
    expect("S2", "a regular payment", body.get("payment_cents"), 14286)
    expect("S2", "7 rows", len(rows), 7)
    expect("S2", "payments", [field(rows, k, "payment_cents") for k in range(len(rows))], [14286] * 6 + [14284])
    expect("S2", "interest", [field(rows, k, "interest_cents") for k in range(len(rows))], [0] * 7)
    expect("S2", "a final balance", field(rows, -1, "balance_cents"), 0)
    expect("S2", "total interest", body.get("total_interest_cents"), 0)

body = schedule_for("S3", {"principal_cents": 700000, "annual_rate_bp": 500, "months": 24})
if body:
    rows = body["rows"]
    expect("S3", "a regular payment", body.get("payment_cents"), 30710)
    expect("S3", "24 rows", len(rows), 24)
    expect("S3", "month 1 interest", field(rows, 0, "interest_cents"), 2917)
    expect("S3", "month 1 principal", field(rows, 0, "principal_cents"), 27793)
    expect("S3", "a last payment", field(rows, -1, "payment_cents"), 30714)
    expect("S3", "last-month interest", field(rows, -1, "interest_cents"), 127)
    expect("S3", "a final balance", field(rows, -1, "balance_cents"), 0)
    expect("S3", "total interest", body.get("total_interest_cents"), 37044)

finish(problems, "scenarios ok: S1, S2, S3")
