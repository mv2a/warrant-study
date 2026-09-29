"""X5 (G1): whitespace is dropped at the ends and every inner run becomes one space.

Only the word structure of the display name is compared, ignoring case, so a
capitalisation fault does not show up here."""

from _audit import display_of, show
from _cmd import finish
from _model import FAMILY, GIVEN, WHITESPACE, new_rng, whitespace_run

problems = []


def expect_words(name, words):
    display, error = display_of(name)
    if error:
        problems.append(f"{show(name)}: expected words {words}, got {error}")
        return
    got = display.split(" ")
    if [w.casefold() for w in got] != [w.casefold() for w in words]:
        problems.append(f"{show(name)}: expected the words {words} joined by single spaces, got {show(display)}")


# Each of the 25 Unicode whitespace characters, at both ends and inside a mixed run.
for ws in WHITESPACE:
    expect_words(f"{ws}{ws}Maren{ws} {ws}Okafor{ws}", ["Maren", "Okafor"])

# Characters that look like spacing but are not whitespace do not split a word.
expect_words("Maren\u200bOkafor Lind", ["Maren\u200bokafor", "Lind"])
expect_words("Maren\u2060Lind", ["Maren\u2060lind"])

# Names of one to five words with random whitespace runs, with a fixed seed.
rng = new_rng(91277)
for _ in range(15):
    words = [w.capitalize() for w in rng.sample(GIVEN + FAMILY, rng.randint(1, 5))]
    name = whitespace_run(rng, 0, 3)
    for i, word in enumerate(words):
        name += word + (whitespace_run(rng, 1, 4) if i < len(words) - 1 else "")
    name += whitespace_run(rng, 0, 3)
    expect_words(name, words)

finish(problems, "whitespace ok: 25 characters, 2 look-alikes, 15 generated names")
