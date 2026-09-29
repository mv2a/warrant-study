"""X6 (G4): the letter bands, on both sides of every boundary and across the whole range."""

import random
from fractions import Fraction

from _cmd import finish
from _grade import LETTERS, describe, exact_percent, exact_tenths, expected, grade_problem, request

# (request, its exact course percentage, the letter the intent requires). Every percentage
# here is exact to one decimal place, so no rounding is involved.
BOUNDARIES = [
    (request([100, 0], [(100, 0)], 100, 100), "100.0", "A"),
    (request([100, 78], [(100, 0)], 100, 100), "100.0", "A"),
    (request([97], [(82, 2), (80, 2), (96, 1), (100, 0)], 94, 92), "90.0", "A"),
    (request([100, 94, 73], [(89, 1), (99, 1)], 94, 88), "90.0", "A"),
    (request([100, 83, 90, 93], [(100, 1), (100, 0)], 75, 95), "89.9", "B+"),
    (request([73, 89, 99, 83], [(98, 0), (88, 3)], 94, 94), "89.9", "B+"),
    (request([96, 75, 83, 95, 80], [(93, 3)], 90, 97), "86.0", "B+"),
    (request([78, 58], [(61, 0)], 99, 98), "86.0", "B+"),
    (request([78, 76, 69, 86], [(88, 0)], 83, 89), "85.9", "B"),
    (request([78, 93], [(88, 3), (96, 0), (70, 7), (80, 0)], 94, 96), "85.9", "B"),
    (request([48], [(61, 0)], 100, 93), "80.0", "B"),
    (request([69, 86, 94], [(85, 0)], 83, 70), "80.0", "B"),
    (request([71, 91], [(78, 0), (100, 4), (90, 1)], 87, 75), "79.9", "C+"),
    (request([80, 94, 78, 81], [(86, 4)], 98, 85), "79.9", "C+"),
    (request([71, 49, 42], [(60, 0)], 68, 100), "76.0", "C+"),
    (request([93, 79, 100, 80], [(94, 5), (100, 5), (100, 7), (80, 0)], 95, 96), "76.0", "C+"),
    (request([65, 32, 38, 57], [(45, 0)], 88, 99), "75.9", "C"),
    (request([90, 68], [(72, 0)], 88, 64), "75.9", "C"),
    (request([70, 94, 85, 87], [(99, 7), (81, 7), (99, 2)], 94, 76), "70.0", "C"),
    (request([62, 74], [(73, 5)], 97, 99), "70.0", "C"),
    (request([97, 74], [(77, 2), (90, 7), (72, 0), (100, 0)], 44, 85), "69.9", "D"),
    (request([74, 83, 85, 81], [(100, 2)], 42, 77), "69.9", "D"),
    (request([83], [(72, 5), (64, 1), (67, 7), (64, 1)], 48, 81), "60.0", "D"),
    (request([78, 97, 83], [(89, 4), (96, 5), (79, 5)], 80, 63), "60.0", "D"),
    (request([61, 74, 55], [(76, 7), (71, 0)], 46, 84), "59.9", "F"),
    (request([89], [(96, 7)], 84, 73), "59.9", "F"),
    (request([0], [(100, 5)], 0, 0), "0.0", "F"),
    (request([0, 0, 0], [(90, 7), (0, 0)], 0, 0), "0.0", "F"),
]

# Generated students of every ability: twelve in each of the seven bands.
rng = random.Random(4_470_193)
generated, per_letter = [], {letter: 0 for letter in LETTERS}
while min(per_letter.values()) < 12:
    level = rng.randint(40, 100)
    near = lambda spread: max(0, min(100, level + rng.randint(-spread, spread)))  # noqa: E731
    req = request([near(12) for _ in range(rng.randint(1, 6))],
                  [(near(10), rng.choice([0, 0, 0, 0, 1, 2, 3, 4, 5, 8])) for _ in range(rng.randint(1, 5))],
                  near(8), near(8))
    letter = expected(req)[1]
    if exact_tenths(req) and per_letter[letter] < 12:
        per_letter[letter] += 1
        generated.append(req)

for req, percent, letter in BOUNDARIES:  # the table above must agree with the audit's own oracle
    assert exact_percent(req) == Fraction(percent) and expected(req)[1] == letter, (req, percent)

problems = []
for req, percent, letter in BOUNDARIES:
    problem = grade_problem(req, label=f"{describe(req)} (exactly {percent})", percent=None)
    if problem:
        problems.append(problem)
for req in generated:
    problem = grade_problem(req, percent=None)
    if problem:
        problems.append(problem)

finish(problems, f"letter bands ok: {len(BOUNDARIES)} boundary and {len(generated)} generated students")
