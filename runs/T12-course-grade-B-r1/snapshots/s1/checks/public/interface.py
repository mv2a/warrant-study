"""P1: `grade` follows the interface in the intent."""

from _cmd import call, finish

LETTERS = {"A", "B+", "B", "C+", "C", "D", "F"}
VALID = [
    {"quizzes": [55, 80, 75], "homework": [{"score": 70, "days_late": 0}], "midterm": 66, "final": 72},
    {"quizzes": [100, 95], "homework": [{"score": 98, "days_late": 0}, {"score": 91, "days_late": 1}],
     "midterm": 97, "final": 99},
]
problems = []

for request in VALID:
    status, body = call(request)
    if status != 0:
        problems.append(f"{request}: exited with status {status}, expected 0")
    elif not isinstance(body, dict) or set(body) != {"percent", "letter"}:
        problems.append(f"{request}: expected an object with exactly percent and letter, got {body!r}")
    elif type(body["percent"]) not in (int, float) or abs(body["percent"] * 10 - round(body["percent"] * 10)) > 1e-6:
        problems.append(f"{request}: percent must be a number with at most one decimal place, got {body['percent']!r}")
    elif body["letter"] not in LETTERS:
        problems.append(f"{request}: letter must be one of {sorted(LETTERS)}, got {body['letter']!r}")

status, body = call({"quizzes": [101, 80], "homework": [{"score": 70, "days_late": 0}], "midterm": 66, "final": 72})
if status != 2 or body is not None:
    problems.append(f"a quiz score of 101 must be refused with status 2 and no output, got status {status} and {body!r}")

finish(problems, "interface ok: 3 requests")
