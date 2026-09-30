"""P2: the example requests written in the intent."""

from _cmd import call, finish

S4_BUSY = [[], [[600, 720]], [[660, 780], [900, 960]], [[700, 750], [930, 1020]]]
SCENARIOS = [
    (
        "S1",
        {"workday": [540, 1020], "min_length": 30, "quorum": 2, "busy": [[[600, 660], [840, 900]], [[630, 720], [735, 780]]]},
        [[540, 600], [780, 840], [900, 1020]],
    ),
    (
        "S2",
        {"workday": [480, 960], "min_length": 45, "quorum": 2, "busy": [[[540, 600], [600, 630], [700, 760]], [[630, 700], [900, 960]]]},
        [[480, 540], [760, 900]],
    ),
    (
        "S3",
        {"workday": [540, 1020], "min_length": 90, "quorum": 3, "busy": [[], [[570, 660], [930, 990]], [[720, 870]]]},
        [],
    ),
    (
        "S4",
        {"workday": [540, 1020], "min_length": 45, "quorum": 3, "busy": S4_BUSY},
        [[540, 660], [750, 930], [960, 1020]],
    ),
    (
        "S4 with quorum 4",
        {"workday": [540, 1020], "min_length": 45, "quorum": 4, "busy": S4_BUSY},
        [[540, 600], [780, 900]],
    ),
]
problems = []
for scenario, request, expected in SCENARIOS:
    status, body = call(request)
    slots = body.get("slots") if isinstance(body, dict) else None
    if status != 0 or slots != expected:
        problems.append(f"{scenario}: expected slots {expected}, got {slots!r} (status {status})")

finish(problems, "scenarios ok: S1, S2, S3, S4")
