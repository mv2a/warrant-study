# Deliberately broken implementations

Each folder holds a `grade` that is the reference with one plausible, honest mistake.
Each one breaks the promise it is named after.

| Folder | Mistake |
|---|---|
| `G1/` | Swaps the exam weights: midterm 35% and final 25%. |
| `G2/` | Drops every quiz that ties for lowest, not just one. If every quiz ties, nothing is left and the command crashes. |
| `G3/` | Takes 10 points off per day late instead of 10% of the homework's own score. The 5-day cutoff is still right. |
| `G4/` | Compares with `>` instead of `>=`, so a percentage exactly on a boundary (90.0, 86.0, 80.0, 76.0, 70.0, 60.0) gets the lower letter. |
| `C1/` | Uses binary floating point and Python's `round()`, which rounds some exact halves down (82.25 becomes 82.2, and 89.95 computes as 89.94999... and becomes 89.9). |
| `C2/` | Checks that `days_late` is an integer but not that it is 0 or more, so a negative `days_late` is graded as a bonus instead of refused. |
| `C3/` | Writes `percent` as a string with one decimal place ("82.3") instead of a JSON number. |

## Promises without a broken implementation

- S1, S2, S3: each scenario is a worked instance of the general promises. S1 exercises
  G1, G2 and G3, S2 exercises G1, C1 and G4, and S3 exercises G1, G2 (a single quiz is
  kept) and G3 (the 5-day cutoff). Any honest mistake that changes a scenario's answer
  also breaks one of those general promises, so a broken implementation "wrong in
  exactly S1" (or S2, S3) is not feasible. The only way to break a scenario alone is to
  special-case its exact input, which is not an honest mistake. The broken
  implementations above already get the scenarios wrong: `G1/` fails S1 and S3,
  `G3/` fails S1 and S3, and `C1/` and `G4/` fail S2.
