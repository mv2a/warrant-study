"""X09 (C3): a zone other than 1, 2, 3 or 4, and a weight or side that is not a whole number
greater than zero (zero, negative, fractional, text, true/false, null, a list or an object),
and a whole zone, weight or side written with a decimal point or an exponent (not a JSON integer),
are refused (status 2, no price); the same parcels with valid values, down to 1 g and 1 cm, are
priced. What a refusal writes is C1's business, and the price is G1 to G4's."""

import json

from _audit import check, parcel, priced, refused

GOOD = parcel(3, 2400, 32, 24, 18)

BAD_ZONES = [0, 5, 7, -1, -4, 12, 1000, "1", "2", "zone 3", "", None, True, False, 2.5, 3.25, [2], {"zone": 2}]
BAD_NUMBERS = {  # per field: values that are not a whole number greater than zero
    "weight_g": [0, -1, -2400, 0.5, 2400.5, 999.99, -0.5, "2400", "2.4 kg", "", True, False, None, [2400], {"g": 2400}],
    "length_cm": [0, -1, -32, 0.5, 32.5, 31.9, -0.5, "32", "thirty", "", True, False, None, [32], {"cm": 32}],
    "width_cm": [0, -1, -24, 0.5, 24.5, 23.75, -0.5, "24", "wide", "", True, False, None, [24], {"cm": 24}],
    "height_cm": [0, -1, -18, 0.5, 18.5, 17.1, -0.5, "18", "short", "", True, False, None, [18], {"cm": 18}],
}

cases = [("valid control", GOOD, priced)]
for zone in (1, 2, 3, 4):
    request = {**GOOD, "zone": zone}
    cases.append((f"zone {zone} control", request, priced))
for field in BAD_NUMBERS:  # 1 is the smallest whole number greater than zero, so it is valid
    request = {**GOOD, field: 1}
    cases.append((f"{field} 1 control", request, priced))
tiny = parcel(4, 1, 1, 1, 1)
cases.append(("1 g, 1 x 1 x 1 cm control", tiny, priced))

for zone in BAD_ZONES:
    cases.append((f"zone {zone!r}", {**GOOD, "zone": zone}, refused))
for field, values in BAD_NUMBERS.items():
    for value in values:
        cases.append((f"{field} {value!r}", {**GOOD, field: value}, refused))
# JSON's -0 is zero; NaN and Infinity are not whole numbers (nor strict JSON): refused either way.
cases.append(("weight_g -0", '{"zone": 3, "weight_g": -0, "length_cm": 32, "width_cm": 24, "height_cm": 18}', refused))
cases.append(("weight_g NaN", '{"zone": 3, "weight_g": NaN, "length_cm": 32, "width_cm": 24, "height_cm": 18}', refused))
cases.append(("height_cm Infinity", '{"zone": 3, "weight_g": 2400, "length_cm": 32, "width_cm": 24, "height_cm": Infinity}', refused))
cases.append(("zone -Infinity", '{"zone": -Infinity, "weight_g": 2400, "length_cm": 32, "width_cm": 24, "height_cm": 18}', refused))
# C3: the fields must be JSON integers, so a whole value written with a decimal point or an
# exponent is refused. JSON text is written out by hand, because json.dumps writes 2400.0 for
# every one of these.
def with_literal(field, literal):
    return "{" + ", ".join(f'"{k}": {literal if k == field else json.dumps(v)}' for k, v in GOOD.items()) + "}"


WHOLE_BUT_NOT_INTEGER = {
    "zone": ["3.0", "1.0", "4e0"],
    "weight_g": ["2400.0", "1.0", "2.4e3"],
    "length_cm": ["32.0", "3.2e1"],
    "width_cm": ["24.00", "2.4E1"],
    "height_cm": ["18.0", "1.8e+1"],
}
for field, literals in WHOLE_BUT_NOT_INTEGER.items():
    for literal in literals:
        cases.append((f"{field} {literal}", with_literal(field, literal), refused))
# Two fields wrong at once.
cases.append(("zero weight and zero side", {**GOOD, "weight_g": 0, "width_cm": 0}, refused))
cases.append(("bad zone and fractional side", {**GOOD, "zone": 9, "height_cm": 18.5}, refused))

check(cases, "invalid values refused")
