"""P2: the example stays written in the intent."""

from _cmd import call, finish

SCENARIOS = [
    ("S1", {"entry": 1990, "exit": 2140, "lost_ticket": False},
     {"minutes": 150, "time_cents": 750, "overnight_cents": 0, "lost_ticket_cents": 0, "total_cents": 750}),
    ("S2", {"entry": 6480, "exit": 6495, "lost_ticket": True},
     {"minutes": 15, "time_cents": 0, "overnight_cents": 0, "lost_ticket_cents": 2500, "total_cents": 2500}),
    ("S3", {"entry": 9840, "exit": 510, "lost_ticket": False},
     {"minutes": 750, "time_cents": 1600, "overnight_cents": 600, "lost_ticket_cents": 0, "total_cents": 2200}),
    ("S4", {"entry": 3360, "exit": 6390, "lost_ticket": False},
     {"minutes": 3030, "time_cents": 3950, "overnight_cents": 1200, "lost_ticket_cents": 0, "total_cents": 5150}),
]
problems = []
for scenario, request, expected in SCENARIOS:
    status, body = call(request)
    if status != 0 or body != expected:
        problems.append(f"{scenario}: expected {expected}, got status {status} and {body!r}")

finish(problems, "scenarios ok: S1, S2, S3, S4")
