"""H8: `split` reads one JSON object and writes one JSON object, with the fields and exit statuses of the intent."""

import copy
import random

from _bills import bill, random_bill
from _cmd import call, finish

FIELDS = {"subtotal_cents", "tip_cents", "total_cents", "shares"}
rng = random.Random(4048)
problems = []


def shape(request, label):
    """Return the response when it has the promised shape, else record a problem."""
    names = [d["name"] for d in request["diners"]]
    status, body = call(request)
    if status != 0:
        problems.append(f"{label}: exited with status {status}, expected 0")
    elif not isinstance(body, dict) or set(body) != FIELDS:
        problems.append(f"{label}: expected one JSON object with exactly {sorted(FIELDS)}, got {body!r}")
    elif not all(type(body[f]) is int for f in FIELDS - {"shares"}):
        problems.append(f"{label}: subtotal_cents, tip_cents and total_cents must be integers, got {body!r}")
    elif not isinstance(body["shares"], dict) or sorted(body["shares"]) != sorted(names):
        problems.append(f"{label}: shares must map each diner's name to cents, got {body['shares']!r}")
    elif not all(type(v) is int for v in body["shares"].values()):
        problems.append(f"{label}: every share must be an integer, got {body['shares']!r}")
    else:
        return body
    return None


# Names with spaces, accents and other scripts come back exactly as given.
unusual = bill([("Zoë", "own"), ("李明", "share"), ("Mary Ann", "share"), ("o'Neil", "own")],
               [("Zoë", 1450), ("李明", 990), ("o'Neil", 305)], 18)
body = shape(unusual, "unusual names")

requests = [random_bill(rng, diners=(1, 10)) for _ in range(25)]
for number, request in enumerate(requests, 1):
    plain = shape(request, f"random bill {number}")
    # Other fields in the request, a diner or an item are ignored.
    extra = copy.deepcopy(request)
    extra["table"] = 12
    extra["currency"] = "EUR"
    extra["note"] = {"tip_percent": 99}
    for d in extra["diners"]:
        d["seat"] = rng.randint(1, 20)
    for i in extra["items"]:
        i["dish"] = "soup of the day"
        i["quantity"] = 3
    decorated = shape(extra, f"random bill {number} with extra fields")
    if plain is not None and decorated is not None and plain != decorated:
        problems.append(f"random bill {number}: extra fields changed the response from {plain} to {decorated}")

# Refusals exit 2 and write nothing on standard output.
for label, raw in [
    ("not JSON", "{diners: []}"),
    ("a negative price", '{"diners": [{"name": "A", "pays": "own"}], "items": [{"diner": "A", "price_cents": -5}], "tip_percent": 10}'),
    ("a tip of 150", '{"diners": [{"name": "A", "pays": "own"}], "items": [{"diner": "A", "price_cents": 500}], "tip_percent": 150}'),
]:
    status, out = call(raw=raw)
    if status != 2 or out is not None:
        problems.append(f"{label}: a refusal must exit with status 2 and write nothing, got status {status} and {out!r}")

finish(problems, "interface ok: 51 valid requests and 3 refusals")
