# Independent review of T02-library-fines

- Task: `tasks/T02-library-fines`
- Reviewer: an AI model, Claude Sonnet, not a human. The reviewer read intent.md,
  checks/public, checks/holdout and audit, and did not read reference/ or broken/.
- Resolver: an AI model (Claude Opus), in the resolver role for this task.
- Result: 2 issues raised; 2 accepted and fixed, 0 rejected. The validity gates pass after
  the changes (`python3 harness/gates.py tasks/T02-library-fines`: PASS, promises 10, V 2, H 8,
  X 17 checks, broken 7, of which 3 pass V).

The reviewer's overall view was that the task is well built, with no must-fix problems. It
hand-checked the arithmetic in the holdout and audit comments, found no check testing
something intent.md does not state apart from issue 1, and found no leakage of holdout or
audit inputs into the public material.

## Issue 1: accepted, with the bound stated in the intent

Raised verbatim:

```json
{
 "where": "audit/_audit.py, function refusal_problem (lines 74-88), used by X03 (audit/x_refusal_form.py) which audit/checks.toml documents only as \"...write a short non-empty reason, not a traceback, on standard error.\"",
 "problem": "The audit's operational definition of intent.md C1's \"gives a short reason on standard error\" is `len(reason) > 500` characters plus the substring \"Traceback\" — a concrete numeric threshold that appears nowhere in intent.md and is not even mentioned in X03's own checks.toml statement (which is supposed to say exactly what is checked). Since X (audit) is the ground truth used for scoring, this silently imports a stricter, undisclosed bar beyond what a builder can read in intent.md.",
 "suggestion": "Either state the bound explicitly in intent.md C1 (e.g. \"a short reason (well under, say, 200 characters), not a traceback\") so builders can target it, or drop the length assertion from refusal_problem and keep only \"non-empty, does not contain 'Traceback'\", and update the X03 checks.toml statement to name whatever is actually enforced.",
 "kind": "wrong-check",
 "severity": "should-fix"
}
```

Disposition: accepted. The reviewer is right on both points. The audit enforced a number the
intent never gave, and the statements of the checks that enforced it did not name it. Of the
two remedies offered, the first was taken: state the bound in the intent. Dropping the
length test would have left "short" in C1 as a word no check can decide, and the spec asks
that every promise be checkable by running the command. The "not a traceback" part was in
the same position: the audit tested for it and the intent did not say it. It is now stated
too.

Changes made:

- `intent.md`, C1: "gives a short reason on standard error" now reads "gives a short reason
  on standard error (at most 200 characters, not a traceback)". The bound is the reviewer's
  suggested 200 characters.
- `audit/_audit.py`: `refusal_problem` now tests the bound C1 states, through a constant
  `REASON_LIMIT = 200` marked as coming from C1, instead of the undisclosed 500. It reports a
  traceback and an over-long reason as separate problems. The test is on the reason with
  surrounding whitespace removed, so a trailing newline does not count.
- `audit/x_refusal_form.py` (X03): three refusals were added whose offending value is about
  300 characters long (a shared id, a type, and a day given as a string of digits). With only
  short inputs, X03 could not tell an implementation that keeps its reason within 200
  characters from one that copies the offending value into the reason.
- `audit/checks.toml`: the X03 statement now names what is enforced: a non-empty reason of at
  most 200 characters (surrounding whitespace aside) without the word Traceback, and the
  long-value cases. X04, X05, X06 and X07 use the same `refusal_problem` helper, so they
  also test the reason on standard error. Their statements said only "status 2 and no
  output", which is the same kind of undisclosed test the reviewer raised, so they now name
  the full refusal form as well. Their scripts and `covers` fields did not change.
- `checks/holdout/interface.py` (H6) and its statement: H6 covers C1 but tested only that a
  refusal's reason was non-empty. It now also requires at most 200 characters and no
  traceback, and it has two more refusals with a 450-character id or type (six refusals in
  all). These inputs were written for H and differ from X03's; X was changed only to match
  the intent, not by copying H.
- `reference/fine` and every `broken/*/fine`: the new X03 case showed that the reference
  broke the new bound. Its duplicate-id refusal copied the whole id into the reason (342
  characters for a 300-character id). The message is now "item N: its id is already used by
  an earlier item". The same line was changed in each of the seven broken copies, so each
  one is still the reference with exactly one mistake, in the promise it is named after
  (their differences from the reference are unchanged). No other reason from the reference
  includes a value taken from the request, so every reason stays within the bound.

## Issue 2: accepted

Raised verbatim:

```json
{
 "where": "intent.md, G1 (lines 14-16) versus G2 (lines 17-20)",
 "problem": "G1 multiplies a rate by \"its number of charged days\" before \"charged days\" has been defined — the grace-period rule that actually determines which late days count as charged only appears afterward, in G2. A reader taking G1 in isolation could momentarily read \"charged days\" as \"days late\" (i.e. skip the grace subtraction) since nothing in G1 points forward to G2.",
 "suggestion": "Add a one-clause forward reference in G1 (e.g. \"...times its type's daily rate; charged days are defined by the grace period in G2\"), or swap the order so the grace-period definition precedes the rate multiplication.",
 "kind": "ambiguity",
 "severity": "minor"
}
```

Disposition: accepted, using the forward reference rather than a reordering. G1 now reads:
"Before any cap, an item's fine is its number of charged days (the late days left after the
grace period in G2) times its type's daily rate." Reordering would have moved the rates away
from the promise the rate checks cover (X10, H1). No check changed, because the checks
already followed G2's definition of charged days.

## Gate result after the changes

`python3 harness/gates.py tasks/T02-library-fines` prints:

```
T02-library-fines: PASS | promises 10 | V 2 H 8 X 17 checks | broken 7 (3 pass V)
```

The reference passes every V, H and X check, including the changed X03 and H6, and `warrant
check` accepts the project. Every broken implementation is still caught by an X check that
covers its promise: G1 by X10 and X14, G2 by X11 and X14, G3 by X12 and X14, G4 by X13 and
X14, C1 by X03, C2 by X09 and X14, C3 by X06 and X07. The broken implementations for G3, C2
and C3 pass V, as before the changes. Before the reference was fixed, the new X03 cases made
it fail with a 342-character reason, which shows the added cases catch an implementation
that copies a long offending value into its reason.
