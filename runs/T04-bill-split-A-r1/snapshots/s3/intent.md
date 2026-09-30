---
owner: warrant study, task T04
---

# Splitting a restaurant bill

A table of friends gets one bill and adds a tip. Some of them want to pay only for what
they ordered themselves; the others agree to pool what they ordered and split it equally.
Everyone should tip at the same rate on the food they pay for, the shares must add up to
the bill to the cent, and the odd cents must land on people by a rule anyone can check by
hand.

## Goals

- G1: The subtotal is the sum of every item's price. The tip is `tip_percent` percent of
  the subtotal, rounded to the nearest cent, with an exact half cent rounded up. The total
  is the subtotal plus the tip.
- G2: A diner whose `pays` is `"own"` is charged for exactly the items they ordered and for
  nobody else's: their part of the subtotal is the sum of the prices of their own items.
  An own-payer who ordered nothing pays nothing.
- G3: The diners whose `pays` is `"share"` pool every item that any of them ordered and
  split the pool equally: each sharer's part of the subtotal is the pool divided by the
  number of sharers, whatever that sharer ordered, even nothing.
- G4: Everyone tips at the same rate on their own part: a diner's fair amount is their part
  of the subtotal multiplied by the total and divided by the subtotal. Fair amounts are
  exact and may fall between two whole cents.

## Constraints

- C1: Every diner gets exactly one share, every share is a whole number of cents, zero or
  more, and the shares add up exactly to the total.
- C2: Leftover cents follow one rule. Each diner is first given their fair amount rounded
  down to a whole cent. The cents still missing from the total are then given out one
  each to the diners whose fair amounts have the largest fractional parts (the part below
  one cent); when fractional parts are equal, the diner listed earlier in `diners` gets
  the cent first. So every share is less than one cent away from the diner's fair amount.
- C3: Invalid requests are refused, never split. That includes: text that is not JSON or is
  not a JSON object; a missing `diners`, `items` or `tip_percent`; a `diners` or `items`
  that is not a list or is empty; a diner or an item that is not an object; a diner whose
  `name` is not a non-empty string, or whose `pays` is anything but `"own"` or `"share"`;
  two diners with the same name; an item whose `price_cents` is not a whole number of at
  least 1, or whose `diner` is not exactly the name of a listed diner; and a `tip_percent`
  that is not a whole number from 0 to 100. Names are compared exactly as written, both
  when looking for two diners with the same name and when matching an item's `diner` to a
  listed diner: case, spaces and every other character count, and nothing is trimmed or
  normalized, so an item for `"ana"` or `"Ana "` does not belong to a diner named `"Ana"`.
  True and false are not numbers, and a number written with a decimal point, such as
  15.0, is not a whole number.
- C4: Splitting runs as a command named `split` that reads one JSON object on standard
  input and writes one JSON object on standard output, both as UTF-8 text. The request
  has `diners`, a list of objects with `name` (a string) and `pays` (`"own"` or
  `"share"`); `items`, a list of objects with `diner` (the name of the diner who ordered
  it) and `price_cents` (an integer); and `tip_percent` (an integer). Any other fields are
  ignored. On success the command exits with status 0 and writes exactly four fields:
  `subtotal_cents`, `tip_cents` and `total_cents` (integers) and `shares` (an object that
  maps each diner's name to the integer number of cents they pay). A refused request exits
  with status 2 and writes nothing on standard output.

## Scenarios

- S1: Ana and Ben each pay their own, with a 20% tip. Ana orders items of 1200 and 300
  cents and Ben one of 2500 cents. The request
  `{"diners": [{"name": "Ana", "pays": "own"}, {"name": "Ben", "pays": "own"}], "items": [{"diner": "Ana", "price_cents": 1200}, {"diner": "Ben", "price_cents": 2500}, {"diner": "Ana", "price_cents": 300}], "tip_percent": 20}`
  gets
  `{"subtotal_cents": 4000, "tip_cents": 800, "total_cents": 4800, "shares": {"Ana": 1800, "Ben": 3000}}`.
- S2: Ana, Ben and Cy share everything, with a 10% tip. The tip on 4734 cents is 473.4
  cents, so 473, and the total of 5207 cents leaves two leftover cents after each gets
  1735; the three fractional parts are equal, so Ana and Ben, listed first, get them. The
  request
  `{"diners": [{"name": "Ana", "pays": "share"}, {"name": "Ben", "pays": "share"}, {"name": "Cy", "pays": "share"}], "items": [{"diner": "Ana", "price_cents": 1234}, {"diner": "Ben", "price_cents": 2000}, {"diner": "Cy", "price_cents": 1500}], "tip_percent": 10}`
  gets
  `{"subtotal_cents": 4734, "tip_cents": 473, "total_cents": 5207, "shares": {"Ana": 1736, "Ben": 1736, "Cy": 1735}}`.
- S3: Cy pays his own 2150-cent order; Ana, Ben and Dee share Ana's 1600 and Ben's 900,
  although Dee ordered nothing; the tip is 18%. Cy's fair amount is exactly 2537 cents,
  each sharer's is 983 1/3 cents, and the one leftover cent goes to Ana, the sharer
  listed first. The request
  `{"diners": [{"name": "Ana", "pays": "share"}, {"name": "Ben", "pays": "share"}, {"name": "Cy", "pays": "own"}, {"name": "Dee", "pays": "share"}], "items": [{"diner": "Ana", "price_cents": 1600}, {"diner": "Cy", "price_cents": 2150}, {"diner": "Ben", "price_cents": 900}], "tip_percent": 18}`
  gets
  `{"subtotal_cents": 4650, "tip_cents": 837, "total_cents": 5487, "shares": {"Ana": 984, "Ben": 983, "Cy": 2537, "Dee": 983}}`.

## Out of scope

- Taxes, service charges, discounts, currencies, and items shared by only some of the
  sharers.
