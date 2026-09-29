"""Shared helpers for the hidden checks: bill generation and the intent's arithmetic."""

from fractions import Fraction

NAMES = [
    "Zara", "Omar", "Beth", "Yuki", "Carl", "Nia", "Hugo", "Asha", "Theo", "Mei",
    "Rui", "Dana", "Ilse", "Kofi", "Pia", "Emil", "Wes", "Lars", "Gia", "Finn",
]


def bill(pays, orders, tip):
    """pays: [(name, "own"|"share"), ...] in list order; orders: [(name, cents), ...]."""
    return {
        "diners": [{"name": n, "pays": p} for n, p in pays],
        "items": [{"diner": n, "price_cents": c} for n, c in orders],
        "tip_percent": tip,
    }


def price(rng):
    """A menu price in cents: mostly ordinary, sometimes tiny or large."""
    roll = rng.random()
    if roll < 0.1:
        return rng.randint(1, 99)
    if roll < 0.9:
        return rng.randint(100, 4999)
    return rng.randint(5000, 60000)


def tip(rng):
    return rng.choice([0, 10, 12, 15, 18, 20, 22, 25, rng.randint(0, 100), rng.randint(0, 100)])


def random_bill(rng, diners=(1, 8), share=0.5, empty=0.2, tip_percent=None):
    """A random valid request. Names come in a shuffled, non-alphabetical order."""
    count = rng.randint(*diners)
    names = rng.sample(NAMES, count)
    pays = [(n, "share" if rng.random() < share else "own") for n in names]
    orders = []
    for n in names:
        if rng.random() >= empty:
            orders += [(n, price(rng)) for _ in range(rng.randint(1, 4))]
    if not orders:
        orders.append((rng.choice(names), price(rng)))
    rng.shuffle(orders)
    return bill(pays, orders, tip(rng) if tip_percent is None else tip_percent)


def expected_tip(subtotal, tip_percent):
    return (subtotal * tip_percent + 50) // 100


def parts(request):
    """Each diner's part of the subtotal (G2, G3), as exact fractions, and the subtotal."""
    pays = {d["name"]: d["pays"] for d in request["diners"]}
    own = {n: 0 for n, p in pays.items() if p == "own"}
    pool = 0
    for item in request["items"]:
        if pays[item["diner"]] == "own":
            own[item["diner"]] += item["price_cents"]
        else:
            pool += item["price_cents"]
    sharers = [n for n, p in pays.items() if p == "share"]
    result = {n: Fraction(c) for n, c in own.items()}
    for n in sharers:
        result[n] = Fraction(pool, len(sharers))
    return result, sum(item["price_cents"] for item in request["items"])


def fair_amounts(request, total):
    """Each diner's fair amount (G4) for the given total."""
    part, subtotal = parts(request)
    return {n: part[n] * total / subtotal for n in part}


def expected_shares(request, total):
    """The shares that the leftover-cent rule (C2) gives for the given total."""
    names = [d["name"] for d in request["diners"]]
    fair = fair_amounts(request, total)
    shares = {n: fair[n].numerator // fair[n].denominator for n in names}
    leftover = total - sum(shares.values())
    order = sorted(range(len(names)), key=lambda i: (-(fair[names[i]] - shares[names[i]]), i))
    for i in order[:leftover]:
        shares[names[i]] += 1
    return shares


def shares_of(body):
    """The shares and total from a response, or None when the response is not usable."""
    if not isinstance(body, dict):
        return None
    shares, total = body.get("shares"), body.get("total_cents")
    if not isinstance(shares, dict) or type(total) is not int:
        return None
    return shares, total


def near(share, fair):
    """True when a share is a whole number of cents less than one cent from its fair amount."""
    return type(share) is int and abs(share - fair) < 1
