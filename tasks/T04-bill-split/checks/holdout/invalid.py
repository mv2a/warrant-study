"""H7: invalid requests are refused with status 2 and no output."""

import json

from _cmd import call, finish

GOOD_DINERS = [{"name": "Zara", "pays": "own"}, {"name": "Omar", "pays": "share"}]
GOOD_ITEMS = [{"diner": "Zara", "price_cents": 1200}, {"diner": "Omar", "price_cents": 800}]


def without(fields):
    """A copy of an object, leaving out the fields set to ... (a missing field)."""
    return {k: v for k, v in fields.items() if v is not ...}


def request(**changes):
    return json.dumps(without({"diners": GOOD_DINERS, "items": GOOD_ITEMS, "tip_percent": 15, **changes}))


def item(**changes):
    return request(items=[GOOD_ITEMS[0], without({**GOOD_ITEMS[1], **changes})])


def diner(**changes):
    return request(diners=[GOOD_DINERS[0], without({**GOOD_DINERS[1], **changes})])


INVALID = [
    ("text that isn't JSON", "Zara and Omar, 20 dollars"),
    ("empty input", ""),
    ("a list instead of an object", "[1200, 800]"),
    ("a JSON string", '"split"'),
    ("a missing diners", request(diners=...)),
    ("a missing items", request(items=...)),
    ("a missing tip_percent", request(tip_percent=...)),
    ("diners as an object", request(diners={"Zara": "own"})),
    ("an empty diners list", request(diners=[])),
    ("items as a number", request(items=2000)),
    ("an empty items list", request(items=[])),
    ("a diner that is a string", request(diners=["Zara", "Omar"])),
    ("a diner that is false", request(diners=[GOOD_DINERS[0], False])),
    ("an item that is a number", request(items=[GOOD_ITEMS[0], 800])),
    ("an item that is true", request(items=[GOOD_ITEMS[0], True])),
    ("a diner without a name", diner(name=...)),
    ("an empty name", diner(name="")),
    ("a name that is a number", diner(name=7)),
    ("a missing pays", diner(pays=...)),
    ('pays of "shared"', diner(pays="shared")),
    ('pays of "OWN"', diner(pays="OWN")),
    ("pays of true", diner(pays=True)),
    ("two diners with the same name", request(diners=[GOOD_DINERS[0], {"name": "Zara", "pays": "share"}])),
    ("a price of 0", item(price_cents=0)),
    ("a negative price", item(price_cents=-800)),
    ("a fractional price", item(price_cents=799.5)),
    ("a price written 800.0", item(price_cents=800.0)),
    ("a price written as text", item(price_cents="800")),
    ("a price of true", item(price_cents=True)),
    ("a missing price", item(price_cents=...)),
    ("an item for an unlisted diner", item(diner="Beth")),
    ("an item whose diner differs only in case", item(diner="omar")),
    ("an item whose diner has a trailing space", item(diner="Omar ")),
    ("an item without a diner", item(diner=...)),
    ("a tip of -1", request(tip_percent=-1)),
    ("a tip of 101", request(tip_percent=101)),
    ("a tip of 12.5", request(tip_percent=12.5)),
    ("a tip written 15.0", request(tip_percent=15.0)),
    ("a tip written as text", request(tip_percent="15")),
    ("a tip of true", request(tip_percent=True)),
    ("a tip of false", request(tip_percent=False)),
    ("a tip of null", request(tip_percent=None)),
]
problems = []
for name, raw in INVALID:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{name}: expected a refusal (status 2, no output), got status {status} and {body!r}")

finish(problems, f"refusals ok: {len(INVALID)} invalid requests")
