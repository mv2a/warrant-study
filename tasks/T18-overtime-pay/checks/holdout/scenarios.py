"""H7: the five example weeks in the intent, field for field, and again with the request reshaped."""

import json

from _cmd import call, finish

SCENARIOS = [
    ("S1", [540, 540, 540, 540, 540, 0, 0], 2000, (2400, 300, 0, 80000, 15000, 0, 95000)),
    ("S2", [480, 480, 480, 480, 480, 360, 0], 1800, (2400, 360, 0, 72000, 16200, 0, 88200)),
    ("S3", [240, 240, 240, 240, 240, 240, 600], 2500, (1440, 480, 120, 60000, 30000, 10000, 100000)),
    ("S4", [500, 0, 0, 0, 0, 0, 0], 1001, (480, 20, 0, 8008, 501, 0, 8509)),
    ("S5", [480, 480, 480, 480, 480, 480, 720], 2250, (2400, 960, 240, 90000, 54000, 18000, 162000)),
]
FIELDS = ("regular_minutes", "overtime_minutes", "double_minutes",
          "regular_cents", "overtime_cents", "double_cents", "total_cents")
problems = []
for scenario, minutes, rate, values in SCENARIOS:
    want = dict(zip(FIELDS, values))
    for shape, raw in [("as written", json.dumps({"minutes": minutes, "rate_cents": rate})),
                       ("reordered", json.dumps({"rate_cents": rate, "minutes": minutes}, indent=1))]:
        status, body = call(raw=raw)
        if status != 0 or body != want:
            problems.append(f"{scenario} {shape}: expected {want}, got {body!r} (status {status})")

finish(problems, "scenarios ok: S1, S2, S3, S4, S5")
