"""X3 (G1): the course percentage weighs quizzes 15%, homework 25%, midterm 25%, final 35%."""

import random

from _cmd import finish
from _grade import exact_tenths, grade_problem, request

# Each component alone at a known value, the others at zero. No quiz is dropped (one quiz or
# equal quizzes) and all homework is on time, so only the weights matter.
ISOLATED = [
    (request([100], [(0, 0)], 0, 0), "quizzes alone at 100 give 15.0"),
    (request([64, 64, 64], [(0, 0)], 0, 0), "quizzes alone at 64 give 9.6"),
    (request([0], [(100, 0)], 0, 0), "homework alone at 100 gives 25.0"),
    (request([0], [(52, 0), (52, 0)], 0, 0), "homework alone at 52 gives 13.0"),
    (request([0], [(0, 0)], 100, 0), "midterm alone at 100 gives 25.0"),
    (request([0], [(0, 0)], 36, 0), "midterm alone at 36 gives 9.0"),
    (request([0], [(0, 0)], 0, 100), "final alone at 100 gives 35.0"),
    (request([0], [(0, 0)], 0, 58), "final alone at 58 gives 20.3"),
    (request([100, 100], [(0, 0)], 0, 100), "quizzes and final at 100 give 50.0"),
    (request([0], [(100, 0)], 100, 0), "homework and midterm at 100 give 50.0"),
    (request([100], [(100, 0)], 100, 100), "every component at 100 gives 100.0"),
    (request([0, 0], [(0, 0)], 0, 0), "every component at 0 gives 0.0"),
    (request([20], [(40, 0)], 60, 80), "20, 40, 60, 80 give 56.0"),
    (request([80], [(60, 0)], 40, 20), "80, 60, 40, 20 give 44.0"),
]

rng = random.Random(1_935_028)
generated = []
while len(generated) < 70:
    quiz = rng.randint(0, 100)
    homework = rng.randint(0, 100)
    req = request([quiz] * rng.randint(1, 5), [(homework, 0)] * rng.randint(1, 4),
                  rng.randint(0, 100), rng.randint(0, 100))
    if exact_tenths(req):
        generated.append(req)

problems = []
for req, label in ISOLATED:
    problem = grade_problem(req, label=label, letter=False)
    if problem:
        problems.append(problem)
for req in generated:
    problem = grade_problem(req, letter=False)
    if problem:
        problems.append(problem)

finish(problems, f"weights ok: {len(ISOLATED)} isolated and {len(generated)} generated students")
