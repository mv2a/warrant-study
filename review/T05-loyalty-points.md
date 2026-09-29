# Review of T05-loyalty-points

- Task: `tasks/T05-loyalty-points`
- Reviewer: an AI model, Claude Sonnet, not a human.
- Resolver: an AI model, Claude Opus, not a human.
- Outcome: 2 issues raised, 2 accepted, 0 rejected. Gates re-run after the changes: see the end of this file.

## Issue 1 (ambiguity, must-fix): accepted

Verbatim from the reviewer:

```json
{
 "where": "intent.md G3 (lines 22-26) and C1 (lines 30-32); checks/audit/category.py (lines 61-64) and checks/audit/giftcards.py (line 52); contrast with checks/holdout/category.py and checks/holdout/giftcards.py, which never test this",
 "problem": "Intent only says category matching is 'matched exactly including case' (G3) and that a gift card is 'An item whose category is \"gift_card\"' (C1). Neither sentence says whether surrounding whitespace or other non-case variation counts as a mismatch. Categories are open, retailer-supplied strings (not a closed enum like tier), so a competent engineer could reasonably trim incidental whitespace before comparing, the way many real catalog/loyalty systems do, and still believe they satisfied 'matched exactly including case.' The audit resolves this one way -- X5 (category.py) treats \"item lawn, listed ' lawn'\" and \"item 'lawn ', listed lawn\" as non-matches, and X6 (giftcards.py) treats \" gift_card\" and \"gift_card \" as ordinary (non-gift-card) categories -- but intent.md never states that resolution in words, so it isn't actually derivable from the promise text alone. Worse, the corresponding holdout checks (H3 category.py, H4 giftcards.py) don't exercise any whitespace-padded category at all, only case variants. That means a defensible whitespace-trimming implementation would pass every visible check and every holdout check and only fail at the hidden audit used for scoring, which the protocol says should never happen since 'ground truth is intent' and intent doesn't actually decide this point on its own text.",
 "suggestion": "Add one shared sentence to intent.md that both G3 and C1 can point to, e.g. under Constraints: \"Category strings -- including the literal `gift_card` and every entry in `bonus_categories` -- are compared as exact strings: case and any surrounding whitespace both matter; nothing is trimmed or normalized.\" That single sentence removes the ambiguity for both promises at once (it also matches what X1's existing 'single-space category' case already assumes). If the holdout is meant to give builders a real chance to discover this rule before the hidden audit, also add one whitespace-padded case to checks/holdout/category.py and checks/holdout/giftcards.py.",
 "kind": "ambiguity",
 "severity": "must-fix"
}
```

Disposition: accepted. The finding is correct. "Matched exactly including case" does not rule out trimming, and X5, X6 and X9 (whose generated categories include `" tools"`) all assume that whitespace counts. The reference compares plain strings, so its behaviour already matched the audit and did not change.

Changes made:

- `intent.md` G3: the phrase "matched exactly including case" is replaced by a full rule: "Categories are compared as exact strings: case matters, every space or other whitespace character matters (leading and trailing ones included), and nothing is trimmed or normalized, so an item in `"garden"` is not promoted by `"Garden"` or `" garden"`." The rule sits inside G3 rather than in a new constraint, so the promise list in `task.json` stays the same and the checks that cover G3 also cover the rule.
- `intent.md` C1: "An item whose category is `"gift_card"`" now reads "An item whose category is exactly the string `"gift_card"`". A new last sentence adds: "The comparison is exact as in G3, so a look-alike such as `"Gift_Card"` or `"gift_card "` is an ordinary category."
- `checks/holdout/category.py` (H3): three fixed cases added, making 18 fixed cases in all. They are an item `garden` with `" garden"` listed (0 points), an item `"garden "` with `garden` listed (0 points), and an item `"garden\t"` next to an item `garden` with only `"garden\t"` listed (20 points, so only the exact item counts). The H3 statement is updated to match.
- `checks/holdout/giftcards.py` (H4): four look-alikes added: `"  gift_card  "`, `"gift_card\t"`, `"\ngift_card"` and `"Gift_card"`. Each is a promoted $40.00 silver item and must be scored as an ordinary item (base 40, bonus 90). The H4 statement is updated to match.
- Audit: no code change was needed, because X5 and X6 already test whitespace padding with their own inputs (`lawn`, `" gift_card"`, `"gift_card "`). The X6 statement now names the leading and trailing space case, which its code already tests. The new H cases use different strings from the X cases, so X stays independent of H.
- Verification: a scratch mutant of the reference that trims categories before comparing now fails H3, H4, X5, X6 and X9. It still passes V, as intended.

## Issue 2 (gap, should-fix): accepted

Verbatim from the reviewer:

```json
{
 "where": "intent.md C3 (lines 37-38, 'price_cents ... an integer', 'quantity ... an integer') and C4 (lines 48-50, 'a price that is ... fractional', 'a quantity ... fractional'); checks/holdout/invalid.py (H7), checks/audit/refusals.py (X2), checks/audit/generated_invalid.py (X10)",
 "problem": "C4 lists 'fractional' as a reason a price or quantity is refused, and C3 separately promises the fields are 'an integer' in type. A JSON literal such as `100.0` or `2.0` is a whole number in value but, parsed with Python's json module (the task's language), comes out as a `float`, not an `int`. It's genuinely unclear from the text alone whether such an input should be refused (a strict `type(x) is int` reading of C3, consistent with how true/false are explicitly called out as non-integers) or accepted as the equivalent whole number (a value-based reading of 'fractional', since `100.0` has no fractional part). I checked every invalid-input generator in H7, X2 and X10 (bad_price/bad_quantity in generated_invalid.py always add a non-zero delta like 0.5, 0.25, 0.99, or a `/7` remainder) and none of them, nor any hand-written case, ever sends a decimal-point value with a zero fractional part for price_cents or quantity. So this exact corner of the type contract is never exercised by any of the three suites, leaving a real ambiguity with no check to force either resolution.",
 "suggestion": "Pick one reading and say it explicitly in C4, e.g. add: '...a price or quantity given as a JSON number with a decimal point (such as `100.0`) is also invalid, even when its value is a whole number.' Then add one such case to checks/holdout/invalid.py and a different one (per the layout's 'different inputs' rule for audit) to checks/audit/refusals.py or generated_invalid.py's bad_price/bad_quantity helpers, so the now-explicit rule is actually enforced rather than just stated.",
 "kind": "gap",
 "severity": "should-fix"
}
```

Disposition: accepted, with the strict reading. The reference already refuses these inputs, because `whole_number` checks `type(value) is int`. The strict reading also matches C3's wording ("an integer") and the way C4 already treats true/false as non-integers. The rule covers exponent notation as well (`1e2`), because Python's json module parses that as a float too, and otherwise it would have been the next gap.

Changes made:

- `intent.md` C4: one item added to the refusal list: "a price or quantity written as a JSON number with a decimal point or an exponent, such as `100.0` or `1e2`, even when its value is a whole number".
- `checks/holdout/invalid.py` (H7): three cases added: price `1250.0`, quantity `2.0`, and a raw request with price `1e3`. H7 now has 41 kinds of invalid request, and its statement is updated to match.
- `audit/refusals.py` (X2): four cases added to the lists (prices `1675.0` and `0.0`, quantities `3.0` and `1.0`). Three raw requests are also added: price `25e2`, quantity `1E0`, and a gift-card price `2500.00`. X2 now has 107 invalid requests, and its statement is updated to match.
- `audit/generated_invalid.py` (X10): `float(ok)` (the item's own whole value sent as a float) is added to both `bad_price` and `bad_quantity`. With seed 90210577 this produces 7 such cases among the 90, and the X10 statement mentions them. The seed stays the same, but the generated sequence after the first such draw is different from before.
- These inputs are chosen from the intent and differ from the H inputs, so X stays independent of H.
- Verification: a scratch mutant of the reference that accepts whole-valued floats now fails H7, X2 and X10. It still passes V.

## Note on the reviewer's own conduct

In its overall view, the reviewer disclosed that it read `broken/README.md`, which its role did not allow. It said its two findings did not depend on that file. Both findings stand on the permitted files alone: they rest on `intent.md`, the holdout checks and the audit checks, and neither one mentions a broken implementation. So both were judged on their merits. The person running the study should still know that the boundary was crossed during this review.

## Gates after the changes

`python3 harness/gates.py tasks/T05-loyalty-points` printed:

```
T05-loyalty-points: PASS | promises 10 | V 2 H 8 X 10 checks | broken 7 (4 pass V)
```

- The reference passes every V, H and X check.
- `warrant check` exits 0.
- Every broken implementation fails at least one X check that covers its promise:
  - G1: X3, X9
  - G2: X4, X9
  - G3: X5, X9
  - C1: X6, X9
  - C2: X7, X9
  - C3: X1, X9
  - C4: X2, X10
- The broken G2, C1, C2 and C4 implementations pass V.
