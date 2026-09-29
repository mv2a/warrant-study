"""H6: invalid requests are refused (status 2, nothing on standard output); valid edge cases are graded."""

import json

from _cmd import call, finish

GOOD = {"quizzes": [70, 80], "homework": [{"score": 90, "days_late": 1}], "midterm": 75, "final": 85}


def with_field(name, value):
    request = json.loads(json.dumps(GOOD))
    request[name] = value
    return json.dumps(request)


def without(name):
    request = json.loads(json.dumps(GOOD))
    del request[name]
    return json.dumps(request)


def with_homework(entry):
    return with_field("homework", [{"score": 90, "days_late": 0}, entry])


INVALID = [
    ("text that is not JSON", "seventy, eighty, ninety"),
    ("empty input", ""),
    ("a JSON list", "[70, 80, 90]"),
    ("a JSON string", '"quizzes"'),
    ("JSON null", "null"),
    ("a missing quizzes field", without("quizzes")),
    ("a missing homework field", without("homework")),
    ("a missing midterm", without("midterm")),
    ("a missing final", without("final")),
    ("an empty quiz list", with_field("quizzes", [])),
    ("an empty homework list", with_field("homework", [])),
    ("quizzes given as one number", with_field("quizzes", 80)),
    ("homework given as one object", with_field("homework", {"score": 90, "days_late": 0})),
    ("a quiz score of -1", with_field("quizzes", [70, -1])),
    ("a quiz score of 101", with_field("quizzes", [101, 70])),
    ("a quiz score of 87.5", with_field("quizzes", [70, 87.5])),
    ("a quiz score of 90.0", with_field("quizzes", [70, 90.0])),
    ('a quiz score of "90"', with_field("quizzes", [70, "90"])),
    ("a quiz score of true", with_field("quizzes", [70, True])),
    ("a quiz score of null", with_field("quizzes", [70, None])),
    ("a midterm of 101", with_field("midterm", 101)),
    ("a midterm of 75.5", with_field("midterm", 75.5)),
    ('a final of "85"', with_field("final", "85")),
    ("a final of -5", with_field("final", -5)),
    ("a final of false", with_field("final", False)),
    ("a homework score of 101", with_homework({"score": 101, "days_late": 0})),
    ("a homework score of 88.5", with_homework({"score": 88.5, "days_late": 0})),
    ("a homework score of true", with_homework({"score": True, "days_late": 0})),
    ("a homework entry that is a number", with_homework(90)),
    ("a homework entry without days_late", with_homework({"score": 90})),
    ("a homework entry without score", with_homework({"days_late": 0})),
    ("a days_late of -1", with_homework({"score": 90, "days_late": -1})),
    ("a days_late of -3", with_homework({"score": 60, "days_late": -3})),
    ("a days_late of 1.5", with_homework({"score": 90, "days_late": 1.5})),
    ('a days_late of "2"', with_homework({"score": 90, "days_late": "2"})),
    ("a days_late of true", with_homework({"score": 90, "days_late": True})),
    ("a days_late of null", with_homework({"score": 90, "days_late": None})),
]

# Edge cases that are valid and must be graded, not refused.
VALID = [
    ("scores of 0 and 100", {"quizzes": [0, 100], "homework": [{"score": 0, "days_late": 0}], "midterm": 100, "final": 0}),
    ("a single quiz and a single homework", {"quizzes": [55], "homework": [{"score": 60, "days_late": 0}],
                                             "midterm": 50, "final": 45}),
    ("homework 1000 days late", {"quizzes": [80, 90], "homework": [{"score": 100, "days_late": 1000}],
                                 "midterm": 70, "final": 80}),
    ("twelve quizzes", {"quizzes": [60] * 12, "homework": [{"score": 60, "days_late": 4}], "midterm": 60, "final": 60}),
]

problems = []
for name, raw in INVALID:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{name}: expected a refusal (status 2, no output), got status {status} and {body!r}")
for name, request in VALID:
    status, body = call(request)
    if status != 0 or not isinstance(body, dict):
        problems.append(f"{name}: a valid request must be graded, got status {status} and {body!r}")

finish(problems, f"validation ok: {len(INVALID)} refused, {len(VALID)} valid edge cases graded")
