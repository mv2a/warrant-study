"""H2: exactly one lowest quiz is dropped when there are two or more; a single quiz is kept."""

import random
from fractions import Fraction

from _cmd import call, finish
from _oracle import expected, percent_tenths, show, tenths

# (quiz scores, the quiz average the intent gives). The other components are fixed below.
CASES = [
    ([73], Fraction(73)),
    ([0], Fraction(0)),
    ([100], Fraction(100)),
    ([90, 30], Fraction(90)),
    ([30, 90], Fraction(90)),
    ([60, 70], Fraction(70)),
    ([0, 0], Fraction(0)),
    ([50, 50, 100], Fraction(75)),
    ([100, 50, 50], Fraction(75)),
    ([80, 80, 80], Fraction(80)),
    ([100, 20, 60, 20], Fraction(60)),
    ([45, 100, 95], Fraction(195, 2)),
    ([12, 99, 12, 99, 12], Fraction(111, 2)),
    ([0, 0, 0, 100], Fraction(100, 3)),
    ([66, 67, 68, 69, 70, 71, 72, 73, 74, 1], Fraction(70)),
]
OTHERS = {"homework": [{"score": 80, "days_late": 0}], "midterm": 70, "final": 60}

requests = []
for quizzes, average in CASES:
    r = {"quizzes": quizzes, **OTHERS}
    # 15% of the stated quiz average, plus 20 + 17.5 + 21 from the other components.
    assert tenths((15 * average + 25 * 80 + 25 * 70 + 35 * 60) / 100) == expected(r)[0], quizzes
    requests.append(r)

rng = random.Random(1202)
POOL = (0, 35, 50, 50, 64, 64, 81, 90, 100)  # repeated values, so ties for lowest are common
for _ in range(70):
    r = {
        "quizzes": [rng.choice(POOL) if rng.random() < 0.7 else rng.randint(0, 100) for _ in range(rng.randint(1, 9))],
        "homework": [{"score": rng.randint(0, 100), "days_late": 0} for _ in range(rng.randint(1, 3))],
        "midterm": rng.randint(0, 100),
        "final": rng.randint(0, 100),
    }
    requests.append(r)

problems = []
for r in requests:
    want = expected(r)[0]
    status, body = call(r)
    got = percent_tenths(body)
    if status != 0 or got != want:
        problems.append(f"quizzes {r['quizzes']}: expected percent {show(want)}, got {body!r} (status {status})")

finish(problems, f"quiz drop ok: {len(requests)} requests")
