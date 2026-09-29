"""X14-X21: many generated requests with fixed seeds, each check judging one promise only.
Usage: python3 generated.py billable|brackets|heavy|oversize|limits|invalid|extra|interface

Four fixed data sets, each from its own seed:
  priced   (seed 604211, 200 parcels): all zones, weights from 1 g to 30,000 g clustered at the
           bracket limits, small, bulky and long shapes; a few are past a carrying limit.
  limits   (seed 3301977, 200 parcels): on or next to a threshold: actual or dimensional weight
           near 30,000 g, longest side 98 to 102 or 148 to 152 cm, length plus girth 218 to 222
           or 298 to 302 cm, in random side order.
  invalid  (seed 81457, 160 requests): valid parcels, each spoiled one way.
  extra    (seed 5150, 60 parcels): parcels with one to four extra fields of random names and types.
  light    (seed 7040913, 150 parcels): 2 g to 10,000 g, clustered at the bracket limits, all zones,
           each small enough to be billed on its actual weight.
"""

import json
import random
import sys

from _audit import (REFUSED, actual_wins, check, expected, is_oversize, sides_of, finish, interface, parcel, parse,
                    priced, refused, run_many, surcharge, values)

WEIGHT_MARKS = (500, 1000, 2000, 5000, 10000, 11000, 15000, 20000, 25000, 30000)


def shuffled(rng, sides):
    sides = list(sides)
    rng.shuffle(sides)
    return sides


def random_weight(rng):
    kind = rng.randrange(4)
    if kind == 0:
        return rng.randint(1, 30000)
    if kind == 1:
        return max(1, rng.choice(WEIGHT_MARKS) + rng.randint(-3, 3))
    if kind == 2:
        return rng.randint(1, 600)
    return rng.randint(10000, 30000)


def random_sides(rng):
    kind = rng.randrange(4)
    if kind == 0:
        return [rng.randint(1, 40) for _ in range(3)]
    if kind == 1:
        return [rng.randint(10, 75) for _ in range(3)]
    if kind == 2:
        return shuffled(rng, (rng.randint(85, 150), rng.randint(1, 30), rng.randint(1, 30)))
    return [rng.randint(1, 120) for _ in range(3)]


def near_limit_sides(rng):
    """Sides whose longest side or length plus girth lands on or right next to a threshold."""
    if rng.random() < 0.4:
        longest = rng.choice((98, 99, 100, 101, 102, 148, 149, 150, 151, 152))
        return shuffled(rng, (longest, rng.randint(1, 35), rng.randint(1, 35)))
    target = rng.choice((218, 219, 220, 221, 222, 298, 299, 300, 301, 302))
    while True:
        longest = rng.randint(50, 150)
        rest = target - longest
        if rest % 2 or rest < 4:
            continue
        pair = rest // 2  # the other two sides add up to this
        low = max(1, pair - longest)
        high = min(longest, pair - 1)
        if low > high:
            continue
        a = rng.randint(low, high)
        return shuffled(rng, (longest, a, pair - a))


def near_limit_parcel(rng):
    zone = rng.randint(1, 4)
    kind = rng.randrange(3)
    if kind == 0:  # actual weight around the 30,000 g limit
        return parcel(zone, 30000 + rng.randint(-6, 6), *shuffled(rng, (rng.randint(5, 40), rng.randint(5, 40), rng.randint(5, 30))))
    if kind == 1:  # dimensional weight around the 30,000 g limit
        while True:
            sides = [rng.randint(20, 150), rng.randint(20, 100), rng.randint(10, 60)]
            volume = sides[0] * sides[1] * sides[2]
            if 146000 <= volume <= 154000:
                return parcel(zone, rng.randint(1, 5000), *shuffled(rng, sides))
    return parcel(zone, random_weight(rng), *near_limit_sides(rng))


def bad_value(rng, good):
    kind = rng.randrange(9)
    if kind == 0:
        return 0
    if kind == 1:
        return -rng.randint(1, 100000)
    if kind == 2:
        return rng.randint(0, 3000) + rng.choice((0.5, 0.25, 0.1, 0.75, 0.001))
    if kind == 3:
        return str(good)
    if kind == 4:
        return rng.choice((True, False))
    if kind == 5:
        return None
    if kind == 6:
        return [good]
    if kind == 7:
        return {"value": good}
    return rng.choice(("", "n/a", "12kg", "1,000", "ten"))


def bad_zone(rng):
    return rng.choice((rng.randint(5, 999), -rng.randint(0, 999), str(rng.randint(1, 4)),
                       rng.randint(1, 3) + 0.5, rng.choice((True, False)), None, [rng.randint(1, 4)]))


def corrupted(rng, request):
    """One way of turning a valid request into an invalid one, as (label, request or raw text)."""
    kind = rng.randrange(6)
    if kind == 0:
        field = rng.choice(list(request))
        return f"missing {field}", {k: v for k, v in request.items() if k != field}
    if kind == 1:
        zone = bad_zone(rng)
        return f"zone {zone!r}", {**request, "zone": zone}
    if kind in (2, 3):
        field = rng.choice(("weight_g", "length_cm", "width_cm", "height_cm"))
        value = bad_value(rng, request[field])
        return f"{field} {value!r}", {**request, field: value}
    text = json.dumps(request)
    if kind == 4:
        cut = rng.randint(1, len(text) - 1)
        return f"cut at {cut}", text[:cut]
    return "wrapped in a list", "[" + text + "]"


EXTRA_NAMES = ("note", "service", "billable_g", "total_cents", "surcharge_cents", "Zone", "weight",
               "weight_kg", "length", "customer_id", "priority", "dims", "", "zone_name", "height_in")


def extra_value(rng):
    return rng.choice((rng.randint(-10 ** 6, 10 ** 6), rng.random() * 100, "x" * rng.randint(0, 5),
                       True, False, None, [rng.randint(0, 9)], {"length_cm": rng.randint(151, 999)}))


def priced_set():
    rng = random.Random(604211)
    return [(f"priced #{i}", parcel(rng.randint(1, 4), random_weight(rng), *random_sides(rng))) for i in range(200)]


def limits_set():
    rng = random.Random(3301977)
    return [(f"limits #{i}", near_limit_parcel(rng)) for i in range(200)]


def invalid_set():
    rng = random.Random(81457)
    cases = []
    for i in range(160):
        base = parcel(rng.randint(1, 4), rng.randint(1, 9000), rng.randint(1, 40), rng.randint(1, 40), rng.randint(1, 40))
        assert expected(base) is not REFUSED  # every corruption starts from a parcel that would be priced
        label, bad = corrupted(rng, base)
        cases.append((f"invalid #{i} {label}", bad))
    return cases


def extra_set():
    """(label, parcel, the same parcel with extra fields in random key order)."""
    rng = random.Random(5150)
    cases = []
    for i in range(60):
        base = parcel(rng.randint(1, 4), random_weight(rng), *random_sides(rng))
        items = list(base.items())
        for _ in range(rng.randint(1, 4)):
            items.append((rng.choice(EXTRA_NAMES) + rng.choice(("", "_2", "_old", " ")), extra_value(rng)))
        rng.shuffle(items)
        request = dict(items)
        assert all(request[field] == value for field, value in base.items())  # extra names never clash
        cases.append((f"extra #{i} {request}", base, request))
    return cases


def light_set():
    rng = random.Random(7040913)
    marks = (500, 1000, 2000, 5000, 10000)
    cases = []
    for i in range(150):
        if rng.random() < 0.5:
            weight = min(10000, rng.choice(marks) + rng.randint(-2, 2))
        else:
            weight = rng.randint(2, 10000)
        cap = max(1, min(40, int((5 * weight - 6) ** (1 / 3))))  # volume <= cap ** 3 < 5 * weight - 5
        p = parcel(rng.randint(1, 4), weight, *(rng.randint(1, cap) for _ in range(3)))
        assert actual_wins(p)
        cases.append((f"light #{i}", p))
    return cases


def carried(dataset):
    """(label, request, the oracle's answer) for the parcels the intent prices."""
    return [(label, p, expected(p)) for label, p in dataset if expected(p) is not REFUSED]


MODE = sys.argv[1]
cases = []
if MODE == "billable":  # G1
    for label, p, want in carried(priced_set() + limits_set()):
        cases.append((f"{label} {p}", p, values(p, {"billable_g": want["billable_g"]})))
elif MODE == "brackets":  # G2, on parcels billed on their actual weight and not oversize (G4)
    for label, p, want in carried(light_set() + priced_set() + limits_set()):
        if want["billable_g"] <= 10000 and actual_wins(p) and not is_oversize(*sides_of(p)):
            cases.append((f"{label} {p}", p, values(p, {"base_cents": want["base_cents"]})))
elif MODE == "heavy":  # G3, on parcels billed on their actual weight and not oversize (G4)
    for label, p, want in carried(priced_set() + limits_set()):
        if want["billable_g"] > 10000 and actual_wins(p) and not is_oversize(*sides_of(p)):
            cases.append((f"{label} {p}", p, values(p, {"base_cents": want["base_cents"]})))
elif MODE == "oversize":  # G4
    for label, p, want in carried(priced_set() + limits_set()):
        cases.append((f"{label} {p}", p, surcharge(p, want["surcharge_cents"])))
elif MODE == "limits":  # C2
    for label, p in priced_set() + limits_set():
        cases.append((f"{label} {p}", p, refused if expected(p) is REFUSED else priced))
elif MODE == "invalid":  # C3
    cases = [(label, bad, refused) for label, bad in invalid_set()]
elif MODE == "interface":  # C1, whatever each answer should be
    cases = [(f"{label} {p}", p, interface()) for label, p in priced_set() + limits_set() + invalid_set()]
elif MODE == "extra":  # C1: extra fields change nothing, compared with the same command's own answer
    dataset = extra_set()
    results = run_many([r for _, base, extended in dataset for r in (base, extended)])
    problems = []
    for i, (label, base, extended) in enumerate(dataset):
        (s0, out0, _), (s1, out1, _) = results[2 * i], results[2 * i + 1]
        same = s0 == s1 and (parse(out0) == parse(out1) if parse(out0) is not None else out0 == out1)
        if not same:
            problems.append(f"{label}: expected the answer without the extra fields (status {s0}, {out0[:80]!r}), "
                            f"got status {s1} and {out1[:80]!r}")
    finish(problems, f"generated extra (seed 5150): {2 * len(dataset)} requests")
    sys.exit(0)
else:
    sys.exit(f"unknown mode {MODE}")

check(cases, f"generated {MODE}")
