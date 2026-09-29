"""X10 (C2): malformed requests are refused with status 2 and no output."""

import json

from _cmd import call, finish

GOOD = {"quizzes": [74, 88, 61], "homework": [{"score": 92, "days_late": 0}, {"score": 70, "days_late": 1}],
        "midterm": 77, "final": 83}
GOOD_TEXT = json.dumps(GOOD)


def without(field):
    return {k: v for k, v in GOOD.items() if k != field}


def but(**changes):
    return {**GOOD, **changes}


def entries(*items):
    return but(homework=list(items))


OK_ENTRY = {"score": 81, "days_late": 0}
RAW = [
    ("empty input", ""),
    ("only whitespace", "  \n\t\n"),
    ("plain words", "grade this student please"),
    ("an unclosed object", '{"quizzes": [74, 88], "homework": ['),
    ("a lone closing brace", "}"),
    ("unquoted keys", "{quizzes: [74], homework: [{score: 90, days_late: 0}], midterm: 70, final: 80}"),
    ("single-quoted keys", str(GOOD)),
    ("a valid object followed by other text", GOOD_TEXT + " and some more"),
    ("a trailing comma", GOOD_TEXT[:-1] + ",}"),
    ("a JSON list", "[]"),
    ("a list holding a valid request", json.dumps([GOOD])),
    ("a JSON string", json.dumps(GOOD_TEXT)),
    ("a JSON number", "85"),
    ("a JSON null", "null"),
    ("a JSON true", "true"),
]
REQUESTS = [
    ("an empty object", {}),
    ("no quizzes field", without("quizzes")),
    ("no homework field", without("homework")),
    ("no midterm field", without("midterm")),
    ("no final field", without("final")),
    ("only a quizzes field", {"quizzes": [90]}),
    ("an empty quiz list", but(quizzes=[])),
    ("quizzes of null", but(quizzes=None)),
    ("quizzes as a number", but(quizzes=90)),
    ("quizzes as text", but(quizzes="90, 80")),
    ("quizzes as an object", but(quizzes={"q1": 90})),
    ("an empty homework list", but(homework=[])),
    ("homework of null", but(homework=None)),
    ("homework as a single object", but(homework={"score": 90, "days_late": 0})),
    ("homework as a number", but(homework=90)),
    ("homework as text", but(homework="[]")),
    ("a homework entry that is a number", entries(90)),
    ("a homework entry that is a list", entries([90, 0])),
    ("a homework entry that is text", entries("90")),
    ("a homework entry of null", entries(None)),
    ("an empty homework entry", entries({})),
    ("a homework entry without days_late", entries({"score": 90})),
    ("a homework entry without score", entries({"days_late": 0})),
    ("a homework entry with Score capitalised", entries({"Score": 90, "days_late": 0})),
    ("a homework entry with late instead of days_late", entries({"score": 90, "late": 0})),
    ("a bad entry after two good ones", entries(OK_ENTRY, OK_ENTRY, {"score": 90})),
    ("a bad entry between good ones", entries(OK_ENTRY, 75, OK_ENTRY)),
]

problems = []
cases = [(label, None, text) for label, text in RAW] + [(label, req, None) for label, req in REQUESTS]
for label, req, text in cases:
    status, body = call(req, raw=text)
    if status != 2 or body is not None:
        problems.append(f"{label}: expected refusal (status 2, no output), got status {status} and {str(body)[:50]!r}")

finish(problems, f"malformed requests refused: {len(cases)}")
