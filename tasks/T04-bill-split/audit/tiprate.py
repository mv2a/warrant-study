"""X4 (G4): everyone tips at the same rate on their own part; a diner's fair amount is
their part of the subtotal times the total divided by the subtotal, exactly.

Bills whose fair amounts are all whole cents must be paid exactly (including bills whose
tip was rounded, where the rate is total / subtotal and not 1 + tip_percent / 100).
Bills with fractional fair amounts are checked without assuming any leftover-cent rule:
each share must be the fair amount rounded down, or one cent more, where the fair amount
uses the total_cents the command reports (so a tip rounding slip is left to X1)."""

import math
import random

from _cmd import call, finish
from _model import bill, fair, random_bill, round_bill, subtotal

# (diners, orders, tip_percent, exact shares), worked out by hand.
EXACT = [
    ([("Rune", "own"), ("Suvi", "own")], [("Rune", 1000), ("Suvi", 3000)], 25,
     {"Rune": 1250, "Suvi": 3750}),
    ([("Caio", "own"), ("Mirte", "own"), ("Nell", "own")], [("Caio", 100), ("Mirte", 900), ("Nell", 9000)], 20,
     {"Caio": 120, "Mirte": 1080, "Nell": 10800}),
    ([("Oda", "own"), ("Pim", "share"), ("Brix", "share")], [("Oda", 333), ("Pim", 500), ("Brix", 1)], 100,
     {"Oda": 666, "Pim": 501, "Brix": 501}),
    ([("Galo", "own"), ("Tove", "own")], [("Galo", 1234), ("Tove", 4321)], 0, {"Galo": 1234, "Tove": 4321}),
    # 606 at 5% is 30.3, so the tip is 30 and the rate is 636/606 = 106/101.
    ([("Ines", "own"), ("Hedda", "own"), ("Elio", "own")], [("Ines", 101), ("Hedda", 202), ("Elio", 303)], 5,
     {"Ines": 106, "Hedda": 212, "Elio": 318}),
    # 1515 at 2% is 30.3, so the tip is 30 and the rate is 1545/1515 = 103/101.
    ([("Zeno", "own"), ("Yara", "own"), ("Fumi", "own")], [("Zeno", 101), ("Yara", 404), ("Fumi", 1010)], 2,
     {"Zeno": 103, "Yara": 412, "Fumi": 1030}),
    # 404 at 5% is 20.2, so the tip is 20 and the rate is 424/404 = 106/101.
    ([("Oda", "own"), ("Pim", "share"), ("Brix", "share")], [("Oda", 202), ("Pim", 150), ("Brix", 52)], 5,
     {"Oda": 212, "Pim": 106, "Brix": 106}),
    ([("Ines", "share"), ("Tove", "share")], [("Ines", 1800), ("Tove", 200)], 20, {"Ines": 1200, "Tove": 1200}),
    ([("Aroha", "share"), ("Björn", "own"), ("Ngozi", "share")],
     [("Björn", 2000), ("Aroha", 500), ("Ngozi", 1500)], 15, {"Aroha": 1150, "Björn": 2300, "Ngozi": 1150}),
]

# Rounded-tip bills with fractional fair amounts where tipping at the unrounded rate
# (part * (100 + tip_percent) / 100) lands a full cent away from the true fair amount.
BOUNDED = [
    ([("Hedda", "own"), ("Caio", "share"), ("Mirte", "share"), ("Pim", "share")],
     [("Hedda", 1736), ("Pim", 157), ("Mirte", 688), ("Hedda", 2517), ("Hedda", 1068)], 22),
    ([("Hedda", "share"), ("Caio", "share"), ("Mirte", "own"), ("Pim", "share"), ("Oda", "share")],
     [("Pim", 11520), ("Pim", 9377), ("Mirte", 2225), ("Mirte", 8143), ("Mirte", 18359), ("Mirte", 16267)], 72),
    ([("Hedda", "share"), ("Caio", "share"), ("Mirte", "own"), ("Pim", "own"), ("Oda", "share")],
     [("Caio", 3323), ("Pim", 11379), ("Pim", 14831), ("Pim", 9510)], 22),
    ([("Hedda", "share"), ("Caio", "own"), ("Mirte", "share"), ("Pim", "own"), ("Oda", "share"), ("Nell", "own")],
     [("Caio", 14018), ("Mirte", 1650), ("Mirte", 1037)], 70),
    ([("Hedda", "share"), ("Caio", "share"), ("Mirte", "share"), ("Pim", "own")],
     [("Hedda", 3244), ("Pim", 18570)], 68),
    ([("Hedda", "share"), ("Caio", "share"), ("Mirte", "own"), ("Pim", "own"), ("Oda", "own"), ("Nell", "share")],
     [("Caio", 526), ("Pim", 13885)], 23),
]

problems = []
count = 0


def get_body(request, label):
    global count
    count += 1
    status, body = call(request)
    shares = body.get("shares") if isinstance(body, dict) else None
    if status != 0 or not isinstance(shares, dict):
        problems.append(f"{label}: expected shares, got {body!r} (status {status})")
        return None
    return body


def get_shares(request, label):
    body = get_body(request, label)
    return None if body is None else body["shares"]


def bounded(request, label):
    body = get_body(request, label)
    if body is None:
        return
    shares, total = body["shares"], body.get("total_cents")
    if not (type(total) is int or (type(total) is float and total.is_integer())):
        problems.append(f"{label}: total_cents is not a whole number: {total!r}")
        return
    for name, amount in fair(request, total=int(total), sub=subtotal(request)):
        low = math.floor(amount)
        got = shares.get(name)
        if not (type(got) is int and low <= got <= low + 1):
            problems.append(f"{label}: {name}'s fair amount is {float(amount):.4f}, "
                            f"so the share should be {low} or {low + 1}, got {got!r}")


for k, (diners, orders, tip_percent, want) in enumerate(EXACT, 1):
    shares = get_shares(bill(diners, orders, tip_percent), f"bill {k}")
    if shares is not None and shares != want:
        problems.append(f"bill {k}: expected shares {want}, got {shares}")

rng = random.Random(8820611)
for k in range(20):
    request = round_bill(rng)
    want = {name: int(amount) for name, amount in fair(request)}
    shares = get_shares(request, f"whole-cent bill {k + 1}")
    if shares is not None and shares != want:
        problems.append(f"whole-cent bill {k + 1}: expected shares {want}, got {shares}")

for k, (diners, orders, tip_percent) in enumerate(BOUNDED, 1):
    bounded(bill(diners, orders, tip_percent), f"rounded-tip bill {k}")

rng = random.Random(8820612)
for k in range(50):
    bounded(random_bill(rng), f"bill {k + 1} with odd cents")

finish(problems, f"tip rate ok: {count} bills")
