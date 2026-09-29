"""X07 (C3): one defect anywhere in a generated request refuses the whole request (fixed seed)."""

import copy
import random

from _audit import TYPES, finish, item, refuse

rng = random.Random(730291)
problems = []


def valid_request(size):
    ids = rng.sample(range(1000, 9999), size)
    items = []
    for ident in ids:
        due = rng.randint(0, 300)
        items.append(item(f"g{ident}", rng.choice(TYPES), due, max(0, due + rng.randint(-10, 60))))
    return {"items": items}


def mutate(request):
    """Apply one refusal-worthy defect; return (label, mutated request)."""
    request = copy.deepcopy(request)
    items = request["items"]
    at = rng.randrange(len(items))
    kind = rng.choice(["drop_field", "bad_type", "bad_day", "bad_id", "duplicate", "not_object",
                       "negative_day", "float_day", "bool_day", "case_type"])
    target = items[at]
    if kind == "drop_field":
        field = rng.choice(["id", "type", "due_day", "returned_day"])
        del target[field]
        return f"item {at} lacks {field}", request
    if kind == "bad_type":
        target["type"] = rng.choice(["audiobook", "periodical", "Dvd", "BOOK", "reference ", None, 3])
        return f"item {at} type {target['type']!r}", request
    if kind == "case_type":
        target["type"] = target["type"].capitalize()
        return f"item {at} type {target['type']!r}", request
    if kind == "bad_day":
        field = rng.choice(["due_day", "returned_day"])
        target[field] = rng.choice([str(target[field]), None, [target[field]], {"n": 1}])
        return f"item {at} {field} {target[field]!r}", request
    if kind == "negative_day":
        field = rng.choice(["due_day", "returned_day"])
        target[field] = -rng.randint(1, 500)
        return f"item {at} {field} {target[field]}", request
    if kind == "float_day":
        field = rng.choice(["due_day", "returned_day"])
        target[field] = rng.choice([target[field] + 0.5, float(target[field])])
        return f"item {at} {field} {target[field]!r}", request
    if kind == "bool_day":
        field = rng.choice(["due_day", "returned_day"])
        target[field] = rng.choice([True, False])
        return f"item {at} {field} {target[field]!r}", request
    if kind == "bad_id":
        target["id"] = rng.choice(["", 0, 42, None, False, ["x"]])
        return f"item {at} id {target['id']!r}", request
    if kind == "duplicate":
        if len(items) < 2:
            items.append(dict(target))
            return "second item repeats the first id", request
        other = rng.choice([n for n in range(len(items)) if n != at])
        items[other]["id"] = target["id"]
        return f"items {at} and {other} share an id", request
    items[at] = rng.choice([target["id"], 5, None, [target["id"]], True])
    return f"item {at} is not an object", request


ROUNDS = 90
for round_number in range(ROUNDS):
    label, bad = mutate(valid_request(rng.randint(1, 9)))
    refuse(problems, f"round {round_number}: {label}", bad)

finish(problems, f"generated refusals ok: {ROUNDS} requests (seed 730291)")
