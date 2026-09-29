"""H1: the course percentage weighs quizzes 15%, homework 25%, midterm 25% and final 35%."""

import random

from _cmd import call, finish
from _oracle import expected, percent_tenths, show


def request(quiz, homework, midterm, final, quiz_count=2, homework_scores=None):
    return {
        "quizzes": [quiz] * quiz_count,
        "homework": [{"score": s, "days_late": 0} for s in (homework_scores or [homework])],
        "midterm": midterm,
        "final": final,
    }


# (request, expected percent in tenths): one component at a time, then pairs that tell weights apart.
CASES = [
    (request(100, 0, 0, 0), 150),
    (request(0, 100, 0, 0), 250),
    (request(0, 0, 100, 0), 250),
    (request(0, 0, 0, 100), 350),
    (request(100, 100, 100, 100), 1000),
    (request(0, 0, 0, 0), 0),
    (request(40, 0, 0, 0, quiz_count=1), 60),
    (request(0, 0, 100, 60), 460),
    (request(0, 0, 60, 100), 500),
    (request(100, 60, 0, 0), 300),
    (request(60, 100, 0, 0), 340),
    (request(20, 40, 60, 80), 560),
    (request(80, 60, 40, 20), 440),
]

rng = random.Random(1201)
for _ in range(60):
    # Equal quiz scores and on-time homework, so only the weighting decides the result.
    quiz_count = rng.randint(1, 5)
    homework_scores = [rng.randint(0, 100) for _ in range(rng.randint(1, 4))]
    r = request(rng.randint(0, 100), None, rng.randint(0, 100), rng.randint(0, 100), quiz_count, homework_scores)
    CASES.append((r, expected(r)[0]))

problems = []
for r, want in CASES:
    assert expected(r)[0] == want, f"check data disagrees with the intent for {r}"
    status, body = call(r)
    got = percent_tenths(body)
    if status != 0 or got != want:
        problems.append(f"{r}: expected percent {show(want)}, got {body!r} (status {status})")

finish(problems, f"weights ok: {len(CASES)} requests")
