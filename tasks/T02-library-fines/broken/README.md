# Broken implementations

Each folder holds a copy of the reference `fine` with one honest-looking mistake, wrong in
exactly the promise it is named after:

- `G1`: fines reference items at the DVD rate (100 cents a day instead of 150), as if all
  non-book media shared one rate.
- `G2`: once an item is past its grace period, charges every late day, including the
  first three (a book 7 days late owes 175 cents instead of 100).
- `G3`: handles reference items in an early-return branch (they have no grace period)
  that never applies the 1500-cent item cap.
- `G4`: trims the last item lines so that they add up to the capped total, instead of
  reporting each item's fine before the account cap.
- `C1`: reports a refusal as a JSON error object on standard output instead of writing
  nothing there (the exit status is still 2).
- `C2`: reports `days_late` as the raw difference, so an early return shows a negative
  number of days (its fine is still 0).
- `C3`: validates day numbers with `isinstance(value, int)`, which accepts `true` and
  `false` because Python booleans are integers.

## Promises without a broken implementation

- `S1`, `S2`, `S3`: each scenario is a worked example of the goals and constraints, and
  its exact output follows from G1 to G4 and C1 to C2. An implementation that gets a
  scenario wrong is therefore necessarily wrong in at least one of those promises too,
  so no implementation can be wrong in a scenario alone, and one that special-cased the
  scenario inputs would not be an honest mistake. The scenarios are exercised instead
  by the broken implementations above: `G1`, `G2` and `G4` each get at least one
  scenario wrong.
