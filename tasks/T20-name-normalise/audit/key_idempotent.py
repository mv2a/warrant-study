"""X16 (G5): for 20 generated names, fixed seed, the key matches the audit model and
normalising the returned display name again gives the same key.

Names have no honorifics and single spaces; key_groups.py covers those differences."""

from _audit import ask, is_result, show
from _cmd import finish
from _model import FAMILY, GIVEN, PARTICLES, accent, new_rng, normalise, rand_case

KEEP = "\xf8\u0142\xe6\xdf\u0434\xf0"  # letters that NFKD leaves alone


def word(rng):
    w = rand_case(rng, rng.choice(GIVEN + FAMILY))
    w = "".join(accent(rng, ch) if rng.random() < 0.25 else ch for ch in w)
    if rng.random() < 0.3:
        i = rng.randint(1, len(w) - 1)
        w = w[:i] + rng.choice(KEEP) + w[i:]                          # never first, never after - ' \u2019 .
    if rng.random() < 0.2:
        w = w + rng.choice("-'\u2019") + rand_case(rng, rng.choice(GIVEN))
    return w


rng = new_rng(24683)
names = []
while len(names) < 20:
    parts = []
    for _ in range(rng.randint(1, 4)):
        parts.append(rand_case(rng, rng.choice(PARTICLES)) if rng.random() < 0.2 else word(rng))
    name = " ".join(parts)
    if len(name) <= 100:
        names.append(name)

problems = []
for name in names:
    expected = normalise(name)["key"]
    status, body = ask(name)
    if status != 0 or not is_result(body):
        problems.append(f"{show(name)}: expected key {show(expected)}, got status {status} and {body!r}"[:200])
        continue
    if body["key"] != expected:
        problems.append(f"{show(name)}: expected key {show(expected)}, got {show(body['key'])}")
        continue
    status, again = ask(body["display"])
    if status != 0 or not is_result(again) or again["key"] != body["key"]:
        problems.append(f"display {show(body['display'])}: normalising it again should give key {show(body['key'])}, got status {status} and {again!r}"[:200])

finish(problems, f"key stability ok: {len(names)} names normalised twice")
