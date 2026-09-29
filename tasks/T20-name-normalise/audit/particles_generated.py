"""X13 (G4): 45 generated names of two to six words mixing particles with
ordinary words, fixed seed; the display name must match the audit model exactly.

Ordinary words are already capitalised and words are separated by single spaces, so
whitespace tidying and capitalisation of ordinary words play no part."""

from _audit import display_of, show
from _cmd import finish
from _model import FAMILY, GIVEN, PARTICLES, new_rng, normalise, rand_case

rng = new_rng(80417)
names = []
for _ in range(45):
    size = rng.randint(2, 6)
    words = []
    for i in range(size):
        if rng.random() < 0.5:
            particle = rng.choice(PARTICLES)
            # Inside the name in random case; at either end in lower case, so that only
            # G4's choice between lower case and capitalised is being tested.
            words.append(rand_case(rng, particle) if 0 < i < size - 1 else particle)
        else:
            words.append(rng.choice(GIVEN + FAMILY).capitalize())
    names.append(" ".join(words))

problems = []
for name in names:
    expected = normalise(name)["display"]
    display, error = display_of(name)
    if error:
        problems.append(f"{show(name)}: expected {show(expected)}, got {error}")
    elif display != expected:
        problems.append(f"{show(name)}: expected {show(expected)}, got {show(display)}")

finish(problems, f"generated particles ok: {len(names)} names")
