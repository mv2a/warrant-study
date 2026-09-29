# Review of T11-reorder-quantity

- Reviewer: an AI model, Claude Sonnet, not a human.
- Resolver: an AI model (Claude Opus), working only inside `tasks/T11-reorder-quantity`.
- Result: 2 issues accepted, 1 rejected. The gates were re-run after the changes and pass.

## Reviewer's overall view (verbatim)

> The task is well-specified and unusually thoroughly tested: every clause in G1-G4/C1-C3/S1-S3 is covered by at least one holdout and one independently-written audit check, gates_report.json shows the reference passes all 32 checks and every broken variant is caught by X, and I found no leakage from intent.md/checks/public into the hidden suites' specific cases, and no check that tests something the intent doesn't promise. The task is not trivial (rounding, priority-ordered greedy funding with budget carry-forward, ~20 distinct refusal rules) and is on the denser side for a one-hour task but not clearly over the line. One real ambiguity is worth a one-line fix before sealing (sku case-sensitivity is never stated in intent.md, yet both hidden suites bake in a case-sensitive reading as ground truth); the other two items are minor polish.

## Issue 1 (ambiguity, should-fix): accepted

**Where (verbatim):** intent.md, C3 ("...and a sku that is not a string, is empty, or repeats an earlier sku")

**Problem (verbatim):** Intent never states whether sku matching for the duplicate-sku rule is case-sensitive. Both checks/holdout/invalid.py (VALID case "skus that differ only in case": "ab" and "AB") and audit/accept_edges.py (X19: "ab-1" beside "AB-1" must be planned, not refused) bake in a case-sensitive reading as ground truth, but a competent engineer building this against a real warehouse catalog (where SKUs often come from a case-insensitive system) could reasonably normalize case before the duplicate check, which would then wrongly refuse those exact test cases and fail H7/X19/X18 for reasons the intent never ruled on.

**Suggestion (verbatim):** Add one clause to C3, e.g. "two skus are the same product only if they match exactly, character for character (case included)", so the case-sensitive behavior both suites test is an explicit promise rather than an inferred one.

**Disposition: accepted.** The reviewer is right: H7 and X19 both require skus that differ only in case to be planned, and intent.md did not say so. Because intent.md is the ground truth, the promise is now stated there rather than left to inference. Added to C3, after the duplicate-sku rule:

> Two skus are the same only when they match exactly, character for character, with upper and lower case counting as different characters.

The wording deliberately gives no example sku, so no case from the hidden suites (`ab`/`AB` in H7, `ab-1`/`AB-1` in X19) leaks into the intent the builder sees. No check changed: H7, X18 and X19 already tested exactly this reading, and the reference compares skus exactly.

## Issue 2 (wrong-check, minor): accepted

**Where (verbatim):** audit/checks.toml (id X4) and audit/target_generated.py

**Problem (verbatim):** The X4 statement claims "a third of them [150 generated products] with stock exactly on or one or two units either side of the target," but the generator picks style = rng.randint(0, 4) (5 equally likely buckets) and uses buckets 0 and 1 for the on-target/near-target cases, giving that subset a 2/5 (~40%) share, not a third (~33%). The check itself is fine; only its documented statement is off.

**Suggestion (verbatim):** Either reword the statement to "roughly two fifths" or change the generator to `rng.randint(0, 5)` with two of six buckets used for those styles so the "a third" claim is accurate.

**Disposition: accepted, by rewording the statement.** Replaying the seeded generator (seed 61903) shows that 64 of the 150 products (43%) are built on or within two units of the target, and 67 land there in all. The X4 statement now reads "about two fifths of them built with stock exactly on or one or two units either side of the target". The generator was left unchanged so the check's cases, seed and results stay as they were; only a comment was added next to `style = rng.randint(0, 4)` to say that styles 0 and 1 (about two fifths) put stock on or near the target. The change was made from the audit's own code, not from H.

## Issue 3 (difficulty, minor): rejected

**Where (verbatim):** intent.md as a whole, especially the C3 sentence (~20 distinct refusal conditions) combined with the G1-G4 funding algorithm

**Problem (verbatim):** A correct solution needs: strict single-JSON-object parsing; a top-level budget check; per-product checks for 9 fields each needing a JSON-integer check that explicitly excludes bool (isinstance(x, int) is not enough in Python) plus a range check; duplicate-sku tracking; the target/rounding formula; and a priority-sorted greedy funding loop with running balance. That is a fair amount of surface to get exactly right inside an hour, more than most of the individual G/C promises would suggest in isolation.

**Suggestion (verbatim):** Time a from-scratch implementation against the stated one-hour budget (or compare its LOC/rule-count against sibling study tasks) before sealing; if it consistently runs long, the C3 rule count is the part to trim first since it's the most repetitive.

**Disposition: rejected, with no change to the task.** Reasons:

1. The size is modest. The complete reference (`reference/reorder`) is 108 lines, comments and docstring included. The refusal rules are repetitive by design: the eight product integers share one helper with a per-field minimum, so the roughly twenty refusal conditions in C3 come to about 50 lines of validation, counting the field table, the helper and blank lines. The planning itself (target, rounding up to packs, a stable sort by priority, a greedy loop with a running balance) is about 27 lines.
2. The reviewer's own overall view puts the task "on the denser side for a one-hour task but not clearly over the line". The issue suggests measuring before sealing; it does not show that the task runs over the one-hour budget.
3. The bool-versus-integer pitfall is intended difficulty, not accidental difficulty. It is stated plainly in C3 ("true and false are not"), and `broken/C3` models exactly this mistake. Trimming C3 would remove the one promise that separates careful validation from a naive `isinstance` check, and would mean rewriting H7, X15 to X19 and `broken/C3` shortly before sealing.
4. The suggested cross-check against sibling tasks is outside this resolver's role, which may not read other tasks. A timed human build is not something this resolver can run. Both remain open to the study's operators if they want to calibrate task difficulty across the set.

## Gate result after the changes

`python3 harness/gates.py tasks/T11-reorder-quantity`:

```
T11-reorder-quantity: PASS | promises 10 | V 2 H 8 X 22 checks | broken 7 (4 pass V)
```

The reference passes all 2 V, 8 H and 22 X checks, and `warrant check` returns 0. Each of the 7 broken implementations (G1, G2, G3, G4, C1, C2, C3) fails at least one X check that covers its promise. Four of them (G2, G3, G4, C3) pass V, as intended, since V is deliberately incomplete. S1 to S3 have no broken implementation, for the reason given in `broken/README.md`.
