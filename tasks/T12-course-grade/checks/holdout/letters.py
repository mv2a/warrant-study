"""H4: the letter follows the rounded percentage, with every boundary included in the higher letter."""

import random

from _cmd import call, finish
from _oracle import expected, letter, random_request

# (request, rounded percent in tenths, letter). For each boundary: exactly on it, an exact
# half below it and a third of a tenth below it (both round up onto it), and three values
# that round to one tenth below it.
CASES = [
    ({"quizzes": [100, 100], "homework": [{"score": 100, "days_late": 0}], "midterm": 100, "final": 100}, 1000, "A"),
    ({"quizzes": [87, 66], "homework": [{"score": 78, "days_late": 0}], "midterm": 94, "final": 97}, 900, "A"),  # exactly 90.0
    ({"quizzes": [64, 82, 63, 76], "homework": [{"score": 91, "days_late": 0}, {"score": 90, "days_late": 0}, {"score": 77, "days_late": 2}], "midterm": 96, "final": 99}, 900, "A"),  # 2699/30, about 89.9667
    ({"quizzes": [70, 82, 89, 60], "homework": [{"score": 92, "days_late": 0}], "midterm": 95, "final": 89}, 900, "A"),  # exactly 89.95
    ({"quizzes": [96], "homework": [{"score": 84, "days_late": 2}, {"score": 68, "days_late": 2}, {"score": 98, "days_late": 1}], "midterm": 95, "final": 98}, 899, "B+"),  # 1349/15, about 89.9333
    ({"quizzes": [83, 75, 65], "homework": [{"score": 99, "days_late": 1}], "midterm": 86, "final": 98}, 899, "B+"),  # exactly 89.925
    ({"quizzes": [81, 72], "homework": [{"score": 92, "days_late": 0}], "midterm": 86, "final": 95}, 899, "B+"),  # exactly 89.9
    ({"quizzes": [75, 76, 74, 91], "homework": [{"score": 91, "days_late": 0}], "midterm": 73, "final": 94}, 860, "B+"),  # exactly 86.0
    ({"quizzes": [74], "homework": [{"score": 100, "days_late": 3}, {"score": 82, "days_late": 0}, {"score": 88, "days_late": 1}], "midterm": 95, "final": 91}, 860, "B+"),  # 2579/30, about 85.9667
    ({"quizzes": [98], "homework": [{"score": 98, "days_late": 1}], "midterm": 89, "final": 77}, 860, "B+"),  # exactly 85.95
    ({"quizzes": [82, 97, 74], "homework": [{"score": 89, "days_late": 0}, {"score": 74, "days_late": 0}, {"score": 81, "days_late": 3}], "midterm": 95, "final": 87}, 859, "B"),  # 1289/15, about 85.9333
    ({"quizzes": [80, 71, 88], "homework": [{"score": 79, "days_late": 0}, {"score": 93, "days_late": 2}], "midterm": 99, "final": 84}, 859, "B"),  # exactly 85.925
    ({"quizzes": [97], "homework": [{"score": 92, "days_late": 0}], "midterm": 87, "final": 76}, 859, "B"),  # exactly 85.9
    ({"quizzes": [62, 63, 71, 60], "homework": [{"score": 70, "days_late": 0}, {"score": 98, "days_late": 0}, {"score": 86, "days_late": 1}], "midterm": 80, "final": 85}, 800, "B"),  # exactly 80.0
    ({"quizzes": [100, 78, 89], "homework": [{"score": 87, "days_late": 0}, {"score": 87, "days_late": 0}, {"score": 71, "days_late": 3}], "midterm": 85, "final": 74}, 800, "B"),  # 2399/30, about 79.9667
    ({"quizzes": [74, 77, 75, 73], "homework": [{"score": 88, "days_late": 0}, {"score": 70, "days_late": 0}], "midterm": 78, "final": 84}, 800, "B"),  # exactly 79.95
    ({"quizzes": [56, 86, 76], "homework": [{"score": 89, "days_late": 3}, {"score": 77, "days_late": 0}, {"score": 83, "days_late": 1}], "midterm": 85, "final": 82}, 799, "C+"),  # 1199/15, about 79.9333
    ({"quizzes": [89, 60], "homework": [{"score": 72, "days_late": 0}, {"score": 94, "days_late": 1}], "midterm": 62, "final": 90}, 799, "C+"),  # exactly 79.925
    ({"quizzes": [100, 94, 94, 95], "homework": [{"score": 98, "days_late": 0}, {"score": 70, "days_late": 5}], "midterm": 91, "final": 87}, 799, "C+"),  # exactly 79.9
    ({"quizzes": [100], "homework": [{"score": 53, "days_late": 0}], "midterm": 100, "final": 65}, 760, "C+"),  # exactly 76.0
    ({"quizzes": [76, 86, 73], "homework": [{"score": 74, "days_late": 0}, {"score": 81, "days_late": 0}, {"score": 78, "days_late": 0}], "midterm": 74, "final": 74}, 760, "C+"),  # 2279/30, about 75.9667
    ({"quizzes": [88], "homework": [{"score": 70, "days_late": 1}, {"score": 78, "days_late": 3}], "midterm": 90, "final": 73}, 760, "C+"),  # exactly 75.95
    ({"quizzes": [85, 93, 96, 73], "homework": [{"score": 86, "days_late": 0}, {"score": 70, "days_late": 2}, {"score": 66, "days_late": 1}], "midterm": 60, "final": 87}, 759, "C"),  # 1139/15, about 75.9333
    ({"quizzes": [86], "homework": [{"score": 95, "days_late": 0}, {"score": 94, "days_late": 0}], "midterm": 40, "final": 84}, 759, "C"),  # exactly 75.925
    ({"quizzes": [88], "homework": [{"score": 91, "days_late": 5}, {"score": 62, "days_late": 2}, {"score": 86, "days_late": 0}], "midterm": 88, "final": 84}, 759, "C"),  # exactly 75.9
    ({"quizzes": [98, 81], "homework": [{"score": 55, "days_late": 0}], "midterm": 50, "final": 83}, 700, "C"),  # exactly 70.0
    ({"quizzes": [61], "homework": [{"score": 65, "days_late": 1}, {"score": 95, "days_late": 1}, {"score": 74, "days_late": 0}], "midterm": 74, "final": 69}, 700, "C"),  # 2099/30, about 69.9667
    ({"quizzes": [54], "homework": [{"score": 70, "days_late": 3}, {"score": 71, "days_late": 0}, {"score": 81, "days_late": 0}], "midterm": 88, "final": 66}, 700, "C"),  # exactly 69.95
    ({"quizzes": [57], "homework": [{"score": 80, "days_late": 0}, {"score": 93, "days_late": 0}, {"score": 92, "days_late": 0}], "midterm": 62, "final": 68}, 699, "D"),  # 1049/15, about 69.9333
    ({"quizzes": [63, 69], "homework": [{"score": 65, "days_late": 1}, {"score": 66, "days_late": 0}, {"score": 76, "days_late": 5}], "midterm": 68, "final": 92}, 699, "D"),  # exactly 69.925
    ({"quizzes": [92, 89], "homework": [{"score": 44, "days_late": 0}], "midterm": 67, "final": 81}, 699, "D"),  # exactly 69.9
    ({"quizzes": [89, 67, 93, 77], "homework": [{"score": 59, "days_late": 2}], "midterm": 57, "final": 60}, 600, "D"),  # exactly 60.0
    ({"quizzes": [78, 66], "homework": [{"score": 99, "days_late": 0}, {"score": 55, "days_late": 0}, {"score": 100, "days_late": 3}], "midterm": 40, "final": 56}, 600, "D"),  # 1799/30, about 59.9667
    ({"quizzes": [88, 68], "homework": [{"score": 82, "days_late": 5}, {"score": 66, "days_late": 0}], "midterm": 56, "final": 70}, 600, "D"),  # exactly 59.95
    ({"quizzes": [49, 56], "homework": [{"score": 59, "days_late": 2}, {"score": 62, "days_late": 0}, {"score": 68, "days_late": 2}], "midterm": 41, "final": 79}, 599, "F"),  # 899/15, about 59.9333
    ({"quizzes": [48, 51, 81, 70], "homework": [{"score": 98, "days_late": 0}, {"score": 82, "days_late": 1}], "midterm": 49, "final": 46}, 599, "F"),  # exactly 59.925
    ({"quizzes": [61, 69], "homework": [{"score": 86, "days_late": 0}], "midterm": 45, "final": 48}, 599, "F"),  # exactly 59.9
    ({"quizzes": [0], "homework": [{"score": 100, "days_late": 7}], "midterm": 0, "final": 0}, 0, "F"),
]

rng = random.Random(1204)
for _ in range(80):
    r = random_request(rng)
    CASES.append((r, *expected(r)))

problems = []
for r, rounded, want in CASES:
    assert expected(r) == (rounded, want) and letter(rounded) == want, r
    status, body = call(r)
    got = body.get("letter") if isinstance(body, dict) else None
    if status != 0 or got != want:
        problems.append(f"{r}: the percent rounds to {rounded / 10}, so expected letter {want}, got {body!r} (status {status})")

finish(problems, f"letters ok: {len(CASES)} requests")
