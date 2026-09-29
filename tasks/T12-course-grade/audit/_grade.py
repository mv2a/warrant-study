"""Audit oracle for the course grade, written from intent.md alone.

Everything is computed with exact fractions, so the expected percent carries no
floating-point error. Used only to compute expected answers; never imported by
the command under test.
"""

import json
import math
import os
import subprocess
from fractions import Fraction

from _cmd import PATH, call

WEIGHTS = {"quiz": Fraction(15, 100), "homework": Fraction(25, 100),
           "midterm": Fraction(25, 100), "final": Fraction(35, 100)}
LETTERS = ("A", "B+", "B", "C+", "C", "D", "F")
CUTS = ((Fraction(900, 10), "A"), (Fraction(860, 10), "B+"), (Fraction(800, 10), "B"),
        (Fraction(760, 10), "C+"), (Fraction(700, 10), "C"), (Fraction(600, 10), "D"))


def quiz_average(quizzes):
    """G2: drop exactly one lowest score when there are two or more, then take the plain mean."""
    kept = sorted(quizzes)
    if len(kept) >= 2:
        kept = kept[1:]
    return Fraction(sum(kept), len(kept))


def homework_value(score, days_late):
    """G3: 10% of the score per day for 1 to 4 days late, zero from 5 days, full when on time."""
    if days_late <= 0:
        return Fraction(score)
    if days_late <= 4:
        return Fraction(score) * (10 - days_late) / 10
    return Fraction(0)


def homework_average(homework):
    """G3: plain mean of every homework after its penalty; nothing is dropped."""
    return sum(homework_value(h["score"], h["days_late"]) for h in homework) / len(homework)


def exact_percent(request):
    """G1 and C1: the exact, unrounded weighted sum."""
    return (WEIGHTS["quiz"] * quiz_average(request["quizzes"])
            + WEIGHTS["homework"] * homework_average(request["homework"])
            + WEIGHTS["midterm"] * request["midterm"]
            + WEIGHTS["final"] * request["final"])


def round_half_up(value):
    """C1: one decimal place, an exact half rounded up (values here are never negative)."""
    return Fraction(math.floor(value * 10 + Fraction(1, 2)), 10)


def letter_for(rounded):
    """G4: the letter for an already rounded percent."""
    for cut, letter in CUTS:
        if rounded >= cut:
            return letter
    return "F"


def expected(request):
    """(rounded percent as a Fraction, letter) for a valid request."""
    rounded = round_half_up(exact_percent(request))
    return rounded, letter_for(rounded)


def exact_tenths(request):
    """True when the exact course percentage already has at most one decimal place.

    Such a student gets the same answer under any rounding rule and survives floating-point
    noise, so the checks for G1, G2, G3 and the letter bands use only such students and
    leave the rounding itself to the C1 checks (and to the letter check for rounded values).
    """
    return (exact_percent(request) * 10).denominator == 1


def percent_matches(got, want):
    """True when the output percent is a JSON number equal to the rounded percent."""
    if type(got) not in (int, float) or isinstance(got, bool):
        return False
    if isinstance(got, float) and not math.isfinite(got):
        return False
    return got == float(want)


def show(value):
    """Short text for a Fraction percent."""
    return f"{float(value):.1f}"


def raw_call(text, timeout=10):
    """Run the command on raw stdin text; returns (status, stdout, stderr) without stripping."""
    if not os.access(PATH, os.X_OK):
        raise SystemExit("the workspace has no executable named grade")
    try:
        done = subprocess.run([PATH], input=text, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, "", "timed out"
    return done.returncode, done.stdout, done.stderr


def request(quizzes, homework, midterm, final, **extra):
    """Build a request; homework is a list of (score, days_late) pairs."""
    body = {"quizzes": list(quizzes),
            "homework": [{"score": s, "days_late": d} for s, d in homework],
            "midterm": midterm, "final": final}
    body.update(extra)
    return body


def describe(req):
    """Compact one-line description of a request for failure messages."""
    return json.dumps(req, separators=(",", ":"))[:160]


def close(got, want):
    """True when the output percent is a JSON number within 1e-6 of the rounded percent.

    Checks for the goals and scenarios use this looser comparison, so that a percent printed
    with float noise (such as 82.30000000000001) counts against C1 and C3, not against them.
    """
    if type(got) not in (int, float) or isinstance(got, bool):
        return False
    if isinstance(got, float) and not math.isfinite(got):
        return False
    return abs(got - float(want)) < 1e-6


def grade_problem(req, label=None, percent="close", letter=True):
    """Grade one valid request and compare it with the oracle.

    percent is "exact" (the JSON number must equal the rounded percent), "close" (within
    1e-6) or None (not compared); letter says whether the letter is compared.
    Returns a short problem line, or None when the case passes.
    """
    status, body = call(req)
    want_p, want_l = expected(req)
    tag = label or describe(req)
    if status != 0:
        return f"{tag}: exit status {status}, expected 0"
    if not isinstance(body, dict):
        return f"{tag}: output {str(body)[:60]!r} is not a JSON object"
    got_p, got_l = body.get("percent"), body.get("letter")
    ok_p = {"exact": percent_matches, "close": close, None: lambda g, w: True}[percent](got_p, want_p)
    ok_l = (got_l == want_l) if letter else True
    if ok_p and ok_l:
        return None
    wanted = []
    if percent:
        wanted.append(f"percent {show(want_p)}")
    if letter:
        wanted.append(f"letter {want_l}")
    return f"{tag}: expected {' and '.join(wanted)}, got percent {got_p!r} and letter {got_l!r}"
