"""H7: `grade` reads one JSON object, ignores extra fields, and answers with exactly percent and letter."""

import json
import random

from _cmd import call, finish
from _oracle import random_request

LETTERS = {"A", "B+", "B", "C+", "C", "D", "F"}
rng = random.Random(1207)
problems = []


def shape_problem(body):
    """Why a successful answer does not have the promised shape, or None if it does."""
    if not isinstance(body, dict) or set(body) != {"percent", "letter"}:
        return "expected an object with exactly the fields percent and letter"
    percent = body["percent"]
    if type(percent) not in (int, float):
        return "percent must be a JSON number"
    if not 0 <= percent <= 100 or abs(percent * 10 - round(percent * 10)) > 1e-6:
        return "percent must lie between 0 and 100 with at most one decimal place"
    if body["letter"] not in LETTERS:
        return f"letter must be one of {sorted(LETTERS)}"
    return None


requests = [random_request(rng) for _ in range(25)]
requests.append({"quizzes": [0], "homework": [{"score": 0, "days_late": 0}], "midterm": 0, "final": 0})
requests.append({"quizzes": [100], "homework": [{"score": 100, "days_late": 0}], "midterm": 100, "final": 100})
for request in requests:
    status, body = call(request)
    problem = "exited with status %s, expected 0" % status if status != 0 else shape_problem(body)
    if problem:
        problems.append(f"{request}: {problem}, got {body!r}")

# Fields other than the four named ones are ignored, at the top level and inside homework entries.
for _ in range(8):
    plain = random_request(rng, max_quizzes=4, max_homework=3)
    extra = json.loads(json.dumps(plain))
    extra.update({"student": "Rosa Quintero", "section": 7, "notes": None, "grade": "A"})
    for index, item in enumerate(extra["homework"]):
        item.update({"title": f"Problem set {index + 1}", "submitted_via": "portal"})
    first, second = call(plain), call(extra)
    if second[0] != 0 or second != first:
        problems.append(f"extra fields changed the answer: {first!r} without them, {second!r} with them")

# The request may be spread over several lines, and field order does not matter.
pretty = json.dumps({"final": 81, "midterm": 77, "homework": [{"days_late": 0, "score": 88}], "quizzes": [90, 70]},
                    indent=2)
status, body = call(raw=pretty + "\n")
if status != 0 or shape_problem(body):
    problems.append(f"a pretty-printed request must be graded, got status {status} and {body!r}")

# A refused request exits 2 and writes nothing on standard output.
for raw in ('{"quizzes": [80], "homework": [], "midterm": 70, "final": 60}', "{", "42"):
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{raw!r} must be refused with status 2 and no output, got status {status} and {body!r}")

finish(problems, f"interface ok: {len(requests) + 16 + 1 + 3} calls")
