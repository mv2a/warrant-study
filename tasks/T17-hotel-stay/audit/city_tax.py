"""X-G3: city tax on the first 10 nights only, never discounted."""

from _audit import DAYS, call_all, is_number, refused, request, show
from _cmd import finish

# Rates that are multiples of 80, so any 10% or 15% discount is an exact share of the room charge.
RATES = [80, 2400, 7520, 10000, 13680, 26640, 99920]

cases = []
for nights in range(1, 31):
    for k in (0, 3):  # two different check-in days for every length
        day = DAYS[(nights + k) % 7]
        if refused(day, nights):
            day = "mon"
        cases.append(request(day, nights, RATES[(nights + k) % len(RATES)]))

problems = []
for req, (status, body) in zip(cases, call_all(cases)):
    nights = req["nights"]
    want_tax = 275 * min(nights, 10)
    if status != 0 or not isinstance(body, dict):
        problems.append(f"{show(req)}: expected a priced stay, got {body!r} (status {status})")
        continue
    if body.get("tax_cents") != want_tax:
        problems.append(f"{show(req)}: expected tax_cents {want_tax}, got {body.get('tax_cents')!r}")
        continue
    room, discount, total = body.get("room_cents"), body.get("discount_cents"), body.get("total_cents")
    if not all(is_number(v) for v in (room, discount, total)):
        problems.append(f"{show(req)}: expected numeric amounts, got {body!r}")
        continue
    # Whatever tier applies (that is X2's concern), the discount must not take a share of the tax:
    # a discount that is 10% or 15% of room plus tax, rather than of the room alone, is caught here.
    room_shares = {room * pct // 100 for pct in (0, 10, 15)}
    taxed_shares = {(room + want_tax) * pct // 100 for pct in (10, 15)}
    if discount in taxed_shares - room_shares:
        problems.append(f"{show(req)}: the discount {discount} is a share of the room charge plus the "
                        f"tax ({room} + {want_tax}); the tax is never discounted")
    if total != room - discount + want_tax:
        problems.append(f"{show(req)}: the full tax {want_tax} should be added after the discount: "
                        f"expected total {room - discount + want_tax}, got {total}")

finish(problems, f"city tax ok on {len(cases)} stays of 1 to 30 nights")
