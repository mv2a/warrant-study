# Deliberately broken implementations

Each folder holds a copy of `reference/reorder` with one honest-looking mistake that breaks
exactly the promise it is named after.

| Promise | Mistake |
|---|---|
| G1 | Ignores stock already on order: units needed are the target minus the stock on hand only. |
| G2 | "Rounds up" as one more pack than the whole packs that fit, so a need that is an exact multiple of the pack size gets an extra pack. |
| G3 | Stops funding at the first product the budget cannot pay for in full, instead of passing the money left on to later products. |
| G4 | Breaks priority ties by sku (alphabetically) instead of by request order. |
| C1 | Reports a refusal as a JSON `{"error": ...}` object on standard output (still with status 2) instead of writing nothing there. |
| C2 | Lists the orders in funding (priority) order instead of request order. |
| C3 | Tests integers with `isinstance(value, int)`, which accepts `true` and `false` as 1 and 0. |

## Promises without a broken implementation

- S1, S2, S3: each scenario is one concrete instance of the goals and constraints. Any
  honest mistake that gets a scenario wrong is already a mistake in one of them (for
  example, broken/G1 gets S1 and S3 wrong, and broken/C2 gets S2 wrong); an implementation
  wrong only in a scenario would have to special-case that exact request, which is not a
  plausible honest mistake.
