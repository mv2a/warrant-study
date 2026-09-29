"""X9 (C2): generated malformed previous numbers (seed 16_7730). Well-formed numbers of the
request's branch are damaged by one to three random edits (a character deleted, inserted,
replaced or swapped, the prefix changed, a part padded or trimmed); every result that the
intent's definition no longer accepts must be refused with status 2."""

import random

from _x import BRANCHES, PREFIX, encode, expect_refusals, finish, well_formed

POOL = "0123456789-" + "ABFGILOPRSXZ" + "abglops" + " _+./:\t\n" + "٤༤４²–"


def mutate(text, rng, prefix):
    kind = rng.randrange(8)
    i = rng.randrange(len(text) + 1)
    if kind == 0 and text:
        return text[: min(i, len(text) - 1)] + text[min(i, len(text) - 1) + 1:]
    if kind == 1:
        return text[:i] + rng.choice(POOL) + text[i:]
    if kind == 2 and text:
        j = min(i, len(text) - 1)
        return text[:j] + rng.choice(POOL) + text[j + 1:]
    if kind == 3 and len(text) > 1:
        j = min(i, len(text) - 2)
        return text[:j] + text[j + 1] + text[j] + text[j + 2:]
    if kind == 4:
        other = rng.choice([q for q in PREFIX.values() if q != prefix])
        return text.replace(prefix, other, 1) if prefix in text else other + text
    if kind == 5:
        return text.replace(prefix, rng.choice([prefix.lower(), prefix.title(), prefix[::-1]]), 1)
    if kind == 6:
        parts = text.split("-")
        k = rng.randrange(len(parts))
        parts[k] = rng.choice(["0", "9", " "]) + parts[k] if rng.random() < 0.5 else parts[k][1:]
        return "-".join(parts)
    return text + rng.choice(POOL)


rng = random.Random(16_7730)
cases = []
while len(cases) < 260:
    branch = rng.choice(BRANCHES)
    prefix = PREFIX[branch]
    dated = rng.randint(2000, 9998)
    year = dated if rng.random() < 0.5 else rng.randint(dated + 1, 9999)
    previous = f"{prefix}-{dated}-{rng.randint(1, 99999):05d}"
    for _ in range(rng.randint(1, 3)):
        previous = mutate(previous, rng, prefix)
    if well_formed(previous, prefix):
        continue  # an edit that happens to give another well-formed number is not a test of C2
    cases.append((f"{branch} {year} previous {previous!r}", {"branch": branch, "year": year, "previous": previous}))

problems = []
n = expect_refusals(problems, [(label, encode(r)) for label, r in cases], "malformed previous number")
finish(problems, f"mutations ok: {n} generated malformed previous numbers refused")
