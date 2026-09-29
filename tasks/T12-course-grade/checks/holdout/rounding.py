"""H5: the percentage is computed exactly and rounded once to one decimal, exact halves up."""

import math
import random
from fractions import Fraction

from _cmd import call, finish
from _oracle import exact_percent, expected, percent_tenths, random_request, show


def half_up(value, places):
    """Round a Fraction half up to the given number of decimal places."""
    scale = 10 ** places
    return Fraction(math.floor(value * scale + Fraction(1, 2)), scale)


def parts(request):
    quizzes = sorted(request["quizzes"])
    kept = quizzes[1:] if len(quizzes) > 1 else quizzes
    homework = [
        Fraction(0) if h["days_late"] >= 5 else Fraction(h["score"] * (10 - h["days_late"]), 10)
        for h in request["homework"]
    ]
    return Fraction(sum(kept), len(kept)), sum(homework, Fraction(0)) / len(homework)


def early_rounding(request, places):
    """What a grader gets by rounding both averages before weighting them (a wrong method)."""
    quiz, homework = parts(request)
    quiz, homework = half_up(quiz, places), half_up(homework, places)
    percent = (15 * quiz + 25 * homework + 25 * request["midterm"] + 35 * request["final"]) / 100
    return math.floor(percent * 10 + Fraction(1, 2))


def float_rounding(request):
    """What a grader gets with binary floating point and Python's round() (a wrong method)."""
    quiz, homework = (float(x) for x in parts(request))
    percent = 0.15 * quiz + 0.25 * homework + 0.25 * request["midterm"] + 0.35 * request["final"]
    return round(round(percent, 1) * 10)


# The intent's own examples: 82.25 becomes 82.3 and 89.95 becomes 90.0.
EXAMPLES = [
    ({"quizzes": [75, 60], "homework": [{"score": 90, "days_late": 0}], "midterm": 82, "final": 80}, 823),
    ({"quizzes": [70, 82, 89, 60], "homework": [{"score": 92, "days_late": 0}], "midterm": 95, "final": 89}, 900),
]
requests = []
for r, rounded in EXAMPLES:
    assert expected(r)[0] == rounded, r
    requests.append(r)

# From one seeded stream of valid requests, take the ones where the method matters.
WANTED = {"exact half": 40, "early rounding differs": 25, "float rounding differs": 25, "any": 40}
taken = {kind: 0 for kind in WANTED}
rng = random.Random(1205)
for _ in range(200000):
    if taken == WANTED:
        break
    r = random_request(rng, max_quizzes=5, max_homework=4)
    right = expected(r)[0]
    kinds = []
    if (exact_percent(r) * 10).denominator == 2:
        kinds.append("exact half")
    if early_rounding(r, 0) != right or early_rounding(r, 1) != right:
        kinds.append("early rounding differs")
    if float_rounding(r) != right:
        kinds.append("float rounding differs")
    kinds.append("any")
    kind = next((k for k in kinds if taken[k] < WANTED[k]), None)
    if kind:
        taken[kind] += 1
        requests.append(r)
assert taken == WANTED, f"could not build every kind of case: {taken}"

problems = []
for r in requests:
    want = expected(r)[0]
    status, body = call(r)
    got = percent_tenths(body)
    if status != 0 or got != want:
        problems.append(f"{r}: exact percent {float(exact_percent(r)):.4f} should give {show(want)}, got {body!r}")

finish(problems, f"rounding ok: {len(requests)} requests, at least {taken['exact half'] + len(EXAMPLES)} of them exact halves")
