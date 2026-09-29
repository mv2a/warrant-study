# Review of T14-row-validator

Reviewer: an AI model, Claude Sonnet, not a human.
Resolver: an AI model (Claude Opus), acting in the resolver role for this task only.

Result after resolution: `python3 harness/gates.py tasks/T14-row-validator` reports PASS, with
12 promises, 2 V, 10 H and 16 X checks, and 9 broken implementations, 4 of which pass V. Every
broken implementation is still caught by an X check that covers its promise, and `warrant check`
returns 0.

Accepted: 2. Rejected: 1.

No X (audit) check was changed. The new holdout cases were written from the intent's wording
and use different values, and different places in the request, from the audit cases the
reviewer pointed to, so X stays independent of H.

## Issue 1: NaN/Infinity and integers near ±2**63 are tested only by X

Verbatim:

```json
{
 "where": "intent.md C4 (\"text that isn't a JSON object\", line ~52) vs. checks/holdout/refusals.py (H9) vs. audit/refusals.py:55-57 (X10) and audit/bounds.py CASE \"big integers\" (X4)",
 "problem": "Two edges of C4's refusal promise are tested only by the hidden audit suite and never by the dev-visible holdout (or public) checks: (1) Python's own json.loads accepts the non-standard literals NaN, Infinity and -Infinity by default (json.loads('{\"x\": NaN}') succeeds), so a straightforward `json.loads(sys.stdin.read())` implementation will silently validate these instead of refusing them — exercised only by 3 of X10's 112 cases; (2) exact-boundary comparison of integers right at ±2**63 (X4's \"big integers\" rule), which a naive float-based bounds comparison could get wrong through precision loss, appears only in audit/bounds.py and has no holdout analogue. Neither is stated as a special case in intent.md beyond the general \"text that isn't a JSON object\"/\"min...max\" wording, and a builder who passes every check they can see (V and H) has no signal that these traps exist before final scoring.",
 "suggestion": "Add at least one NaN/Infinity/-Infinity case to checks/holdout/refusals.py's REFUSED list, and one min/max case near ±2**63 to checks/holdout/range_allowed.py, mirroring the existing X10/X4 cases, so a builder can discover and fix these during development instead of only at audit time.",
 "kind": "gap",
 "severity": "should-fix"
}
```

Disposition: **accepted, with changes to H only.**

One correction to the framing: builders never see H. It is hidden and runs only in Warrant's
gate in conditions B and C. The gap is still real, because the spec asks H to be thorough on
invalid input and boundaries. Without these cases, the B and C gates had no way to report
either trap. I checked this with throwaway copies of the reference. One copy reads NaN and
Infinity the way Python's `json` module does by default. The other compares bounds as
floats. Each copy passed all of V and all of the old H, and failed only X10 or X4.

Changes:

- `checks/holdout/refusals.py` (H9): three new refused requests. They put NaN in a `min`,
  Infinity inside an `allowed` list, and -Infinity in a row value. X10 puts these literals in
  other places (NaN and Infinity in row values, -Infinity as a `max`). REFUSED went from 55 to
  58 cases, and the H9 statement in `checks/holdout/checks.toml` now says so.
- `checks/holdout/range_allowed.py` (H3): a new "bounds beyond float precision" set of 12
  cases on two rules. One is an integer field with min 2^55 + 1 and max 2^62 - 1. The other is
  a number field with min -2^53 and max 10^20. It checks the values on and one past each
  bound, where a float would round the value onto the bound. These are different magnitudes
  from X4's ±2^63, but they exercise the same promise, exact comparison by value. The H3
  statement and the script's summary line were updated.
- Results: the reference passes H9 and H3. The NaN copy now fails H9, and the float copy now
  fails H3, each only on the new cases.
- V was not extended. The spec keeps V deliberately incomplete, and V already covers C4
  through one refusal. intent.md was not changed for this issue. Standard JSON has no NaN or
  Infinity, so C4's "text that isn't a JSON object" already covers them. "Numbers are equal
  when their values are" and the inclusive bounds in G3 already require exact comparison.

## Issue 2: G3 is silent on Unicode normalization, but X5 and X6 assume none

Verbatim:

```json
{
 "where": "intent.md G3, lines 23-26 (\"Strings are equal only when they match exactly, case and spaces included\") vs. audit/allowed.py X5 lines 8 and 15 (NFD variable and the ñandú case) and audit/duplicate.py X6 lines 8 and 13 (NFD case)",
 "problem": "G3 says string equality is exact on \"case and spaces\" but is silent on Unicode normalization forms. X5 and X6 (audit-only, never mirrored in holdout or public checks) assert that a precomposed accented string (e.g. \"ñandú\") and its decomposed NFD equivalent (\"ñandú\") are NOT equal, even though they render identically. A competent engineer who reads \"match exactly\" as \"the same text a person would read\" and normalizes Unicode before comparing (a defensible choice for text matching) would pass every visible check and only fail this distinction at final audit scoring, for a rule intent.md never states.",
 "suggestion": "Add a clause to G3, e.g. \"strings are compared as their exact sequence of Unicode code points; composed and decomposed accent forms are not normalized and so do not match,\" and move at least one NFC/NFD case into checks/holdout (e.g. unique.py or range_allowed.py) so it is visible during development.",
 "kind": "ambiguity",
 "severity": "should-fix"
}
```

Disposition: **accepted, with changes to intent.md and H.**

The intent is the ground truth, and X5 and X6 test something the intent only implied. Reading
"match exactly" as "renders the same" is a defensible reading, so the intent now states the rule
outright. X5 and X6 already match the new wording and were not changed.

Changes:

- `intent.md` G3 now reads: "Strings are equal only when they match exactly, case and spaces
  included: they are compared as sequences of Unicode code points and never normalized, so an
  accented letter written as one code point does not equal the same letter written as a base
  letter followed by a combining accent. Numbers are equal when their values are, so `2` equals
  `2.0`." G4 defines equality "as in G3", so the rule carries over to duplicates.
- `checks/holdout/range_allowed.py` (H3): a new string field whose `allowed` list holds one
  composed entry (`über`) and one decomposed entry (`cafe` + U+0301). Five cases check both
  directions: each entry matches itself, and neither matches its other form. X5 uses `ñandú`,
  and only a composed entry.
- `checks/holdout/unique.py` (H4): three new rows in the unique `code` field. `ça` composed,
  then decomposed (no duplicate), then decomposed again (duplicate). X6 uses `é`. The H3 and
  H4 statements and the summary lines were updated.
- Results: the reference passes H3 and H4. A throwaway copy of the reference that normalizes
  strings to NFC now fails H3 and H4 on the new cases only. It also fails X5, X6 and X15.
- "Visible during development" does not apply here either: H is hidden from builders. The
  intent sentence is what every condition sees.

## Issue 3: overall size of the task, especially C4

Verbatim:

```json
{
 "where": "intent.md as a whole, especially the Constraints section (C4, lines 52-59) alongside the five Goals and C2/C3",
 "problem": "The task carries 12 promises, at the top of the study's 5-12 range, and C4 alone names roughly 15 distinct malformed-request categories (schema-list shape; rule name presence/emptiness/repetition; type presence/validity; the exact seven allowed rule keys; boolean-typed required/unique; numeric-typed min/max with field-type applicability and min≤max ordering; allowed-list non-emptiness and per-entry type conformance; rows-list-of-objects shape) on top of G1-G5's per-cell validation logic, C2's five-way precedence and C3's two-level sort. Implementing C4's refusal logic alone, correctly and exhaustively (including traps like the NaN/Infinity and big-integer points above), is comparable in scope to a small task by itself, which makes \"solvable by a competent engineer in under an hour\" (per TASK_SPEC.md's Honesty section) a stretch for the task as a whole.",
 "suggestion": "Consider trimming C4's scope — for example dropping the \"unknown rule key\" category and/or the \"min/max forbidden on string or boolean fields\" category (folding them into fewer, broader rules) — to bring total implementation scope back comfortably under an hour, or explicitly accept that this task intentionally sits at the top of the size range.",
 "kind": "difficulty",
 "severity": "minor"
}
```

Disposition: **rejected (no trimming).** I took the reviewer's alternative instead: the task
deliberately sits at the top of the size range, and it stays within the spec.

Reasons:

- 12 promises is inside the protocol's 5 to 12 range, and the gate accepts it.
- C4 is long but not open-ended. It lists every refusal category explicitly, so implementing
  it means following a checklist, not making design decisions. Each category is a one- or
  two-line check.
- I measured the size directly. I wrote a compact implementation of the whole task from
  intent.md (Python standard library, with `decimal.Decimal` for exact numbers and
  `parse_constant` to refuse NaN and Infinity). It has 69 non-blank lines, and the C4 part is
  about 25 of them. It passes all 2 V, 10 H and 16 X checks. It was a throwaway sanity check
  in a scratch folder, not part of the task. It supports the claim that a competent engineer
  can finish the task in under an hour.
- The two suggested cuts ("unknown rule key", and min/max on string or boolean fields) would
  also mean changing X10, X16, H9, the reference and `broken/C4` for a subjective concern
  that the reviewer rated minor. Refusing an unknown rule key is also a useful part of the
  task: it catches a misspelled `maximum` or `Required`, which would otherwise be silently
  ignored.
