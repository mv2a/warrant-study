"""X5 (G3): late homework keeps 90%, 80%, 70%, 60% of its score for 1 to 4 days late, and 0 from 5 days on."""

import random

from _cmd import finish
from _grade import exact_tenths, grade_problem, request

# One quiz of 70, midterm 60 and final 50 give 43.0 points; homework adds 25% of its
# average, so each label names the homework average the intent requires.
BASE = {"quizzes": [70], "midterm": 60, "final": 50}
CASES = [
    ([(100, 0)], "100 on time keeps 100"),
    ([(100, 1)], "100 one day late counts 90"),
    ([(100, 2)], "100 two days late counts 80"),
    ([(100, 3)], "100 three days late counts 70"),
    ([(100, 4)], "100 four days late counts 60"),
    ([(100, 5)], "100 five days late counts 0"),
    ([(100, 6)], "100 six days late counts 0"),
    ([(100, 9)], "100 nine days late counts 0"),
    ([(100, 30)], "100 thirty days late counts 0"),
    ([(100, 1000)], "100 a thousand days late counts 0"),
    ([(100, 10 ** 12)], "100 a trillion days late counts 0"),
    ([(85, 2)], "85 two days late counts 68"),
    ([(50, 2)], "50 two days late loses 10% of its own score per day: 40"),
    ([(72, 3)], "72 three days late counts 50.4, unrounded"),
    ([(80, 4)], "80 four days late counts 48"),
    ([(60, 1)], "60 one day late counts 54"),
    ([(76, 0)], "76 on time keeps 76"),
    ([(0, 3)], "0 three days late counts 0"),
    ([(100, 0), (0, 0)], "no homework is dropped: 100 and 0 average 50"),
    ([(100, 0), (100, 6)], "homework scoring 0 for lateness still counts: average 50"),
    ([(90, 1), (80, 3), (71, 0), (60, 6)], "81, 56, 71 and 0 average 52"),
    ([(96, 0), (88, 1), (76, 2), (90, 3), (85, 4), (99, 5), (100, 12)],
     "96, 79.2, 60.8, 63, 51, 0 and 0 average 50"),
    ([(64, 4), (64, 4), (64, 4)], "three of 64, four days late, average 38.4"),
]

rng = random.Random(2_718_281)
DAYS = [0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 7, 8, 10, 14, 45]
generated = []
while len(generated) < 80:
    homework = [(rng.randint(0, 100), rng.choice(DAYS)) for _ in range(rng.randint(1, 8))]
    req = request([rng.randint(0, 100)], homework, rng.randint(0, 100), rng.randint(0, 100))
    if exact_tenths(req):
        generated.append(req)

problems = []
for homework, label in CASES:
    problem = grade_problem(request(homework=homework, **BASE), label=label, letter=False)
    if problem:
        problems.append(problem)
for req in generated:
    problem = grade_problem(req, letter=False)
    if problem:
        problems.append(problem)

finish(problems, f"late homework ok: {len(CASES)} described and {len(generated)} generated students")
