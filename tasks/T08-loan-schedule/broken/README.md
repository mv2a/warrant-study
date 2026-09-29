# Broken implementations for T08-loan-schedule

Each folder holds a copy of `reference/schedule` with one honest-looking mistake that
breaks exactly the promise it is named after.

| Promise | Mistake |
|---|---|
| G1 | The level payment is rounded to the nearest cent instead of up, so roughly half of all loans get a payment one cent too low (and a larger last payment). |
| G2 | Monthly interest is truncated with integer division instead of rounded to the nearest cent with halves up. |
| G3 | The schedule always runs the full term: it never finishes early when a month's balance plus interest is at most the regular payment, so such loans get extra rows with zero or negative balances. |
| G4 | An interest-free payment is the amount divided by the months rounded down instead of up, so the last payment is too large (and loans smaller than the number of months get a payment of 0). |
| C1 | A refused request still exits with status 2 but writes an `{"error": ...}` object on standard output instead of nothing. |
| C2 | `total_interest_cents` is worked out as the regular payment times the number of rows minus the amount borrowed, which is wrong whenever the last payment differs from the regular one. |
| C3 | Fields are validated with `isinstance(value, int)`, so `true` and `false` pass as 1 and 0 (for example `"months": true` is scheduled as a one-month loan). |

## Promises without a broken implementation

- S1, S2, S3: the scenarios are concrete instances of G1 to G4 and C2. Any honest mistake
  that changes a scenario's figures breaks one of those promises too (the broken G1, G2,
  G4 and C2 implementations above all get at least one scenario wrong). An implementation
  wrong in a scenario and in nothing else would have to special-case that exact request,
  which is not a plausible honest mistake.
