"""X1 (C3): the shape of every answer and every refusal."""

import json
import math
import random

from _cmd import finish
from _grade import LETTERS, describe, raw_call, request

rng = random.Random(61_803)
VALID = [
    request([48, 91, 77], [(66, 0), (73, 3)], 58, 81),
    request([100], [(100, 0)], 100, 100),
    request([0], [(0, 0)], 0, 0),
    request([35, 35, 35, 35, 35, 35], [(12, 9)], 44, 29),
    request([83, 64], [(95, 1), (88, 2), (79, 4), (91, 0)], 87, 90),
]
for _ in range(10):
    VALID.append(request([rng.randint(0, 100) for _ in range(rng.randint(1, 7))],
                         [(rng.randint(0, 100), rng.choice([0, 0, 1, 2, 3, 4, 5, 11]))
                          for _ in range(rng.randint(1, 6))],
                         rng.randint(0, 100), rng.randint(0, 100)))

REFUSED = [
    ("a quiz score of -3", request([-3, 80], [(70, 0)], 60, 60)),
    ("a midterm of 100.0", request([80], [(70, 0)], 100.0, 60)),
    ("a days_late of \"1\"", request([80], [(70, "1")], 60, 60)),
    ("a missing final", {"quizzes": [80], "homework": [{"score": 70, "days_late": 0}], "midterm": 60}),
    ("an empty homework list", request([80], [], 60, 60)),
]
problems = []


def shape_problem(tag, status, out):
    if status != 0:
        return f"{tag}: exit status {status}, expected 0"
    try:
        body = json.loads(out)
    except json.JSONDecodeError:
        return f"{tag}: standard output is not one JSON value: {out[:60]!r}"
    if not isinstance(body, dict):
        return f"{tag}: standard output is not a JSON object: {out[:60]!r}"
    if set(body) != {"percent", "letter"}:
        return f"{tag}: expected exactly the fields percent and letter, got {sorted(body)}"
    p = body["percent"]
    if type(p) not in (int, float) or (isinstance(p, float) and not math.isfinite(p)):
        return f"{tag}: percent must be a JSON number, got {p!r}"
    if not 0 <= p <= 100 or float(p) != round(float(p), 1):
        return f"{tag}: percent must lie in 0..100 with at most one decimal place, got {p!r}"
    if body["letter"] not in LETTERS:
        return f"{tag}: letter must be one of {list(LETTERS)}, got {body['letter']!r}"
    return None


def graded(status, out):
    """True when the command answered with exit 0 and a JSON object instead of refusing."""
    if status != 0:
        return False
    try:
        return isinstance(json.loads(out), dict)
    except json.JSONDecodeError:
        return False


answers = {}
for req in VALID:
    status, out, _ = raw_call(json.dumps(req))
    problem = shape_problem(describe(req), status, out)
    if problem:
        problems.append(problem)
    else:
        answers[describe(req)] = json.loads(out)

# The same request, pretty-printed with the keys in another order and surrounded by blank
# lines, is still one JSON object and must get the same answer.
for req in VALID[:5]:
    text = "\n\n" + json.dumps(dict(reversed(list(req.items()))), indent=3) + "\n\n"
    status, out, _ = raw_call(text)
    problem = shape_problem("pretty-printed " + describe(req), status, out)
    if problem:
        problems.append(problem)
    elif describe(req) in answers and json.loads(out) != answers[describe(req)]:
        problems.append(f"pretty-printed {describe(req)}: answer {out.strip()} differs from "
                        f"the compact request's {answers[describe(req)]}")

# How a refusal looks. Which requests must be refused is C2's business (X10, X11), so an
# invalid request that the command grades anyway is not counted here.
refusals = 0
for label, req in REFUSED:
    status, out, _ = raw_call(json.dumps(req))
    if graded(status, out):
        continue
    refusals += 1
    # Standard output is JSON text, where whitespace carries nothing (a success answer is
    # likewise judged with surrounding whitespace ignored), so whitespace alone is no output.
    if status != 2 or out.strip() != "":
        problems.append(f"{label}: a refusal must exit 2 and write nothing on standard output, "
                        f"got status {status} and output {out[:40]!r}")

finish(problems, f"interface ok: {len(VALID)} answers, 5 pretty-printed, {refusals} refusals")
