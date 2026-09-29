"""X06 (G4): a surcharge of exactly 1500 cents is added on top of the base price when, and only
when, the longest side is over 100 cm or length plus girth is over 220 cm, where the length is
the longest side whatever order the sides come in; checked at 100/101 cm and 210 to 222 cm in
every side order. Judged: surcharge_cents, total_cents = base_cents + surcharge, and a base
price equal to that of a small parcel of the same zone and weight, so the surcharge is not
folded into the base. Every actual weight here outweighs the dimensional weight, so the price
itself (G1 to G3) cannot fail this check."""

from itertools import permutations

from _audit import check, dim_weight, expected, finish, is_price, number, parcel, parse, run_many, surcharge

# (weight_g, sides, oversize?) -- the flag is written out by hand from G4.
SHAPES = [
    (2400, (100, 12, 9), False),     # longest exactly 100
    (2400, (101, 12, 9), True),      # longest 101
    (18000, (99, 30, 30), False),    # length + girth 219
    (18000, (100, 35, 25), False),   # 220 exactly
    (19000, (100, 30, 31), True),    # 222
    (20000, (80, 35, 35), False),    # 220 exactly, longest well under 100
    (20000, (81, 35, 35), True),     # 221
    (15000, (60, 60, 20), False),    # 220 with a tie for longest side
    (15000, (61, 60, 20), True),     # 221
    (15500, (60, 60, 21), True),     # 222 with a tie for longest side
    (15000, (90, 40, 20), False),    # 210 -- over 220 only if a short side were taken as the length
    (5000, (70, 70, 5), False),      # 220 exactly
    (6000, (70, 70, 6), True),       # 222
    (700, (150, 1, 1), True),        # longest 150, the largest accepted
    (3300, (120, 5, 5), True),       # long and thin
    (12500, (50, 50, 5), False),     # heavy but compact: base over 10 kg, no surcharge
]
SMALL = (10, 10, 10)  # a companion parcel that is not oversize and whose dimensional weight is 200 g

cases, companions = [], []
for n, (weight, sides, flag) in enumerate(SHAPES):
    zone = n % 4 + 1
    assert weight >= dim_weight(*sides) and weight >= dim_weight(*SMALL)
    companion = parcel(zone, weight, *SMALL)
    for order in sorted(set(permutations(sides))):
        request = parcel(zone, weight, *order)
        want = 1500 if flag else 0
        assert expected(request)["surcharge_cents"] == want, request  # the oracle agrees with the hand flag
        cases.append((f"{request} ({'oversize' if flag else 'not oversize'})", request, surcharge(request, want)))
        companions.append((request, companion))

# The base price does not change with the surcharge: it equals the base price of a small parcel
# of the same zone and weight, which is not oversize.
results = run_many([r for pair in companions for r in pair])
problems = []
for i, (request, companion) in enumerate(companions):
    got, small = results[2 * i], results[2 * i + 1]
    if is_price(got) and is_price(small):
        base, small_base = number(parse(got[1]), "base_cents"), number(parse(small[1]), "base_cents")
        if base != small_base:
            problems.append(f"{request}: base_cents {base} differs from {small_base} for {companion}; "
                            "the surcharge must come on top of the base price")
if problems:
    finish(problems, "")

check(cases, "oversize surcharge ok")
