"""X5 (C2): results round to the nearest step, halfway rounds up, and are written in C2's exact shape."""

import random

from _audit import (KINDS, decimal_text, expected, finish, request, rounded, run_all, short, tie, well_formed)

# (value, from, to, places, wanted), worked out by hand.
HAND = [
    # The two examples written in C2.
    ("5", "mm", "cm", 0, "1"),
    ("125", "mm", "m", 2, "0.13"),
    # Exactly halfway: always up, even where rounding half to even or half down would not go up.
    ("0.5", "m", "m", 0, "1"),
    ("2.5", "g", "g", 0, "3"),
    ("4.5", "l", "l", 0, "5"),
    ("0.0625", "m", "m", 3, "0.063"),
    ("25", "mm", "cm", 0, "3"),
    ("0.75", "in", "mm", 1, "19.1"),              # 19.05 mm
    ("0.5", "lb", "g", 5, "226.79619"),           # 226.796185 g
    ("1", "oz", "g", 8, "28.34952313"),           # 28.349523125 g
    ("1", "floz", "ml", 9, "29.573529563"),       # 29.5735295625 ml
    ("5", "floz", "ml", 9, "147.867647813"),      # 147.8676478125 ml
    ("1", "floz", "l", 12, "0.029573529563"),     # 0.0295735295625 l
    ("0.375", "st", "g", 6, "2381.359943"),       # 2381.3599425 g
    ("1.25", "in", "mm", 0, "32"),                # 31.75 mm
    ("0.0000000000005", "kg", "kg", 12, "0.000000000001"),
    # Halfway with a carry into the next digits.
    ("9.9995", "km", "km", 3, "10.000"),
    ("999.5", "ft", "ft", 0, "1000"),
    ("0.9995", "m", "m", 3, "1.000"),
    ("99.95", "l", "l", 1, "100.0"),
    ("9.5", "m", "m", 0, "10"),
    # Not halfway: to the nearest step, so neither always up nor always down.
    ("0.4999", "m", "m", 0, "0"),
    ("0.5001", "m", "m", 0, "1"),
    ("0.1245", "m", "m", 2, "0.12"),
    ("0.129", "m", "m", 2, "0.13"),
    ("4", "mm", "cm", 0, "0"),
    ("14", "mm", "cm", 0, "1"),
    ("16", "mm", "cm", 0, "2"),
    ("1", "in", "mm", 0, "25"),                   # 25.4 mm
    ("1", "ft", "m", 0, "0"),                     # 0.3048 m
    ("2", "ft", "m", 0, "1"),                     # 0.6096 m
    # The shape of the result: exactly `places` digits after a point, a single leading 0 at most,
    # no point at 0 places, no exponent or separators however large or small.
    ("0", "m", "km", 0, "0"),
    ("0", "m", "km", 3, "0.000"),
    ("0.4", "m", "m", 0, "0"),
    ("1", "mg", "kg", 3, "0.000"),
    ("0.0004", "mg", "t", 12, "0.000000000000"),
    ("500", "ml", "l", 2, "0.50"),
    ("250", "mm", "m", 2, "0.25"),
    ("1.134", "kg", "kg", 4, "1.1340"),
    ("12", "m", "m", 0, "12"),
    ("0.05", "m", "m", 1, "0.1"),
    ("1", "t", "mg", 0, "1000000000"),
    ("1", "m3", "ml", 12, "1000000.000000000000"),
    ("123456789012345678901234567890", "mm", "mm", 0, "123456789012345678901234567890"),
    ("100000000000000000000", "mg", "t", 0, "100000000000"),
    ("1", "mm", "km", 12, "0.000001000000"),
    ("1", "mg", "t", 12, "0.000000001000"),
    ("0.000000000001", "km", "km", 12, "0.000000000001"),
    ("000", "g", "g", 0, "0"),
    ("0.00000", "g", "g", 0, "0"),
    ("007.50", "m", "m", 4, "7.5000"),
    ("0012", "yd", "yd", 2, "12.00"),
]
for v, a, b, p, want in HAND:
    assert expected(v, a, b, p) == want, (v, a, b, p, want, expected(v, a, b, p))
cases = list(HAND)

# Generated amounts whose exact result is exactly halfway between two steps, over random
# pairs of the same kind and every places value: each must round up.
rng = random.Random(91520177)
tables = [list(t) for t in KINDS.values()]
for i in range(104):
    units = rng.choice(tables)
    source, target = rng.choice(units), rng.choice(units)
    places = i % 13
    amount, result = tie(rng, source, target, places)
    value = decimal_text(amount)
    want = rounded(result, places)
    assert want == expected(value, source, target, places)
    cases.append((value, source, target, places, want))

# A sweep of the shape: one amount at every places value, for a unit of each kind.
for places in range(13):
    for value, source, target in (("0.07", "km", "m"), ("3", "oz", "lb"), ("0", "gal", "l"), ("1234567.5", "ml", "ml")):
        cases.append((value, source, target, places, expected(value, source, target, places)))

problems = []
results = run_all([request(v, a, b, p) for v, a, b, p, _ in cases])
for (value, source, target, places, want), (status, body) in zip(cases, results):
    got = body.get("value") if isinstance(body, dict) else None
    label = f"{short(value, 40)} {source} to {target} at {places} places"
    if status != 0:
        problems.append(f"{label}: expected {want!r}, got status {status} and {short(body, 60)}")
    elif not well_formed(got, places):
        problems.append(f"{label}: {short(got, 50)} is not written as C2 requires (expected {want!r})")
    elif got != want:
        problems.append(f"{label}: expected {want!r}, got {short(got, 50)}")

finish(problems, f"rounding ok: {len(HAND)} hand-worked results, 104 exact halfway cases, 52 shape checks")
