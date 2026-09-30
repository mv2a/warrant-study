---
owner: fares desk, city bus network
---

# Bus fares

Our buses run through six zones, numbered 1 to 6 in a line from one end of the network to
the other. Given one rider's trips for one day, we work out what each trip costs. Longer
rides cost more, changing buses shouldn't cost extra, children and seniors pay less, and
nobody pays more in a day than the daily cap. The ticket machines, the journey planner and
the monthly statement all use this one command, so they must agree to the cent.

## Goals

- G1: An adult fare is 270 cents, plus 95 cents for each zone boundary the trip crosses.
  A trip from zone a to zone b crosses |a - b| boundaries, in either direction: a trip
  within one zone costs 270 cents, and a trip from zone 1 to zone 6, or from 6 to 1,
  costs 745 cents.
- G2: Changing buses is free for 90 minutes. The first trip opens a transfer window at its
  boarding minute. A later trip that boards at most 90 minutes after the boarding minute of
  the trip that opened the current window is a transfer and costs nothing, whatever zones
  it covers. A trip that boards later than that pays its fare and opens a new window.
  Transfers never extend a window: it always runs from the trip that opened it.
- G3: The rider's age in whole years sets their fare. Riders under 5 ride free. Riders aged
  5 to 15 pay the child fare, 50% of the adult fare. Riders aged 65 and over pay the senior
  fare, 40% of the adult fare. Riders aged 16 to 64 pay the adult fare.
- G4: A day's fares are capped. After transfers and concessions, the amounts charged
  across all the trips in one request never add up to more than the rider's daily cap:
  1100 cents for adults, 550 cents for children and 440 cents for seniors. The trip that
  would take the running total past the cap is charged only what is left under the cap,
  and every trip after the cap is reached costs nothing.

## Constraints

- C1: Money is counted in whole cents. A child or senior fare that is not a multiple of
  5 cents is rounded down to the multiple of 5 cents below it: half of 365 cents is
  182.5 cents, charged as 180 cents. Each trip's fare is rounded on its own, before the
  trips are summed or capped.
- C2: Invalid requests are refused, never priced. That includes text that isn't exactly
  one JSON object, optionally surrounded by whitespace, such as an object followed by a
  second object or by other text; a missing age or trips field; an age below 0 or above
  120; trips that isn't a list; a trip that isn't an object or lacks board_minute,
  from_zone or to_zone; a boarding minute below 0 or above 1439; a zone below 1 or above
  6; any of these numbers written as anything other than a JSON integer, such as 30.0,
  "30", true or null; and trips out of boarding order, where a trip boards at an earlier
  minute than the trip listed just before it. Trips boarding in the same minute are in
  order, and an empty trips list is valid and costs nothing.
- C3: Pricing runs as a command named `fare` that reads one JSON object on standard input,
  `{"age": integer, "trips": [{"board_minute": integer, "from_zone": integer, "to_zone": integer}, ...]}`,
  where board_minute counts minutes since midnight on the day of travel. On success it
  writes one JSON object on standard output with exactly two fields,
  `{"fares_cents": [integer, ...], "total_cents": integer}`, and exits with status 0:
  fares_cents holds the amount charged for each trip, one per trip in the order given, and
  total_cents is their sum. A refused request exits with status 2 and writes nothing on
  standard output. Fields in the request or in a trip that are not named here are ignored.

## Scenarios

- S1: A 40-year-old rides from zone 2 to zone 5 boarding at minute 450, from zone 5 to
  zone 6 at minute 490, and within zone 6 at minute 600. The fares are 555, 0 and 270
  cents, 825 cents in total: the second trip is a transfer, and the third boards 150
  minutes after the first.
- S2: An 11-year-old rides from zone 1 to zone 3 boarding at minute 480 and within zone 3
  at minute 1000. The fares are 230 and 135 cents, 365 cents in total.
- S3: A 30-year-old rides from zone 1 to zone 6 boarding at minute 420, from zone 6 to
  zone 4 at minute 480, from zone 4 to zone 6 at minute 720 and within zone 6 at minute
  1080. The fares are 745, 0, 355 and 0 cents, 1100 cents in total: the third trip would
  cost 460 cents, but only 355 cents are left under the cap.

## Out of scope

- Passes and season tickets, refunds, trips that run past midnight, more than one rider in
  a request, and any currency other than cents.
