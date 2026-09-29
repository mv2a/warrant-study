"""H9 (S1, S2, S3, S4): the example requests in the intent, exactly as written there."""

from _cmd import call, finish

S4 = '{"workday": [540, 1020], "min_length": 45, "quorum": %d, "busy": [[], [[600, 720]], [[660, 780], [900, 960]], [[700, 750], [930, 1020]]]}'
SCENARIOS = [
    (
        "S1",
        '{"workday": [540, 1020], "min_length": 30, "quorum": 2, "busy": [[[600, 660], [840, 900]], [[630, 720], [735, 780]]]}',
        {"slots": [[540, 600], [780, 840], [900, 1020]]},
    ),
    (
        "S2",
        '{"workday": [480, 960], "min_length": 45, "quorum": 2, "busy": [[[540, 600], [600, 630], [700, 760]], [[630, 700], [900, 960]]]}',
        {"slots": [[480, 540], [760, 900]]},
    ),
    (
        "S3",
        '{"workday": [540, 1020], "min_length": 90, "quorum": 3, "busy": [[], [[570, 660], [930, 990]], [[720, 870]]]}',
        {"slots": []},
    ),
    ("S4", S4 % 3, {"slots": [[540, 660], [750, 930], [960, 1020]]}),
    ("S4 with quorum 4", S4 % 4, {"slots": [[540, 600], [780, 900]]}),
]
problems = []
for scenario, raw, expected in SCENARIOS:
    status, body = call(raw=raw)
    if status != 0 or body != expected:
        problems.append(f"{scenario}: expected {expected}, got {body!r} (status {status})")

finish(problems, "scenarios ok: S1, S2, S3, S4")
