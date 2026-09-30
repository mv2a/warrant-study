---
owner: head of operations, a regional parcel courier
---

# Parcel rates

We are a regional courier. Before a parcel is accepted at the counter, the clerk asks for
a rate: the zone the parcel is going to, what it weighs and how big it is. Light but bulky
parcels must pay for the space they take up in the van, long or bulky parcels pay extra for
special handling, and parcels we cannot carry must be turned away instead of priced.

## Goals

- G1: A parcel is charged on its billable weight, which is the greater of its actual weight
  and its dimensional weight. The dimensional weight in grams is length × width × height in
  centimetres divided by 5, rounded up to a whole gram.
- G2: A parcel with a billable weight of 10,000 g or less pays the base price in the rate
  table below for its zone and the lightest bracket that holds its billable weight. Each
  bracket includes its upper limit: a parcel of exactly 500 g is in the 500 g bracket, and
  one of 501 g is in the 1,000 g bracket.
- G3: A parcel with a billable weight over 10,000 g pays its zone's 10,000 g price plus its
  zone's price per extra kilogram for every started kilogram above 10,000 g: 10,001 g and
  11,000 g pay for one extra kilogram, and 11,001 g pays for two.
- G4: An oversize parcel pays a surcharge of 1500 cents on top of its base price; any other
  parcel pays no surcharge. A parcel is oversize when its longest side is more than 100 cm,
  or when its length plus girth is more than 220 cm. The length is the longest side and the
  girth is twice the sum of the other two sides, whatever order the three sides are given in.

Base prices, in cents:

| Billable weight           | Zone 1 | Zone 2 | Zone 3 | Zone 4 |
|---------------------------|-------:|-------:|-------:|-------:|
| up to 500 g               |    450 |    520 |    610 |    780 |
| up to 1,000 g             |    540 |    630 |    740 |    950 |
| up to 2,000 g             |    690 |    810 |    960 |   1240 |
| up to 5,000 g             |    920 |   1090 |   1310 |   1700 |
| up to 10,000 g            |   1350 |   1600 |   1930 |   2520 |
| each started kg over 10,000 g |  85 |    105 |    130 |    175 |

## Constraints

- C1: Rating runs as a command named `rate` that reads one JSON object on standard input and
  writes one JSON object on standard output. The request has the integer fields `zone`,
  `weight_g` (grams), `length_cm`, `width_cm` and `height_cm` (centimetres); any other
  fields in the request are ignored. A priced request exits with status 0 and writes an
  object with exactly the integer fields `billable_g`, `base_cents`, `surcharge_cents` and
  `total_cents`, where `total_cents` is `base_cents` plus `surcharge_cents`. A refused
  request exits with status 2 and writes nothing on standard output.
- C2: Parcels we cannot carry are refused, never priced: a billable weight over 30,000 g, a
  longest side over 150 cm, or a length plus girth (length and girth as G4 defines them) over
  300 cm. A parcel exactly at a limit is accepted.
- C3: Invalid requests are refused, never priced: text that is not JSON, JSON that is not an
  object, a missing field, a zone other than 1, 2, 3 or 4, and a weight or side that is not
  a whole number greater than zero, such as zero, a negative number, a fraction, text or
  true/false. The zone, weight and sides must be written as JSON integers: a number written
  with a decimal point or an exponent, such as 2.0 or 1.5e3, is refused even when its value
  is whole.

## Scenarios

- S1: `{"zone": 1, "weight_g": 1500, "length_cm": 30, "width_cm": 20, "height_cm": 10}` is
  priced `{"billable_g": 1500, "base_cents": 690, "surcharge_cents": 0, "total_cents": 690}`:
  its dimensional weight is only 1,200 g, so it is charged on its actual weight.
- S2: `{"zone": 3, "weight_g": 800, "length_cm": 50, "width_cm": 40, "height_cm": 30}` is
  priced `{"billable_g": 12000, "base_cents": 2190, "surcharge_cents": 0, "total_cents": 2190}`:
  it is charged on its dimensional weight, 1930 cents plus two extra kilograms at 130 cents.
- S3: `{"zone": 4, "weight_g": 3500, "length_cm": 20, "width_cm": 110, "height_cm": 15}` is
  priced `{"billable_g": 6600, "base_cents": 2520, "surcharge_cents": 1500, "total_cents": 4020}`:
  its longest side, given as the width, is over 100 cm.
- S4: `{"zone": 1, "weight_g": 3000, "length_cm": 20, "width_cm": 10, "height_cm": 155}` is
  refused, because its longest side is over 150 cm.

## Out of scope

- Pickup, insurance, fuel or seasonal surcharges, taxes, discounts, and currencies other
  than the one the table is written in.
- How zones are worked out from addresses: the request already names the zone.
