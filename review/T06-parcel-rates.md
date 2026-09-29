# Review of T06-parcel-rates

Reviewer: an AI model, Claude Sonnet, not a human. The reviewer did not read `reference/` or
`broken/` and changed no files. The resolver (an AI model, Claude Opus) decided each issue
below and made the changes.

Result: 3 issues raised. Issue 2 and issue 3 were accepted. Issue 1 was rejected as stated,
because the parcels it describes cannot be carried, but looking into it turned up a real gap
next to it in the audit checks, and that gap was fixed.

## Issue 1 (gap, must-fix): rejected as stated; a related audit gap was fixed

Verbatim:

> **where:** audit/_audit.py (rounding_decides_carrying), audit/generated.py (near_limit_parcel, MODE=="limits"/"billable"), checks/holdout/limits.py, audit/dimweight.py, checks/holdout/billable.py
>
> **problem:** G1's ceiling rounding is never actually verified at the one point where it decides whether a parcel is carried at all. For a cuboid with volume 150,001-150,004 cm3, correct rounding (ceil(volume/5)) gives a dimensional weight of 30,001 g, just over the 30,000 g carry limit (C2), so a correct implementation must REFUSE it (status 2, empty stdout). An implementation that floors/truncates instead of ceiling at this one spot would compute 30,000 g and wrongly PRICE it. This is exactly the bug class the study is designed to catch (e.g. a carry-limit check written against an unrounded/differently-rounded dimensional weight than the one used for pricing), but no check anywhere can currently catch it: (1) audit/_audit.py's rounding_decides_carrying() explicitly excludes volumes 150,000-150,004 from every C2 check (X07's hand-picked SHAPES, X15's generated "limits" mode via `if not rounding_decides_carrying(p)`, and holdout H6 has no equivalent exclusion but also has no case in that exact 5-integer-wide volume window - its 80 random sides are drawn from a range up to 160x110x60=1,056,000, so landing in a 5-wide window by chance is negligible); (2) the G1 checks (H1/billable.py, X03/dimweight.py, X14/generated.py "billable" mode) can only observe billable_g through the `values()` judge, which only reads a priced response - but a correctly-implemented parcel in this exact window is refused, so its billable_g is never observable, and none of the hand-picked HAND/CHARGED cases in dimweight.py nor billable.py's hand cases target this window (the nearest hand case, (1,1,60,50,50,30000), sits at exactly 150,000 cm3, which divides evenly by 5 and therefore is NOT actually rounding-sensitive - flooring and ceiling agree there). Randomly generated G1 cases can't land there either, because random_parcel()/near_limit_parcel()'s "billable" mode only keeps parcels the oracle says are carried, which structurally excludes this window. Net result: an implementation could pass every single holdout and audit check while silently mispricing (in fact, wrongly accepting) parcels whose carry status hinges on this rounding, and no check would notice.
>
> **suggestion:** Add a small number of hand-picked cases - e.g. in checks/holdout/limits.py and audit/limits.py (or a new small check explicitly scoped to G1) - using a tiny actual weight (so the dimensional weight decides billable_g) and sides whose product is 150,001-150,004 cm3 (e.g. 150,002 = 2 x 75,001, or any convenient factoring), asserting the parcel is REFUSED with status 2, paired with the existing 150,000 cm3 case (must stay PRICED with billable_g 30,000). Since output is empty on refusal, this has to be phrased as a priced/refused check rather than a billable_g value check, and the check's statement/comment should say plainly that it is testing G1's rounding direction at the point it decides C2's outcome, so the exclusion in rounding_decides_carrying() is no longer a silent hole.

**Disposition: rejected as stated.** No parcel that is within the side limits has a volume of
150,001 to 150,004 cm3. Each of those volumes has a prime factor over 150: 150,001 is prime,
150,002 = 2 x 179 x 419, 150,003 = 63 x 2381 and 150,004 = 4 x 37,501. So any parcel with
one of these volumes has a side over 150 cm, and C2 refuses it for that side whatever the
rounding. The reviewer's own example sides (2 x 75,001) include a 75,001 cm side. An exhaustive
search of all side triples up to 150 cm confirms it. Rounding the dimensional weight up or down
therefore never changes whether a parcel is carried, and there is no behaviour here for a check
to catch. As a test, the resolver built the reviewer's exact mutant: the reference with only the
30,000 g test changed to use `volume // 5`. It passes every V, H and X check because its output
is the same as the reference's for every request, not because a check is missing. The
suggested cases would only test the 150 cm side limit again, which X07, X15 and H6 already do.

**Related gap found and fixed (X side, from intent.md).** The old `rounding_decides_carrying()`
also excluded volumes of exactly 150,000 cm3, which is a dimensional weight of exactly
30,000 g and therefore exactly at C2's weight limit ("a parcel exactly at a limit is
accepted"). The G1 judges excuse a refusal of a parcel that is exactly on a limit, leaving it to
C2, while the C2 checks skipped these parcels. So no X check required a light parcel with a
dimensional weight of exactly 30,000 g to be priced. A second mutant was used to test this:
it refuses when the dimensional weight is 30,000 g or more. It passed all 21 X checks and was
caught only by H3 and H6. Changes:

- `audit/_audit.py`: `rounding_decides_carrying()` is removed. In its place, a comment and an
  import-time assertion (a search of all side triples up to 150 cm) check the fact above,
  that rounding never decides C2.
- `audit/limits.py` (X07): no longer excludes any parcel. It adds four shapes, each in three
  side orders. Three are priced: a 1 g parcel of 125 x 40 x 30 cm (dimensional exactly
  30,000 g), a 29,999 g parcel of 75 x 50 x 40 cm, and a 30,000 g parcel of 80 x 75 x 25 cm
  (actual and dimensional both exactly 30,000 g). One is refused: a 1 g parcel of
  62 x 55 x 44 cm, a dimensional weight of exactly 30,008 g with no rounding. The statement now
  covers 33 shapes and 99 requests.
- `audit/generated.py` (X15): the `limits` mode now judges every generated parcel, and the
  statement no longer mentions the exclusion.
- `audit/checks.toml`: the header comment and the X07 and X15 statements are updated.

X07 now catches the at-limit mutant under C2. `broken/G1`, which floors everywhere, still
passes X07 and X15, so dropping the exclusion does not blame C2 for a G1 mistake. H already
covered this case (H6 prices a 1 g parcel of 100 x 50 x 30 cm), so H is unchanged. The new X
shapes were chosen independently of H and differ from its shapes.

## Issue 2 (ambiguity, should-fix): accepted

Verbatim:

> **where:** intent.md (C1, C3); checks/holdout/invalid.py; audit/invalid_values.py
>
> **problem:** intent.md never says whether a numeric field supplied as a JSON float literal that is mathematically a whole number - e.g. `"weight_g": 1500.0` or `"zone": 2.0` - counts as valid. C1 calls zone/weight_g/length_cm/width_cm/height_cm "the integer fields", which leans toward refusing 1500.0 (it isn't a JSON integer literal), but C3's own wording ("a weight or side that is not a whole number greater than zero") reads as a purely mathematical test, under which 1500.0 would be a valid whole number. Two competent engineers could reasonably land on opposite answers, and neither holdout nor audit ever exercises this: audit/invalid_values.py's BAD_ZONES includes fractional floats (2.5, 3.25) but no whole-number float (2.0), and BAD_NUMBERS for every measurement field includes 0.5/2400.5/etc. but never a whole-number float like 1500.0; checks/holdout/invalid.py's variant()/without() cases have the same gap. So an implementation that (incorrectly, by one reading) accepts `2400.0` for weight_g would pass every check in the suite.
>
> **suggestion:** Add one clarifying clause to C1 or C3 (e.g. "a value written with a decimal point, such as 1500.0, does not count as a whole number" or the opposite, whichever is intended), and add one case per affected field (plus one for zone) to both checks/holdout/invalid.py and audit/invalid_values.py using a whole-number float value, asserting the intended refused/priced outcome.

**Disposition: accepted.** The intended reading is the one C1 already leans towards ("the
integer fields"), and it is what the reference does. Changes:

- `intent.md` C3 gains the sentence: "The zone, weight and sides must be written as JSON
  integers: a number written with a decimal point or an exponent, such as 2.0 or 1.5e3, is
  refused even when its value is whole."
- `checks/holdout/invalid.py` (H7): 6 new refused cases: each of the five fields written as a
  whole float (2.0, 1200.0, 30.0, 20.0, 10.0) and `"weight_g": 1.2e3`. The statement now
  says 55 requests.
- `audit/invalid_values.py` (X09): 12 new refused cases, written from the intent with different
  values and literals from H: zone 3.0, 1.0 and 4e0; weight 2400.0, 1.0 and 2.4e3; length 32.0
  and 3.2e1; width 24.00 and 2.4E1; height 18.0 and 1.8e+1. These are sent as raw JSON text,
  because `json.dumps` would write every one of them as `x.0`. The statement now says 106
  requests.

No existing check sent a whole number written as a float, so no other check needed to change.

## Issue 3 (ambiguity, minor): accepted

Verbatim:

> **where:** intent.md, Constraints, C2
>
> **problem:** C2 says a parcel is refused when it has "a longest side over 150 cm, or a length plus girth over 300 cm", but does not restate that "length" here means the same thing G4 defines two paragraphs earlier ("The length is the longest side and the girth is twice the sum of the other two sides, whatever order the three sides are given in"). Read in isolation, C2's "length plus girth" could be misread as using the literal length_cm request field rather than the longest of the three sides. The checks already enforce the correct (G4) reading via side-order rotation in checks/holdout/limits.py and audit/limits.py (every SHAPE is tested in multiple/all side orders), so this is a documentation-clarity issue rather than an actual coverage gap - a builder who misreads it would be caught by holdout - but tightening the wording would remove the ambiguity up front.
>
> **suggestion:** Add a short parenthetical to C2, e.g. "...or a length plus girth (as defined in G4) over 300 cm", so C2 is self-evidently using the same longest-side/girth definition as G4.

**Disposition: accepted.** C2 now reads "... or a length plus girth (length and girth as G4
defines them) over 300 cm." This is a wording change only. The checks already test this
reading, so none of them changed.

## Gate result after the changes

`python3 harness/gates.py tasks/T06-parcel-rates`:
`T06-parcel-rates: PASS | promises 11 | V 3 H 8 X 21 checks | broken 7 (6 pass V)`.
The reference passes all 3 V, 8 H and 21 X checks, and `warrant check` exits 0. Each broken
implementation is caught by X checks covering its own promise and no others:
G1 by X03 and X14, G2 by X04 and X18, G3 by X05 and X19, G4 by X06 and X20, C1 by X01 and
X21, C2 by X07 and X15, and C3 by X09 and X16. Only broken/C1 fails V.

The resolver also ran three temporary mutants from the scratchpad, which were deleted after
the runs and are not part of the task:

- The floor-only-in-the-limit mutant from issue 1 passes every check. It gives the same
  output as the reference for every request.
- The mutant that refuses a dimensional weight of exactly 30,000 g is now caught by X07 and
  X15 (C2), as well as H3 and H6.
- A mutant that accepts whole numbers written as floats (such as `"zone": 2.0` or
  `"weight_g": 1.5e3`) is caught by H7 and X09 (C3).
