# Broken implementations

Each folder holds a copy of the reference with one honest-looking mistake that breaks
exactly the promise it is named after. All but broken/C1 pass the public checks.

| Promise | Mistake |
| --- | --- |
| G1 | Braga's prefix is written `BRA`, the obvious first-three-letters abbreviation, instead of `BRG`. Because a previous number must carry the branch's prefix, this one table entry also makes it refuse Braga's real `BRG-` numbers, so it fails every holdout check that sends a Braga number, not only H1. |
| G2 | The padding is removed with `strip("0")` instead of `lstrip("0")`, so a sequence ending in zero loses its trailing zeros too: after `00040` comes 5, not 41. |
| G3 | The count restarts only when the previous number is from exactly the year before; a gap of two or more years is refused as suspicious instead of restarting at 1. |
| C1 | The sequence is padded to four digits instead of five (`LIS-2026-0042`). |
| C2 | The previous number is read with `re.match` and `^...(\d{4})-(\d+)$`, so unpadded or over-long sequences, a trailing newline and non-ASCII digits are accepted. |
| C3 | Any change of year restarts the count, so a previous number from a later year is continued at 1 instead of being refused. Running out at 99999 is still refused. |
| C4 | The year is converted with `int()`, so `"2026"`, `2026.0` and `2026.5` are accepted as 2026. |
| C5 | Requests with fields other than `branch`, `year` and `previous` are refused, although the interface says extra fields are ignored. |

## Promises without a broken implementation

- S1, S2, S3, S4: each scenario is one concrete instance of the general promises (S1 of
  G1, G2 and C1; S2 of G1, G3 and C1; S3 of G1, G3 and C1; S4 of C2 and C5). Any
  implementation that gets a scenario wrong also breaks one of those general promises, so
  no implementation can be wrong in exactly one scenario and nothing else. The scenario
  checks still catch a wrong underlying rule: broken/C1 fails S1, S2 and S3.
