"""X9 (G3): 45 generated names of mixed-case words with letters from several alphabets,
digits, hyphens, apostrophes, full stops and other punctuation, fixed seed.

Names here have no leading honorific, no particle and single spaces, so only G3 decides
the display name, which must match the audit model exactly."""

from _audit import display_of, show
from _cmd import finish
from _model import PARTICLES, check_alphabet, is_honorific, is_letter, new_rng, normalise

LOWER = "abcdefghijklmnopqrstuvwxyz\xe9\xe8\xfc\xf6\xf1\xe5\xf8\u0142\xe6\xe7\u017e\u0151\u0434\u044f\u0451\xf0\xfe"
LETTERS = LOWER + LOWER.upper() + "\u4e2d\u3055"
BREAKS = "-'\u2019."
OTHER = "0123456789\u2018\u2013_/()\xb7"
check_alphabet(LETTERS + BREAKS + OTHER)


def word(rng):
    chars = []
    for _ in range(rng.randint(1, 9)):
        roll = rng.random()
        chars.append(rng.choice(LETTERS) if roll < 0.72 else rng.choice(BREAKS) if roll < 0.9 else rng.choice(OTHER))
    return "".join(chars)


rng = new_rng(60613)
names = []
while len(names) < 45:
    words = [word(rng) for _ in range(rng.randint(1, 4))]
    if any(w.lower() in PARTICLES for w in words) or is_honorific(words[0]):
        continue
    if not any(is_letter(ch) for w in words for ch in w):
        continue
    names.append(" ".join(words))

problems = []
for name in names:
    expected = normalise(name)["display"]
    display, error = display_of(name)
    if error:
        problems.append(f"{show(name)}: expected {show(expected)}, got {error}")
    elif display != expected:
        problems.append(f"{show(name)}: expected {show(expected)}, got {show(display)}")

finish(problems, f"generated capitalisation ok: {len(names)} names")
