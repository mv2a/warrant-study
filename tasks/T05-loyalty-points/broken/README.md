# Broken implementations for T05-loyalty-points

Each folder holds a copy of `reference/points` with one honest-looking mistake that breaks
exactly the promise it is named after.

| Promise | Mistake |
|---|---|
| G1 | Drops the fraction of a dollar on each line (`price_cents * quantity // 100`, summed) instead of once on the order total, so an order of two separate $0.60 lines earns 0 base points instead of 1. |
| G2 | Rounds the multiplied base to the nearest point with `round()` instead of down, so a silver member with 7 base points gets a tier bonus of 2 instead of 1. |
| G3 | Doubles the promoted cents before dropping the fraction (`2 * cents // 100`), so $10.99 of promoted items earns 21 points instead of 20. |
| C1 | Adds up promoted spend over all items instead of only the eligible ones, so a gift card earns category points when `gift_card` is promoted. Base points and `eligible_cents` stay correct. |
| C2 | Caps only the category bonus at 500 and leaves the tier bonus uncapped, so a gold order with 1,004 base points gets 502 bonus points instead of 500. |
| C3 | Floors the multiplied base with `// 1` on a float, so `bonus_points` and `total_points` come out as floats such as `4.0` in every tier. The values are right; the types break the interface. |
| C4 | Validates prices and quantities with `isinstance(value, int)`, which accepts `true` and `false`, so a price or quantity of `true` is scored instead of refused. |

## Promises without a broken implementation

- S1, S2 and S3 are worked examples of G1, G2, G3, C1 and C2. Their inputs and outputs
  follow entirely from those rules, so any honest mistake that changes a scenario's answer
  also breaks one of those general promises; a program wrong in a scenario and in nothing
  else would have to special-case that one request, which is not an honest mistake. The
  scenarios are still exercised by the broken implementations above: broken/G1 and
  broken/G3 both get S2 wrong (36 base points instead of 37, and 65 category points
  instead of 64).
