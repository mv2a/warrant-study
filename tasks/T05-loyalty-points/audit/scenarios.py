"""X8 (S1, S2, S3): the intent's example orders get exactly the responses it gives.

Each request is sent as written in the intent, and again with its keys in another order,
its items reversed and the JSON pretty-printed; none of that changes the answer.
"""

import json

from _cmd import finish
from _expect import expect

SCENARIOS = {
    "S1": (
        '{"tier": "gold", "items": [{"category": "grocery", "price_cents": 2550, "quantity": 2}, {"category": "gift_card", "price_cents": 5000, "quantity": 1}]}',
        {"eligible_cents": 5100, "base_points": 51, "bonus_points": 25, "total_points": 76},
    ),
    "S2": (
        '{"tier": "silver", "items": [{"category": "garden", "price_cents": 1099, "quantity": 3}, {"category": "grocery", "price_cents": 450, "quantity": 1}], "bonus_categories": ["garden"]}',
        {"eligible_cents": 3747, "base_points": 37, "bonus_points": 73, "total_points": 110},
    ),
    "S3": (
        '{"tier": "standard", "items": [{"category": "electronics", "price_cents": 34999, "quantity": 1}], "bonus_categories": ["electronics"]}',
        {"eligible_cents": 34999, "base_points": 349, "bonus_points": 500, "total_points": 849},
    ),
}

problems = []
for scenario, (text, want) in SCENARIOS.items():
    expect(problems, f"{scenario} as written", None, want, raw=text)
    request = json.loads(text)
    shuffled = {key: request[key] for key in reversed(list(request))}
    shuffled["items"] = [{key: it[key] for key in reversed(list(it))} for it in reversed(request["items"])]
    expect(problems, f"{scenario} reordered and pretty-printed", None, want, raw=json.dumps(shuffled, indent=2) + "\n")

finish(problems, "scenarios ok: S1, S2, S3, each in two layouts")
