"""X07 (C2): parcels exactly at a carrying limit are priced, and parcels past one are refused
(status 2, no price): billable weight 30,000 g, longest side 150 cm, length plus girth 300 cm,
with each shape given in three side orders. Only priced or refused is judged: the price is
G1 to G4's business and what a refusal writes is C1's. The 30,000 g limit is reached by the
actual weight, by the dimensional weight, and by both at once."""

from _audit import REFUSED, check, expected, parcel, priced, refused


def rotations(sides):
    a, b, c = sides
    return ((a, b, c), (b, c, a), (c, a, b))


# (zone, weight_g, sides, carried?) -- the flag is written out by hand from C2.
SHAPES = [
    # billable weight
    (1, 30000, (10, 10, 10), True),
    (2, 29999, (12, 11, 10), True),
    (3, 30001, (10, 10, 10), False),
    (4, 30002, (1, 1, 1), False),
    (1, 45000, (20, 20, 20), False),
    (2, 10 ** 9, (10, 10, 10), False),
    (3, 10 ** 18, (5, 5, 5), False),
    (4, 1, (58, 50, 50), True),        # dimensional 29000, far above the actual weight
    (1, 30000, (150, 50, 19), True),   # 30000 actual, longest 150, length + girth 288
    (2, 1, (94, 84, 19), False),       # dimensional 30005 (150024 / 5 rounded up), length + girth exactly 300
    (3, 1, (141, 56, 19), False),      # dimensional 30005
    (4, 2000, (100, 50, 50), False),   # dimensional 50000, length + girth exactly 300
    (1, 1, (125, 40, 30), True),       # dimensional exactly 30000 (150000 / 5), 1 g actual
    (2, 29999, (75, 50, 40), True),    # dimensional exactly 30000 beats an actual 29999
    (3, 30000, (80, 75, 25), True),    # actual and dimensional both exactly 30000
    (4, 1, (62, 55, 44), False),       # dimensional exactly 30008 (150040 / 5), no rounding
    # longest side
    (1, 700, (150, 10, 10), True),
    (2, 700, (151, 10, 10), False),
    (3, 1, (151, 1, 1), False),
    (4, 3000, (152, 20, 20), False),
    (1, 500, (400, 5, 5), False),
    (2, 500, (10 ** 6, 1, 1), False),
    # length plus girth
    (3, 300, (100, 99, 1), True),      # 300
    (4, 300, (101, 99, 1), False),     # 301
    (1, 800, (150, 74, 1), True),      # 300 with the longest side at its limit too
    (2, 800, (150, 74, 2), False),     # 302
    (3, 800, (149, 75, 1), False),     # 301
    (4, 5000, (90, 90, 15), True),     # 300, dimensional 24300
    (1, 5000, (91, 90, 15), False),    # 301
    (2, 5000, (90, 90, 16), False),    # 302
    (3, 10, (120, 89, 1), True),       # 300
    (4, 30000, (150, 74, 1), True),    # every limit reached at once
    (1, 50000, (200, 200, 200), False),
]

cases = []
for zone, weight, sides, carried in SHAPES:
    for order in rotations(sides):
        request = parcel(zone, weight, *order)
        want = expected(request)
        assert (want is not REFUSED) == carried, (request, want)
        cases.append((f"{request} ({'carried' if carried else 'past a limit'})", request, priced if carried else refused))

check(cases, "carrying limits ok")
