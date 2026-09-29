"""H7: invalid requests are refused with status 2 and no output, never scored."""

import json

from _cmd import call, finish

GOOD = {"category": "books", "price_cents": 1250, "quantity": 2}


def with_item(**changes):
    item = {**GOOD, **changes}
    return json.dumps({"tier": "silver", "items": [GOOD, item], "bonus_categories": ["books"]})


def without(field):
    item = {k: v for k, v in GOOD.items() if k != field}
    return json.dumps({"tier": "silver", "items": [item]})


def promoted(value):
    return json.dumps({"tier": "gold", "items": [GOOD], "bonus_categories": value})


INVALID = [
    ("empty input", ""),
    ("text that isn't JSON", "twelve dollars of books"),
    ("two JSON objects", '{"tier": "gold", "items": []} {"tier": "gold", "items": []}'),
    ("a list instead of an object", '[{"tier": "gold", "items": []}]'),
    ("a bare string", '"gold"'),
    ("null", "null"),
    ("a missing tier", '{"items": []}'),
    ("an unknown tier", '{"tier": "platinum", "items": []}'),
    ("a capitalised tier", '{"tier": "Gold", "items": []}'),
    ("an empty tier", '{"tier": "", "items": []}'),
    ("a numeric tier", '{"tier": 2, "items": []}'),
    ("a tier given as a list", '{"tier": ["gold"], "items": []}'),
    ("missing items", '{"tier": "gold"}'),
    ("items as one object", '{"tier": "gold", "items": {"category": "books", "price_cents": 100, "quantity": 1}}'),
    ("items of null", '{"tier": "gold", "items": null}'),
    ("an item that is a string", '{"tier": "gold", "items": ["books"]}'),
    ("an item that is a list", '{"tier": "gold", "items": [["books", 100, 1]]}'),
    ("an item without a category", without("category")),
    ("an item without a price", without("price_cents")),
    ("an item without a quantity", without("quantity")),
    ("a numeric category", with_item(category=7)),
    ("an empty category", with_item(category="")),
    ("a null category", with_item(category=None)),
    ("a negative price", with_item(price_cents=-1)),
    ("a fractional price", with_item(price_cents=12.5)),
    ("a price written as text", with_item(price_cents="1250")),
    ("a price of true", with_item(price_cents=True)),
    ("a price of false", with_item(price_cents=False)),
    ("a null price", with_item(price_cents=None)),
    ("a quantity of 0", with_item(quantity=0)),
    ("a negative quantity", with_item(quantity=-2)),
    ("a fractional quantity", with_item(quantity=1.5)),
    ("a quantity written as text", with_item(quantity="2")),
    ("a quantity of true", with_item(quantity=True)),
    ("a whole-number price with a decimal point", with_item(price_cents=1250.0)),
    ("a whole-number quantity with a decimal point", with_item(quantity=2.0)),
    ("a price written with an exponent",
     '{"tier": "gold", "items": [{"category": "books", "price_cents": 1e3, "quantity": 1}]}'),
    ("bonus_categories as a string", promoted("books")),
    ("bonus_categories holding a number", promoted(["books", 1])),
    ("bonus_categories of null", promoted(None)),
    ("bonus_categories as an object", promoted({"books": True})),
]
problems = []
for name, raw in INVALID:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{name}: expected a refusal (status 2, no output), got status {status} and {body!r}")

problems = [p if len(p) <= 220 else p[:217] + "..." for p in problems]
finish(problems, f"refusals ok: {len(INVALID)} invalid requests")
