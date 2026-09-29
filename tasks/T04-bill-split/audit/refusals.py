"""X7 (C3): every kind of invalid request the intent lists is refused with status 2 and
nothing on standard output. Each case changes one thing in an otherwise valid request."""

import copy
import json

from _cmd import call, finish

BASE = {
    "diners": [{"name": "Galo", "pays": "own"}, {"name": "Suvi", "pays": "share"}, {"name": "Pim", "pays": "share"}],
    "items": [{"diner": "Galo", "price_cents": 1375}, {"diner": "Suvi", "price_cents": 2240},
              {"diner": "Pim", "price_cents": 95}],
    "tip_percent": 12,
}
DROP = object()


def top(key, value):
    r = copy.deepcopy(BASE)
    if value is DROP:
        del r[key]
    else:
        r[key] = value
    return r


def edit(kind, index, key, value):
    r = copy.deepcopy(BASE)
    if value is DROP:
        del r[kind][index][key]
    else:
        r[kind][index][key] = value
    return r


def extra(kind, element, at=None):
    r = copy.deepcopy(BASE)
    r[kind].insert(len(r[kind]) if at is None else at, element)
    return r


text = json.dumps(BASE)
CASES = [
    # Text that is not JSON, or not a JSON object.
    ("empty input", ""),
    ("blank input", "  \n\t"),
    ("plain words", "split the bill four ways"),
    ("cut-off JSON", text[: len(text) // 2]),
    ("JSON followed by more text", text + " please"),
    ("two JSON objects", text + text),
    ("Python-style quotes", str(BASE)),
    ("NaN tip", text.replace('"tip_percent": 12', '"tip_percent": NaN')),
    ("Infinity price", text.replace('"price_cents": 1375', '"price_cents": Infinity')),
    ("an empty list", "[]"),
    ("the request inside a list", json.dumps([BASE])),
    ("a string", json.dumps("diners")),
    ("a number", "12"),
    ("null", "null"),
    ("true", "true"),
]
CASES += [
    # Missing, non-list or empty diners, items and tip_percent.
    ("no diners", top("diners", DROP)),
    ("no items", top("items", DROP)),
    ("no tip_percent", top("tip_percent", DROP)),
    ("diners is an object", top("diners", {"name": "Galo", "pays": "own"})),
    ("diners is a string", top("diners", "Galo, Suvi, Pim")),
    ("diners is null", top("diners", None)),
    ("diners is a number", top("diners", 3)),
    ("diners is empty", top("diners", [])),
    ("items is an object", top("items", {"diner": "Galo", "price_cents": 1375})),
    ("items is a string", top("items", "risotto")),
    ("items is null", top("items", None)),
    ("items is a number", top("items", 3)),
    ("items is empty", top("items", [])),
    # A diner or an item that is not an object.
    ("a diner that is a string", extra("diners", "Tove")),
    ("a diner that is a list", extra("diners", ["Tove", "own"])),
    ("a diner that is null", extra("diners", None)),
    ("a diner that is a number", extra("diners", 4)),
    ("a diner that is true", extra("diners", True)),
    ("a diner that is false", extra("diners", False, at=0)),
    ("an item that is a string", extra("items", "Galo")),
    ("an item that is a list", extra("items", ["Galo", 100])),
    ("an item that is null", extra("items", None)),
    ("an item that is a number", extra("items", 100)),
    ("an item that is true", extra("items", True, at=1)),
    ("an item that is false", extra("items", False)),
    # Names that are not non-empty strings.
    ("a diner without a name", edit("diners", 1, "name", DROP)),
    ("an empty name", extra("diners", {"name": "", "pays": "share"})),
    ("a null name", extra("diners", {"name": None, "pays": "share"})),
    ("a numeric name", extra("diners", {"name": 7, "pays": "share"})),
    ("a numeric name its item uses", {**extra("items", {"diner": 7, "price_cents": 100}),
                                      "diners": BASE["diners"] + [{"name": 7, "pays": "own"}]}),
    ("a true name", extra("diners", {"name": True, "pays": "share"})),
    ("a list name", extra("diners", {"name": ["Tove"], "pays": "share"})),
    ("an object name", extra("diners", {"name": {"first": "Tove"}, "pays": "share"})),
]
for pays in ["OWN", "Own", "Share", "SHARE", " own", "own ", "share\n", "", "split", "shared", "equal",
             None, True, 1, 0, ["own"], {"own": True}]:
    CASES.append((f"pays {json.dumps(pays)}", extra("diners", {"name": "Tove", "pays": pays})))
CASES += [
    ("a diner without pays", extra("diners", {"name": "Tove"})),
    ("an existing diner's pays changed to Own", edit("diners", 0, "pays", "Own")),
    # Duplicate names, compared exactly.
    ("the same name twice", extra("diners", {"name": "Galo", "pays": "own"})),
    ("the same name with different pays", extra("diners", {"name": "Suvi", "pays": "own"})),
    ("the same name first and last", extra("diners", {"name": "Pim", "pays": "share"}, at=0)),
]
for price in [DROP, 0, -1, -1375, 1.5, 1375.0, 1.0, "1375", "", None, True, False, [1375], {"cents": 1375}]:
    label = "missing" if price is DROP else json.dumps(price)
    CASES.append((f"price_cents {label}", edit("items", 0, "price_cents", price)))
CASES += [
    ("a zero-priced item after valid ones", extra("items", {"diner": "Pim", "price_cents": 0})),
    ("a 100.0 price on a new item", extra("items", {"diner": "Suvi", "price_cents": 100.0})),
    ("a true price on a new item", extra("items", {"diner": "Suvi", "price_cents": True})),
]
for who in ["Stranger", "galo", "GALO", "Galo ", " Galo", "", None, 1, ["Galo"], {"name": "Galo"}, DROP]:
    label = "missing" if who is DROP else json.dumps(who)
    CASES.append((f"item diner {label}", edit("items", 0, "diner", who)))
for tip in [-1, -100, 101, 150, 1000, 10 ** 20, 12.0, 0.0, 100.0, 12.5, "12", "", None, True, False,
            [12], {"percent": 12}]:
    CASES.append((f"tip_percent {json.dumps(tip)}", top("tip_percent", tip)))

problems = []
status, body = call(BASE)
if status != 0:
    problems.append(f"the valid base request was refused (status {status}), so the refusals below prove nothing")
for label, case in CASES:
    status, body = call(raw=case) if isinstance(case, str) else call(case)
    if status != 2 or body is not None:
        problems.append(f"{label}: expected status 2 and no output, got status {status} and {body!r}")

finish(problems, f"refusals ok: {len(CASES)} invalid requests")
