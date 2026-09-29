"""X7 (C4): malformed requests are refused, never converted, and the forms C4 allows are accepted."""

import json

from _audit import check_conversions, finish, refused, short

BASE = {"value": "4.5", "from": "yd", "to": "m", "places": 2}


def but(**changes):
    body = dict(BASE)
    body.update(changes)
    return body


def without(field):
    return {k: v for k, v in BASE.items() if k != field}


GOOD = json.dumps(BASE)

# Input that is not one JSON object.
NOT_OBJECT = [
    "",
    "   \n",
    "null",
    "[]",
    "[" + GOOD + "]",
    json.dumps(GOOD),
    "42",
    "true",
    "value=4.5&from=yd&to=m&places=2",
    "{'value': '4.5', 'from': 'yd', 'to': 'm', 'places': 2}",
    GOOD[:-1] + ",}",
    GOOD[:-1],
    GOOD + GOOD,
    GOOD + " x",
    "{value: \"4.5\", from: \"yd\", to: \"m\", places: 2}",
]

# A missing field, a field other than the four, or a field name in the wrong case.
FIELDS = [
    {},
    without("value"),
    without("from"),
    without("to"),
    without("places"),
    but(extra=1),
    but(unit="m"),
    but(dimension="length"),
    but(note=None),
    but(Value="4.5"),
    but(**{"": ""}),
    {"Value": "4.5", "from": "yd", "to": "m", "places": 2},
    {"value": "4.5", "FROM": "yd", "to": "m", "places": 2},
    {"value": "4.5", "from": "yd", "To": "m", "places": 2},
    {"value": "4.5", "from": "yd", "to": "m", "Places": 2},
    {"value": "4.5", "from": "yd", "to": "m", "precision": 2},
]

# A value that is not a string of ASCII digits, optionally with a point and more digits.
BAD_VALUES = [
    5, 4.5, 0, None, True, False, [], ["4.5"], {"amount": "4.5"},
    "", "-1", "+1", "1e3", "1E3", ".5", "5.", " 5", "5 ", "5\n", "12.5\n", "\t5", "1,5", "1/2",
    "1 000", "1_000", "1_0.5", "1.2.3", "1..2", ".", "..", "-0", "+0", "0x1F", "inf", "Infinity",
    "NaN", "nan", "½", "٥", "５", "²", "\U0001d7d3", "1.٥", "١٢",
    "12a", "a12", "1.5e0", "1.-5", "−1", "1.5.", "1 .5", "4.5 yd", "0b101", "1 000",
]

# A from or to that is not a string.
BAD_UNITS = [
    but(**{"from": 1}), but(**{"from": None}), but(**{"from": True}), but(**{"from": ["yd"]}),
    but(**{"from": {"unit": "yd"}}), but(to=1000), but(to=None), but(to=["m"]), but(to=False),
]

# A places that is not written as a JSON integer from 0 to 12.
BAD_PLACES = [13, 14, 100, 10 ** 20, -1, -12, 2.5, 2.0, 0.0, 12.0, "2", "0", True, False, None, [2], {"n": 2}]
RAW_PLACES = ["1e1", "2E0", "2.00", "1.2e1", "NaN", "Infinity", "-Infinity", "0x2", "02"]

items = list(NOT_OBJECT) + FIELDS + [but(value=v) for v in BAD_VALUES] + BAD_UNITS
items += [but(places=p) for p in BAD_PLACES]
items += [GOOD.replace('"places": 2', '"places": ' + text) for text in RAW_PLACES]
assert GOOD.endswith('"places": 2}') and all(item != GOOD for item in items[-len(RAW_PLACES):])
problems = refused(items)

# Forms C4 allows are converted, not refused: leading zeros, zero itself, places 0 and 12.
ACCEPTED = [
    ("0", "m", "cm", 0, "0"),
    ("007.50", "m", "cm", 1, "750.0"),
    ("000", "kg", "g", 0, "0"),
    ("00.000", "l", "ml", 2, "0.00"),
    ("0.0", "gal", "qt", 0, "0"),
    ("0012", "ft", "in", 0, "144"),
    ("1.0000", "yd", "ft", 0, "3"),
    ("1", "lb", "oz", 12, "16.000000000000"),
    ("1.5", "st", "lb", 0, "21"),
    ("0.000000000001", "m", "mm", 12, "0.000000001000"),
    ("4.5", "yd", "m", 2, "4.11"),
]
problems += check_conversions(ACCEPTED)

finish(problems, f"malformed ok: {len(items)} malformed requests refused, {len(ACCEPTED)} allowed forms accepted")
