# Broken implementations for T17-hotel-stay

Each folder holds a copy of `reference/stay` with one honest-looking mistake that breaks
exactly the promise it is named after.

| Promise | Mistake |
|---|---|
| G1 | The weekday of each night is `first + i` with no `% 7`, so only the first week's Friday and Saturday are surcharged. Stays that reach a second weekend are undercharged. |
| G2 | "A week or more" coded as `nights > 7`, so a 7-night stay gets no discount. The 14-night tier is right. |
| G3 | The 10-night cap on the city tax is missed, so every night is taxed. |
| G4 | The minimum stay is enforced only for Saturday check-ins, so a Friday check-in for 2 nights (which includes Saturday night) is priced instead of refused. |
| C1 | Refusals use `sys.exit(message)`, which writes the reason on standard error but exits with status 1, not 2. |
| C2 | The surcharge uses Python's `round()`, which rounds an exact half cent to even. A rate 2 more than a multiple of 8 (for example 1002, surcharge 250.5) gets 250 instead of 251. |
| C3 | `nights` and `rate_cents` are converted with `int()` instead of being type-checked, so `true`, `2.0`, `2.5` (as 2) and `"3"` are accepted and priced. |

## Promises without a broken implementation

- S1, S2, S3, S4: these scenarios are fixed examples of G1 to G4 and C1 to C3, not separate
  behaviour. A mistake that breaks one of them is a mistake in the goal or constraint it
  illustrates, and those mistakes are already here: broken/G1 and broken/G3 get S4 wrong,
  and broken/C1 gets S3 wrong. The only way to break a scenario and nothing else is to
  special-case its exact request, which is not a plausible honest mistake.
