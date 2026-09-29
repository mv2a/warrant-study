"""X13 to X15 (S1, S2, S3): each scenario's student, exactly as the intent states it.

A scenario promises one answer for one student. Other students (a reordered list, a
different dropped quiz, a late score handed in on time) are the goals' business and are
checked there, so a failure here always means the stated student got the wrong answer.

Usage: python3 scenario.py S1|S2|S3
"""

import sys
from fractions import Fraction

from _cmd import call, finish
from _grade import close, describe, expected, request

SCENARIOS = {
    # S1: the 40 is dropped and the 80 two days late counts as 64: 82.3, B.
    "S1": (82.3, "B", request([70, 85, 90, 40], [(90, 0), (80, 2), (100, 0)], 78, 84)),
    # S2: the 62 is dropped and the exact 89.95 rounds up: 90.0, A.
    "S2": (90.0, "A", request([85, 62], [(88, 0)], 92, 92)),
    # S3: the single quiz is kept and the homework counts 0, 63 and 75: 63.0, D.
    "S3": (63.0, "D", request([64], [(100, 5), (90, 3), (75, 0)], 71, 69)),
}

scenario = sys.argv[1] if len(sys.argv) > 1 else ""
if scenario not in SCENARIOS:
    sys.exit(f"usage: scenario.py {'|'.join(SCENARIOS)}")
percent, letter, req = SCENARIOS[scenario]
assert expected(req) == (Fraction(str(percent)), letter), req  # the audit's oracle agrees with the intent

problems = []
status, body = call(req)
got = (body.get("percent"), body.get("letter")) if isinstance(body, dict) else (None, None)
if status != 0 or not close(got[0], percent) or got[1] != letter:
    problems.append(f"{scenario}: expected percent {percent} and letter {letter}, "
                    f"got {got!r} (status {status}) for {describe(req)}")

finish(problems, f"{scenario} ok: percent {percent} and letter {letter}")
