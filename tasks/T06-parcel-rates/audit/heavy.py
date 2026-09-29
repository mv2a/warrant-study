"""X05 (G3): over 10,000 g, a parcel pays its zone's 10,000 g price plus the zone's price per
extra kilogram for every started kilogram above 10,000 g, in every zone, from 10,001 g up to
the 30,000 g limit. Only base_cents is judged, on parcels billed on their actual weight, so that
a G1 mistake cannot fail this check (that a parcel billed on its dimensional weight pays the
same as a parcel of that actual weight is checked in X03)."""

from _audit import TABLE, actual_wins, check, expected, parcel, values


def heavy_price(zone, grams):  # written out again from G3, independently of the oracle
    extra = grams - 10000
    started = extra // 1000 + (1 if extra % 1000 else 0)
    return TABLE[zone][4] + TABLE[zone][5] * started


WEIGHTS = (10001, 10002, 10500, 10999, 11000, 11001, 11999, 12000, 12001, 14000,
           14001, 17777, 19999, 20000, 20001, 24500, 28000, 29001, 29999, 30000)
SIDES = ((30, 20, 15), (20, 15, 30), (15, 30, 20), (44, 21, 9))  # volumes of 9,000 and 8,316 cm3

cases = []
for zone in (1, 2, 3, 4):
    for weight in WEIGHTS:
        request = parcel(zone, weight, *SIDES[zone - 1])
        want = expected(request)
        assert actual_wins(request) and want["billable_g"] == weight
        assert want["base_cents"] == heavy_price(zone, weight) and want["surcharge_cents"] == 0
        cases.append((f"zone {zone}, {weight} g", request, values(request, {"base_cents": want["base_cents"]})))

check(cases, "over-10-kg pricing ok")
