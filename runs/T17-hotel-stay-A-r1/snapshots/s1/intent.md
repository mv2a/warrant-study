---
owner: revenue manager, a small city-centre hotel
---

# Hotel stay pricing

Before a guest books, we quote the price of their stay. A stay is a check-in weekday and a
number of nights at one nightly rate. Weekend nights cost more, long stays are rewarded,
the city's tourist tax is passed on exactly, and short stays over a Saturday are not sold,
because they block the busiest night of the week.

## Goals

- G1: Friday and Saturday nights cost the nightly rate plus a 25% weekend surcharge; every
  other night costs the nightly rate. Each night is named by the weekday on which it
  begins: the first night falls on the check-in day, the next on the following day, and so
  on through as many weeks as the stay lasts. The room charge is the sum of the nightly
  prices.
- G2: Stays of 7 to 13 nights get 10% off the room charge, and stays of 14 nights or more
  get 15% off. Shorter stays get no discount. The discount is taken from the whole room
  charge, weekend surcharges included.
- G3: The city tax is $2.75 for each of the first 10 nights of a stay; nights after the
  tenth carry no city tax. The city tax is never discounted.
- G4: A stay that includes a Saturday night must be at least 3 nights long. A shorter stay
  that includes a Saturday night is refused. A stay without a Saturday night may be as
  short as one night.

## Constraints

- C1: Pricing runs as a command named `stay`. It reads one JSON object on standard input
  with the fields `check_in` (a string naming the weekday of the first night: `mon`,
  `tue`, `wed`, `thu`, `fri`, `sat` or `sun`), `nights` (an integer from 1 to 30) and
  `rate_cents` (an integer, the nightly rate in cents, at least 1); any other fields are
  ignored. On success it writes one JSON object on standard output with exactly the
  integer fields `room_cents`, `discount_cents`, `tax_cents` and `total_cents`, and exits
  with status 0. A refused request writes nothing on standard output, says why on standard
  error, and exits with status 2.
- C2: Money is counted in whole cents. The weekend surcharge is worked out night by night:
  25% of the nightly rate, rounded to the nearest cent, with an exact half cent rounded
  up. The length-of-stay discount is rounded down to a whole cent. The total is the room
  charge minus the discount plus the city tax.
- C3: Invalid requests are refused, never priced. That includes input that is not a JSON
  object, a missing field, a check-in day other than the seven lowercase names above (so
  `Fri` and `friday` are refused), a night count or rate that is not a JSON integer
  (`true`, `2.5`, `2.0` and `"3"` are all refused), fewer than 1 or more than 30 nights,
  and a rate below 1 cent. Input that is not valid UTF-8 text is refused the same way,
  whatever the locale of the system running the command, and so is input with anything
  other than spaces, tabs or line breaks after the JSON object.

## Scenarios

- S1: `{"check_in": "wed", "nights": 2, "rate_cents": 12000}` is priced
  `{"room_cents": 24000, "discount_cents": 0, "tax_cents": 550, "total_cents": 24550}`:
  two weekday nights at $120.00, plus $5.50 city tax.
- S2: `{"check_in": "thu", "nights": 3, "rate_cents": 12000}` is priced
  `{"room_cents": 42000, "discount_cents": 0, "tax_cents": 825, "total_cents": 42825}`:
  Thursday at $120.00, Friday and Saturday at $150.00 each, plus $8.25 city tax.
- S3: `{"check_in": "sat", "nights": 2, "rate_cents": 12000}` is refused with exit
  status 2, because it includes a Saturday night but is shorter than 3 nights.
- S4: `{"check_in": "sun", "nights": 14, "rate_cents": 8000}` is priced
  `{"room_cents": 120000, "discount_cents": 18000, "tax_cents": 2750, "total_cents": 104750}`:
  ten weekday nights at $80.00 and four weekend nights at $100.00, 15% off the room
  charge, and city tax on the first 10 nights only.

## Out of scope

- Calendar dates, holidays, seasons, room types, guest counts, currencies other than US
  dollars, and cancellations.
