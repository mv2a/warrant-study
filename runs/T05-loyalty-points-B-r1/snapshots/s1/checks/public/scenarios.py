"""P2: the example orders written in the intent."""

from _cmd import call, finish

SCENARIOS = [
    (
        "S1",
        {"tier": "gold", "items": [
            {"category": "grocery", "price_cents": 2550, "quantity": 2},
            {"category": "gift_card", "price_cents": 5000, "quantity": 1},
        ]},
        {"eligible_cents": 5100, "base_points": 51, "bonus_points": 25, "total_points": 76},
    ),
    (
        "S2",
        {"tier": "silver", "items": [
            {"category": "garden", "price_cents": 1099, "quantity": 3},
            {"category": "grocery", "price_cents": 450, "quantity": 1},
        ], "bonus_categories": ["garden"]},
        {"eligible_cents": 3747, "base_points": 37, "bonus_points": 73, "total_points": 110},
    ),
    (
        "S3",
        {"tier": "standard", "items": [
            {"category": "electronics", "price_cents": 34999, "quantity": 1},
        ], "bonus_categories": ["electronics"]},
        {"eligible_cents": 34999, "base_points": 349, "bonus_points": 500, "total_points": 849},
    ),
]
problems = []
for scenario, request, expected in SCENARIOS:
    status, body = call(request)
    if status != 0 or body != expected:
        problems.append(f"{scenario}: expected {expected}, got {body!r} (status {status})")

finish(problems, "scenarios ok: S1, S2, S3")
