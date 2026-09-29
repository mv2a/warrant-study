# Independent review of T15-unit-convert

- Task: `tasks/T15-unit-convert`
- Reviewer: an AI model, Claude Sonnet, not a human.
- Resolver: an AI model (Claude Opus), in the resolver role for this task.
- Result: 3 issues raised; 2 accepted and fixed, 1 rejected. The validity gates pass after
  the changes (`python3 harness/gates.py tasks/T15-unit-convert`: PASS, promises 11, V 3,
  H 9, X 12 checks, broken 8, of which 6 pass V).

Reviewer's overall view, verbatim:

> The task is well built: checks.toml `statement` fields were verified against their implementing scripts and all counts matched exactly (e.g. H7's 65/6, X7's 120/11, H4's "33 digits", H6/X6's 322 cross-kind pairs), and the two independently-written oracles (checks/holdout/_units.py and audit/_audit.py) derive identical exact Fraction tables for every unit, so there is no evidence intent.md is ambiguous enough to have caused H and X to diverge. gates_report.json confirms the reference passes every check and every broken/ implementation is caught by at least one X check. I found no check that tests something intent.md doesn't state, no wrong check, and no leak of hidden-check specifics into the public materials. The one substantive finding is a coverage gap: C1's "however many digits" promise is only stress-tested at Python's int-conversion ceiling (~4300 digits) by the audit-only X12, with nothing in holdout coming close (H4 tops out around 33 digits), so a builder has no way to discover that specific failure mode until the final, one-shot audit run. Two minor/should-fix items round out the review: an untested assumption that stdin whitespace padding is tolerated (tested by H8/X8 but never promised in C5), and an unaddressed duplicate-JSON-key edge case in C4. Task size and complexity (11 promises, exact rational arithmetic, JSON validation with several deliberate traps like bool-as-int and 2.0-vs-2) look appropriately scoped for a competent engineer inside an hour, aside from the X12 digit-limit trap noted above.

## Issue 1: accepted

Raised verbatim:

```json
{
 "where": "checks/holdout/exact.py (H4, covers C1) vs audit/long_amounts.py (X12, covers C1)",
 "problem": "C1 requires the converter to be exact \"however many digits the input has,\" and X12 deliberately tests amounts of 4400-4500 integer digits specifically because that exceeds Python's default int()/str() 4300-digit conversion ceiling (its own docstring says it \"fails any implementation that parses the amount with int() or Fraction() under that default\"). But H4 -- the only check available during the iterative build/gate loop, since per TASK_SPEC.md X is \"never run during development\" -- tops out at roughly 33 significant digits (whole up to 10**18 inclusive = 19 digits, fraction up to 14 digits; see exact.py lines 21-25). No public or holdout check comes anywhere close to the length needed to trip the Python digit-limit trap. A builder can therefore pass every check they are able to run during development and still fail X12 on the first (and only) audit run, with no prior signal that this specific failure mode exists.",
 "suggestion": "Add one case to checks/holdout/exact.py (or a new H check) with an amount longer than Python's 4300-digit int-conversion limit (e.g. ~4500 digits, mirroring audit/long_amounts.py's digits(4400)/digits(4500) cases), so this promise is discoverable during the holdout-gated development loop rather than only at final audit.",
 "kind": "gap",
 "severity": "should-fix"
}
```

Disposition: accepted. TASK_SPEC.md asks for thorough H checks, and C1 says in so many
words that the result must be right "however many digits the input has". An H check for C1
that never goes past 33 digits leaves the most concrete part of that promise untested in
the gated conditions (B and C). The gap was in H, so the fix is in H. X was not changed:
X12 already tests this, and it was written from the intent.

Changes made:

- `checks/holdout/exact.py` (H4) now adds four long amounts from their own seed
  (`random.Random(150415)`). The units, lengths and shapes were chosen for H, not taken
  from X12's cases. Each amount crosses Python's default 4300-digit limit on converting
  between text and int in a different way:
  - a 4800-digit whole number of yd to km at 12 places (too long to read);
  - `2.` followed by a 4450-digit fraction part, oz to kg at 12 places (the fraction part
    alone is too long, while the result is short);
  - a 4298-digit amount of m3 to floz at 6 places. The amount is under the limit, but the
    result has 4303 integer digits, so the limit is hit when the result is written;
  - 2600 digits on each side of the point, in to mi at 10 places. Each part is under the
    limit but the two parts joined are over it.
  None of the four is exactly halfway. The generator draws again if one is.
- `checks/holdout/_units.py` (the H oracle) lifts the digit limit with
  `sys.set_int_max_str_digits(0)` when Python has it, so that it can compute the expected
  results for these amounts.
- Failure messages in `exact.py` now shorten long amounts and results to their first and
  last digits plus a length, so the check still prints only a few short lines.
- The H4 statement in `checks/holdout/checks.toml` now describes the four long amounts
  exactly.

Verified: the reference passes the new H4. A copy of the reference with the digit limit left
at its default fails the first three long cases. A copy that also reads the amount by
joining the whole and fraction digits into one int fails all four. Among the broken
implementations, the ones for G1, G2, G3 and C1 fail H4 as before, and the ones for C2, C3,
C4 and C5 still pass it. `broken/README.md` therefore stays accurate. Every broken
implementation, like the reference, already lifts the digit limit.

## Issue 2: accepted

Raised verbatim:

```json
{
 "where": "intent.md C5 (line 47, \"It reads one JSON object on standard input\") vs checks/holdout/interface.py line 30 (H8) and audit/interface.py lines 20-28 (X8)",
 "problem": "Intent.md never states whether whitespace/newlines surrounding the JSON payload on stdin must be tolerated or could be treated as making the input something other than \"one JSON object.\" Both H8 and X8 independently test that leading/trailing whitespace and newlines around the object are accepted (H8's `padded` case, X8's multi-line/trailing-newline entries in `forms`), so this is being scored as a promise even though it is never written as one. In practice any implementation using a standard JSON parser gets this for free, so risk is low, but a literal reading of C5 doesn't establish it.",
 "suggestion": "Add a short clause to C5 (or a fourth scenario) stating that insignificant whitespace before or after the JSON object on stdin is ignored, so the promise that H8/X8 already test is actually written down.",
 "kind": "ambiguity",
 "severity": "minor"
}
```

Disposition: accepted. A check should not score behavior that the intent does not state.
C5 in `intent.md` now reads: "It reads one JSON object on standard input, ignoring any
whitespace before or after the object, with the fields ...". The clause sits in C5 because
H8 and X8, the checks that test padded input, cover C5. The H8 statement in
`checks/holdout/checks.toml` changed "padded input is read" to "a request with spaces and
newlines before and after the object is read", so it names the behavior plainly. The H8
script did not change. X8's script and statement did not change. Its statement already
counts the padded requests among "5 differently written but equivalent JSON requests". The
reference already behaves this way because it parses standard input with `json.loads`. The
clause only covers whitespace around an object. Input made only of whitespace is still not
a JSON object and is still refused under C4, which X7 checks.

## Issue 3: rejected

Raised verbatim:

```json
{
 "where": "intent.md C4 (malformed-request rules) -- no check file addresses this",
 "problem": "C4 lists every way a request can be malformed (non-object, missing/extra field, bad value, bad from/to, bad places) but never says what happens when the input JSON object has a duplicate key (e.g. `{\"value\":\"1\",\"value\":\"2\",\"from\":\"m\",\"to\":\"cm\",\"places\":0}`). No check in checks/public, checks/holdout, or audit exercises this. Because it is unstated, two implementations that build their own hand-rolled parser (rather than a standard JSON library) could legitimately disagree on whether to refuse or to apply last-key-wins.",
 "suggestion": "Either add one line to C4 clarifying duplicate-key behavior (most simply: silently defer to standard JSON semantics, i.e. last value wins) or add a single check case for it if precise behavior matters to scoring; otherwise leave as documented low-risk residual ambiguity.",
 "kind": "gap",
 "severity": "minor"
}
```

Disposition: rejected. No change was made, and this record documents the residual
ambiguity, which is the reviewer's third option. As the reviewer notes, no V, H or X check
sends a duplicate key. An implementation that refuses such a request and one that applies
the last value therefore get the same score on every check. The ambiguity cannot bias the
study's results.

Writing a rule into C4 would add a promise clause that is either untested, or tested only
with new H and X cases. TASK_SPEC.md asks that every promise be checkable by running the
command. New cases would test JSON parser details that have nothing to do with what this
task probes: exact arithmetic, rounding once, and the listed malformed forms. Either choice
of rule would also add work for some builders. "Refuse" would force the many builders who
use `json.loads` to add an `object_pairs_hook`. "Last value wins" would constrain the rare
hand-written parser. That work would earn nothing the study measures. Behavior on duplicate
keys is left open and unscored.
