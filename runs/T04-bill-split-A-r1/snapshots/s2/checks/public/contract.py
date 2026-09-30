"""P1: `split` follows the interface in the intent."""

from _cmd import call, finish

FIELDS = {"subtotal_cents", "tip_cents", "total_cents", "shares"}
VALID = [
    {
        "diners": [{"name": "Mo", "pays": "own"}, {"name": "Lia", "pays": "share"}, {"name": "Raf", "pays": "share"}],
        "items": [{"diner": "Mo", "price_cents": 1450}, {"diner": "Lia", "price_cents": 2210}],
        "tip_percent": 15,
    },
    {
        "diners": [{"name": "Kit", "pays": "own"}],
        "items": [{"diner": "Kit", "price_cents": 899}],
        "tip_percent": 0,
    },
]
problems = []

for request in VALID:
    names = [d["name"] for d in request["diners"]]
    status, body = call(request)
    if status != 0:
        problems.append(f"{names}: exited with status {status}, expected 0")
    elif not isinstance(body, dict) or set(body) != FIELDS:
        problems.append(f"{names}: expected an object with exactly {sorted(FIELDS)}, got {body!r}")
    elif not all(type(body[f]) is int for f in FIELDS - {"shares"}):
        problems.append(f"{names}: subtotal_cents, tip_cents and total_cents must be integers, got {body!r}")
    elif not isinstance(body["shares"], dict) or set(body["shares"]) != set(names):
        problems.append(f"{names}: shares must map each diner's name to cents, got {body['shares']!r}")
    elif not all(type(v) is int for v in body["shares"].values()):
        problems.append(f"{names}: every share must be an integer number of cents, got {body['shares']!r}")

refused = {
    "diners": [{"name": "Mo", "pays": "own"}],
    "items": [{"diner": "Nobody", "price_cents": 500}],
    "tip_percent": 10,
}
status, body = call(refused)
if status != 2 or body is not None:
    problems.append(f"an item for an unlisted diner must be refused with status 2 and no output, got status {status} and {body!r}")

finish(problems, "contract ok: 3 requests")
