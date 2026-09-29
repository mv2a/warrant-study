"""H6: the interface: request fields, exactly four integer fields out, exit statuses."""

import random

from _cmd import call, finish

FIELDS = {"eligible_cents", "base_points", "bonus_points", "total_points"}
CATEGORIES = ["grocery", "garden", "books", "toys", "electronics", "gift_card"]
TIERS = ["standard", "silver", "gold"]
rng = random.Random(505606)


def random_request():
    request = {"tier": rng.choice(TIERS), "items": [
        {"category": rng.choice(CATEGORIES),
         "price_cents": rng.choice([rng.randint(0, 99), rng.randint(100, 9999), rng.randint(10000, 200000)]),
         "quantity": rng.randint(1, 6)}
        for _ in range(rng.randint(0, 5))
    ]}
    if rng.random() < 0.7:
        request["bonus_categories"] = rng.sample(CATEGORIES, rng.randint(0, 3))
    return request


def shape_problem(body):
    if not isinstance(body, dict) or set(body) != FIELDS:
        return f"expected an object with exactly {sorted(FIELDS)}, got {body!r}"
    if not all(type(body[field]) is int for field in FIELDS):
        return f"every field must be an integer, got {body!r}"
    if min(body.values()) < 0:
        return f"no field may be negative, got {body!r}"
    if body["total_points"] != body["base_points"] + body["bonus_points"]:
        return f"total_points must be base_points plus bonus_points, got {body!r}"
    return None


problems = []
calls = 0

for request in [random_request() for _ in range(50)]:
    status, body = call(request)
    calls += 1
    problem = "exited with status %s, expected 0" % status if status != 0 else shape_problem(body)
    if problem:
        problems.append(f"{request}: {problem}")

# An empty order is valid and earns nothing.
for tier in TIERS:
    status, body = call({"tier": tier, "items": []})
    calls += 1
    if status != 0 or body != dict.fromkeys(FIELDS, 0):
        problems.append(f"an empty {tier} order must earn all zeros, got {body!r} (status {status})")

# Leaving out bonus_categories means none; extra fields are ignored.
for _ in range(12):
    request = random_request()
    request.pop("bonus_categories", None)
    status_a, plain = call(request)
    status_b, empty = call({**request, "bonus_categories": []})
    padded = {**request, "customer": "M-1042", "note": None, "channel": ["web"],
              "items": [{**item, "sku": "SKU-%d" % n, "name": "thing", "discount": 5}
                        for n, item in enumerate(request["items"])]}
    status_c, extra = call(padded)
    calls += 3
    if status_a != 0 or shape_problem(plain):
        problems.append(f"{request}: a request without bonus_categories must be accepted, got {plain!r} (status {status_a})")
    elif (status_b, empty) != (0, plain):
        problems.append(f"{request}: an empty bonus_categories list must mean the same as none, got {empty!r}")
    elif (status_c, extra) != (0, plain):
        problems.append(f"{request}: extra fields must be ignored, got {extra!r} instead of {plain!r}")

# A refusal exits 2 and prints nothing on standard output.
for raw in ('{"tier": "gold"}', '{"tier": "bronze", "items": []}', "points please"):
    status, body = call(raw=raw)
    calls += 1
    if status != 2 or body is not None:
        problems.append(f"{raw!r} must be refused with status 2 and no output, got status {status} and {body!r}")

problems = [p if len(p) <= 220 else p[:217] + "..." for p in problems]
finish(problems, f"interface ok: {calls} requests")
