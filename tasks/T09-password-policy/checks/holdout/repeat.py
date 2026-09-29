"""H4 (G4): repeat is broken by the same character three or more times in a row; case matters."""

import random

from _cmd import call, finish
from _oracle import breaks_repeat, violations_of

# (password, whether it breaks the repeat rule)
CASES = [
    ("Harbor-Lamp-42", False),
    ("Bell-Book-77", False),                 # doubles are allowed
    ("aabbaabbAABB11", False),
    ("Harbor-Laaamp-42", True),
    ("aaaHarbor-Lamp-4", True),              # at the start
    ("Harbor-Lamp-4111", True),              # at the end
    ("Harbor-Laaaaaaaaaamp", True),          # a long run
    ("Harbor-Lamp-aaaa", True),
    ("aAa-Harbor-Lamp-4", False),            # case matters
    ("AaA-Harbor-Lamp-4", False),
    ("aAA-Harbor-Lamp-4", False),
    ("AAa-Harbor-Lamp-4", False),
    ("Harbor-LAMMm-42", False),
    ("Harbor-AAA-Lamp-4", True),
    ("Harbor!!!Lamp-42", True),
    ("Harbor   Lamp-42", True),              # three spaces
    ("Harbor\t\t\tLamp-42", True),
    ("Harbor-L\u00e9\u00e9\u00e9mp-42", True),
    ("Harbor-L\u00e9\u00c9\u00e9mp-42", False),
    ("Harbor-\U0001f600\U0001f600\U0001f600-42", True),
    ("Harbor-\U0001f600\U0001f600-\U0001f600-42", False),
    ("Harbor-L-a-a-a-mp", False),            # not in a row
    ("121212-Harbor-La", False),
    ("Har", False),
    ("zzz", True),
    ("", False),
    # Text is judged as given, never Unicode-normalized.
    ("Harbor-ööö-42", True),               # precomposed o-diaeresis three times
    ("Harbor-ööö-42", False),           # o and a separate diaeresis: no run
    ("Harbor-á́́-42", True),              # three combining accents in a row
    ("Harbor-ｘxｘ-42", False),                   # fullwidth x, x, fullwidth x
]

rng = random.Random(9404)
for i in range(70):
    pool = rng.choice(("aAbB1!", "aA", "xX-", "zZ9 ", "\u00e9\u00c9e"))
    CASES.append(("".join(rng.choice(pool) for _ in range(rng.randint(3, 18))), None))

problems = []
for password, should in CASES:
    if should is None:
        should = breaks_repeat(password)
    status, body = call({"password": password, "username": "zq", "banned": []})
    got = violations_of(body)
    if status != 0 or got is None:
        problems.append(f"{password!r}: expected status 0 and a violations list, got status {status} and {body!r}")
    elif ("repeat" in got) != should:
        verb = "should" if should else "should not"
        problems.append(f"{password!r}: {verb} break repeat, got {got}")

finish(problems, f"repeat ok: {len(CASES)} passwords")
