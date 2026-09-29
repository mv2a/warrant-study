# Deliberately broken implementations for T04-bill-split

Each folder holds a copy of `reference/split` with one plausible, honest mistake in the
promise it is named after.

| Folder | Mistake |
| --- | --- |
| G1 | Rounds the tip with Python's `round()` on a float, which sends exact half cents to the even cent (2525 cents at 10% tips 252, not 253). |
| G2 | Recognises own-payers by their having items, so an own-payer who ordered nothing is treated as a sharer and pays part of the pool. |
| G3 | Splits the sharers' pool in whole cents and lets the last-listed sharer cover the odd cents, so sharers' parts are unequal. |
| G4 | Splits the tip evenly among all diners instead of in proportion to each diner's part of the subtotal. |
| C1 | Rounds each fair amount to the nearest cent on its own, with no leftover step, so the shares can miss the total by a cent or more. |
| C2 | Hands out leftover cents by largest fractional part as promised, but breaks ties by name instead of by position in `diners`. |
| C3 | Tests numbers with `isinstance(value, int)`, so `true` and `false` are accepted as 1 and 0 for prices and tips. |
| C4 | Refuses with `sys.exit(message)`, which exits with status 1 instead of 2. |

Because the shares always add up to the total, a mistake in one diner's part moves money
to or from the others: G2 and G3 also upset the sharers' amounts, and G4 and C1 change
the exact shares that C2 would give. Each mistake still sits in the named promise.

## Promises without a broken implementation

- S1, S2 and S3 are concrete instances of G1 to G4 and C1 to C2 (S3 also shows a sharer
  who ordered nothing). Any honest mistake that gets one of these scenarios wrong is a
  mistake in one of those general promises, and those already have broken
  implementations (G3, G4 and C1 fail the scenarios). A version wrong in exactly one
  scenario and nothing else would have to special-case that scenario's inputs, which is
  not a plausible honest mistake.
