"""H8: the scenarios S1, S2 and S3 in the intent, exactly as written, each asked twice."""

from _cmd import call, finish

SCENARIOS = [
    ("S1",
     {"items": [{"id": "b1", "type": "book", "due_day": 10, "returned_day": 17}]},
     {"items": [{"id": "b1", "days_late": 7, "fine_cents": 100}], "total_cents": 100}),
    ("S2",
     {"items": [{"id": "r1", "type": "reference", "due_day": 40, "returned_day": 42},
                {"id": "d1", "type": "dvd", "due_day": 40, "returned_day": 42}]},
     {"items": [{"id": "r1", "days_late": 2, "fine_cents": 300},
                {"id": "d1", "days_late": 2, "fine_cents": 0}], "total_cents": 300}),
    ("S3",
     {"items": [{"id": "d7", "type": "dvd", "due_day": 5, "returned_day": 35},
                {"id": "r3", "type": "reference", "due_day": 5, "returned_day": 10}]},
     {"items": [{"id": "d7", "days_late": 30, "fine_cents": 2000},
                {"id": "r3", "days_late": 5, "fine_cents": 750}], "total_cents": 2500}),
]
problems = []
for name, request, expected in SCENARIOS:
    for attempt in (1, 2):
        status, body = call(request)
        if status != 0 or body != expected:
            problems.append(f"{name} (attempt {attempt}): expected status 0 and {expected}, got status {status} and {body!r}")

finish(problems, f"scenarios ok: {len(SCENARIOS)}, each twice")
