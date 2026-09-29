"""X17 (C3): a negative budget, on hand, on order, daily demand, lead time or safety stock is refused, and so is a pack size, unit cost or priority of 0 or less."""

from _cmd import finish
from _refuse import expect_plan, expect_refusal, good_request

problems = []
expect_plan("the unspoilt request", problems, good_request())

for value in (-1, -250, -10 ** 9):
    request = good_request()
    request["budget_cents"] = value
    expect_refusal(f"budget_cents of {value}", problems, request)

NON_NEGATIVE = ("on_hand", "on_order", "daily_demand", "lead_time_days", "safety_stock")
AT_LEAST_ONE = ("pack_size", "unit_cost_cents", "priority")
for position, field in enumerate(NON_NEGATIVE):
    for value in (-1, -37):
        where = (position + value) % 3
        request = good_request()
        request["products"][where][field] = value
        expect_refusal(f"{field} of {value} in product {where + 1}", problems, request)
for position, field in enumerate(AT_LEAST_ONE):
    for value in (0, -1, -900):
        where = (position + value) % 3
        request = good_request()
        request["products"][where][field] = value
        expect_refusal(f"{field} of {value} in product {where + 1}", problems, request)

# A negative value must be refused even when the rest of the request would plan to nothing.
request = {"budget_cents": 0, "products": [{"sku": "RG-1", "on_hand": 500, "on_order": -1, "daily_demand": 0,
                                            "lead_time_days": 0, "safety_stock": 0, "pack_size": 1,
                                            "unit_cost_cents": 1, "priority": 1}]}
expect_refusal("on_order of -1 on a product that needs nothing", problems, request)
request = good_request()
request["products"][2]["safety_stock"] = -1
request["products"][2]["on_hand"] = 0
expect_refusal("safety_stock of -1 on the last product", problems, request)

finish(problems, "range refusals ok")
