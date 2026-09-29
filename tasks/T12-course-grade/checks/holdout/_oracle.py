"""Exact grading rules from intent.md, for the hidden checks. Not a check itself."""

from fractions import Fraction

LETTERS = (("A", 900), ("B+", 860), ("B", 800), ("C+", 760), ("C", 700), ("D", 600))


def exact_percent(request):
    """The unrounded course percentage, as a Fraction (G1, G2, G3)."""
    quizzes = list(request["quizzes"])
    if len(quizzes) > 1:
        quizzes.remove(min(quizzes))  # one copy only, even when tied
    quiz = Fraction(sum(quizzes), len(quizzes))
    kept = []
    for item in request["homework"]:
        late = item["days_late"]
        kept.append(Fraction(0) if late >= 5 else Fraction(item["score"]) * Fraction(10 - late, 10))
    homework = sum(kept, Fraction(0)) / len(kept)
    return (15 * quiz + 25 * homework + 25 * Fraction(request["midterm"]) + 35 * Fraction(request["final"])) / 100


def tenths(percent):
    """Round a non-negative Fraction to a whole number of tenths, exact halves up (C1)."""
    scaled = percent * 10
    return (2 * scaled.numerator + scaled.denominator) // (2 * scaled.denominator)


def letter(tenths_value):
    """The letter for a rounded percentage given in tenths (G4)."""
    for name, lowest in LETTERS:
        if tenths_value >= lowest:
            return name
    return "F"


def expected(request):
    """(rounded percent in tenths, letter) for a valid request."""
    rounded = tenths(exact_percent(request))
    return rounded, letter(rounded)


def percent_tenths(body):
    """The returned percent as a whole number of tenths, or None if it is missing or not such a number."""
    value = body.get("percent") if isinstance(body, dict) else None
    if type(value) not in (int, float):
        return None
    scaled = round(value * 10)
    return scaled if abs(value * 10 - scaled) < 1e-6 else None


def show(tenths_value):
    return "None" if tenths_value is None else f"{tenths_value // 10}.{tenths_value % 10}"


def random_request(rng, max_quizzes=8, max_homework=6):
    """A valid request with plenty of ties, late work and spread-out scores."""
    def score():
        style = rng.random()
        if style < 0.1:
            return rng.choice((0, 100))
        if style < 0.4:
            return rng.choice((40, 55, 60, 72, 85, 90))  # a small pool, so ties are common
        return rng.randint(0, 100)

    def days_late():
        style = rng.random()
        if style < 0.5:
            return 0
        if style < 0.85:
            return rng.randint(1, 4)
        if style < 0.97:
            return rng.randint(5, 12)
        return rng.randint(13, 400)

    return {
        "quizzes": [score() for _ in range(rng.randint(1, max_quizzes))],
        "homework": [{"score": score(), "days_late": days_late()} for _ in range(rng.randint(1, max_homework))],
        "midterm": score(),
        "final": score(),
    }
