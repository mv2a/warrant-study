# Broken implementations of `tax`

Each folder holds a copy of the reference with one honest-looking mistake that breaks
exactly the promise it is named after. In the audit suite each one fails only the X checks
that cover its own promise; G3 also fails X13, because S3 is an instance of G3 (see below).

| Promise | Mistake |
|---|---|
| G1 | The part of taxable income above 100,000.00 is taxed with the loop's leftover rate (25%) instead of the 38% top rate. |
| G2 | The allowance phase-out is not stopped at zero, so from 140,000.00 of income the allowance goes negative and taxable income exceeds income. |
| G3 | The credit is taken off in full, so it becomes refundable: the tax owed can go below zero and the credit reported can exceed the tax. |
| C1 | The band tax is rounded with Python's `round()`, which sends an exact half cent to the even cent instead of up. |
| C2 | Taxable income is income minus allowance without the floor at zero, so incomes below 12,000.00 report a negative taxable income (the tax itself stays right). |
| C3 | Fields are validated with `isinstance(value, int)`, so `true` and `false` are taxed as 1 and 0 instead of refused. |
| C4 | A refused request exits with status 2 but writes a JSON error object on standard output instead of nothing. |

## Promises without a broken implementation

- S1, S2, S3, S4: each scenario is a concrete instance of the goals and constraints (S1
  of G1 and G2's full allowance, S2 of the phase-out and the credit, S3 of the
  non-refundable credit, S4 of the half-cent rounding). An implementation that gets one
  scenario wrong while keeping every goal and constraint cannot exist, and one that breaks
  a scenario through an honest mistake is already a broken implementation of a goal or
  constraint (for example `broken/G3` gets S3 wrong). The only way to break a scenario
  alone would be to special-case its input, which is not a plausible honest mistake.
