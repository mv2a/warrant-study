"""X10 (G4): each of the eleven particles is lower-cased inside a name and capitalised as
the first or the last word, and runs of particles follow the same rule.

A particle at the start or end is sent in lower case, so the check does not depend on
G3 lower-casing the rest of a word."""

from _audit import display_of, show
from _cmd import finish
from _model import PARTICLES, new_rng, rand_case

problems = []


def expect(name, expected):
    display, error = display_of(name)
    if error:
        problems.append(f"{show(name)}: expected {show(expected)}, got {error}")
    elif display != expected:
        problems.append(f"{show(name)}: expected {show(expected)}, got {show(display)}")


rng = new_rng(1147)
for i, p in enumerate(PARTICLES):
    inner = [p.upper(), p.capitalize(), rand_case(rng, p)][i % 3]
    expect(f"Amara {inner} Castillo", f"Amara {p} Castillo")
    expect(f"{p} Castillo", f"{p.capitalize()} Castillo")
    expect(f"Amara {p}", f"Amara {p.capitalize()}")

expect("amara DE LA cruz", "Amara de la Cruz")
expect("teodor VON DER horst", "Teodor von der Horst")
expect("amara van der DE berg", "Amara van der de Berg")
expect("de la", "De La")
expect("van", "Van")
expect("de la van", "De la Van")
expect("di DA du", "Di da Du")

finish(problems, f"particles ok: {len(PARTICLES)} particles in three positions, 7 runs")
