"""X12 (C2, C3): requests at the edges of what is valid are graded, not refused.

Each must exit 0 with a JSON object on standard output. The shape of that answer is
checked by X1, and whether its percent and letter are right by the goal and rounding
checks, so neither an arithmetic mistake nor a formatting one counts here.
"""

import json
import random

from _cmd import finish
from _grade import raw_call, request

rng = random.Random(3_141_592)
many = request([rng.randint(0, 100) for _ in range(40)],
               [(rng.randint(0, 100), rng.randint(0, 7)) for _ in range(40)], rng.randint(0, 100), 72)
EDGES = [
    ("every score 0", request([0], [(0, 0)], 0, 0)),
    ("every score 100", request([100], [(100, 0)], 100, 100)),
    ("quizzes of 0 and 100", request([0, 100, 0, 100], [(62, 0)], 71, 67)),
    ("homework scores of 0 and 100", request([84], [(0, 0), (100, 0), (100, 2)], 58, 90)),
    ("a midterm of 0 and a final of 100", request([77, 80], [(69, 2)], 0, 100)),
    ("a midterm of 100 and a final of 0", request([77, 80], [(69, 2)], 100, 0)),
    ("days_late of 0, 4 and 5", request([88], [(90, 0), (90, 4), (90, 5)], 84, 80)),
    ("a days_late of 1000", request([88], [(90, 1000), (76, 0)], 84, 80)),
    ("a days_late of 10**12", request([88], [(90, 10 ** 12), (76, 0)], 84, 80)),
    ("forty quizzes and forty homework", many),
    ("one quiz and one homework, both 0", request([0], [(0, 3)], 93, 97)),
]

problems = []
for label, req in EDGES:
    status, out, _ = raw_call(json.dumps(req))
    try:
        body = json.loads(out)
    except json.JSONDecodeError:
        body = None
    if status != 0 or not isinstance(body, dict):
        problems.append(f"{label}: a valid request must be graded (exit 0 with a JSON object), "
                        f"got status {status} and output {out[:40]!r}")

finish(problems, f"valid edge requests graded: {len(EDGES)}")
