# Deliberately broken implementations

Each folder holds a `convert` that is wrong in one promise, with a mistake an honest
engineer could make. Everything else is the reference.

| Folder | Promise | Mistake |
|---|---|---|
| G1 | G1 | The mile is taken as the rounded 1609.34 m instead of exactly 5280 ft (1609.344 m). |
| G2 | G2 | The ounce is taken as the familiar rounded 28.35 g instead of exactly 1/16 lb (28.349523125 g). |
| G3 | G3 | The gallon is the UK imperial gallon, 4546.09 ml, instead of the US liquid gallon, so qt, pt and floz are also imperial. |
| C1 | C1 | The arithmetic is done in floating point, then rounded half up with `Decimal`, so long inputs and many places lose digits. |
| C2 | C2 | The exact result is rounded with Python's `round()`, which rounds exact halves to even instead of up. |
| C3 | C3 | Every unit sits in one table of sizes with no check that the two units measure the same kind of thing, so kg to l gets an answer. |
| C4 | C4 | The amount is parsed with `Fraction()` instead of being checked against the allowed form, so "-1", "1e3", "1/2", " 5" and similar strings are converted. |
| C5 | C5 | A refused request still exits with status 2, but writes a JSON error object on standard output instead of nothing. |

## Promises without a broken implementation

- S1, S2 and S3 have none. Each scenario is one concrete request that the general
  promises already decide (S1 by G1, C1 and C2; S2 by G2, C1 and C2; S3 by C3 and C5).
  An implementation that gets a scenario wrong must also break the promise behind it, so
  no implementation can be wrong in exactly one scenario and nothing else; tailoring code
  to fail only those literal inputs would not be an honest mistake.

## Overlaps worth knowing

- C3 and C5 also get S3 wrong, because S3 is a concrete case of both: C3 converts kg to l,
  and C5 writes an error object on standard output.
- G1, G2 and G3 also fail the holdout exactness check (H4), and G2 and G3 the holdout
  rounding check (H5), because those checks convert miles, ounces and gallons too. The
  float implementation for C1 also misses some exact halves in H5, because float noise
  pushes them off the half. The per-promise checks for G1 to G3 (H1 to H3) and the
  exactness check avoid exact halves, and H1 to H3 avoid very long results, so that they
  fail only for a wrong unit definition or for inexact arithmetic.
