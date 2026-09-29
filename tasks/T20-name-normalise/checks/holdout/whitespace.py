"""H1 (G1): whitespace at the ends is dropped and every inner run becomes one space."""

import random

from _cmd import call, finish
from _names import WORDS, cap

FIXED = [
    ("anna weber", "Anna Weber"),
    ("   anna weber   ", "Anna Weber"),
    ("anna\tweber", "Anna Weber"),
    ("anna\nweber", "Anna Weber"),
    ("anna\r\nweber", "Anna Weber"),
    ("anna\rweber", "Anna Weber"),
    ("anna weber", "Anna Weber"),
    (" anna weber ", "Anna Weber"),
    ("anna \t \n  weber\r", "Anna Weber"),
    ("anna weber", "Anna Weber"),
    ("\tanna\t\tmaria\n\nweber\n", "Anna Maria Weber"),
    ("\n\n  anna  \t", "Anna"),
]
SEPARATORS = [" ", "  ", "   ", "\t", "\n", "\r", "\r\n", " ", " \t ", "  ", "\t\n\r"]
EDGES = ["", "", " ", "  ", "\t", "\n", " \n", " ", "\r\n"]

rng = random.Random(4120260929)
cases = list(FIXED)
for _ in range(150):
    words = [rng.choice(WORDS) for _ in range(rng.randint(1, 4))]
    name = rng.choice(EDGES) + words[0]
    for word in words[1:]:
        name += rng.choice(SEPARATORS) + word
    name += rng.choice(EDGES)
    cases.append((name, " ".join(cap(w) for w in words)))

problems = []
for name, display in cases:
    status, body = call({"name": name})
    got = body.get("display") if isinstance(body, dict) else None
    key = body.get("key") if isinstance(body, dict) else None
    # Letter case belongs to G3; here only the spacing and the key matter.
    if status != 0 or not isinstance(got, str) or got.lower() != display.lower():
        problems.append(f"{name!r}: expected display {display!r}, got {got!r} (status {status})")
    elif key != display.replace(" ", "").lower():
        problems.append(f"{name!r}: expected key {display.replace(' ', '').lower()!r}, got {key!r}")

finish(problems, f"whitespace ok: {len(cases)} names")
