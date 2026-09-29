"""X04 (G2): up to 10,000 g, every zone pays the table price of the lightest bracket that holds
the billable weight, each bracket including its upper limit; checked on both sides of every
limit and inside every bracket, in every zone. Only base_cents is judged, on parcels billed on
their actual weight, so that a G1 mistake cannot fail this check (that a parcel billed on its
dimensional weight pays the same as a parcel of that actual weight is checked in X03)."""

from _audit import TABLE, actual_wins, check, expected, parcel, values

BRACKETS = (500, 1000, 2000, 5000, 10000)


def table_price(zone, grams):  # written out again from the table, independently of the oracle
    for limit, price in zip(BRACKETS, TABLE[zone]):
        if grams <= limit:
            return price
    raise ValueError(grams)


WEIGHTS = (2, 137, 499, 500, 501, 820, 999, 1000, 1001, 1456,
           1999, 2000, 2001, 3871, 4999, 5000, 5001, 8123, 9999, 10000)
SMALL = ((1, 1, 1), (12, 9, 4), (9, 4, 12), (4, 12, 9))  # volumes of 1 and 432 cm3

cases = []
for zone in (1, 2, 3, 4):
    for weight in WEIGHTS:
        sides = SMALL[0] if weight < 88 else SMALL[zone - 1]
        request = parcel(zone, weight, *sides)
        want = expected(request)
        assert actual_wins(request) and want["billable_g"] == weight
        assert want["base_cents"] == table_price(zone, weight) and want["surcharge_cents"] == 0
        cases.append((f"zone {zone}, {weight} g", request, values(request, {"base_cents": want["base_cents"]})))

check(cases, "rate table brackets ok")
