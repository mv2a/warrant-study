"""P2: the example days written in the intent."""

from _cmd import call, finish


def trip(minute, start, end):
    return {"board_minute": minute, "from_zone": start, "to_zone": end}


SCENARIOS = [
    ("S1", {"age": 40, "trips": [trip(450, 2, 5), trip(490, 5, 6), trip(600, 6, 6)]}, [555, 0, 270], 825),
    ("S2", {"age": 11, "trips": [trip(480, 1, 3), trip(1000, 3, 3)]}, [230, 135], 365),
    ("S3", {"age": 30, "trips": [trip(420, 1, 6), trip(480, 6, 4), trip(720, 4, 6), trip(1080, 6, 6)]}, [745, 0, 355, 0], 1100),
]
problems = []
for scenario, request, fares, total in SCENARIOS:
    status, body = call(request)
    expected = {"fares_cents": fares, "total_cents": total}
    if status != 0 or body != expected:
        problems.append(f"{scenario}: expected {expected}, got {body!r} (status {status})")

finish(problems, "scenarios ok: S1, S2, S3")
