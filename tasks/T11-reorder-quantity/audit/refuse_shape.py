"""X15 (C3): text that is not JSON, anything but a JSON object, missing budget or products, products that are not a list, and products that are not objects or lack a field are refused."""

import json

from _cmd import finish
from _model import FIELDS
from _refuse import expect_plan, expect_refusal, good_product, good_request

problems = []
expect_plan("the unspoilt request", problems, good_request())
VALID = json.dumps({"budget_cents": 100, "products": []})

NOT_JSON = [
    ("empty input", ""),
    ("only whitespace", "  \n\t \n"),
    ("plain words", "budget 100, no products"),
    ("an unclosed object", '{"budget_cents": 100, "products": ['),
    ("single-quoted keys", "{'budget_cents': 100, 'products': []}"),
    ("a trailing comma", '{"budget_cents": 100, "products": [],}'),
    ("an object followed by more text", VALID + " and more"),
    ("two objects in a row", VALID + "\n" + VALID),
    ("unquoted keys", "{budget_cents: 100, products: []}"),
]
NOT_OBJECT = [
    ("an empty list", "[]"),
    ("a list holding a valid request", "[" + VALID + "]"),
    ("a string", json.dumps(VALID)),
    ("a number", "60000"),
    ("null", "null"),
    ("true", "true"),
    ("a fraction", "3.5"),
]
for name, raw in NOT_JSON + NOT_OBJECT:
    expect_refusal(name, problems, raw=raw)

MISSING = [
    ("no budget_cents", {"products": good_request()["products"]}),
    ("no products", {"budget_cents": 60000}),
    ("an empty object", {}),
    ("budget under another name", {"budget": 60000, "products": good_request()["products"]}),
    ("products under another name", {"budget_cents": 60000, "items": good_request()["products"]}),
]
BAD_LIST = [
    ("products as an object", {"budget_cents": 60000, "products": good_product("RF-1")}),
    ("products as an object of products", {"budget_cents": 60000, "products": {"RF-1": good_product("RF-1")}}),
    ("products as a string", {"budget_cents": 60000, "products": "RF-1"}),
    ("products as null", {"budget_cents": 60000, "products": None}),
    ("products as a number", {"budget_cents": 60000, "products": 3}),
    ("products as false", {"budget_cents": 60000, "products": False}),
]
BAD_ITEM = [
    ("a product that is a number", [good_product("RF-1"), 7]),
    ("a product that is a string", ["RF-1"]),
    ("a product that is a list", [good_product("RF-1"), ["RF-2", 4, 2]]),
    ("a product that is null", [None, good_product("RF-1")]),
    ("a product that is true", [good_product("RF-1"), good_product("RF-2"), True]),
    ("a product that is an empty object", [good_product("RF-1"), {}]),
]
for name, request in MISSING + BAD_LIST:
    expect_refusal(name, problems, request)
for name, products in BAD_ITEM:
    expect_refusal(name, problems, {"budget_cents": 60000, "products": products})

for field in ("sku",) + FIELDS:
    request = good_request()
    del request["products"][1][field]
    expect_refusal(f"the second product without {field}", problems, request)
    request = good_request()
    for p in request["products"]:
        del p[field]
    expect_refusal(f"every product without {field}", problems, request)

finish(problems, "shape refusals ok")
