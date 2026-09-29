"""X7 (G4): the letter follows the rounded course percentage, not the unrounded one."""

from fractions import Fraction

from _cmd import finish
from _grade import describe, exact_percent, expected, grade_problem, request

# (request, its exact course percentage, the letter of the rounded percentage).
# Exact halves just under a boundary round up into the higher band.
HALVES = [
    (request([80], [(88, 0)], 88, 97), "89.95", "A"),
    (request([92, 98, 78], [(94, 0), (78, 0), (77, 0)], 98, 87), "89.95", "A"),
    (request([71, 60, 70, 84], [(64, 0)], 99, 97), "85.95", "B+"),
    (request([76, 44], [(68, 0)], 100, 93), "85.95", "B+"),
    (request([73, 62, 73], [(78, 3)], 94, 91), "79.95", "B"),
    (request([91, 89, 72, 76, 98], [(100, 0), (70, 3)], 97, 68), "79.95", "B"),
    (request([81, 99], [(72, 3)], 82, 80), "75.95", "C+"),
    (request([45, 60, 52], [(78, 2)], 93, 82), "75.95", "C+"),
    (request([100, 67, 100, 79, 85], [(100, 0)], 79, 33), "69.95", "C"),
    (request([72, 78, 88, 91], [(88, 7), (76, 2)], 79, 85), "69.95", "C"),
    (request([80], [(78, 2)], 79, 36), "59.95", "D"),
    (request([79, 74, 77, 80], [(72, 5)], 89, 74), "59.95", "D"),
]
# Unrounded percentages that are not halves: above the half they round up into the higher
# band, below it they stay in the lower band.
NEAR = [
    (request([76, 100, 90, 97], [(100, 4), (100, 0), (85, 0)], 92, 92), "89.9667", "A"),
    (request([92, 71, 99], [(77, 0), (99, 1), (95, 1)], 97, 87), "89.9917", "A"),
    (request([79, 86, 71], [(100, 0), (100, 3)], 95, 93), "89.9250", "B+"),
    (request([75, 65, 68, 94, 92], [(94, 4), (87, 0), (99, 0)], 85, 92), "85.9875", "B+"),
    (request([72, 66, 87, 72, 69, 79, 96], [(88, 2), (98, 2)], 82, 100), "85.9750", "B+"),
    (request([82, 89, 92, 77, 76, 72, 100], [(81, 0), (100, 2), (87, 0)], 89, 86), "85.9167", "B"),
    (request([65, 88, 78, 71, 77], [(84, 1)], 88, 78), "79.9750", "B"),
    (request([58, 83, 91, 75], [(73, 1)], 91, 81), "79.9750", "B"),
    (request([58, 52, 43, 55, 45], [(69, 0)], 96, 88), "79.9250", "C+"),
    (request([52, 69, 74, 42, 56], [(73, 1), (66, 2)], 67, 100), "75.9750", "C+"),
    (request([72, 42, 76, 76, 73], [(53, 0)], 93, 81), "75.9875", "C+"),
    (request([97, 62, 100, 67, 75, 89, 65], [(81, 3), (99, 4), (95, 3)], 83, 79), "75.9417", "C"),
    (request([61, 47, 55, 52, 27, 61, 51, 53], [(58, 0), (39, 2), (37, 3)], 83, 90), "69.9845", "C"),
    (request([61, 57, 45, 59, 73, 71, 45, 53], [(66, 2)], 89, 73), "69.9786", "C"),
    (request([93, 100, 86, 98, 94, 76, 82], [(99, 6)], 97, 91), "69.9250", "D"),
    (request([16, 36, 20, 38], [(32, 3), (31, 1)], 63, 95), "59.9875", "D"),
    (request([55, 39, 58, 29], [(55, 3), (47, 0), (41, 0)], 61, 76), "59.9917", "D"),
    (request([85, 68, 70, 82, 71, 59, 69, 84], [(78, 2), (69, 6), (58, 4)], 71, 65), "59.9357", "F"),
]

for req, percent, letter in HALVES:  # the tables must agree with the audit's own oracle
    assert exact_percent(req) == Fraction(percent) and expected(req)[1] == letter, (req, percent)
for req, percent, letter in NEAR:
    assert abs(exact_percent(req) - Fraction(percent)) < Fraction(1, 10000) and expected(req)[1] == letter

problems = []
for req, percent, _ in HALVES + NEAR:
    problem = grade_problem(req, label=f"{describe(req)} (unrounded {percent})", percent=None)
    if problem:
        problems.append(problem)

finish(problems, f"letters follow the rounded percent: {len(HALVES)} halves and {len(NEAR)} near misses")
