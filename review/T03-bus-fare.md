# Independent review of T03-bus-fare

- Task: `tasks/T03-bus-fare`
- Reviewer: an AI model, Claude Sonnet, not a human. The reviewer read intent.md,
  checks/public, checks/holdout and audit, and did not read reference/ or broken/.
- Resolver: an AI model (Claude Opus), in the resolver role for this task.
- Result: 3 issues raised; 2 accepted and fixed, 1 rejected. The validity gates pass after
  the changes (`python3 harness/gates.py tasks/T03-bus-fare`: PASS, promises 10, V 2, H 9,
  X 12 checks, broken 7, of which 6 pass V).

## Issue 1: accepted

Raised verbatim:

```json
{
 "where": "tasks/T03-bus-fare/intent.md:35-37 (promise C1)",
 "problem": "C1 gives only one worked example of rounding a single trip's fare, and never says whether rounding is applied per trip or to the day's summed total. The two readings genuinely diverge: for three age-7 (child) trips each with an unrounded fare of 182.5 cents, rounding per trip gives 180+180+180=540, while summing first and rounding once gives 547.5→545 — a 5-cent difference in total_cents. A competent engineer implementing straight from C1 in isolation (without noticing that C3's fares_cents/'amount charged for each trip' and G4's per-trip cap language settle the question) could reasonably round the aggregate instead of each trip, and would only be caught by the hidden H5/holdout and X5/audit 'per-trip rounding' checks, not by the visible V checks (P1/P2 never exercise a case where the two orderings differ).",
 "suggestion": "Add one clause to C1, e.g. \"Each trip's fare is rounded on its own, before the trips are summed or capped,\" so the ordering is stated directly instead of only being inferable by cross-referencing C3 and G4.",
 "kind": "ambiguity",
 "severity": "should-fix"
}
```

Disposition: accepted. The order was only inferable from C3 and G4, and the audit check X5
asserts it directly, so the intent should state it. Change made to C1 in `intent.md`, using
the reviewer's wording: "Each trip's fare is rounded on its own, before the trips are summed
or capped." No check changed: X5 (`audit/rounding.py`) already tests per-trip rounding and
its statement already says so, and the reference already rounds each trip before adding it
to the running total and applying the cap. The caps (1100, 550, 440) are multiples of 5, so
rounding before capping never leaves a remainder that is not a multiple of 5.

## Issue 2: accepted, with the clause placed in C2 instead of C3

Raised verbatim:

```json
{
 "where": "tasks/T03-bus-fare/audit/refusals.py:35 (X6, covers C2) and checks/holdout texts",
 "problem": "The refusal checks include standard input that is a syntactically valid JSON object followed by trailing non-whitespace, e.g. '{\"age\": 47, \"trips\": []} {\"age\": 47, \"trips\": []}' and the same plus a trailing 'x', and require status 2. Neither C2 nor C3 (\"reads one JSON object on standard input\") explicitly says what must happen when stdin holds more than one JSON value or has non-whitespace trailing data — it is asserted only by the checks. In practice this is low-risk because any implementation that parses the whole of stdin with a standard-library JSON decoder rejects trailing data automatically, so it is unlikely to trip up a competent engineer, but it is still a concrete instance of \"a check testing something the intent does not literally state.\"",
 "suggestion": "Add a short clause to C3, e.g. \"Anything other than exactly one JSON value, optionally surrounded by whitespace, on standard input is refused,\" so the trailing-data behavior the checks assert is traceable back to the intent.",
 "kind": "gap",
 "severity": "minor"
}
```

Disposition: accepted. A check should not assert behavior the intent does not state. The
clause went into C2 rather than C3 because C2 is the promise that lists what is refused, and
X6, the check that asserts refusal of trailing data, covers C2. Tracing the check back
through its `covers` field then lands on the promise that states the rule. C2 now begins:
"That includes text that isn't exactly one JSON object, optionally surrounded by whitespace,
such as an object followed by a second object or by other text; ...". The statement of X6 in
`audit/checks.toml` now names "an object followed by a second object or other text" among
the refused inputs, so the statement says exactly what the check tests. The script
`audit/refusals.py` did not change. Only X6 tests trailing data. The holdout checks do not,
and they were not changed, which keeps X independent of H. The reference already refuses
these inputs because it parses the whole of standard input with `json.loads`, which accepts
whitespace around the value and rejects any other trailing text.

## Issue 3: rejected

Raised verbatim:

```json
{
 "where": "tasks/T03-bus-fare/intent.md (task as a whole: G1-G4, C1-C3)",
 "problem": "The task chains four interacting pricing rules (zone distance, a stateful 90-minute transfer window carried by an 'opener' pointer across trips, age-banded concession rounding, and a running daily cap applied trip-by-trip) on top of a strict, many-branched JSON validator (20+ distinct invalid-input categories in C2, each needing exact-type checks such as rejecting bool/float/string where an int is required). Each rule reads simply on its own, but correctly composing the evaluation order (transfer check → concession/rounding → cap, applied sequentially against a running total) plus covering the validation surface is a meaningful amount of design and self-testing for a one-hour budget.",
 "suggestion": "If a pilot build run shows testers routinely running over an hour, trim the validation surface (e.g. collapse some of the many 'value written as a non-integer' variants into fewer required checks) rather than the pricing rules, since the pricing interactions are the substance the study is meant to probe.",
 "kind": "difficulty",
 "severity": "minor"
}
```

Disposition: rejected, with no change now. The reviewer's suggestion depends on pilot
evidence that does not exist yet ("If a pilot build run shows testers routinely running over
an hour"). Nothing in the review shows that the task is over budget. The size of the task
points the other way. The complete reference implementation is about 110 lines of standard-
library Python. The whole of C2 is one parse function of about 30 lines, and every numeric
field goes through a single helper that checks for an exact integer in a range, so the
"20+ categories" reduce to presence checks for five fields, three container-type checks
(the request and each trip are objects, trips is a list), one type-and-range check applied
to four fields, and one ordering comparison. Pricing is a single loop of about a dozen
lines. Also, the non-integer variants are not separate things a builder has to implement:
they are several inputs to that one exact-type check, which the intent already asks for in
one clause. Trimming them from C2 now would weaken the intent and the X6 check without evidence
that they cost builders time. If a pilot shows builders over the hour, the reviewer's
proposed remedy is reasonable (trim validation, keep the pricing rules) and should be
decided then under the protocol, before sealing.
