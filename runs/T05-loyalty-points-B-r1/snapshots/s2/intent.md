---
owner: loyalty programme lead, home-and-garden retailer
---

# Loyalty points

We run a loyalty programme for our shops. When an order is paid, we turn it into the
points the member earns. Spending more earns more, higher tiers and promoted categories
earn extra, gift cards earn nothing, and no single order may hand out an unlimited number
of bonus points. Points are always whole numbers: every fraction is rounded down.

## Goals

- G1: Every whole dollar of eligible spend earns 1 base point. Eligible spend
  (`eligible_cents`) is `price_cents` times `quantity`, added up over every item that is
  not a gift card. The fraction of a dollar is dropped once, on that order total, not item
  by item: two items at $0.60 earn 1 base point, and $19.99 earns 19.
- G2: The member's tier multiplies the base points: standard x1, silver x1.25, gold x1.5.
  The tier bonus is the multiplied amount rounded down to a whole point, minus the base
  points: a silver member with 7 base points gets a tier bonus of 1, because 8.75 rounds
  down to 8. The multiplier applies to base points only, never to category bonus points.
- G3: Items in the order's promoted categories (`bonus_categories`) earn a category bonus
  of 2 points per whole dollar spent on them. That spend is added up over all eligible
  items whose category is listed, and its fraction of a dollar is dropped once, before
  doubling: $10.99 of promoted items earns 20 bonus points, not 21. Categories are compared
  as exact strings: case matters, every space or other whitespace character matters
  (leading and trailing ones included), and nothing is trimmed or normalized, so an item in
  `"garden"` is not promoted by `"Garden"` or `" garden"`. An item counts once even if its
  category is listed more than once.

## Constraints

- C1: Gift cards earn nothing. An item whose category is exactly the string `"gift_card"`
  is left out of `eligible_cents` and earns no base, tier or category points, even when
  `"gift_card"` is listed as a bonus category. An order of only gift cards earns 0 points.
  The comparison is exact as in G3, so a look-alike such as `"Gift_Card"` or `"gift_card "`
  is an ordinary category.
- C2: Bonus points (the tier bonus plus the category bonus) are capped at 500 per order.
  Base points are never capped, so an order earns its base points plus at most 500.
- C3: Points are computed by a command named `points`. It reads one JSON object on
  standard input with `tier` (`"standard"`, `"silver"` or `"gold"`), `items` (a list,
  possibly empty, of objects with `category`, a non-empty string; `price_cents`, the price
  of one unit as an integer of 0 or more; and `quantity`, an integer of 1 or more) and,
  optionally, `bonus_categories` (a list of strings; leaving it out means none). Other
  fields, in the request or in an item, are ignored. On success it exits with status 0 and
  writes one JSON object with exactly four integer fields: `eligible_cents`,
  `base_points`, `bonus_points` and `total_points`, where `total_points` is `base_points`
  plus `bonus_points`. A refused request exits with status 2 and writes nothing on
  standard output.
- C4: Invalid requests are refused, never scored. That includes input that is not a JSON
  object; a missing tier, or one that is not exactly one of the three names; missing
  `items`, or `items` that is not a list; an item that is not an object or lacks one of
  its three fields; a category that is not a non-empty string; a price that is negative,
  fractional, text or true/false; a quantity below 1, fractional, text or true/false; a
  price or quantity written as a JSON number with a decimal point or an exponent, such as
  `100.0` or `1e2`, even when its value is a whole number; and `bonus_categories` that is
  present but not a list of strings.

## Scenarios

- S1: A gold member buys two $25.50 grocery items and a $50.00 gift card, with nothing
  promoted. The request
  `{"tier": "gold", "items": [{"category": "grocery", "price_cents": 2550, "quantity": 2}, {"category": "gift_card", "price_cents": 5000, "quantity": 1}]}`
  gets `{"eligible_cents": 5100, "base_points": 51, "bonus_points": 25, "total_points": 76}`:
  51 x 1.5 = 76.5 rounds down to 76.
- S2: A silver member buys three $10.99 garden items and one $4.50 grocery item while
  garden is promoted. The request
  `{"tier": "silver", "items": [{"category": "garden", "price_cents": 1099, "quantity": 3}, {"category": "grocery", "price_cents": 450, "quantity": 1}], "bonus_categories": ["garden"]}`
  gets `{"eligible_cents": 3747, "base_points": 37, "bonus_points": 73, "total_points": 110}`:
  a tier bonus of 9 plus a category bonus of 64 for $32.97 of garden items.
- S3: A standard member buys a $349.99 television while electronics is promoted. The
  request
  `{"tier": "standard", "items": [{"category": "electronics", "price_cents": 34999, "quantity": 1}], "bonus_categories": ["electronics"]}`
  gets `{"eligible_cents": 34999, "base_points": 349, "bonus_points": 500, "total_points": 849}`:
  the 698 category bonus points are capped at 500.

## Out of scope

- Redeeming, expiring or refunding points, returns, taxes, and currencies other than US
  dollars.
