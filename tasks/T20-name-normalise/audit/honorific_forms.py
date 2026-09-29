"""X6 (G2): each of the ten honorifics is removed from the start in several spellings.

Only the words of the display name are compared, ignoring case."""

from _audit import display_of, show
from _cmd import finish
from _model import HONORIFICS, new_rng, rand_case

problems = []
rng = new_rng(3319)
for word in HONORIFICS:
    mixed = rand_case(rng, word)
    if mixed in (word, word.upper(), word.capitalize()):
        mixed = word[0].lower() + word[1:].upper()
    forms = [word, word.upper() + ".", word.capitalize() + ".", mixed + ("." if len(word) % 2 else "")]
    for form in forms:
        name = f"{form} kofi varga"
        display, error = display_of(name)
        if error:
            problems.append(f"{show(name)}: expected Kofi Varga, got {error}")
        elif [w.casefold() for w in display.split(" ")] != ["kofi", "varga"]:
            problems.append(f"{show(name)}: the honorific should be removed, got {show(display)}")

finish(problems, f"honorific spellings ok: {len(HONORIFICS)} honorifics, 4 spellings each")
