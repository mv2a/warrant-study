"""Expected values, worked out from intent.md alone, shared by the holdout checks."""

import itertools

TABLE = (  # (heaviest billable weight in the bracket, prices for zones 1 to 4), in cents
    (500, (450, 520, 610, 780)),
    (1000, (540, 630, 740, 950)),
    (2000, (690, 810, 960, 1240)),
    (5000, (920, 1090, 1310, 1700)),
    (10000, (1350, 1600, 1930, 2520)),
)
EXTRA_KG = (85, 105, 130, 175)
FIELDS = {"billable_g", "base_cents", "surcharge_cents", "total_cents"}


def parcel(zone, weight, sides):
    length, width, height = sides
    return {"zone": zone, "weight_g": weight, "length_cm": length, "width_cm": width, "height_cm": height}


def sides_of(p):
    return p["length_cm"], p["width_cm"], p["height_cm"]


def dimensional(p):
    length, width, height = sides_of(p)
    return -(-(length * width * height) // 5)


def billable(p):
    return max(p["weight_g"], dimensional(p))


def longest_and_length_plus_girth(p):
    a, b, c = sorted(sides_of(p), reverse=True)
    return a, a + 2 * (b + c)


def base(zone, billable_g):
    for limit, prices in TABLE:
        if billable_g <= limit:
            return prices[zone - 1]
    extra_kg = -(-(billable_g - 10000) // 1000)
    return TABLE[-1][1][zone - 1] + extra_kg * EXTRA_KG[zone - 1]


def surcharge(p):
    longest, length_plus_girth = longest_and_length_plus_girth(p)
    return 1500 if longest > 100 or length_plus_girth > 220 else 0


def carriable(p):
    longest, length_plus_girth = longest_and_length_plus_girth(p)
    return billable(p) <= 30000 and longest <= 150 and length_plus_girth <= 300


def expected(p):
    b = billable(p)
    base_cents = base(p["zone"], b)
    extra = surcharge(p)
    return {"billable_g": b, "base_cents": base_cents, "surcharge_cents": extra, "total_cents": base_cents + extra}


def orders(sides):
    """Every distinct order in which the three sides can be given."""
    return sorted(set(itertools.permutations(sides)))


def random_parcel(rng, accept=lambda p: True):
    """A random parcel we can carry, of a random shape, for which accept(parcel) holds."""
    while True:
        shape = rng.choice(("small", "box", "long", "flat"))
        if shape == "small":
            sides = [rng.randint(1, 30) for _ in range(3)]
        elif shape == "box":
            sides = [rng.randint(10, 70) for _ in range(3)]
        elif shape == "long":
            sides = [rng.randint(60, 150), rng.randint(1, 30), rng.randint(1, 30)]
        else:
            sides = [rng.randint(40, 120), rng.randint(30, 90), rng.randint(1, 8)]
        rng.shuffle(sides)
        weight = rng.choice((rng.randint(1, 2000), rng.randint(1, 12000), rng.randint(1, 30000)))
        p = parcel(rng.randint(1, 4), weight, sides)
        if carriable(p) and accept(p):
            return p


def exact(p):
    """The billable weight needs no rounding: the actual weight wins, or the volume divides by 5."""
    length, width, height = sides_of(p)
    return p["weight_g"] >= dimensional(p) or (length * width * height) % 5 == 0


def priced(status, body):
    return status == 0 and isinstance(body, dict)


def refused(status, body):
    """Refused and never priced (what a refusal writes is C1's business)."""
    return status == 2 and not (isinstance(body, dict) and "total_cents" in body)
