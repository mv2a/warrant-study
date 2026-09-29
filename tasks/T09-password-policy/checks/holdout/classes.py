"""H2 (G2): classes is broken when fewer than three of lowercase, uppercase, digit, symbol appear."""

import itertools
import random

from _cmd import call, finish
from _oracle import DIGIT, LOWER, SYMBOL, UPPER, breaks_classes, violations_of

SAMPLES = {"lower": "harbolmp", "upper": "HARBOLMP", "digit": "4271", "symbol": "-!. "}

CASES = [("the empty password", "")]
# Every combination of classes, each as a 14-character password with no repeats.
for size in range(1, 5):
    for combo in itertools.combinations(("lower", "upper", "digit", "symbol"), size):
        parts = [SAMPLES[k] for k in combo]
        text = "".join(c for group in itertools.zip_longest(*parts, fillvalue="") for c in group)
        text = (text * 4)[:14]
        CASES.append((f"only {'+'.join(combo)}", text))

# Characters outside ASCII letters and digits are symbols, including the space and non-ASCII
# letters and digits.
CASES += [
    ("lowercase, digits and spaces", "harbor lamp 42"),
    ("lowercase, digits and a tab", "harbor\tlamp42"),
    ("lowercase, digits and e-acute", "harborlamp\u00e9x1"),
    ("uppercase, digits and E-acute", "HARBORLAMP\u00c942"),
    ("lowercase and sharp s only", "stra\u00dfenlampe"),
    ("lowercase and Arabic-Indic digits only", "harborlamp\u0663\u0664"),
    ("lowercase, Arabic-Indic and ASCII digits", "harborlamp\u0663\u06647"),
    ("uppercase and fullwidth letters only", "HARBOR\uff41\uff42\uff43LAMP"),
    ("lowercase, digits and Greek capital omega", "harbor\u03a9lamp42"),
    ("lowercase, digits and an emoji", "harborlamp42\U0001f600"),
    ("Greek and Cyrillic letters only", "\u03b1\u03b2\u03b3\u03b4\u0430\u0431\u0432\u0433\u03b5\u03b6\u0434\u0435"),
    ("uppercase, lowercase and Cyrillic only", "Harbor\u0430\u0431Lamp\u0432"),
    ("digits, symbols and an uppercase letter", "4271-!.-42X9"),
]

# Text is judged as given, never Unicode-normalized: a separate combining accent is a symbol
# of its own, a precomposed accented capital is one symbol, and fullwidth forms stay symbols.
CASES += [
    ("uppercase E, a separate combining accent and lowercase", "Éharborlamp"),
    ("precomposed E-acute and lowercase only", "Éharborlamp"),
    ("lowercase with a fullwidth A and a fullwidth one", "harborＡlamp１"),
]

rng = random.Random(9202)
POOLS = {"lower": LOWER, "upper": UPPER, "digit": DIGIT, "symbol": SYMBOL}
for i in range(70):
    chosen = rng.sample(sorted(POOLS), rng.randint(1, 4))
    pool = "".join(POOLS[k] for k in chosen)
    CASES.append((f"generated password {i}", "".join(rng.choice(pool) for _ in range(rng.randint(12, 30)))))

problems = []
for name, password in CASES:
    status, body = call({"password": password, "username": "zq", "banned": []})
    got = violations_of(body)
    if status != 0 or got is None:
        problems.append(f"{name}: expected status 0 and a violations list, got status {status} and {body!r}")
        continue
    should = breaks_classes(password)
    if ("classes" in got) != should:
        verb = "should" if should else "should not"
        problems.append(f"{name} {password!r}: {verb} break classes, got {got}")

finish(problems, f"classes ok: {len(CASES)} passwords")
