"""H6 (G5): normalising a display name again gives back the same key (and the same
display name), for messy names mixing every rule."""

import random

from _cmd import call, finish
from _names import HONORIFICS, PARTICLES, WORDS, recase

SEPARATORS = [" ", "  ", "\t", "\n", " ", " \r\n "]
DECOR = ["", "", "", "-", "'", "’", "."]

rng = random.Random(6620260929)
names = ["  prof. DR.  anna-maria   o'neil ", "LUDWIG VAN BEETHOVEN", "Mr José García"]
while len(names) < 150:
    parts = []
    for _ in range(rng.randint(0, 2)):
        parts.append(recase(rng, rng.choice(HONORIFICS)) + rng.choice(["", "."]))
    for _ in range(rng.randint(1, 5)):
        if rng.random() < 0.3:
            parts.append(recase(rng, rng.choice(PARTICLES)))
        else:
            word = rng.choice(WORDS)
            decor = rng.choice(DECOR)
            if decor:
                word += decor + rng.choice(WORDS)
            parts.append(recase(rng, word))
    name = rng.choice(["", " ", "\t"]) + "".join(p + rng.choice(SEPARATORS) for p in parts)
    if len(name) <= 100:
        names.append(name)

problems = []
for name in names:
    status, first = call({"name": name})
    if status != 0 or not isinstance(first, dict):
        problems.append(f"{name!r}: expected a result, got {first!r} (status {status})")
        continue
    status, again = call({"name": first.get("display")})
    if status != 0 or not isinstance(again, dict):
        problems.append(f"{first.get('display')!r}: normalising the display name failed (status {status})")
    elif again.get("key") != first.get("key") or again.get("display") != first.get("display"):
        problems.append(f"{name!r}: first {first}, then {again} when normalised again")

finish(problems, f"stability ok: {len(names)} names normalised twice")
