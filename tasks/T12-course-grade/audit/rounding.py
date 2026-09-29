"""X8 (C1): the percent is computed exactly and rounded once to one decimal, halves up."""

from fractions import Fraction

from _cmd import finish
from _grade import describe, exact_percent, grade_problem, request, round_half_up

# Exact halves, which must round up (including 82.25, the intent's own example).
HALVES = [
    (request([82, 69], [(98, 0), (68, 0)], 61, 97), "82.25", "82.3"),
    (request([96], [(84, 0), (100, 2)], 76, 81), "82.25", "82.3"),
    (request([84, 75], [(91, 4)], 84, 100), "82.25", "82.3"),
    (request([40, 70, 67, 40, 59], [(60, 5), (54, 0)], 61, 96), "64.45", "64.5"),
    (request([88, 84], [(78, 0), (63, 0), (81, 0)], 99, 92), "88.65", "88.7"),
    (request([76, 79, 62, 88], [(92, 0)], 92, 94), "91.05", "91.1"),
    (request([78, 78], [(58, 0)], 39, 98), "70.25", "70.3"),
    (request([100, 99, 100, 50], [(100, 0)], 100, 100), "99.95", "100.0"),
    (request([0, 0, 0, 1], [(0, 0)], 0, 0), "0.05", "0.1"),
]

# Students whose rounded percent comes out wrong under a common shortcut: rounding the quiz
# or homework average, a late homework score or a weighted part before the end; rounding
# twice; truncating; rounding halves to even or down; or summing in binary floating point
# and rounding that. Each of those shortcuts changes at least three of these answers; a
# floating-point sum taken as (15q + 25h + 25m + 35f) / 100 changes at least one.
TRAPS = [
    (request([56], [(97, 8)], 37, 58), "38.0"),
    (request([10], [(52, 0)], 60, 37), "42.5"),
    (request([78], [(38, 4)], 52, 42), "45.1"),
    (request([2], [(24, 1)], 86, 54), "46.1"),
    (request([45], [(66, 8)], 44, 89), "48.9"),
    (request([78], [(96, 5)], 38, 85), "51.0"),
    (request([68], [(26, 8)], 38, 95), "53.0"),
    (request([12], [(71, 5)], 97, 78), "53.4"),
    (request([37], [(30, 2)], 92, 56), "54.2"),
    (request([54], [(71, 0)], 36, 60), "55.9"),
    (request([44], [(68, 0)], 60, 55), "57.9"),
    (request([50], [(73, 0)], 74, 94), "77.2"),
    (request([57], [(85, 8), (45, 8)], 42, 33), "30.6"),
    (request([43], [(26, 8), (37, 5)], 94, 36), "42.6"),
    (request([46], [(40, 5), (100, 8)], 90, 45), "45.2"),
    (request([44, 51], [(97, 8)], 90, 67), "53.6"),
    (request([38], [(59, 2), (60, 0)], 45, 69), "54.5"),
    (request([18], [(89, 2), (91, 2)], 43, 66), "54.6"),
    (request([20], [(40, 2), (47, 1)], 90, 57), "54.7"),
    (request([38], [(14, 0), (88, 8)], 98, 80), "60.0"),
    (request([62, 98], [(98, 8)], 58, 89), "60.4"),
    (request([68, 64], [(86, 2)], 88, 33), "61.0"),
    (request([88], [(71, 8), (37, 2), (85, 1)], 52, 62), "56.7"),
    (request([0, 24, 8, 74], [(36, 2)], 32, 82), "49.2"),
    (request([76, 99, 75, 25], [(32, 8)], 98, 45), "52.8"),
    (request([12, 48, 76, 36], [(60, 0)], 85, 50), "61.8"),
    (request([19, 56, 82, 79], [(64, 3)], 88, 62), "65.8"),
    (request([47, 96, 71, 93], [(40, 0)], 90, 70), "70.0"),
    (request([79, 41], [(49, 8), (42, 3), (88, 2), (70, 5)], 90, 44), "56.0"),
    (request([21, 14, 25, 16], [(18, 0), (30, 5), (71, 5)], 96, 58), "48.9"),
    (request([80, 1, 24], [(91, 2), (87, 0), (2, 0), (46, 1)], 32, 76), "55.1"),
    (request([19, 8, 32, 81, 29], [(16, 1), (84, 8), (98, 2)], 83, 62), "56.2"),
    (request([80, 87, 50, 61], [(1, 8), (69, 4), (54, 4), (78, 4)], 56, 72), "58.1"),
    (request([70, 53, 11, 31, 76], [(79, 1), (72, 4), (16, 5)], 91, 70), "65.4"),
    (request([0, 78, 71, 2, 50, 89, 12, 49], [(93, 3)], 65, 42), "54.7"),
    (request([59, 46, 9, 46, 27, 46, 83], [(40, 2), (20, 4), (32, 3)], 34, 50), "39.2"),
    (request([78, 92, 52, 2, 46, 77, 56], [(69, 5), (26, 3), (68, 3)], 34, 78), "51.3"),
    (request([44, 35, 98, 57], [(57, 4), (64, 5), (99, 0), (16, 4), (63, 0), (48, 3), (8, 3)], 33, 30), "37.5"),
    (request([10, 58, 52, 38, 56, 2, 93], [(59, 3), (68, 5), (59, 0), (28, 0)], 52, 31), "39.5"),
    (request([63, 19, 68, 8, 8, 51, 16], [(20, 2), (30, 3), (37, 5), (57, 1)], 76, 36), "42.7"),
    (request([59, 80, 70, 87, 81, 85, 39, 80], [(29, 3), (44, 0), (1, 1)], 84, 40), "52.0"),
    (request([39, 16, 95, 50, 58, 45, 45, 63], [(79, 5), (67, 0), (1, 8)], 34, 100), "57.5"),
    (request([71, 80, 83, 24, 21, 39, 77, 5], [(68, 1), (45, 4), (44, 3), (72, 8)], 34, 35), "36.7"),
    (request([21, 60, 93, 75, 67, 2, 16, 76], [(4, 3), (27, 1), (73, 8), (5, 0)], 82, 34), "43.1"),
    (request([5, 70, 88, 77, 100, 60, 38, 59], [(2, 0), (70, 0), (64, 0), (9, 1)], 70, 36), "49.6"),
    (request([23, 94, 43, 95, 93, 4, 11], [(96, 3), (52, 8), (72, 0), (53, 1), (3, 0), (22, 0)], 94, 47),
     "57.8"),
    (request([70, 88, 80, 8, 63, 0, 32], [(43, 8), (53, 4), (56, 3), (43, 5), (80, 0), (73, 0), (34, 4)],
             41, 37), "40.5"),
    (request([90, 9, 82, 19, 3, 84, 45, 1], [(4, 4), (58, 1), (46, 5), (10, 2), (57, 4), (39, 2)], 81, 73),
     "58.2"),
    (request([37, 32, 89, 92, 38, 7, 3, 74], [(8, 0), (98, 4), (72, 0), (56, 5), (57, 0), (20, 1), (10, 0)],
             50, 41), "42.8"),
]

for req, exact, rounded in HALVES:  # the tables must agree with the audit's own oracle
    assert exact_percent(req) == Fraction(exact) and round_half_up(Fraction(exact)) == Fraction(rounded)
for req, rounded in TRAPS:
    assert round_half_up(exact_percent(req)) == Fraction(rounded), req

problems = []
for req, exact, rounded in HALVES:
    problem = grade_problem(req, label=f"{describe(req)} (exactly {exact})", percent="exact", letter=False)
    if problem:
        problems.append(problem)
for req, rounded in TRAPS:
    problem = grade_problem(req, percent="exact", letter=False)
    if problem:
        problems.append(problem)

finish(problems, f"rounding ok: {len(HALVES)} exact halves and {len(TRAPS)} shortcut traps")
