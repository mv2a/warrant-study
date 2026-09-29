---
owner: head of circulation, town library
---

# Library overdue fines

When borrowed items come back late, the circulation desk works out what the borrower's
account owes. Fines should nudge people to bring things back on time without ever
becoming punishing: a short delay on ordinary loans is forgiven, and neither a single
item nor a single account can run up an unlimited bill.

## Goals

- G1: Each charged day costs 25 cents for a book, 100 cents for a DVD and 150 cents for a
  reference item. Before any cap, an item's fine is its number of charged days (the late
  days left after the grace period in G2) times its type's daily rate.
- G2: Books and DVDs have a grace period of 3 days: one returned up to 3 days late owes
  nothing, and one returned later is charged only for the days after the third (6 days
  late means 3 charged days). Reference items have no grace period: every day late is a
  charged day.
- G3: No single item's fine exceeds the cap for its type: 800 cents for a book, 2000 cents
  for a DVD and 1500 cents for a reference item. Once an item reaches its cap, further
  late days add nothing.
- G4: No account owes more than 2500 cents: `total_cents` is the sum of the item fines,
  capped at 2500. The account cap changes only the total. Each item's `fine_cents` is
  still reported after its own item cap and before the account cap, so the item fines
  may add up to more than `total_cents`.

## Constraints

- C1: The fines run as a command named `fine`. It reads one JSON object on standard
  input, `{"items": [...]}`, where each item is an object `{"id": string, "type": string,
  "due_day": integer, "returned_day": integer}`; the list may be empty, and fields other
  than these, at either level, are ignored. On success it writes one JSON object on
  standard output with exactly the fields `items` and `total_cents` (an integer), where
  `items` holds one object per request item, in the request's order, with exactly the
  fields `id` (the request item's id), `days_late` (an integer) and `fine_cents` (an
  integer), and exits with status 0. A refused request writes nothing on standard output,
  gives a short reason on standard error (at most 200 characters, not a traceback), and
  exits with status 2.
- C2: Days are whole day numbers, not calendar dates. An item's `days_late` is its
  `returned_day` minus its `due_day`, but never below zero: an item returned on or before
  its due day is 0 days late and owes nothing, whatever its type.
- C3: A request is refused as a whole, with no fines worked out, when: it is not a JSON
  object; `items` is missing or not a list; an item is not an object or lacks any of its
  four fields; an `id` is not a non-empty string, or two items share an `id`; a `type` is
  not exactly `book`, `dvd` or `reference` (so `DVD` is refused); or a `due_day` or
  `returned_day` is not a JSON integer of 0 or more (so -1, 3.0, 2.5, "7", true, false
  and null are all refused).

## Scenarios

- S1: The request `{"items": [{"id": "b1", "type": "book", "due_day": 10, "returned_day":
  17}]}` gives `{"items": [{"id": "b1", "days_late": 7, "fine_cents": 100}],
  "total_cents": 100}`: 7 days late, of which 4 are charged at 25 cents.
- S2: The request `{"items": [{"id": "r1", "type": "reference", "due_day": 40,
  "returned_day": 42}, {"id": "d1", "type": "dvd", "due_day": 40, "returned_day": 42}]}`
  gives `{"items": [{"id": "r1", "days_late": 2, "fine_cents": 300}, {"id": "d1",
  "days_late": 2, "fine_cents": 0}], "total_cents": 300}`: the reference item has no
  grace period, the DVD is still within its grace period.
- S3: The request `{"items": [{"id": "d7", "type": "dvd", "due_day": 5, "returned_day":
  35}, {"id": "r3", "type": "reference", "due_day": 5, "returned_day": 10}]}` gives
  `{"items": [{"id": "d7", "days_late": 30, "fine_cents": 2000}, {"id": "r3", "days_late":
  5, "fine_cents": 750}], "total_cents": 2500}`: the DVD's 27 charged days (2700 cents)
  stop at its 2000-cent cap, and the account's 2750 cents stop at 2500.

## Out of scope

- Calendar dates, opening hours and holidays, renewals, lost or damaged items, items not
  yet returned, payments, and differences between kinds of borrower.
