"""Shared body of the length, mass and volume checks (H1 to H3)."""

import random

from _cmd import call, finish
from _units import KINDS, converted, exact, expected, is_half, random_value


def check_kind(kind, seed, known):
    units = list(KINDS[kind])
    rng = random.Random(seed)
    cases = [(v, s, t, p, want) for v, s, t, p, want in known]
    for source in units:
        for target in units:
            made = 0
            while made < 2:
                value = random_value(rng, 4, 3)
                places = rng.randint(0, 9)
                if is_half(exact(value, source, target), places):
                    continue  # exact halves belong to the rounding check (C2)
                want = expected(value, source, target, places)
                if len(want.replace(".", "").lstrip("0")) > 14:
                    continue  # very long results belong to the exactness check (C1)
                made += 1
                cases.append((value, source, target, places, want))
    problems = []
    for value, source, target, places, want in cases:
        status, got, _ = converted(call, value, source, target, places)
        if status != 0 or got != want:
            problems.append(f"{value} {source} to {target} at {places} places: expected {want!r}, got {got!r} (status {status})")
    finish(problems, f"{kind} ok: {len(cases)} conversions over all {len(units) ** 2} unit pairs")
