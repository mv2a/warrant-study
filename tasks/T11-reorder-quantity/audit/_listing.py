"""Shared by the C2 checks: the response's own amounts must follow the definitions in C2."""

from _model import short


def consistent(label, request, body, problems):
    """C2's definitions, checked against the response's own quantities. Returns the wanted list or None."""
    if not isinstance(body, dict) or not isinstance(body.get("orders"), list):
        problems.append(f"{label}: expected a plan, got {short(body, 100)}")
        return None
    orders = body["orders"]
    skus = [o.get("sku") if isinstance(o, dict) else None for o in orders]
    sent = [p["sku"] for p in request["products"]]
    if skus != sent:
        problems.append(f"{label}: expected each sku listed once in request order {sent}, got {short(skus, 100)}")
        return None
    for o, p in zip(orders, request["products"]):
        if type(o.get("quantity")) is not int or o.get("cost_cents") != o["quantity"] * p["unit_cost_cents"]:
            problems.append(f"{label}: {p['sku']} costs {p['unit_cost_cents']} a unit, so cost_cents must be "
                            f"quantity x {p['unit_cost_cents']}, got {short(o, 90)}")
            return None
    total = sum(o["cost_cents"] for o in orders)
    if body.get("total_cost_cents") != total:
        problems.append(f"{label}: the costs add up to {total}, got total_cost_cents={body.get('total_cost_cents')!r}")
    elif body.get("budget_left_cents") != request["budget_cents"] - total:
        problems.append(f"{label}: budget {request['budget_cents']} minus {total} is {request['budget_cents'] - total}, "
                        f"got budget_left_cents={body.get('budget_left_cents')!r}")
    return [o.get("wanted") for o in orders]
