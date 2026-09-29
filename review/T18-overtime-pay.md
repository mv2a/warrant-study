# Review of T18-overtime-pay

- Reviewer: an AI model, Claude Sonnet, not a human.
- Resolver: an AI model (Claude Opus), working only inside `tasks/T18-overtime-pay`.
- Result: 2 issues accepted, 0 rejected. The gates were re-run after the changes and pass.

## Reviewer's overall view (verbatim)

> Reviewed intent.md, task.json, checks/public, checks/holdout, and audit for T18-overtime-pay (did not read reference/ or broken/, and changed nothing). This task is unusually well constructed. G1 (daily thresholds), G2 (weekly 2400-minute cap on regular time), and G3 (seventh-consecutive-day rule) are stated with exact minute boundaries and an explicit tie-breaking sentence ("Overtime and double-time minutes from G1 and G3 do not count toward the 40 hours, and no minute ever moves between overtime and double time") that forecloses the interaction ambiguities I would otherwise expect in an overtime-pay spec. C1's rounding rule explicitly requires pricing "once" per category from weekly totals with halves-up rounding, closing the usual per-day-vs-per-week rounding ambiguity, and C3 enumerates refusal conditions precisely enough (including the true/false and decimal/exponent gotchas) that Python's json module naturally distinguishes the required cases.
>
> To stress-test for a real (not just cosmetic) ambiguity, I cross-checked the two independently written ground-truth models - checks/holdout/_model.py (walks the week minute-by-minute) and audit/_expect.py (computes per-day totals then applies the cap arithmetically) - against several thousand random and boundary weeks (including money/rounding) and found zero disagreements, which is strong evidence the G1/G2/G3/C1 interaction has only one correct reading. I also verified that every checks.toml `statement` matches what its script actually does, including exact case counts stated in several statements (e.g. H1's "66 weeks," H2's "15 fixed and 50 random," H3's "89 weeks," H4's "91 weeks and rates," H6's "Thirty-five kinds," X2's "Over 130") all matched by direct count. Promise coverage (G1-G3, C1-C3, S1-S4) is complete across V/H/X per checks.toml and gates_report.json, which already shows the mechanical gates passing (reference passes V/H/X, X covers every promise, every broken implementation is caught by X while several are deliberately left uncaught by V). I found no leakage of hidden-check specifics into the public checks or intent, and no check that tests something the intent does not state.
>
> The two issues I did surface are both about intent.md's illustrative completeness, not correctness: the four worked Scenarios never show the hardest case (G2 and G3 binding together in one week) worked out by hand, and none of them models a refusal the way S1-S4 model a payment. Neither blocks sealing; both are small, concrete additions to the Scenarios section. Task difficulty (strict JSON validation with the bool/float gotchas, a three-tier day/week/seventh-day split, and exact-fraction halves-up rounding) is appropriately scoped for a single competent engineer inside an hour, consistent with the layered V/H/X design already built for it.

## Issue 1 (gap, should-fix): accepted

**Where (verbatim):** tasks/T18-overtime-pay/intent.md, Scenarios section (lines 51-67, S1-S4)

**Problem (verbatim):** The four worked scenarios each exercise at most two of the three minute-splitting rules together (S1/S2 exercise G1+G2; S3 exercises G1+G3), but none is a week where G2 and G3 bind simultaneously: all seven days worked (so day 7 is a seventh-consecutive day contributing only overtime/double, per G3) *and* days 1-6 alone already total more than 2400 regular-candidate minutes (so G2's weekly cap also converts some of them to overtime). The prose in G2/G3 is precise enough that this case is not actually ambiguous (I cross-checked the holdout minute-by-minute model against the audit's independent aggregate model over several thousand random and edge-case weeks and found zero disagreements), and it is exercised by generated cases in checks/holdout/weekly.py and audit/week_mix.py (X6) - but a reader trying to hand-verify their own understanding of the hardest interaction has no worked number in intent.md itself to check against.

**Suggestion (verbatim):** Add a fifth scenario (or extend S3) such as minutes=[480,480,480,480,480,480,600] at some rate, with days 1-6 totaling 2880 regular-candidate minutes (480 of which convert to overtime under the 2400 cap) and day 7 as a seventh-consecutive day. Spell out the exact expected regular/overtime/double minutes and cents the way S1-S4 do.

**Disposition: accepted, with a new scenario S5.** The reviewer is right that intent.md has no worked week in which G2 and G3 both apply. A worked number for that case helps a builder check their reading of G2 and G3 together.

I did not use the reviewer's exact week. `[480, 480, 480, 480, 480, 480, 600]` is already a fixed case in H2 (`checks/holdout/weekly.py`). Printing it in intent.md would show the builder the input of a hidden check. I used the same shape with a 12-hour seventh day instead. Before the change, I logged every request that V, H and X send to the command, and `[480, 480, 480, 480, 480, 480, 720]` is not among them.

The week was also chosen so that the 40 hours run out exactly at the end of day 5. As a result, none of the broken implementations for G1, G2, G3, C1 or C3 changes the S5 response, and C2 changes only the JSON type of the cents. `broken/README.md` promises this for every scenario. It also means adding S5 to V does not make V catch more of the goal and constraint mistakes: the same five broken implementations pass V as before. If the week had run past 40 hours partway through a day, V would have started catching `broken/G2`, which checks the 40 hours only at the start of each day.

Changes made:

1. **intent.md.** New scenario after S4:

   > - S5: Six 8-hour days and a 12-hour seventh day at $22.50 an hour. The request
   >   `{"minutes": [480, 480, 480, 480, 480, 480, 720], "rate_cents": 2250}` gets
   >   `{"regular_minutes": 2400, "overtime_minutes": 960, "double_minutes": 240, "regular_cents": 90000, "overtime_cents": 54000, "double_cents": 18000, "total_cents": 162000}`.
   >   Days 1 to 6 have 2880 regular minutes under G1, so the 480 beyond 2400 are overtime. Day
   >   7 is a seventh consecutive day: its first 480 minutes are overtime and the other 240
   >   double time, and none of them count toward the 40 hours.

   Worked by hand: 40 hours at $22.50 is $900.00; 16 hours of overtime at $33.75 is $540.00; 4 hours of double time at $45.00 is $180.00; the total is $1,620.00. No rounding is involved. The reference, the H model (`checks/holdout/_model.py`) and the X model (`audit/_expect.py`) all give this response.

2. **task.json.** `S5` added to `promises`. The task now has 11 promises, within the protocol's limit of 5 to 12.

3. **V, P2 (`checks/public/scenarios.py`).** S5 added. TASK_SPEC.md requires V to cover the S scenarios. The statement now reads "The five example weeks in the intent get exactly the responses the intent gives, field for field."

4. **H, H7 (`checks/holdout/scenarios.py`).** S5 added, sent both as written and reordered and pretty-printed, like S1 to S4. The statement now says "five example weeks".

5. **X, new check X13 (`audit/scenarios.py S5`).** X13 covers S5 and uses the same three ways of sending the request as X9 to X12. Its expected response was copied from the S5 text in intent.md, not from H, so X stays independent of H.

6. **broken/S5/pay and broken/README.md.** A new broken implementation makes the mistake of not stacking premiums: when days 1 to 6 already hold more than 40 hours of regular time, it treats day 7 as an ordinary day. On S5 it pays 2400 regular, 1140 overtime and 60 double-time minutes, a total of 158,625 cents instead of 162,000. It still gets S1 to S4 right, since none of them is a seven-day week past 40 hours. It fails V (P2), is caught in X by X13 (and also fails X6 and X7), and fails H2, H3, H4 and H7. The README table has an S5 row, and its closing paragraph now says S3 and S5 also break G3 and refers to five scenario outputs.

## Issue 2 (gap, minor): accepted

**Where (verbatim):** tasks/T18-overtime-pay/intent.md, Scenarios section (lines 51-67) vs. Constraints C3 (lines ~40-45)

**Problem (verbatim):** Every S scenario demonstrates a successful/paid request; none demonstrates a refusal with a concrete request and its exit status, even though C3 states five distinct refusal conditions entirely in prose. Intent.md is self-contained for the 'paid' shape of the response but not for the 'refused' shape, so a reader has to infer the refusal example format solely from the check scripts rather than the intent.

**Suggestion (verbatim):** Add one short worked refusal example alongside S1-S4 (or in the C3 bullet), e.g. {"minutes": [480, -10, 0, 0, 0, 0, 0], "rate_cents": 1500} -> exit status 2, nothing on standard output, mirroring the S1-S4 request/response style for at least one invalid-input class.

**Disposition: accepted, with a worked example in the C3 bullet.** One part of the premise is not accurate: C2 already states the refused shape in full ("A refused request exits with status 2 and writes nothing on standard output"), so a reader does not have to infer it from the checks. Still, a concrete refused request next to the prose list costs one sentence, and it makes the intent's refusal side read as concretely as its paid side, so I accepted it.

I took the reviewer's second option and put the example in C3 rather than adding a scenario. The example is an instance of C3. A separate S promise would have needed its own broken implementation and its own V, H and X checks, and would have brought the task to the protocol's maximum of 12 promises without stating anything C2 and C3 do not already say.

Changes made:

1. **intent.md, C3.** Appended after "is not a whole number.":

   > For example, the request
   > `{"minutes": [480, -30, 0, 0, 0, 0, 0], "rate_cents": 1500}` is refused because day 2 is
   > below 0: the command exits with status 2 and writes nothing on standard output.

   I used -30 rather than the reviewer's -10. This request is exactly the "a negative day" case that the public check P1 already sends. So the example reveals no request that is not already visible to the builder, and V already checks it word for word.

2. **X, X2 (`audit/refusals.py`).** X2 now sends the C3 example exactly as written in intent.md and requires exit status 2 with standard output exactly empty. The rest of X2 ignores whitespace-only output, so this is stricter, matching the sentence "writes nothing on standard output". The X2 statement now also says: "the refused example in C3 exits 2 with nothing at all on standard output". X2 still sends 138 other invalid requests, so "Over 130" remains accurate. The change comes from intent.md, not from H.

   I checked it on a variant of the reference that writes a newline before exiting 2 on a refusal. X2 now fails that variant on the C3 example, and it still passes the reference.

3. **H was not changed.** H6 already refuses a negative day (`[480, -1, 0, 0, 0, 0, 0]`), and V checks the exact example. No check that already existed changed its outcome for the reference or for any broken implementation.

## Gate result after the changes

`python3 harness/gates.py tasks/T18-overtime-pay`:

```
T18-overtime-pay: PASS | promises 11 | V 3 H 7 X 13 checks | broken 11 (5 pass V)
```

The reference passes all 3 V, 7 H and 13 X checks, and `warrant check` returns 0. Each of the 11 broken implementations fails at least one X check that covers its promise: G1 (X3, X7), G2 (X4, X6, X7), G3 (X5, X7), C1 (X8), C2 (X1), C3 (X2), S1 (X9), S2 (X10), S3 (X11), S4 (X12), S5 (X13). As intended, five of them (G1, G2, G3, C1, C3) pass V, since V is deliberately incomplete. That is the same five as before the review.

Before the review the gate line was `promises 10 | V 3 H 7 X 12 checks | broken 10 (5 pass V)`. The review added one promise (S5), one X check (X13) and one broken implementation (`broken/S5`). The only other changes are to the contents of P2, H7 and X2 and their statements, the C3 sentence in intent.md, and `broken/README.md`.
