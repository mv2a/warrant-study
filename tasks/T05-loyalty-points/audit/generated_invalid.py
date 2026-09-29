"""X10 (C3, C4): 90 generated invalid requests with a fixed seed are refused.

Each starts as a valid order and gets exactly one defect from C4's list, at a random place
(any item, gift cards included). Every one must exit with status 2 and print nothing.
"""

import copy
import random

from _cmd import finish
from _expect import refuse

rng = random.Random(90210577)
CATEGORIES = ["garden", "grocery", "tools", "gift_card", "paint", "pets"]
CASES = 90


def valid_order():
    request = {"tier": rng.choice(["standard", "silver", "gold"]), "items": []}
    for _ in range(rng.randint(1, 4)):
        request["items"].append({"category": rng.choice(CATEGORIES), "price_cents": rng.randint(0, 30000), "quantity": rng.randint(1, 5)})
    if rng.random() < 0.6:
        request["bonus_categories"] = rng.sample(CATEGORIES, rng.randint(0, 3))
    return request


def bad_tier():
    return rng.choice([None, "", "Standard", "SILVER", "gold!", "platinum", "diamond", " silver", 2, 1.25, True, ["gold"], {"tier": "gold"}])


def bad_price(ok):
    return rng.choice([
        -rng.randint(1, 50000),
        ok + rng.choice([0.5, 0.25, 0.99]),
        float(ok),  # whole value written as a JSON number with a decimal point
        rng.randint(0, 999) / 7 + 0.001,
        str(ok),
        f"{ok / 100:.2f}",
        True,
        False,
        None,
        [ok],
    ])


def bad_quantity(ok):
    return rng.choice([0, -rng.randint(1, 20), ok + 0.5, rng.choice([0.1, 1.9, 3.3]), float(ok), str(ok), "two", True, False, None, [ok]])


def bad_category():
    return rng.choice(["", None, 0, 12, True, False, ["garden"], {"name": "garden"}])


def bad_bonus(request):
    listed = list(request.get("bonus_categories", [])) or ["garden"]
    spoilers = [None, 3, True, ["garden"], {"garden": 1}, 1.5]
    choice = rng.randint(0, 2)
    if choice == 0:
        return rng.choice(["garden", None, 7, True, {"garden": True}])
    listed.insert(rng.randint(0, len(listed)), rng.choice(spoilers))
    return listed


def corrupt(request):
    """Apply one defect; return a description of it."""
    items = request["items"]
    index = rng.randrange(len(items))
    target = items[index]
    where = f"item {index} ({target['category']})"
    kind = rng.randrange(11)
    if kind == 0:
        request["tier"] = value = bad_tier()
        return f"tier {value!r}"
    if kind == 1:
        del request["tier"]
        return "tier missing"
    if kind == 2:
        value = rng.choice([None, "items", {}, dict(target), 0, False])
        request["items"] = value
        return f"items {value!r}"
    if kind == 3:
        del request["items"]
        return "items missing"
    if kind == 4:
        value = rng.choice([None, target["category"], target["price_cents"], [target["category"], target["price_cents"], target["quantity"]], True])
        items[index] = value
        return f"{where} replaced by {value!r}"
    if kind == 5:
        field = rng.choice(["category", "price_cents", "quantity"])
        del target[field]
        return f"{where} without {field}"
    if kind == 6:
        target["category"] = value = bad_category()
        return f"{where} category {value!r}"
    if kind in (7, 8):
        target["price_cents"] = value = bad_price(target["price_cents"])
        return f"{where} price {value!r}"
    if kind == 9:
        target["quantity"] = value = bad_quantity(target["quantity"])
        return f"{where} quantity {value!r}"
    request["bonus_categories"] = value = bad_bonus(request)
    return f"bonus_categories {value!r}"


problems = []
for n in range(CASES):
    request = valid_order()
    broken = copy.deepcopy(request)
    defect = corrupt(broken)
    refuse(problems, f"case {n}: {defect}", request=broken)

finish(problems, f"generated invalid requests refused: {CASES} cases, seed 90210577")
