"""H3 (G3): each word is capitalised part by part, where a hyphen, an apostrophe (' or
the typographic one) or a full stop starts a new part, and nothing else does."""

import random

from _cmd import call, finish

FIXED = [
    ("anna-MARIA weber", "Anna-Maria Weber"),
    ("o'neil", "O'Neil"),
    ("O'NEIL", "O'Neil"),
    ("o’neil", "O’Neil"),
    ("D’ANGELO", "D’Angelo"),
    ("d'artagnan", "D'Artagnan"),
    ("j.r.r. tolkien", "J.R.R. Tolkien"),
    ("st.john smythe", "St.John Smythe"),
    ("J.R.R. TOLKIEN", "J.R.R. Tolkien"),
    ("mcdonald", "Mcdonald"),
    ("McDONALD", "Mcdonald"),
    ("MACLEOD", "Macleod"),
    ("thurston howell 3RD", "Thurston Howell 3rd"),
    ("henry 2Nd", "Henry 2nd"),
    ("élodie DUPRÉ", "Élodie Dupré"),
    ("ÅSA ÖBERG", "Åsa Öberg"),
    ("zoË", "Zoë"),
    ("mary-kate o'hara-smith", "Mary-Kate O'Hara-Smith"),
    ("anna--maria", "Anna--Maria"),
    ("-anna", "-Anna"),
    ("anna-", "Anna-"),
    ("'anna", "'Anna"),
    ("a.b.c", "A.B.C"),
    ("anna_maria", "Anna_maria"),
    ("anna/maria", "Anna/maria"),
    ("李 小龙", "李 小龙"),
]

SYLLABLES = ["an", "na", "ma", "ri", "ko", "we", "ber", "lu", "ca", "sen", "dro", "vik",
             "ol", "ga", "él", "ör", "ås", "ña", "ün", "za"]
SEPARATORS = ["-", "'", "’", "."]
NOT_PLAIN = {"da", "de", "del", "della", "der", "di", "du", "la", "le", "van", "von",
             "mr", "mrs", "ms", "miss", "mx", "dr", "prof", "rev", "sir", "dame"}


def random_case(rng, text):
    return "".join(c.upper() if rng.random() < 0.5 else c.lower() for c in text)


rng = random.Random(3320260929)
cases = list(FIXED)
while len(cases) < len(FIXED) + 150:
    words, expected = [], []
    for _ in range(rng.randint(1, 3)):
        parts = ["".join(rng.choice(SYLLABLES) for _ in range(rng.randint(2, 3))) for _ in range(rng.randint(1, 3))]
        seps = [rng.choice(SEPARATORS) for _ in parts[1:]]
        word = parts[0]
        shaped = parts[0][0].upper() + parts[0][1:].lower()
        for sep, part in zip(seps, parts[1:]):
            word += sep + part
            shaped += sep + part[0].upper() + part[1:].lower()
        words.append(random_case(rng, word))
        expected.append(shaped)
    if any(w.lower().rstrip(".") in NOT_PLAIN for w in words):
        continue
    cases.append((" ".join(words), " ".join(expected)))

problems = []
for name, display in cases:
    status, body = call({"name": name})
    got = body.get("display") if isinstance(body, dict) else None
    if status != 0 or got != display:
        problems.append(f"{name!r}: expected display {display!r}, got {got!r} (status {status})")

finish(problems, f"capitals ok: {len(cases)} names")
