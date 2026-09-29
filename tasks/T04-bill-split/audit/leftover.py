"""X6 (C2): the leftover cents follow the one rule. Each diner first gets their fair amount
rounded down; the missing cents go one each to the largest fractional parts, compared
exactly, and on equal fractional parts to the diner listed earlier in `diners`.

To judge this rule on its own, the fair amounts here use the total_cents the command
itself reports (so a tip rounding slip is left to X1), with parts taken from G2 and G3."""

import random

from _cmd import call, finish
from _model import allocate, bill, expected, fair, random_bill, subtotal

# (diners, orders, tip_percent, shares), each worked out by hand from C2.
HAND = [
    # Equal thirds: the cent goes to the first listed, not alphabetically or to whoever ordered.
    ([("Zeno", "share"), ("Yara", "share"), ("Mirte", "share")], [("Mirte", 1000)], 0,
     {"Zeno": 334, "Yara": 333, "Mirte": 333}),
    # Largest fractional parts win over listing order: .3, .9, .8 with two cents left.
    ([("Tove", "own"), ("Galo", "own"), ("Ines", "own")], [("Tove", 1003), ("Galo", 1009), ("Ines", 998)], 10,
     {"Tove": 1103, "Galo": 1110, "Ines": 1098}),
    # An own-payer and two sharers with equal fractional parts: listing order across kinds.
    ([("Pim", "share"), ("Oda", "own"), ("Brix", "share")], [("Pim", 10), ("Oda", 7), ("Brix", 4)], 50,
     {"Pim": 11, "Oda": 11, "Brix": 10}),
    # Whole fair amounts never take a leftover cent, even when listed first.
    ([("Nell", "own"), ("Hedda", "own"), ("Fumi", "share"), ("Caio", "share"), ("Suvi", "share")],
     [("Nell", 500), ("Fumi", 1000), ("Caio", 1)], 0,
     {"Nell": 500, "Hedda": 0, "Fumi": 334, "Caio": 334, "Suvi": 333}),
    # Three of four cents left over (the most possible for four diners).
    ([("Elio", "share"), ("Björn", "share"), ("Aroha", "share"), ("Ngozi", "share")], [("Ngozi", 7)], 0,
     {"Elio": 2, "Björn": 2, "Aroha": 2, "Ngozi": 1}),
    # Rounding to nearest would give 67 + 67 + 67 and leave Yara -1.
    ([("Galo", "share"), ("Tove", "share"), ("Rune", "share"), ("Yara", "own")], [("Tove", 200)], 0,
     {"Galo": 67, "Tove": 67, "Rune": 66, "Yara": 0}),
    # The sharer who ordered nothing is listed first and takes the tied cent.
    ([("Ines", "share"), ("Galo", "share")], [("Galo", 3)], 0, {"Ines": 2, "Galo": 1}),
    # Fair 33.6, 33.6, 37.8 at 5%: two cents go to the .8 and then the first .6; rounding
    # each to the nearest cent would ask for 106 of a 105-cent total.
    ([("Mirte", "own"), ("Fumi", "own"), ("Oda", "own")], [("Mirte", 32), ("Fumi", 32), ("Oda", 36)], 5,
     {"Mirte": 34, "Fumi": 33, "Oda": 38}),
    # A smaller fraction listed first loses to a larger one listed last: .25 vs .75.
    ([("Zoë", "own"), ("Aroha", "own")], [("Zoë", 5), ("Aroha", 15)], 25, {"Zoë": 6, "Aroha": 19}),
]

# Bills whose fractional parts tie exactly, or nearly, where floating point misorders them.
FLOATY = [
    ([("Rune", "share"), ("Suvi", "own"), ("Yara", "own"), ("Zeno", "share"), ("Elio", "own")],
     [("Yara", 318), ("Rune", 4715), ("Elio", 16), ("Suvi", 481), ("Suvi", 2695), ("Rune", 4065)], 10),
    ([("Rune", "share"), ("Suvi", "share"), ("Yara", "own"), ("Zeno", "share"), ("Elio", "share")],
     [("Elio", 582), ("Yara", 1548)], 20),
    ([("Rune", "own"), ("Suvi", "own"), ("Yara", "share"), ("Zeno", "share")],
     [("Rune", 1078), ("Yara", 2662), ("Yara", 1326), ("Suvi", 4324)], 10),
    ([("Rune", "share"), ("Suvi", "own"), ("Yara", "own")],
     [("Rune", 915), ("Yara", 3087), ("Rune", 1251), ("Suvi", 4087)], 20),
    ([("Rune", "own"), ("Suvi", "own"), ("Yara", "own"), ("Zeno", "share")],
     [("Zeno", 1085), ("Zeno", 2534), ("Yara", 28), ("Suvi", 1350), ("Rune", 2373)], 20),
    ([("Rune", "share"), ("Suvi", "own"), ("Yara", "share"), ("Zeno", "own"), ("Elio", "own")],
     [("Yara", 2295), ("Elio", 2662), ("Suvi", 211), ("Zeno", 4652)], 20),
]

cases = []
for diners, orders, tip_percent, want in HAND:
    request = bill(diners, orders, tip_percent)
    assert expected(request)["shares"] == want, (diners, want)  # guards the worked examples
    cases.append(request)
cases += [bill(d, o, t) for d, o, t in FLOATY]

rng = random.Random(6061301)
for _ in range(80):
    cases.append(random_bill(rng))
# Tables with many sharers and few items, so many fractional parts tie.
for _ in range(20):
    names = rng.sample(["Oda", "Brix", "Nell", "Tove", "Ines", "Galo", "Pim", "Rune", "Suvi", "Yara"],
                       rng.randint(3, 9))
    diners = [(n, "own" if rng.random() < 0.25 else "share") for n in names]
    orders = [(rng.choice(names), rng.randint(1, 3000)) for _ in range(rng.randint(1, 4))]
    cases.append(bill(diners, orders, rng.choice([0, 7, 10, 15, 18, 20, 33])))


def whole_number(value):
    """An integer, or a float holding a whole number (the type itself is C4's business)."""
    return not isinstance(value, bool) and (type(value) is int or (type(value) is float and value.is_integer()))


problems = []
for k, request in enumerate(cases, 1):
    status, body = call(request)
    shares = body.get("shares") if isinstance(body, dict) else None
    total = body.get("total_cents") if isinstance(body, dict) else None
    if status != 0 or not isinstance(shares, dict) or not whole_number(total):
        problems.append(f"bill {k}: expected shares and a whole total_cents, got {body!r} (status {status})")
        continue
    total = int(total)
    fairs = fair(request, total=total, sub=subtotal(request))
    want = allocate(fairs, total)
    if shares != want:
        wrong = {n: (shares.get(n), want[n]) for n in want if shares.get(n) != want[n]}
        problems.append(f"bill {k} (tip {request['tip_percent']}%, total {total}): "
                        f"shares that break the rule, as (got, expected): {wrong}")

finish(problems, f"leftover cents ok: {len(cases)} bills")
