# Review of T19-seat-groups

Reviewer: an AI model, Claude Sonnet, not a human.

Summary: 3 issues raised; 2 accepted and fixed, 1 rejected. After the fixes,
`python3 harness/gates.py tasks/T19-seat-groups` reports
`PASS | promises 10 | V 2 H 8 X 17 checks | broken 7 (4 pass V)`.

## Reviewer's overall view (verbatim)

> T19-seat-groups is a well-built task. intent.md is unusually precise where ambiguity commonly creeps in (it spells out the exact whole-number definition excluding bool/float/exponent, gives a worked G2 example, and states exit-code semantics exactly), the three S scenarios are internally consistent and hand-verified against the model in audit/_cases.py and audit/_audit.py, and I independently re-derived S1-S3 by hand and confirmed they match. checks.toml statements' claimed case counts (57, 119, 29, 48, 13, 10, 8, etc.) all check out against the actual scripts when executed, and gates_report.json confirms the reference passes V/H/X and every broken/ variant is caught by X for every promise (G1-G4, C1-C3). I found two concrete issues worth fixing before sealing: (1) X17's rejection of non-standard JSON tokens (NaN/Infinity/-Infinity) is not clearly required by intent.md's wording and is untested by V or H, so a natural, fully-compliant implementation risks a silent audit-only failure; (2) checks/holdout/_theatre.py's split_name() is more permissive (and less crash-safe) than audit/_audit.py's parse() for the same C1 seat-name-format promise, due to Python's str.isdigit() accepting non-ASCII digits. I also flag, at low confidence, that the combination of a real allocation algorithm with C3's dense validation surface may be near or past the one-hour budget and is worth a timed pilot check. I found no promise that a check fails to test at all, no check that tests something clearly outside the promises, and no leak of the hidden suites' specific cases through intent.md or checks/public.

## Issue 1 (ambiguity, must-fix): ACCEPTED

- **where**: intent.md (C1/C3) vs audit/checks.toml X17 vs audit/strict_json.py
- **problem**: C3 says a malformed request is refused 'when standard input is not JSON', but never says whether that means strict RFC 8259 JSON or whatever Python's json module accepts. Python's json.loads() accepts the bare tokens NaN, Infinity and -Infinity by default (they are not valid JSON but are a documented Python extension). X17 (audit/strict_json.py) requires the command to refuse these as malformed, but neither checks/public nor checks/holdout tests this at all. A competent engineer who reads C3 and reasonably implements 'parse with json.loads, catch JSONDecodeError' will pass every V and H check and only discover the discrepancy at audit time, with zero developmental signal. Since the protocol states 'ground truth is intent.md' and a check that disagrees with the intent should lose, this is exactly the kind of promise two competent engineers could read differently, and it risks an audit-only, silent failure of an otherwise fully compliant implementation.
- **suggestion**: Add one explicit clause to C1 or C3, e.g. 'standard input must be valid JSON per RFC 8259; the non-standard tokens NaN, Infinity and -Infinity, even where they would otherwise be ignored, make the input not JSON.' Alternatively, add at least one NaN/Infinity case to checks/holdout so builders get a signal before the sealed audit, or drop X17 if this strictness isn't actually intended.

**Disposition: accepted.** The strictness is intended (the reference already refuses these
words through `json.loads(..., parse_constant=...)`), so the fix is to state it in the
intent rather than drop X17. Changes:

1. `intent.md`, C3: added the sentence "Standard input is JSON only when it is valid JSON as
   RFC 8259 defines it: the bare words `NaN`, `Infinity` and `-Infinity`, which some JSON
   readers accept by default, make it not JSON, even where they stand in a field that would
   otherwise be ignored." X17 now tests a promise the intent states in so many words.
2. `checks/holdout/invalid.py` (H7): added three malformed requests holding `Infinity`,
   `NaN` and `-Infinity` in ignored fields, so the builder's gate in conditions B and C
   gives a signal before the audit. The cases were chosen to differ from X17's (different
   field names, values and nesting: a top-level `price`, a group `rating`, and a value
   inside a nested list), and X17 was not changed. The H7 statement in
   `checks/holdout/checks.toml` now says 51 malformed requests (was 48) and names the three
   new ones.

Verified: a copy of the reference that calls plain `json.loads(text)` (built in the
scratchpad, outside the task) now fails both H7 (3 cases) and X17 (3 cases); the reference
passes both.

## Issue 2 (gap, should-fix): ACCEPTED

- **where**: checks/holdout/_theatre.py:15-20 (split_name), used by checks/holdout/interface.py (H5) and checks/holdout/split.py (H3); contrast with audit/_audit.py:27-34 (parse)
- **problem**: split_name() validates the digits of an output seat name with `seat[1:].isdigit()`, but Python's str.isdigit() returns True for many non-ASCII decimal-digit characters (e.g. Arabic-Indic '١', fullwidth '１'), so a seat name like 'B١' would be wrongly accepted as a well-formed seat by H5/H3 even though C1 requires seat names 'written exactly' like B7. Worse, for digit-like characters that satisfy isdigit() but that int() cannot parse (e.g. superscript '¹'), split_name falls through to `int(seat[1:])` and raises an uncaught ValueError instead of returning None, which would crash the check script rather than report a clean failure. audit/_audit.py's parse() avoids both problems with an explicit ASCII-digit check. This makes holdout's verification of C1's seat-name format strictly weaker (and less robust) than audit's, for no stated reason.
- **suggestion**: Change checks/holdout/_theatre.py's split_name to use an explicit ASCII-only digit test (e.g. `seat[1:].isascii() and seat[1:].isdigit()`, or reuse audit/_audit.py's DIGITS-based check) so H is at least as strict and as crash-safe as X for the same promise.

**Disposition: accepted.** Confirmed before the fix: `split_name("B١")` and
`split_name("B１")` returned `(1, 1)`, and `split_name("B¹")` raised `ValueError`. Change:
`checks/holdout/_theatre.py` `split_name` now requires `seat[1:].isascii() and
seat[1:].isdigit()` (the reviewer's first suggestion, not a copy of the audit's code). After
the fix all three return `None`, `B7` and `Z50` still parse, and `A0`/`A01` are still
rejected. Only H changed; audit/_audit.py was not touched. H3 and H5 still pass on the
reference (31 interface requests; 52 generated splits).

## Issue 3 (difficulty, minor): REJECTED

- **where**: intent.md as a whole (10 promises: G1-G4, C1-C3, S1-S3), especially C3's validation surface combined with the G1-G4 seat-block/split/refuse algorithm
- **problem**: The task bundles a genuine multi-step allocation algorithm (booking order, frontmost-row/lowest-block search, last-resort split, two-reason refusal) with an unusually large and precise malformed-input surface (row/seat count bounds, exact whole-number typing that excludes bool/float/exponent, exact seat-name syntax with case/padding/whitespace rules, duplicate-id and duplicate-seat detection). Each piece is individually reasonable and intent.md is careful to remove ambiguity, but getting all of C3 exactly right (in particular the whole-number type check and the seat-name regex) on top of a correct allocation algorithm is a meaningful amount of careful work, and is plausibly at or beyond the stated 'under an hour' budget for a careful implementation plus self-testing against the three S scenarios.
- **suggestion**: If not already piloted with a timed run, do a quick timed pilot with a competent engineer; if it regularly runs past an hour, consider trimming C3 (e.g. drop the leading-zero/whitespace seat-name edge cases from the promise, keeping them only as bonus audit checks) rather than removing any of G1-G4.

**Disposition: rejected, no change.** Reasons:

1. The size of the work is modest. The whole reference is 153 lines (126 non-blank),
   including comments; all of C3 (`read_request` and its three small helpers) is about 80
   lines of straight-line checks including blank lines and comments, and each rule is one
   condition. The rules the reviewer singles out are each a single line: the
   whole-number test is `type(value) is int` (the intent already says true, false, 3.0 and
   1e1 are not whole numbers), and every seat-name rule (case, leading zero, whitespace,
   padding) is one `re.fullmatch(r"[A-Z][1-9][0-9]*", name)` plus a bounds check. The
   allocation is a row scan for a run of free seats and a first-free fallback. The intent
   spells each rule out, so there is little design work to do, and the three S scenarios
   are exact.
2. The proposed trim would break the protocol. Keeping the seat-name edge cases "only as
   bonus audit checks" would mean X checks something intent.md does not promise, and
   intent.md is the ground truth that X is scored against. The edge cases have to stay in
   C3 or leave X too. Removing them would weaken C1/C3 and save the builder almost nothing,
   since the one regex covers all of them.
3. A timed pilot with a human engineer is a study-level step, not something this resolver
   role can run or fake. The concern is recorded here so the study's pilot phase can time
   T19 along with the other tasks. If a pilot shows it regularly runs past an hour, the
   fix should be to trim C3 in intent.md and in H and X together, not to leave audit-only
   checks.

The low-confidence flag is noted, but no change is made to the task.

## Files changed

- `tasks/T19-seat-groups/intent.md` (C3: explicit RFC 8259 / NaN / Infinity clause)
- `tasks/T19-seat-groups/checks/holdout/invalid.py` (H7: three strict-JSON cases)
- `tasks/T19-seat-groups/checks/holdout/checks.toml` (H7 statement: 51 malformed requests)
- `tasks/T19-seat-groups/checks/holdout/_theatre.py` (`split_name`: ASCII digits only)
- `tasks/T19-seat-groups/gates_report.json` (regenerated by the gate run)

Not changed: `audit/` (X), `checks/public/` (V), `reference/`, `broken/`.
