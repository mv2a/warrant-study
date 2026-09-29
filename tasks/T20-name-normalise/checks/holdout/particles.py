"""H4 (G4): particles are lower case between the first and last word, capitalised at
either end (counted after honorifics are removed), and never inside a hyphenated word."""

import random

from _cmd import call, finish
from _names import PARTICLES, WORDS, cap, recase

cases = []
for particle in PARTICLES:
    for form in (particle, particle.upper(), cap(particle)):
        cases.append((f"anna {form} weber", f"Anna {particle} Weber"))
        cases.append((f"{form} weber", f"{cap(particle)} Weber"))
        cases.append((f"anna {form}", f"Anna {cap(particle)}"))
        cases.append((form, cap(particle)))

cases += [
    ("maria DE LA cruz", "Maria de la Cruz"),
    ("ludwig van der beethoven", "Ludwig van der Beethoven"),
    ("De La Cruz", "De la Cruz"),
    ("anna maria della VALLE weber", "Anna Maria della Valle Weber"),
    ("Dr. van gogh", "Van Gogh"),
    ("mr de la cruz", "De la Cruz"),
    ("Prof. anna van", "Anna Van"),
    ("Dr. Ms. von", "Von"),
    ("anna de la", "Anna de La"),
    ("anna-de-la-cruz", "Anna-De-La-Cruz"),
    ("maria van-dyke weber", "Maria Van-Dyke Weber"),
    ("anna de. weber", "Anna De. Weber"),
    ("anna vanda weber", "Anna Vanda Weber"),
    ("anna dela weber", "Anna Dela Weber"),
    ("anna dei weber", "Anna Dei Weber"),
    ("anna d'la weber", "Anna D'La Weber"),
]

rng = random.Random(5520260929)
for _ in range(120):
    count = rng.randint(2, 6)
    words, expected = [], []
    for index in range(count):
        edge = index in (0, count - 1)
        if rng.random() < 0.45:
            particle = rng.choice(PARTICLES)
            words.append(recase(rng, particle))
            expected.append(cap(particle) if edge else particle)
        else:
            word = rng.choice(WORDS)
            words.append(recase(rng, word))
            expected.append(cap(word))
    prefix = rng.choice(["", "", "Dr. ", "mrs ", "PROF. DR. "])
    cases.append((prefix + " ".join(words), " ".join(expected)))

problems = []
for name, display in cases:
    status, body = call({"name": name})
    got = body.get("display") if isinstance(body, dict) else None
    if status != 0 or got != display:
        problems.append(f"{name!r}: expected display {display!r}, got {got!r} (status {status})")

finish(problems, f"particles ok: {len(cases)} names")
