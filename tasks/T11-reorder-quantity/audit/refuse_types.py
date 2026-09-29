"""X16 (C3): a budget, count, cost or priority that is not a JSON integer (fraction, whole-valued fraction, text, null, true, false, list, object) is refused."""

import json

from _cmd import finish
from _model import FIELDS
from _refuse import expect_plan, expect_refusal, good_request

problems = []
expect_plan("the unspoilt request", problems, good_request())


def spoiled_values(good):
    """Values that are not JSON integers, several of them equal to or near the good value."""
    return [("a fraction", good + 0.5), ("a whole-valued fraction", float(good)), ("text", str(good)),
            ("null", None), ("true", True), ("false", False), ("a list", [good]), ("an object", {"value": good})]


for name, value in spoiled_values(60000):
    request = good_request()
    request["budget_cents"] = value
    expect_refusal(f"budget_cents as {name} ({json.dumps(value)})", problems, request)

for position, field in enumerate(FIELDS):
    where = position % 3                      # spoil the first, second or third product in turn
    for name, value in spoiled_values(good_request()["products"][where][field]):
        request = good_request()
        request["products"][where][field] = value
        expect_refusal(f"{field} of product {where + 1} as {name} ({json.dumps(value)})", problems, request)

# Python's json module also reads NaN and Infinity; neither is a JSON integer.
base = json.dumps(good_request())
for token in ("NaN", "Infinity", "-Infinity"):
    expect_refusal(f"budget_cents as {token}", problems, raw=base.replace('"budget_cents": 60000', f'"budget_cents": {token}'))
    expect_refusal(f"pack_size as {token}", problems, raw=base.replace('"pack_size": 8', f'"pack_size": {token}', 1))

finish(problems, "type refusals ok")
