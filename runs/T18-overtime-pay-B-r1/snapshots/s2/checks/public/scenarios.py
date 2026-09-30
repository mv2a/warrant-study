"""P2: the example weeks written in the intent."""

from _cmd import call, finish

SCENARIOS = [
    ("S1", {"minutes": [540, 540, 540, 540, 540, 0, 0], "rate_cents": 2000},
     {"regular_minutes": 2400, "overtime_minutes": 300, "double_minutes": 0,
      "regular_cents": 80000, "overtime_cents": 15000, "double_cents": 0, "total_cents": 95000}),
    ("S2", {"minutes": [480, 480, 480, 480, 480, 360, 0], "rate_cents": 1800},
     {"regular_minutes": 2400, "overtime_minutes": 360, "double_minutes": 0,
      "regular_cents": 72000, "overtime_cents": 16200, "double_cents": 0, "total_cents": 88200}),
    ("S3", {"minutes": [240, 240, 240, 240, 240, 240, 600], "rate_cents": 2500},
     {"regular_minutes": 1440, "overtime_minutes": 480, "double_minutes": 120,
      "regular_cents": 60000, "overtime_cents": 30000, "double_cents": 10000, "total_cents": 100000}),
    ("S4", {"minutes": [500, 0, 0, 0, 0, 0, 0], "rate_cents": 1001},
     {"regular_minutes": 480, "overtime_minutes": 20, "double_minutes": 0,
      "regular_cents": 8008, "overtime_cents": 501, "double_cents": 0, "total_cents": 8509}),
    ("S5", {"minutes": [480, 480, 480, 480, 480, 480, 720], "rate_cents": 2250},
     {"regular_minutes": 2400, "overtime_minutes": 960, "double_minutes": 240,
      "regular_cents": 90000, "overtime_cents": 54000, "double_cents": 18000, "total_cents": 162000}),
]
problems = []
for scenario, request, expected in SCENARIOS:
    status, body = call(request)
    if status != 0 or body != expected:
        problems.append(f"{scenario}: expected {expected}, got {body!r} (status {status})")

finish(problems, "scenarios ok: S1, S2, S3, S4, S5")
