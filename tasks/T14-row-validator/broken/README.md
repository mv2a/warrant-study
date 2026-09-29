# Broken implementations for T14 row validator

Each folder holds a copy of `reference/validate` with one honest-looking mistake that breaks
exactly the promise the folder is named after. The one exception is G2: its mistake lives in how
Python types numbers, so it keeps the older way of reading JSON numbers as Python `int` and `float`
instead of the reference's exact `Number`. Apart from that mistake it differs from the reference only
on numbers a float cannot hold (such as `1e400`), which no check uses and which G2 also covers.

| Promise | Mistake |
|---|---|
| G1 | Only a left-out key counts as missing; a `null` value is treated as present, so it gets a `type` error (required or not) instead of `missing` or nothing. |
| G2 | Types are tested with plain `isinstance`: `true` and `false` pass as numbers and integers (bool is an int in Python), and `4.0` fails as an integer. |
| G3 | The upper bound is exclusive, like Python's `range()`: a value equal to `max` gets a `range` error. |
| G4 | A value is flagged as `duplicate` whenever it occurs more than once in the field, so the first occurrence is flagged too. |
| G5 | Once a row has one error, the rest of that row's fields are skipped. |
| C1 | Rows are numbered from 1, the way a spreadsheet numbers them, instead of from 0. |
| C2 | `range`, `allowed` and `duplicate` are checked independently, so one field of one row can collect several errors. |
| C3 | Errors are sorted by row and then by field name "for a predictable order", not by the field's position in the schema. |
| C4 | The schema is trusted beyond names and types: unknown keys (top level and in field rules), an empty schema, empty or repeated names, non-boolean flags, misplaced or non-numeric `min`/`max`, `min` above `max` and bad `allowed` lists are all accepted instead of refused. |

Some of these also change results on promises that depend on the broken one. For example,
C4 and G4 define "the field's type" and "null" through G2 and G1, and every expected error
list contains row positions (C1). The mistake itself still lies in the named promise.

## Promises without a broken implementation

- S1, S2, S3: these scenarios are exact instances of the goals and constraints on one fixed
  schema (ROSTER). Any honest mistake that changes a scenario's output also breaks a G or
  C promise, and each such mistake already has its own folder: for example G1 fails S1 and
  S2, G4 fails S3, G5 and C3 fail S2. An implementation wrong in a scenario and nowhere else
  would have to special-case that scenario's input, which is not a plausible honest
  mistake, so none is included.
