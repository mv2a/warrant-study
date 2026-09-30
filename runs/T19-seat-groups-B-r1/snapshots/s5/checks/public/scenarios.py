"""P2: the three example requests in the intent get exactly the documented responses."""

from _cmd import call, finish

SCENARIOS = {
    "S1": (
        {"rows": [6, 6], "groups": [{"id": "Ruiz", "size": 4}, {"id": "Chen", "size": 3}, {"id": "Patel", "size": 2}]},
        {
            "seated": [
                {"id": "Ruiz", "seats": ["A1", "A2", "A3", "A4"]},
                {"id": "Chen", "seats": ["B1", "B2", "B3"]},
                {"id": "Patel", "seats": ["A5", "A6"]},
            ],
            "refused": [],
            "free": 3,
        },
    ),
    "S2": (
        {
            "rows": [5, 5],
            "blocked": ["A3", "B3"],
            "groups": [{"id": "Novak", "size": 3}, {"id": "Okafor", "size": 2}, {"id": "Lind", "size": 2}],
        },
        {
            "seated": [{"id": "Okafor", "seats": ["A1", "A2"]}, {"id": "Lind", "seats": ["A4", "A5"]}],
            "refused": [{"id": "Novak", "reason": "not_together"}],
            "free": 4,
        },
    ),
    "S3": (
        {
            "rows": [4, 4],
            "groups": [
                {"id": "Ito", "size": 3},
                {"id": "Berg", "size": 3},
                {"id": "Kim", "size": 3},
                {"id": "Diaz", "size": 2, "may_split": True},
            ],
        },
        {
            "seated": [
                {"id": "Ito", "seats": ["A1", "A2", "A3"]},
                {"id": "Berg", "seats": ["B1", "B2", "B3"]},
                {"id": "Diaz", "seats": ["A4", "B4"]},
            ],
            "refused": [{"id": "Kim", "reason": "not_enough_seats"}],
            "free": 0,
        },
    ),
}
problems = []
for name, (request, expected) in SCENARIOS.items():
    status, body = call(request)
    if status != 0 or body != expected:
        problems.append(f"{name}: expected status 0 and {expected}, got status {status} and {body!r}")

finish(problems, f"scenarios ok: {', '.join(SCENARIOS)}")
