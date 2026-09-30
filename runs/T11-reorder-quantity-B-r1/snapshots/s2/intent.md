---
owner: the purchasing lead of a small spare-parts warehouse
---

# Reorder quantities

Every evening we decide how many units of each product to reorder from our suppliers.
Each product should hold enough stock to cover demand until a new delivery arrives, plus
a safety margin. Suppliers only sell whole packs, and the evening's orders must fit a
budget, so when money is short the most urgent products are bought first.

## Goals

- G1: Each product is topped up to its target level, which is its daily demand times its
  lead time in days, plus its safety stock. Units on hand and units already on order both
  count toward the target, so the units needed are the target minus the units on hand
  minus the units on order. When that is zero or less, nothing is needed.
- G2: Suppliers sell only whole packs. The units wanted for a product are its units needed
  rounded up to the next multiple of its pack size. A need that is already an exact
  multiple of the pack size is not rounded further, and a product that needs nothing
  wants nothing.
- G3: The orders never cost more than the budget. Products are funded one at a time in
  priority order (G4). Each product gets the largest number of whole packs, up to the
  packs it wants, that the money still left can pay for in full. What it costs comes out
  of the money left, and the rest goes on to the next product, even when an earlier
  product was cut short or got nothing.
- G4: Priority 1 is the most urgent, then 2, and so on; priority numbers need not be
  consecutive. A product with a smaller priority number is always funded before one with
  a larger number, and products with the same priority are funded in the order they
  appear in the request.

## Constraints

- C1: The planner runs as a command named `reorder` that reads one JSON object on standard
  input and writes one JSON object on standard output. The request has `budget_cents`
  (integer) and `products` (a list of objects, each with `sku` (string) and the integers
  `on_hand`, `on_order`, `daily_demand`, `lead_time_days`, `safety_stock`, `pack_size`,
  `unit_cost_cents` and `priority`); other fields are ignored. The response has exactly
  `orders` (a list of objects with exactly `sku` (string) and the integers `wanted`,
  `quantity` and `cost_cents`), `total_cost_cents` and `budget_left_cents` (integers).
  The command exits with status 0 on success. For a refused request it exits with status
  2 and writes nothing on standard output.
- C2: The response lists every product of the request exactly once, in the order of the
  request, whatever its priority and even when it orders nothing. `wanted` is the units
  wanted before the budget is applied (G2), `quantity` is the units actually ordered (G3),
  `cost_cents` is the quantity times the unit cost, `total_cost_cents` is the sum of the
  costs, and `budget_left_cents` is the budget minus that total.
- C3: Invalid requests are refused, never planned. That includes text that is not JSON;
  anything other than a JSON object; a missing `budget_cents` or `products`; `products`
  that is not a list; a product that is not an object or lacks one of its fields; a
  budget, count, cost or priority that is not a JSON integer (2.5, 2.0, "7", null, true
  and false are not); a negative budget, stock on hand, stock on order, daily demand,
  lead time or safety stock; a pack size, unit cost or priority below 1; and a sku that
  is not a string, is empty, or repeats an earlier sku. Two skus are the same only when
  they match exactly, character for character, with upper and lower case counting as
  different characters. An empty product list is valid.

## Scenarios

- S1: With a budget of 100000 cents and one product `BOLT-M6` with 20 on hand, 12 on order,
  a daily demand of 8, a lead time of 5 days, a safety stock of 15, packs of 24 and a unit
  cost of 35 cents at priority 1, the target is 55 and 32 units count toward it, so 23 are
  needed and one pack is bought. The response is
  `{"orders": [{"sku": "BOLT-M6", "wanted": 24, "quantity": 24, "cost_cents": 840}], "total_cost_cents": 840, "budget_left_cents": 99160}`.
- S2: With a budget of 3500 cents, the request lists three products in this order:
  `OF-220` (4 on hand, 0 on order, daily demand 2, lead time 7, safety stock 6, packs of
  10 at 150 cents a unit, priority 2), `GK-110` (10 on hand, 5 on order, daily demand 3,
  lead time 6, safety stock 8, packs of 6 at 100 cents a unit, priority 1) and `HS-300`
  (0 on hand, 0 on order, daily demand 1, lead time 10, safety stock 2, packs of 5 at 400
  cents a unit, priority 3). `GK-110` is funded first and costs 1200, `OF-220` then gets
  one of the two packs it wants for 1500, and the 800 cents left cannot buy a 2000-cent
  pack of `HS-300`. The response is
  `{"orders": [{"sku": "OF-220", "wanted": 20, "quantity": 10, "cost_cents": 1500}, {"sku": "GK-110", "wanted": 12, "quantity": 12, "cost_cents": 1200}, {"sku": "HS-300", "wanted": 15, "quantity": 0, "cost_cents": 0}], "total_cost_cents": 2700, "budget_left_cents": 800}`.
- S3: With a budget of 0 cents, the request lists `WS-40` (30 on hand, 10 on order, daily
  demand 5, lead time 4, safety stock 20, packs of 12 at 90 cents a unit, priority 1),
  which already reaches its target of 40, and `WS-41` (0 on hand, 0 on order, daily demand
  1, lead time 3, safety stock 0, packs of 4 at 250 cents a unit, priority 2), which wants
  one pack that the budget cannot pay for. The response is
  `{"orders": [{"sku": "WS-40", "wanted": 0, "quantity": 0, "cost_cents": 0}, {"sku": "WS-41", "wanted": 4, "quantity": 0, "cost_cents": 0}], "total_cost_cents": 0, "budget_left_cents": 0}`.

## Out of scope

- Forecasting demand, supplier minimum order values, volume discounts, splitting a
  product across several suppliers, and currencies other than whole cents.
