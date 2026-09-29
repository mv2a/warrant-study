"""H3: late homework keeps (100 - 10 x days late)% of its score for 1 to 4 days, and 0 from 5 days."""

import random
from fractions import Fraction

from _cmd import call, finish
from _oracle import expected, percent_tenths, show, tenths


def after_penalty(score, days_late):
    """The intent's rule, written out as a table of the share of the score that is kept."""
    kept = {0: Fraction(1), 1: Fraction(9, 10), 2: Fraction(8, 10), 3: Fraction(7, 10), 4: Fraction(6, 10)}
    return score * kept.get(days_late, Fraction(0))


requests = []
# One homework at a time, with every other component at 0, so the percent is 25% of the penalized score.
for score in (100, 85, 73, 50, 19, 7, 0):
    for days_late in (0, 1, 2, 3, 4, 5, 6, 9, 30, 1000):
        r = {"quizzes": [0, 0], "homework": [{"score": score, "days_late": days_late}], "midterm": 0, "final": 0}
        assert tenths(after_penalty(score, days_late) / 4) == expected(r)[0], r
        requests.append(r)

# The intent's example: 85 handed in two days late counts as 68, so 25% of it is 17.0.
example = {"quizzes": [0], "homework": [{"score": 85, "days_late": 2}], "midterm": 0, "final": 0}
assert expected(example)[0] == 170
requests.append(example)

# No homework is dropped: a zero, on time or very late, still counts in the average.
for late in (0, 5, 40):
    r = {"quizzes": [0], "homework": [{"score": 100, "days_late": 0}, {"score": 60, "days_late": late}],
         "midterm": 0, "final": 0}
    requests.append(r)

rng = random.Random(1203)
for _ in range(60):
    r = {
        "quizzes": [rng.randint(0, 100)],
        "homework": [
            {"score": rng.randint(0, 100), "days_late": rng.choice((0, 1, 2, 3, 4, 4, 5, 5, 6, 8, 15))}
            for _ in range(rng.randint(1, 6))
        ],
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
        problems.append(f"homework {r['homework']}: expected percent {show(want)}, got {body!r} (status {status})")

finish(problems, f"late penalty ok: {len(requests)} requests")
