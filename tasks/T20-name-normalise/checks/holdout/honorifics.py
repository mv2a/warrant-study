"""H2 (G2): every listed honorific is removed from the start, however it is written,
several in a row are all removed, and the same words later in the name are kept."""

import random

from _cmd import call, finish
from _names import HONORIFICS, WORDS, cap, recase

cases = []
# Every honorific in three casings, with and without a full stop.
for title in HONORIFICS:
    for form in (title.lower(), title.upper(), title):
        for dot in ("", "."):
            cases.append((f"{form}{dot} anna weber", "Anna Weber"))

# Several honorifics in a row, with messy spacing.
rng = random.Random(7720260929)
for _ in range(50):
    titles = [recase(rng, rng.choice(HONORIFICS)) + rng.choice(["", "."]) for _ in range(rng.randint(2, 4))]
    words = [rng.choice(WORDS) for _ in range(rng.randint(1, 3))]
    name = rng.choice(["", " ", "\t"]) + rng.choice([" ", "  ", "\t"]).join(titles + [recase(rng, w) for w in words])
    cases.append((name, " ".join(cap(w) for w in words)))

# Honorific words after the first ordinary word are ordinary words.
cases += [
    ("Anna Dr. Weber", "Anna Dr. Weber"),
    ("anna weber miss", "Anna Weber Miss"),
    ("anna MR. mrs. weber", "Anna Mr. Mrs. Weber"),
    ("Dr. Anna Prof. Weber", "Anna Prof. Weber"),
    ("Sir anna dame", "Anna Dame"),
    ("rev. REV. anna rev", "Anna Rev"),
]
# Words that look like honorifics but are not on the list or not whole.
cases += [
    ("Dr.. Anna Weber", "Dr.. Anna Weber"),
    ("Drs Anna Weber", "Drs Anna Weber"),
    ("Doctor Anna Weber", "Doctor Anna Weber"),
    ("Mister Anna Weber", "Mister Anna Weber"),
    ("Madam Anna Weber", "Madam Anna Weber"),
    ("Mr-Anna Weber", "Mr-Anna Weber"),
    ("mr.anna weber", "Mr.Anna Weber"),
    ("Profe Anna Weber", "Profe Anna Weber"),
    ("Mrs, Anna Weber", "Mrs, Anna Weber"),
]

problems = []
for name, display in cases:
    status, body = call({"name": name})
    got = body.get("display") if isinstance(body, dict) else None
    # Letter case belongs to G3; here only which words survive matters.
    if status != 0 or not isinstance(got, str) or got.lower() != display.lower():
        problems.append(f"{name!r}: expected display {display!r}, got {got!r} (status {status})")

for name in ("Dr. Anna Weber", "PROF DR anna weber", "dame anna weber"):
    status, body = call({"name": name})
    key = body.get("key") if isinstance(body, dict) else None
    if key != "annaweber":
        problems.append(f"{name!r}: the honorific must not reach the key; expected 'annaweber', got {key!r}")

finish(problems, f"honorifics ok: {len(cases) + 3} names")
