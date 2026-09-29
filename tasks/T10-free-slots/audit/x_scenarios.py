"""X2-X4, X13 (S1, S2, S3, S4): the example requests in the intent get exactly the answer it writes.

Usage: python3 x_scenarios.py S1|S2|S3|S4
"""

import json
import sys

from _cmd import call, finish

S4_REQUEST = '{"workday": [540, 1020], "min_length": 45, "quorum": %s, "busy": [[], [[600, 720]], [[660, 780], [900, 960]], [[700, 750], [930, 1020]]]}'
SCENARIOS = {
    "S1": [(
        '{"workday": [540, 1020], "min_length": 30, "quorum": 2, "busy": [[[600, 660], [840, 900]], [[630, 720], [735, 780]]]}',
        '{"slots": [[540, 600], [780, 840], [900, 1020]]}',
    )],
    "S2": [(
        '{"workday": [480, 960], "min_length": 45, "quorum": 2, "busy": [[[540, 600], [600, 630], [700, 760]], [[630, 700], [900, 960]]]}',
        '{"slots": [[480, 540], [760, 900]]}',
    )],
    "S3": [(
        '{"workday": [540, 1020], "min_length": 90, "quorum": 3, "busy": [[], [[570, 660], [930, 990]], [[720, 870]]]}',
        '{"slots": []}',
    )],
    "S4": [
        (S4_REQUEST % 3, '{"slots": [[540, 660], [750, 930], [960, 1020]]}'),
        (S4_REQUEST % 4, '{"slots": [[540, 600], [780, 900]]}'),
    ],
}

name = sys.argv[1]
problems = []
for request, answer in SCENARIOS[name]:
    want = json.loads(answer)
    status, body = call(raw=request)
    if status != 0:
        problems.append(f"{name}: exited with status {status}, expected 0")
    # The same JSON value as the intent writes: same fields, same slots in the same order, whole numbers.
    elif json.dumps(body, sort_keys=True) != json.dumps(want, sort_keys=True):
        problems.append(f"{name}: expected {answer}, got {json.dumps(body)[:160]}")
finish(problems, f"{name} ok")
