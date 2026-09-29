"""H5 (G5): the key is the display name decomposed (NFKD), lower-cased and stripped of
every character that is not a letter, so spelling variants of one name share a key."""

import random

from _cmd import call, finish
from _names import HONORIFICS, WORDS, recase

FIXED = [
    ("José García", "josegarcia"),
    ("José García", "josegarcia"),
    ("Łukasz Żółć", "łukaszzołc"),
    ("Søren Kierkegaard", "sørenkierkegaard"),
    ("Ærø Hansen", "ærøhansen"),
    ("Johann Strauß", "johannstrauß"),
    ("Олег Петров", "олегпетров"),
    ("Thurston Howell 3rd", "thurstonhowellrd"),
    ("J.R.R. Tolkien", "jrrtolkien"),
    ("J R R Tolkien", "jrrtolkien"),
    ("Anna-Maria O'Neil", "annamariaoneil"),
    ("anna maria o’neil", "annamariaoneil"),
    ("Åsa Öberg", "asaoberg"),
    ("Zoë Müller", "zoemuller"),
    ("François Ñúñez", "francoisnunez"),
    ("Stefﬁ Graf", "steffigraf"),
    ("Ａｎｎａ Weber", "annaweber"),
    ("李小龙", "李小龙"),
    ("Dr. Renée d'Arcy-Smith", "reneedarcysmith"),
]

# One name, many spellings: all must share the key.
GROUP = [
    "Anna-Maria O'Neil", "anna maria oneil", "Dr. ANNA  MARIA O’NEIL",
    "Ánna-María Ó'Néil", "mrs. anna.maria o.neil", "\tANNA-maria o'neil\n",
]

ACCENTS = {"a": "áàâäåã", "e": "éèêë", "i": "íïî",
           "o": "óöôõ", "u": "úüû", "n": "ñ", "c": "ç", "y": "ý"}


def variant(rng, words):
    """A spelling of the same name that differs only in ways the key must ignore."""
    out = []
    for word in words:
        letters = []
        for i, c in enumerate(word):
            if c in ACCENTS and rng.random() < 0.3:
                c = rng.choice(ACCENTS[c])
            if 0 < i and rng.random() < 0.08:
                letters.append(rng.choice(["'", "’", ".", "-"]))
            letters.append(c)
        out.append(recase(rng, "".join(letters)))
    name = out[0]
    for word in out[1:]:
        name += rng.choice([" ", "  ", "-", "\t", " ", ". "]) + word
    if rng.random() < 0.4:
        name = recase(rng, rng.choice(HONORIFICS)) + rng.choice(["", "."]) + " " + name
    return rng.choice(["", " ", "\n"]) + name + rng.choice(["", " ", "\t"])


problems = []
for name, key in FIXED:
    status, body = call({"name": name})
    got = body.get("key") if isinstance(body, dict) else None
    if status != 0 or got != key:
        problems.append(f"{name!r}: expected key {key!r}, got {got!r} (status {status})")

for name in GROUP:
    status, body = call({"name": name})
    got = body.get("key") if isinstance(body, dict) else None
    if got != "annamariaoneil":
        problems.append(f"{name!r}: expected the shared key 'annamariaoneil', got {got!r}")

rng = random.Random(9120260929)
checked = len(FIXED) + len(GROUP)
for _ in range(60):
    words = [rng.choice(WORDS) for _ in range(rng.randint(1, 3))]
    key = "".join(words)
    for _ in range(3):
        name = variant(rng, words)
        status, body = call({"name": name})
        got = body.get("key") if isinstance(body, dict) else None
        checked += 1
        if status != 0 or got != key:
            problems.append(f"{name!r}: expected key {key!r}, got {got!r} (status {status})")

finish(problems, f"keys ok: {checked} names")
