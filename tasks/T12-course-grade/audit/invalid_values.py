"""X11 (C2): any score or days_late outside the allowed integers is refused, wherever it appears."""

import json

from _cmd import call, finish


def student(quizzes=(66, 91, 78), homework=((84, 0), (73, 2)), midterm=69, final=88):
    return {"quizzes": list(quizzes),
            "homework": [{"score": s, "days_late": d} for s, d in homework],
            "midterm": midterm, "final": final}


BAD_SCORES = [-1, -100, 101, 1000, 87.5, 0.5, 100.5, 90.0, 0.0, 100.0, "90", "", True, False, None,
              [90], {"score": 90}]
BAD_DAYS = [-1, -10, 1.5, 2.0, 0.0, 5.0, "2", "0", True, False, None, [1], {"days": 2}]

cases = []
for bad in BAD_SCORES:
    tag = json.dumps(bad)
    cases += [
        (f"a single quiz of {tag}", student(quizzes=[bad])),
        (f"a quiz of {tag} among valid ones", student(quizzes=[71, bad, 95])),
        (f"a homework score of {tag} on time", student(homework=[(bad, 0)])),
        (f"a homework score of {tag} six days late", student(homework=[(88, 1), (bad, 6)])),
        (f"a midterm of {tag}", student(midterm=bad)),
        (f"a final of {tag}", student(final=bad)),
    ]
# A bad score must be refused even where the rules would drop it or zero it.
cases += [
    ("a quiz of -1 that would be the dropped lowest", student(quizzes=[-1, 80, 90])),
    ("a quiz of -5 among many", student(quizzes=[70, 80, 90, 100, 60, -5])),
    ("a homework score of 101 twenty days late", student(homework=[(101, 20)])),
    ("a homework score of 55.5 five days late", student(homework=[(70, 0), (55.5, 5)])),
]
for bad in BAD_DAYS:
    tag = json.dumps(bad)
    cases += [
        (f"a days_late of {tag}", student(homework=[(84, bad)])),
        (f"a days_late of {tag} after a valid homework", student(homework=[(84, 0), (79, bad)])),
    ]

RAW = [
    ("a quiz of NaN", '{"quizzes": [70, NaN], "homework": [{"score": 80, "days_late": 0}], "midterm": 70, "final": 70}'),
    ("a final of Infinity", '{"quizzes": [70], "homework": [{"score": 80, "days_late": 0}], "midterm": 70, "final": Infinity}'),
    ("a days_late of -Infinity",
     '{"quizzes": [70], "homework": [{"score": 80, "days_late": -Infinity}], "midterm": 70, "final": 70}'),
    ("a midterm written as 7e1", '{"quizzes": [70], "homework": [{"score": 80, "days_late": 0}], "midterm": 7e1, "final": 70}'),
]

problems = []
for label, req in cases:
    status, body = call(req)
    if status != 2 or body is not None:
        problems.append(f"{label}: expected refusal (status 2, no output), got status {status} and {str(body)[:50]!r}")
for label, text in RAW:
    status, body = call(raw=text)
    if status != 2 or body is not None:
        problems.append(f"{label}: expected refusal (status 2, no output), got status {status} and {str(body)[:50]!r}")

finish(problems, f"invalid values refused: {len(cases) + len(RAW)}")
