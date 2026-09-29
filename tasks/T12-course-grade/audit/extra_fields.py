"""X2 (C3): fields other than the named ones, in the request or in a homework object, are ignored.

Each request is compared with the same request without the extra fields, not with the
audit's oracle: whether the grade itself is right is the goal and rounding checks' job.
"""

import json

from _cmd import call, finish
from _grade import describe, request

BASES = [
    request([72, 58, 94], [(80, 0), (67, 2)], 74, 69),
    request([90], [(100, 6), (84, 1)], 88, 95),
    request([41, 57], [(55, 0)], 62, 48),
]
# Unknown fields at the top level of the request.
EXTRAS = [
    {"name": "Student 17", "student_id": 5521},
    {"extra_credit": 15},
    {"curve": 7.5, "bonus": -4},
    {"percent": 12.5, "letter": "F"},
    {"notes": None, "incomplete": True},
    {"labs": [100, 100, 100], "attendance": {"present": 30, "absent": 0}},
    {"quiz": [0, 0], "Final": 0, "midterm_exam": 100, "homework_count": 99},
    {"weights": {"quiz": 100, "homework": 0, "midterm": 0, "final": 0}},
    {"drop_lowest": False, "late_policy": "none"},
]
# Unknown fields added to every homework object.
HOMEWORK_EXTRAS = [
    {"title": "Problem set"},
    {"submitted": "2026-03-02", "late_reason": None, "excused": True},
    {"max_score": 50, "weight": 3, "penalty": 0},
    {"Score": 0, "days_early": 4, "late": False, "score_after_penalty": 100},
]


def with_homework_extra(base, extra):
    body = json.loads(json.dumps(base))
    for item in body["homework"]:
        item.update(extra)
    return body


problems = []
checked = 0
for base in BASES:
    plain = call(base)
    if plain[0] != 0 or not isinstance(plain[1], dict):
        problems.append(f"{describe(base)} without extra fields: expected a graded answer, "
                        f"got status {plain[0]} and {str(plain[1])[:50]!r}")
        continue
    variants = [({**base, **extra}, describe(extra)) for extra in EXTRAS]
    variants += [(with_homework_extra(base, extra), "in every homework object " + describe(extra))
                 for extra in HOMEWORK_EXTRAS]
    for req, label in variants:
        got = call(req)
        checked += 1
        if got != plain:
            problems.append(f"{label} added to {describe(base)}: expected status {plain[0]} and "
                            f"{plain[1]} as without them, got status {got[0]} and {str(got[1])[:50]!r}")

finish(problems, f"extra fields ignored: {checked} requests")
