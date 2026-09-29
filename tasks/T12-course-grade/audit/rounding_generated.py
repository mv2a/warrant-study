"""X9 (C1): generated students of every kind get exactly the once-rounded percent."""

import random

from _cmd import finish
from _grade import grade_problem, request

rng = random.Random(5_092_117)
DAYS = [0, 0, 0, 1, 2, 3, 4, 5, 6, 9]
students = []
for _ in range(160):
    level = rng.randint(0, 100)
    near = lambda: max(0, min(100, level + rng.randint(-40, 40)))  # noqa: E731
    students.append(request([near() for _ in range(rng.randint(1, 9))],
                            [(near(), rng.choice(DAYS)) for _ in range(rng.randint(1, 9))],
                            near(), near()))

problems = []
for req in students:
    problem = grade_problem(req, percent="exact", letter=False)
    if problem:
        problems.append(problem)

finish(problems, f"generated rounding ok: {len(students)} students")
