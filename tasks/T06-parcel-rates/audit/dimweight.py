"""X03 (G1): billable weight is the greater of the actual weight and ceil(L x W x H / 5),
with the rounding always upward, including where rounding up moves a parcel into the next
bracket, and the result does not depend on the order the sides are given in. And a parcel is
charged on that billable weight: a light parcel billed on its dimensional weight gets the same
base_cents as a small parcel of the same zone whose actual weight equals that dimensional
weight. What the table price is (G2, G3) and the surcharge (G4) are judged elsewhere."""

from itertools import permutations

from _audit import at_limit, check, expected, finish, is_oversize, is_price, number, parcel, parse, run_many, values

# (zone, weight_g, length, width, height, billable_g the intent requires); the last column
# is written out by hand from G1 and also compared with the shared oracle below.
HAND = [
    (1, 4200, 25, 20, 30, 4200),     # dim 3000 < actual
    (2, 700, 40, 30, 25, 6000),      # dim 6000 > actual
    (3, 2000, 20, 25, 20, 2000),     # dim 2000 = actual
    (1, 201, 10, 10, 10, 201),       # dim exactly 200, actual one gram more
    (1, 1, 3, 1, 1, 1),              # 3 / 5 = 0.6 -> 1
    (1, 1, 11, 1, 1, 3),             # 2.2 -> 3
    (2, 1, 7, 2, 1, 3),              # 2.8 -> 3
    (3, 1, 13, 1, 1, 3),             # 2.6 -> 3
    (4, 1, 3, 3, 1, 2),              # 1.8 -> 2
    (1, 10, 17, 19, 23, 1486),       # 7429 / 5 = 1485.8 -> 1486
    (3, 499, 50, 50, 1, 500),        # 2500 / 5 = 500 exactly
    (2, 100, 61, 41, 1, 501),        # 2501 / 5 = 500.2 -> 501: into the 1,000 g bracket
    (4, 500, 61, 41, 1, 501),        # dim 501 beats an actual 500
    (1, 502, 61, 41, 1, 502),        # actual 502 beats dim 501
    (3, 100, 41, 61, 2, 1001),       # 5002 / 5 = 1000.4 -> 1001: into the 2,000 g bracket
    (4, 1, 4, 61, 41, 2001),         # 10004 / 5 = 2000.8 -> 2001: into the 5,000 g bracket
    (2, 2001, 61, 41, 4, 2001),      # dim equals actual at 2001
    (1, 5, 7, 94, 38, 5001),         # 25004 / 5 = 5000.8 -> 5001: into the 10,000 g bracket
    (3, 1, 100, 25, 20, 10000),      # 50000 / 5 = 10000 exactly
    (4, 1, 137, 73, 5, 10001),       # 50005 / 5 = 10001: one extra kilogram
    (2, 9, 103, 89, 6, 11001),       # 55002 / 5 = 11000.4 -> 11001: two extra kilograms
    (1, 1, 60, 50, 50, 30000),       # 150000 / 5 = 30000, the heaviest accepted
    (2, 25000, 5, 5, 5, 25000),      # heavy and small
    (4, 7654, 9, 8, 7, 7654),        # dim 101 (100.8 rounded up) far below actual
]

cases = []
for zone, weight, length, width, height, grams in HAND:
    request = parcel(zone, weight, length, width, height)
    want = expected(request)
    assert want["billable_g"] == grams, (request, want)  # the oracle agrees with the hand column
    cases.append((f"{request}", request, values(request, {"billable_g": grams})))

# The same parcel in all six side orders is billed the same.
for zone, weight, sides in ((3, 150, (17, 9, 4)), (2, 60, (61, 41, 1)), (4, 2222, (33, 21, 16))):
    for order in sorted(set(permutations(sides))):
        request = parcel(zone, weight, *order)
        cases.append((f"{request} (side order)", request, values(request, {"billable_g": expected(request)["billable_g"]})))

# Charged on the billable weight: parcels billed on a dimensional weight on or just over each
# bracket or kilogram limit (several reached only by rounding up), in every zone, against a small
# parcel of the same zone whose actual weight is that dimensional weight. The small parcel is
# oversize exactly when the bulky one is (a 120 x 1 x 1 cm tube), so the surcharge (G4) cannot
# make their base prices differ.
CHARGED = {500: (50, 50, 1), 501: (61, 41, 1), 1000: (50, 20, 5), 1001: (82, 61, 1),
           2000: (100, 10, 10), 2001: (61, 41, 4), 5000: (50, 50, 10), 5001: (94, 38, 7),
           10000: (80, 25, 25), 10001: (137, 73, 5), 11000: (55, 40, 25), 11001: (103, 89, 6),
           30000: (60, 50, 50)}
pairs = []
for zone in (1, 2, 3, 4):
    for grams, sides in CHARGED.items():
        bulky = parcel(zone, 1 + 37 * zone, *sides)
        dense = parcel(zone, grams, *((120, 1, 1) if is_oversize(*sides) else (1, 1, 1)))
        assert expected(bulky)["billable_g"] == grams == expected(dense)["billable_g"]
        assert expected(bulky)["surcharge_cents"] == expected(dense)["surcharge_cents"]
        pairs.append((bulky, dense))
results = run_many([r for pair in pairs for r in pair])
problems = []
for i, (bulky, dense) in enumerate(pairs):
    got, ref = results[2 * i], results[2 * i + 1]
    if not is_price(got):
        if not (got[0] == 2 and at_limit(bulky)):  # a refusal on a carrying limit is C2's business
            problems.append(f"{bulky}: expected a price, got status {got[0]} and {got[1][:80]!r}")
    elif is_price(ref):
        base, ref_base = number(parse(got[1]), "base_cents"), number(parse(ref[1]), "base_cents")
        if base != ref_base:
            problems.append(f"{bulky}: billable weight {expected(bulky)['billable_g']} g, but base_cents {base} "
                            f"differs from {ref_base} for {dense}")
if problems:
    finish(problems, "")

check(cases, "dimensional weight ok")
