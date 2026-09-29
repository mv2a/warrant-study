"""X18 (C3): a sku that is not a string, is empty, or repeats an earlier sku (next to it or further back) is refused."""

import json

from _cmd import finish
from _refuse import expect_plan, expect_refusal, good_product, good_request

problems = []
expect_plan("the unspoilt request", problems, good_request())

for name, value in [("a number", 100), ("a fraction", 1.5), ("null", None), ("true", True), ("false", False),
                    ("a list", ["RF-200"]), ("an object", {"code": "RF-200"}), ("the empty string", "")]:
    for where in (0, 2):
        request = good_request()
        request["products"][where]["sku"] = value
        expect_refusal(f"sku of product {where + 1} as {name} ({json.dumps(value)})", problems, request)

DUPLICATES = [
    ("the same sku twice in a row", ["DP-1", "DP-1"]),
    ("a sku repeated two places later", ["DP-1", "DP-2", "DP-1"]),
    ("a sku repeated at the end of five", ["DP-1", "DP-2", "DP-3", "DP-4", "DP-3"]),
    ("the same sku three times", ["DP-9", "DP-9", "DP-9"]),
]
for name, skus in DUPLICATES:
    products = [good_product(sku, priority=1 + i) for i, sku in enumerate(skus)]
    expect_refusal(name, problems, {"budget_cents": 60000, "products": products})

# Repeats that differ in every other field, and repeats of products that need nothing.
expect_refusal("a repeated sku with different stock and priority", problems, {"budget_cents": 60000, "products": [
    good_product("DP-X", priority=5), good_product("DP-Y"), good_product("DP-X", on_hand=900, pack_size=1, priority=1)]})
expect_refusal("a repeated sku on products that need nothing", problems, {"budget_cents": 0, "products": [
    good_product("DP-Z", on_hand=500), good_product("DP-Z", on_hand=700)]})

finish(problems, "sku refusals ok")
