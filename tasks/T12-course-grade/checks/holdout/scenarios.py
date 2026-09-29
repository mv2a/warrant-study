"""H8: the students described in the intent's scenarios get exactly the stated percent and letter."""

from _cmd import call, finish

SCENARIOS = [
    (
        "S1",
        {
            "quizzes": [70, 85, 90, 40],
            "homework": [
                {"score": 90, "days_late": 0},
                {"score": 80, "days_late": 2},
                {"score": 100, "days_late": 0},
            ],
            "midterm": 78,
            "final": 84,
        },
        82.3,
        "B",
    ),
    (
        "S2",
        {"quizzes": [85, 62], "homework": [{"score": 88, "days_late": 0}], "midterm": 92, "final": 92},
        90.0,
        "A",
    ),
    (
        "S3",
        {
            "quizzes": [64],
            "homework": [
                {"score": 100, "days_late": 5},
                {"score": 90, "days_late": 3},
                {"score": 75, "days_late": 0},
            ],
            "midterm": 71,
            "final": 69,
        },
        63.0,
        "D",
    ),
]
problems = []
for scenario, request, percent, letter in SCENARIOS:
    status, body = call(request)
    got = (body.get("percent"), body.get("letter")) if isinstance(body, dict) else (None, None)
    number_ok = type(got[0]) in (int, float) and abs(got[0] - percent) < 1e-9
    if status != 0 or not number_ok or got[1] != letter:
        problems.append(f"{scenario}: expected percent {percent} and letter {letter}, got {got!r} (status {status})")

finish(problems, "scenarios ok: S1, S2, S3")
