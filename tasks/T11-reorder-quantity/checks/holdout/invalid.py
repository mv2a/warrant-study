"""H7 (C3): invalid requests are refused with status 2 and never planned; valid edge cases are accepted."""

import json

from _cmd import call, finish
from _model import FIELDS, product

GOOD = product("V-1", 3, 1, 2, 4, 5, 6, 80, 1)


def with_product(**changes):
    return json.dumps({"budget_cents": 5000, "products": [dict(GOOD, **changes)]})


def without(field):
    return json.dumps({"budget_cents": 5000, "products": [{k: v for k, v in GOOD.items() if k != field}]})


INVALID = [
    ("text that isn't JSON", "reorder the usual"),
    ("empty input", ""),
    ("a list instead of an object", "[5000, []]"),
    ("a JSON string", '"reorder"'),
    ("JSON null", "null"),
    ("a missing budget", json.dumps({"products": [GOOD]})),
    ("a missing product list", json.dumps({"budget_cents": 5000})),
    ("a product list that is an object", json.dumps({"budget_cents": 5000, "products": {"V-1": GOOD}})),
    ("a product list of null", json.dumps({"budget_cents": 5000, "products": None})),
    ("a product that is a list", json.dumps({"budget_cents": 5000, "products": [list(GOOD.values())]})),
    ("a product that is a string", json.dumps({"budget_cents": 5000, "products": ["V-1"]})),
    ("a negative budget", json.dumps({"budget_cents": -1, "products": [GOOD]})),
    ("a fractional budget", json.dumps({"budget_cents": 2.5, "products": [GOOD]})),
    ("a budget of 5000.0", '{"budget_cents": 5000.0, "products": []}'),
    ("a budget written as text", json.dumps({"budget_cents": "5000", "products": [GOOD]})),
    ("a budget of true", json.dumps({"budget_cents": True, "products": [GOOD]})),
    ("a budget of null", json.dumps({"budget_cents": None, "products": []})),
    ("a negative stock on hand", with_product(on_hand=-1)),
    ("a negative stock on order", with_product(on_order=-3)),
    ("a negative daily demand", with_product(daily_demand=-1)),
    ("a negative lead time", with_product(lead_time_days=-2)),
    ("a negative safety stock", with_product(safety_stock=-5)),
    ("a pack size of zero", with_product(pack_size=0)),
    ("a negative pack size", with_product(pack_size=-6)),
    ("a unit cost of zero", with_product(unit_cost_cents=0)),
    ("a priority of zero", with_product(priority=0)),
    ("a negative priority", with_product(priority=-1)),
    ("a fractional stock on hand", with_product(on_hand=2.5)),
    ("a pack size of 6.0", with_product(pack_size=6.0)),
    ("a daily demand written as text", with_product(daily_demand="7")),
    ("a safety stock of true", with_product(safety_stock=True)),
    ("a lead time of false", with_product(lead_time_days=False)),
    ("a pack size of true", with_product(pack_size=True)),
    ("a priority of true", with_product(priority=True)),
    ("a unit cost of null", with_product(unit_cost_cents=None)),
    ("a priority of 1.5", with_product(priority=1.5)),
    ("a sku that is a number", with_product(sku=42)),
    ("an empty sku", with_product(sku="")),
    ("a sku of null", with_product(sku=None)),
    ("a repeated sku", json.dumps({"budget_cents": 5000, "products": [GOOD, dict(GOOD, priority=2)]})),
    ("a bad product after good ones", json.dumps({"budget_cents": 5000, "products": [
        GOOD, dict(GOOD, sku="V-2"), dict(GOOD, sku="V-3", on_order=-1)]})),
] + [(f"a product without {field}", without(field)) for field in ("sku",) + FIELDS]

VALID = [
    ("an empty product list", json.dumps({"budget_cents": 5000, "products": []})),
    ("a budget of zero", json.dumps({"budget_cents": 0, "products": [GOOD]})),
    ("every count at zero and every minimum at one", json.dumps({"budget_cents": 5000, "products": [
        product("V-4", 0, 0, 0, 0, 0, 1, 1, 1)]})),
    ("extra fields", json.dumps({"budget_cents": 5000, "extra": [1, 2], "products": [dict(GOOD, note=None)]})),
    ("very large integers", json.dumps({"budget_cents": 10**15, "products": [
        product("V-5", 10**9, 10**9, 10**6, 10**4, 10**9, 10**3, 10**4, 10**6)]})),
    ("two products sharing a priority", json.dumps({"budget_cents": 5000, "products": [GOOD, dict(GOOD, sku="V-6")]})),
    ("skus that differ only in case", json.dumps({"budget_cents": 5000, "products": [dict(GOOD, sku="ab"), dict(GOOD, sku="AB")]})),
    ("a sku with spaces and accents", json.dumps({"budget_cents": 5000, "products": [dict(GOOD, sku="Joint torique 3/8 é")]})),
]

problems = []
for name, raw in INVALID:
    status, body = call(raw=raw)
    planned = isinstance(body, dict) and "orders" in body
    if status != 2 or planned:
        problems.append(f"{name}: expected a refusal with status 2 and no plan, got status {status} and {body!r}")
for name, raw in VALID:
    status, body = call(raw=raw)
    if status != 0 or not isinstance(body, dict) or "orders" not in body:
        problems.append(f"{name}: a valid request must be planned, got status {status} and {body!r}")

finish(problems, f"validation ok: {len(INVALID)} invalid requests refused and {len(VALID)} valid edge cases accepted")
