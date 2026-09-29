"""X4 (G2): exactly one lowest quiz is dropped when there are two or more, then the rest are averaged."""

import random

from _cmd import finish
from _grade import exact_tenths, grade_problem, request

# Homework 80 on time, midterm 70 and final 60 give 58.5 points; the quizzes add 15% of
# their average, so each label names the quiz average the intent requires.
BASE = {"homework": [(80, 0)], "midterm": 70, "final": 60}
CASES = [
    ([58], "a single quiz of 58 is kept: average 58"),
    ([0], "a single quiz of 0 is kept: average 0"),
    ([100], "a single quiz of 100 is kept: average 100"),
    ([58, 94], "two quizzes 58 and 94: the 58 is dropped, average 94"),
    ([94, 58], "two quizzes 94 and 58: the 58 is dropped, average 94"),
    ([50, 50], "two equal quizzes of 50: one is dropped, average 50"),
    ([0, 0], "two quizzes of 0: average 0"),
    ([2, 0], "quizzes 2 and 0: the 0 is dropped, average 2"),
    ([60, 60, 92], "60, 60, 92: only one 60 is dropped, average 76"),
    ([70, 70, 70], "three quizzes of 70: one is dropped, average 70"),
    ([100, 20, 20, 20, 84], "100, 20, 20, 20, 84: only one 20 is dropped, average 56"),
    ([0, 100, 100, 100], "0, 100, 100, 100: the 0 is dropped, average 100"),
    ([88, 76, 92, 64, 70, 84], "the 64 is dropped from six quizzes, average 82"),
    ([90, 80, 70, 60], "the last quiz, 60, is dropped: average 80"),
    ([90, 44, 82], "the middle quiz, 44, is dropped: average 86"),
    ([60, 80, 100], "only the lowest is dropped, never the highest: average 90"),
    ([85, 90, 91, 40], "the 40 is dropped and the rest averaged exactly: average 88 2/3"),
    ([96, 96, 30], "the 30 is dropped: average 96"),
    ([55, 72, 61, 90, 88, 47, 73, 66, 81, 80], "the 47 is dropped from ten quizzes: average 74"),
]

rng = random.Random(8_816_442)
generated = []
while len(generated) < 80:
    quizzes = [rng.randint(0, 100) for _ in range(rng.randint(1, 9))]
    if len(quizzes) >= 2 and rng.random() < 0.4:
        low = min(quizzes)
        quizzes[rng.randrange(len(quizzes))] = low  # at least two quizzes may tie for lowest
        quizzes.append(low)
        rng.shuffle(quizzes)
    req = request(quizzes, [(rng.randint(0, 100), rng.choice([0, 0, 0, 2, 6]))],
                  rng.randint(0, 100), rng.randint(0, 100))
    if exact_tenths(req):
        generated.append(req)

problems = []
for quizzes, label in CASES:
    problem = grade_problem(request(quizzes, **BASE), label=label, letter=False)
    if problem:
        problems.append(problem)
for req in generated:
    problem = grade_problem(req, letter=False)
    if problem:
        problems.append(problem)

finish(problems, f"quiz drop ok: {len(CASES)} described and {len(generated)} generated students")
