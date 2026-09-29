"""X01 (C1): the success side of the interface, on requests unlike the visible ones."""

import json
import random

from _audit import TYPES, finish, item, succeed

problems = []

# The empty list: exactly {"items": [], "total_cents": 0}.
succeed(problems, "empty list", {"items": []}, want={"items": [], "total_cents": 0})

# One item of each type, a mix of early, on-time and late returns.
succeed(problems, "three types", {"items": [
    item("ref-A", "reference", 120, 124),
    item("bk-A", "book", 120, 131),
    item("dv-A", "dvd", 120, 118),
]})

# Pretty-printed input spread over many lines, with a trailing newline, is still one JSON object.
request = {"items": [item("q1", "dvd", 7, 16), item("q2", "book", 0, 0)]}
succeed(problems, "pretty-printed input", request, raw=json.dumps(request, indent=4) + "\n")

# Order and count: long lists in a shuffled, non-alphabetical order keep the request's order.
rng = random.Random(40417)
for round_number in range(6):
    size = rng.randint(2, 25)
    ids = [f"L{rng.randint(0, 99999):05d}-{n}" for n in range(size)]
    rng.shuffle(ids)
    request = {"items": []}
    for ident in ids:
        due = rng.randint(0, 400)
        request["items"].append(item(ident, rng.choice(TYPES), due, due + rng.randint(-5, 30)))
    succeed(problems, f"shuffled list {round_number} ({size} items)", request)

# Ids are echoed exactly, including non-ASCII and punctuation.
succeed(problems, "unusual ids", {"items": [
    item("Łódź/42", "book", 3, 9),
    item("id with spaces", "dvd", 3, 9),
    item("éè-书", "reference", 3, 9),
    item("0", "book", 3, 3),
]})

finish(problems, "interface ok: success responses have the promised shape and order")
