"""H1: subtotal, tip rounded to the nearest cent with halves up, and total."""

import random

from _bills import bill, expected_tip, random_bill
from _cmd import call, finish

rng = random.Random(4041)
requests = []

# One diner, one item: the tip on exact halves and just either side of them.
for cents, tip in [
    (2525, 10), (2535, 10), (1005, 10), (1, 50), (3, 50), (5, 10), (1, 49), (1, 51),
    (150, 1), (250, 1), (350, 1), (12345, 0), (999999, 100), (1250, 18), (4125, 2),
    (8250, 1), (99, 50), (1050, 5), (2150, 3), (7, 50),
]:
    requests.append(bill([("Zara", "own")], [("Zara", cents)], tip))

# Many diners and items, with the subtotal forced to end in a half-cent tip.
for _ in range(40):
    request = random_bill(rng, diners=(1, 6), tip_percent=rng.choice([10, 30, 50, 70, 90]))
    first = request["items"][0]
    missing = (5 - sum(i["price_cents"] for i in request["items"])) % 10
    first["price_cents"] += missing  # subtotal ends in 5, so subtotal x tip ends in 50
    requests.append(request)

# Ordinary random bills.
requests += [random_bill(rng) for _ in range(40)]

problems = []
for request in requests:
    subtotal = sum(i["price_cents"] for i in request["items"])
    tip = expected_tip(subtotal, request["tip_percent"])
    want = (subtotal, tip, subtotal + tip)
    status, body = call(request)
    got = tuple(body.get(k) for k in ("subtotal_cents", "tip_cents", "total_cents")) if isinstance(body, dict) else None
    if status != 0 or got != want:
        problems.append(
            f"subtotal {subtotal} at {request['tip_percent']}%: expected subtotal, tip, total {want}, got {got} (status {status})"
        )

finish(problems, f"tip ok: {len(requests)} bills")
