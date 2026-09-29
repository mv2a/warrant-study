"""The splitting rules of intent.md, written from the intent alone, in exact arithmetic.

Used by the audit checks to work out what a correct `split` must answer. Nothing here
calls the command.
"""

from fractions import Fraction
import math


def bill(diners, orders, tip, **extra):
    """diners: [(name, "own"|"share"), ...] in listing order; orders: [(name, cents), ...]."""
    request = {
        "diners": [{"name": n, "pays": p} for n, p in diners],
        "items": [{"diner": n, "price_cents": c} for n, c in orders],
        "tip_percent": tip,
    }
    request.update(extra)
    return request


def subtotal(request):
    """G1: the sum of every item's price."""
    return sum(item["price_cents"] for item in request["items"])


def tip(sub, tip_percent):
    """G1: tip_percent percent of the subtotal, to the nearest cent, an exact half cent up."""
    return (sub * tip_percent + 50) // 100


def parts(request):
    """G2 and G3: each diner's part of the subtotal, as an exact fraction, in listing order."""
    diners = request["diners"]
    pays = {d["name"]: d["pays"] for d in diners}
    sharers = sum(1 for d in diners if d["pays"] == "share")
    pool = sum(i["price_cents"] for i in request["items"] if pays[i["diner"]] == "share")
    out = []
    for d in diners:
        if d["pays"] == "own":
            own = sum(i["price_cents"] for i in request["items"] if i["diner"] == d["name"])
            out.append((d["name"], Fraction(own)))
        else:
            out.append((d["name"], Fraction(pool, sharers)))
    return out


def fair(request, total=None, sub=None):
    """G4: part * total / subtotal for each diner, exact, in listing order."""
    sub = subtotal(request) if sub is None else sub
    if total is None:
        total = sub + tip(sub, request["tip_percent"])
    return [(name, part * total / sub) for name, part in parts(request)]


def allocate(fairs, total):
    """C2: floor every fair amount, then hand out the missing cents one each by largest
    fractional part, earlier listing first on equal fractional parts."""
    floors = [math.floor(f) for _, f in fairs]
    missing = total - sum(floors)
    order = sorted(range(len(fairs)), key=lambda k: (-(fairs[k][1] - floors[k]), k))
    shares = list(floors)
    for k in order[:missing]:
        shares[k] += 1
    return {name: shares[k] for k, (name, _) in enumerate(fairs)}


def expected(request):
    """The full response a correct `split` gives for a valid request."""
    sub = subtotal(request)
    t = tip(sub, request["tip_percent"])
    return {
        "subtotal_cents": sub,
        "tip_cents": t,
        "total_cents": sub + t,
        "shares": allocate(fair(request, sub + t, sub), sub + t),
    }


NAMES = ["Oda", "Brix", "Nell", "Tove", "Ines", "Galo", "Pim", "Rune", "Suvi", "Yara",
         "Zeno", "Elio", "Hedda", "Fumi", "Caio", "Mirte", "Zoë", "Björn", "Ngozi", "Aroha"]


def random_bill(rng, max_diners=8, max_items=14, max_price=9999, tips=None):
    """A valid random bill: 1..max_diners diners, 1..max_items items, any mix of payers."""
    n = rng.randint(1, max_diners)
    names = rng.sample(NAMES, n) if n <= len(NAMES) else [f"G{k:03d}" for k in range(n)]
    diners = [(name, rng.choice(["own", "share"])) for name in names]
    orders = []
    for _ in range(rng.randint(1, max_items)):
        price = rng.choice([rng.randint(1, min(99, max_price)), rng.randint(min(100, max_price), max_price),
                            rng.randint(1, max_price)])
        orders.append((rng.choice(names), price))
    tip_percent = rng.choice(tips) if tips else rng.choice(
        [0, 5, 10, 12, 15, 18, 20, 22, 25, 33, 100, rng.randint(0, 100), rng.randint(0, 100)])
    return bill(diners, orders, tip_percent)


def cut(rng, amount, pieces):
    """Split a whole amount of at least `pieces` cents into that many positive whole pieces."""
    pieces = max(1, min(pieces, amount))
    marks = sorted(rng.sample(range(1, amount), pieces - 1)) if pieces > 1 else []
    edges = [0] + marks + [amount]
    return [edges[k + 1] - edges[k] for k in range(pieces)]


def round_bill(rng, need_own=False, need_share=False):
    """A random bill whose fair amounts are all whole cents: every own-payer's items and
    the pool per sharer are whole hundreds of cents, so the tip is exact and nothing is
    left over. Such bills test the parts and the tip rate without touching rule C2."""
    n = rng.randint(2, 7)
    names = rng.sample(NAMES, n)
    pays = [rng.choice(["own", "share"]) for _ in names]
    if need_own and "own" not in pays:
        pays[rng.randrange(n)] = "own"
    if need_share and "share" not in pays:
        pays[rng.randrange(n)] = "share"
    if need_own and need_share and len(set(pays)) < 2:
        pays[0], pays[-1] = "own", "share"
    diners = list(zip(names, pays))
    owners = [nm for nm, p in diners if p == "own"]
    sharers = [nm for nm, p in diners if p == "share"]
    orders = []
    for nm in owners:
        for _ in range(rng.choice([0, 1, 1, 2, 3])):
            orders.append((nm, 100 * rng.randint(1, 60)))
    if sharers:
        for _ in range(rng.randint(0, 5)):
            orders.append((rng.choice(sharers), 100 * rng.randint(1, 60)))
        pool = sum(c for nm, c in orders if nm in sharers)
        step = 100 * len(sharers)
        if pool % step or pool == 0:
            orders.append((rng.choice(sharers), step - pool % step))
    if not orders:
        orders.append((rng.choice(names), 100 * rng.randint(1, 60)))
    rng.shuffle(orders)
    return bill(diners, orders, rng.randint(0, 100))
