"""P2: the example requests written in the intent."""

from _cmd import call, finish

SCENARIOS = [
    (
        "S1",
        {"diners": [{"name": "Ana", "pays": "own"}, {"name": "Ben", "pays": "own"}],
         "items": [{"diner": "Ana", "price_cents": 1200}, {"diner": "Ben", "price_cents": 2500},
                   {"diner": "Ana", "price_cents": 300}],
         "tip_percent": 20},
        {"subtotal_cents": 4000, "tip_cents": 800, "total_cents": 4800, "shares": {"Ana": 1800, "Ben": 3000}},
    ),
    (
        "S2",
        {"diners": [{"name": "Ana", "pays": "share"}, {"name": "Ben", "pays": "share"}, {"name": "Cy", "pays": "share"}],
         "items": [{"diner": "Ana", "price_cents": 1234}, {"diner": "Ben", "price_cents": 2000},
                   {"diner": "Cy", "price_cents": 1500}],
         "tip_percent": 10},
        {"subtotal_cents": 4734, "tip_cents": 473, "total_cents": 5207,
         "shares": {"Ana": 1736, "Ben": 1736, "Cy": 1735}},
    ),
    (
        "S3",
        {"diners": [{"name": "Ana", "pays": "share"}, {"name": "Ben", "pays": "share"},
                    {"name": "Cy", "pays": "own"}, {"name": "Dee", "pays": "share"}],
         "items": [{"diner": "Ana", "price_cents": 1600}, {"diner": "Cy", "price_cents": 2150},
                   {"diner": "Ben", "price_cents": 900}],
         "tip_percent": 18},
        {"subtotal_cents": 4650, "tip_cents": 837, "total_cents": 5487,
         "shares": {"Ana": 984, "Ben": 983, "Cy": 2537, "Dee": 983}},
    ),
]
problems = []
for scenario, request, expected in SCENARIOS:
    status, body = call(request)
    if status != 0 or body != expected:
        problems.append(f"{scenario}: expected {expected}, got {body!r} (status {status})")

finish(problems, "scenarios ok: S1, S2, S3")
