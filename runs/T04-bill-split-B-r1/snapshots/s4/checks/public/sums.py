"""P3: the shares are whole cents and add up to the total."""

from _cmd import call, finish


def bill(pays, orders, tip):
    """pays: {name: "own"|"share"}; orders: [(name, cents), ...]."""
    return {
        "diners": [{"name": n, "pays": p} for n, p in pays.items()],
        "items": [{"diner": n, "price_cents": c} for n, c in orders],
        "tip_percent": tip,
    }


BILLS = [
    bill({"Ivo": "share", "Jun": "share", "Kai": "share"}, [("Ivo", 1000)], 0),
    bill({"Ivo": "own", "Jun": "own", "Kai": "own"}, [("Ivo", 333), ("Jun", 333), ("Kai", 334)], 17),
    bill({"Ivo": "share", "Jun": "own", "Kai": "share", "Lu": "share"},
         [("Ivo", 1999), ("Jun", 1275), ("Lu", 845), ("Jun", 120)], 22),
    bill({"Pat": "own", "Quin": "share", "Rey": "share", "Sol": "own", "Tam": "share", "Uma": "share"},
         [("Pat", 2890), ("Quin", 1110), ("Sol", 640), ("Tam", 2395), ("Uma", 115)], 12),
    bill({"Vic": "share", "Wen": "share"}, [("Vic", 1), ("Wen", 2)], 25),
]
problems = []
for request in BILLS:
    names = [d["name"] for d in request["diners"]]
    status, body = call(request)
    shares = body.get("shares") if isinstance(body, dict) else None
    if status != 0 or not isinstance(shares, dict):
        problems.append(f"{names}: expected shares, got {body!r} (status {status})")
    elif set(shares) != set(names):
        problems.append(f"{names}: expected one share per diner, got {shares!r}")
    elif not all(type(v) is int and v >= 0 for v in shares.values()):
        problems.append(f"{names}: every share must be a whole number of cents, zero or more, got {shares!r}")
    elif sum(shares.values()) != body.get("total_cents"):
        problems.append(f"{names}: shares {shares!r} add up to {sum(shares.values())}, not total_cents {body.get('total_cents')!r}")

finish(problems, f"sums ok: {len(BILLS)} bills")
