---
owner: study task T15
---

# Unit conversion

A small command converts an amount from one unit to another of the same kind: length,
mass or volume. Every unit has an exact definition, so every answer is exact except for
the one rounding the caller asks for. Converting between kinds, such as kilograms to
litres, makes no sense and is refused.

## Goals

- G1: Lengths convert between mm, cm, m, km, in, ft, yd and mi, defined exactly as
  1 cm = 10 mm, 1 m = 1000 mm, 1 km = 1000 m, 1 in = 25.4 mm, 1 ft = 12 in, 1 yd = 3 ft
  and 1 mi = 5280 ft.
- G2: Masses convert between mg, g, kg, t, oz, lb and st, defined exactly as
  1 g = 1000 mg, 1 kg = 1000 g, 1 t (tonne) = 1000 kg, 1 lb = 453.59237 g,
  1 oz = 1/16 lb and 1 st (stone) = 14 lb.
- G3: Volumes convert between ml, l, m3, floz, pt, qt and gal, in US liquid measure,
  defined exactly as 1 l = 1000 ml, 1 m3 = 1000 l, 1 gal = 3785.411784 ml,
  1 qt = 1/4 gal, 1 pt = 1/8 gal and 1 floz = 1/128 gal.

## Constraints

- C1: Conversions are exact. The result is the input amount times the exact ratio of the
  two units, rounded once, at the end, to the requested number of places. It must be
  right however many digits the input has and for every allowed number of places, so
  floating-point arithmetic, or any rounding along the way, is not good enough.
- C2: The result is rounded to the nearest multiple of one unit in the last requested
  place, and an amount exactly halfway is rounded up: 5 mm is "1" cm at 0 places, and
  125 mm is "0.13" m at 2 places. It is written as a string of ASCII digits with exactly
  `places` digits after a decimal point, and no point at all when `places` is 0; with no
  leading zeros except a single 0 before the point; and with no sign, exponent, spaces
  or separators. Examples of well-formed results: "1.1340", "0.50", "0.000" and "12".
- C3: Any unit converts to any unit of the same kind, including itself. Unit symbols are
  case-sensitive and must be written exactly as in G1 to G3. A request with an unknown
  unit (such as "KG", "lbs" or "gallon"), or with units of two different kinds (such as
  "kg" and "l"), is refused.
- C4: Malformed requests are refused, never converted: input that is not a JSON object;
  a missing field, or any field other than the four named in C5; a `value` that is not a
  string of one or more ASCII digits, optionally followed by a point and one or more
  digits (so the number 5 and the strings "", "-1", "+1", "1e3", ".5", "5.", " 5", "1,5"
  and "1/2" are all refused, while "0" and "007.50" are accepted); a `from` or `to` that
  is not a string; and a `places` that is not written as a JSON integer from 0 to 12 (so
  13, -1, 2.5, 2.0, "2" and true are refused).
- C5: The converter is a command named `convert`. It reads one JSON object on standard
  input, ignoring any whitespace before or after the object, with the fields `value`
  (string: the amount), `from` (string: the unit of the amount), `to` (string: the unit
  wanted) and `places` (integer: the number of decimal places wanted). On success it exits with status 0 and writes one JSON object on
  standard output with exactly the fields `value` (string: the converted amount, written
  as in C2), `unit` (string: the `to` unit) and `dimension` (string: "length", "mass" or
  "volume"). A refused request exits with status 2 and writes nothing on standard output.

## Scenarios

- S1: The request `{"value": "12", "from": "ft", "to": "m", "places": 3}` gives
  `{"value": "3.658", "unit": "m", "dimension": "length"}`, because 12 ft is exactly
  3.6576 m.
- S2: The request `{"value": "2.5", "from": "lb", "to": "kg", "places": 4}` gives
  `{"value": "1.1340", "unit": "kg", "dimension": "mass"}`, because 2.5 lb is exactly
  1.133980925 kg.
- S3: The request `{"value": "3", "from": "kg", "to": "l", "places": 2}` is refused: the
  command exits with status 2 and writes nothing on standard output.

## Out of scope

- Temperature, area, speed and other kinds of measure; UK (imperial) gallons and pints;
  negative amounts; unit names spelled out or in the plural.
