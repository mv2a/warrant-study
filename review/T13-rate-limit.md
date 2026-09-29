# Independent review of T13-rate-limit

- Task: `tasks/T13-rate-limit`
- Reviewer: an AI model, Claude Sonnet, not a human.
- Resolver: an AI model (Claude Opus), in the resolver role for this task.
- Result: 1 issue raised; 0 accepted, 1 rejected. Nothing in the task was changed. The
  validity gates pass (`python3 harness/gates.py tasks/T13-rate-limit`: PASS, promises 11,
  V 2, H 12, X 12 checks, broken 11, of which 3 pass V).

Reviewer's overall view, verbatim:

> T13-rate-limit is a well-constructed task: intent.md's promises (G1-G4, C1-C4, S1-S3) are precise and internally consistent, I hand-verified the token-bucket arithmetic for all three scenarios and several audit boundary cases against the stated formula and it matches exactly, every checks.toml statement I checked accurately describes its script's actual test logic (including exact case counts), all 11 promises are covered by the audit (X) suite per gates_report.json, every broken/<ID> variant is caught by an X check covering its promise, and the public checks (P1/P2) do not leak any holdout- or audit-specific constants (seeds, generated edge values) that would let a builder overfit. I found no promise a check fails to really test, no check testing something intent.md doesn't state, and no genuine reading ambiguity in the promises themselves (a few candidate ambiguities I chased down, e.g. whether G3's refill state updates on rejects, turned out to be either explicitly resolved by G4's retry-vs-wait clause or mathematically immaterial regardless of implementation strategy). The single actionable item is confirming the one-hour solvability empirically, given how much exacting validation and exact-arithmetic detail C1-C4/G2-G4/C2 combine into for one task.

## Issue 1: rejected

Raised verbatim:

```json
{
 "where": "tasks/T13-rate-limit/intent.md (Constraints C1-C4) together with checks/audit/invalid.py (89 invalid-input cases) and the exact-fraction refill math in G2-G4/C2",
 "problem": "The task bundles a large, exhaustive invalid-input type matrix (bool-vs-int exclusion, decimal/exponent exclusion, per-field null/missing/wrong-type checks across burst, rate, requests, client, at) with exact-fraction token-bucket arithmetic and a time-order check. Each piece is simple in isolation, but getting all of it bug-free (e.g. remembering Python's bool is a subclass of int, using Fraction/integer math instead of float to avoid drift) is a lot of exacting detail for the 'under an hour' honesty bound in TASK_SPEC.md, and nothing in the task directory (no timing note, no pilot log) shows this was empirically confirmed against that bound.",
 "suggestion": "Have a competent engineer build this from intent.md alone under a stopwatch before sealing. If it runs over an hour, trim C4's boundary matrix in intent.md (e.g. collapse the separate decimal-point and exponent-notation exclusions into one 'not written as a bare integer' rule) rather than cutting the G/C token-bucket promises, which are the task's core and are already well covered.",
 "kind": "difficulty",
 "severity": "should-fix"
}
```

Disposition: rejected. No change was made to `intent.md`, the checks or the
implementations.

The reviewer's statement of fact is correct. No human engineer has built T13 from
`intent.md` under a stopwatch, and none did so during this resolution. The resolver is an
AI model and cannot supply that measurement. The change the reviewer proposes, however,
depends on an overrun ("If it runs over an hour, trim ..."). There is no evidence of an
overrun, and the evidence the resolver could gather without a human points the other way.
The reasons are these.

1. **The size of the invalid-input matrix is on the test side, not the build side.** The 89
   cases in X2 (and the 37 in H8) are written by the task, not by the builder. What a
   builder must write for C4 is short. Python's `json.loads` already turns `2.0`, `2.5`,
   `1e3`, `NaN` and `Infinity` into floats, so one integer test that also excludes
   booleans (`isinstance(v, int) and not isinstance(v, bool)`, or `type(v) is int`)
   handles booleans, decimal points and exponents for `burst`, `rate` and `at` at once.
   The rest of C4 is one type check per field.

2. **The details the reviewer names as easy to miss are written into the intent.** C4
   says "true and false are not integers" and names 2.0, 2.5 and 1e3 as examples. C2 says
   tokens are "counted exactly, never rounded" and gives two worked examples (rate 3:
   rejected at 333 ms, accepted at 334 ms; rate 10: nine rejects and an accept at exactly
   100 ms). Because `burst`, `rate` and `at` are all integers, k + rate × (t − p) / 1000
   is exact when kept in integer thousandths of a token or as a `Fraction`. The exact
   version takes no more code than the float version. Whether a builder acts on promises
   that V does not test is what the study measures: `broken/C2` (floats) and `broken/C4`
   (booleans taken as integers) pass V by design. That is a question of attention, not of
   whether the task can be done in an hour.

3. **The proposed trim would not reduce the work.** "Not written as a bare integer"
   describes the same set of inputs as "a number written with a decimal point or an
   exponent". The same code satisfies both wordings, and X2 and H8 would test exactly the
   same cases. The trim would only remove the examples that make the rule concrete.
   Dropping the rule itself would change what H8 and X2 score, and the reviewer did not
   propose that.

4. **A pilot build passed every check on its first run.** The resolver wrote a pilot
   `limit` from `intent.md` in a scratch folder outside the study repository. It was not
   kept, and the task does not use it. It was written in a different style from
   `reference/limit`: `fractions.Fraction` for token counts instead of integer
   thousandths, and an `isinstance`-and-not-`bool` integer test instead of
   `type(v) is int`. It has 50 lines of code, not counting blank lines and comments. Of
   those, 25 do parsing and validation (C1, C3, C4) and 16 do the replay (G1 to G4, C2).
   Run against every check, it passed V 2 of 2, H 12 of 12 and X 12 of 12 the first time.
   This has two limits. The pilot was not blind, because the resolver had already read
   `reference/limit` and the checks. And a build by an AI model does not measure a human
   engineer's time. What it shows is the size of a complete solution, and that a second,
   natural approach to exact arithmetic passes all the checks. It does not replace the
   stopwatch pilot.

Left open for the operator: a human-timed pilot before sealing is still possible if the
operator wants one. If such a pilot ran over an hour, point 3 suggests looking at where
the time went before changing C4's wording, since that change would not shorten the build.
