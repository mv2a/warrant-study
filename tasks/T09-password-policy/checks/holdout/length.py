"""H1 (G1): too_short below 12 characters, too_long above 64, counting code points, not bytes."""

import random

from _cmd import call, finish
from _oracle import random_password, violations_of

UNIT = "Harbor-Lamp-42"  # four classes, no repeats, nothing shared with the usernames below


def ascii_of(n):
    return (UNIT * 10)[:n]


def with_wide(n, wide):
    """n code points: the ASCII pattern with every third character replaced by `wide`."""
    return "".join(wide if i % 3 == 1 else c for i, c in enumerate(ascii_of(n)))


CASES = [(f"{n} ASCII characters", ascii_of(n)) for n in (0, 1, 5, 11, 12, 13, 40, 63, 64, 65, 66, 100, 200)]
for wide, label in (("\u00e9", "e-acute, 2 bytes"), ("\u4e2d", "CJK, 3 bytes"), ("\U0001f600", "emoji, 4 bytes")):
    for n in (11, 12, 64, 65):
        CASES.append((f"{n} code points with {label}", with_wide(n, wide)))
# 11 letters plus one combining accent is 12 code points, even though it shows as 11 glyphs.
CASES.append(("12 code points ending in a combining accent", "Harbor-Lamp" + "\u0301"))
CASES.append(("11 code points of which 5 are emoji", "Ab1" + "\U0001f600x" * 3 + "\U0001f600\U0001f601"))
CASES.append(("65 code points of which 13 are emoji", ("\U0001f600Harb" * 13)[:65]))

rng = random.Random(9101)
for i in range(80):
    CASES.append((f"generated password {i}", random_password(rng, 0, 90)))

problems = []
for name, password in CASES:
    status, body = call({"password": password, "username": "zq", "banned": []})
    got = violations_of(body)
    if status != 0 or got is None:
        problems.append(f"{name}: expected status 0 and a violations list, got status {status} and {body!r}")
        continue
    n = len(password)
    for code, should in (("too_short", n < 12), ("too_long", n > 64)):
        if (code in got) != should:
            verb = "should" if should else "should not"
            problems.append(f"{name} ({n} code points): {verb} break {code}, got {got}")

finish(problems, f"length ok: {len(CASES)} passwords")
