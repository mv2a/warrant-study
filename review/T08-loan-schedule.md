# Review of T08-loan-schedule

- Reviewer: an AI model, Claude Sonnet, not a human. It worked as the independent reviewer under protocol §4.
- Resolver: an AI model, Claude Opus 5.5, not a human.
- Outcome: 2 issues accepted and fixed, 1 rejected. The gates were re-run after the fixes:
  `T08-loan-schedule: PASS | promises 10 | V 2 H 8 X 10 checks | broken 7 (2 pass V)`.

## Issue 1: accepted

Verbatim:

```json
{
 "where": "checks/holdout/refusals.py (H7), checks/holdout/interface.py (H1), checks/public/contract.py (P1); root cause in checks/public/_cmd.py and checks/holdout/_cmd.py's call() helper",
 "problem": "C1 promises a refused request \"exits with status 2 and writes nothing on standard output,\" but no public or holdout check actually verifies stdout is empty. call() collapses \"wrote nothing\" and \"wrote the JSON literal null\" into the same body=None (json.loads(\"null\") == None), and H7 doesn't even use that signal — it only checks whether the parsed body is schedule-shaped (is_schedule(body)), so any non-schedule JSON or text printed on a status-2 exit passes silently. Only the audit suite's raw-stdout check (audit/_batch.py's raw(), used by X1 and X7 as `out != \"\"`) actually enforces \"nothing\".",
 "suggestion": "Give public/holdout _cmd.py a raw-stdout accessor like audit's _batch.raw(), and change the refusal assertions in P1 (contract.py), H1 (interface.py) and H7 (refusals.py) to assert the raw stdout text is exactly \"\", the way X1/X7 already do, instead of testing body is not None / is_schedule(body).",
 "kind": "wrong-check",
 "severity": "must-fix"
}
```

**Disposition: accepted.** I reproduced it before changing anything. Two probe implementations (in the
scratchpad, not in the task) were copies of the reference changed in one way each. When a refusal
printed `null`, it passed P1, H1 and H7. When a refusal printed a plain-text message, it passed H7.
X1 and X7 caught both.

Changes:
- `checks/public/_cmd.py` and `checks/holdout/_cmd.py` gain `call_exact()`, which returns the exit
  status and standard output exactly as written, without trimming or parsing. `call()` is unchanged,
  as copied from the template.
- P1 (`checks/public/contract.py`) now requires status 2 and a standard output of exactly `""` for
  its two refusals. The statement now says "nothing at all on standard output".
- H1 (`checks/holdout/interface.py`) makes the same change for its eight refusals, and its statement
  is updated to match.
- H7 (`checks/holdout/refusals.py`) now requires status 2 and a standard output of exactly `""` for
  all 47 invalid requests, instead of only "not schedule-shaped". The statement now says "nothing at
  all on standard output". C3 says a refusal is "never scheduled", and C1 defines a refusal as exit
  status 2 with nothing written, so this is what the intent already required.
- The audit suite needed no change for this issue: X1 and X7 already compare the raw output with `""`.

After the change, both probes fail P1, H1, H7, X1 and X7. The reference still passes.

## Issue 2: accepted

Verbatim:

```json
{
 "where": "intent.md, constraint C1 (the request-shape sentence); untested in checks/public, checks/holdout and audit alike",
 "problem": "C1 says \"The request has three whole-number fields: principal_cents, ..., annual_rate_bp, ..., and months\" but — unlike the very next sentence about the response (\"The response has exactly the fields...\") — never states whether a request carrying an extra/unknown field (e.g. a stray \"currency\": \"USD\") must be refused or silently accepted. Two competent engineers could read this either way, and no check in any of the three suites sends a request with an extra field, so the ambiguity is never resolved or graded.",
 "suggestion": "Add one clause to C1 resolving it either way (e.g. \"A request object with any field beyond these three is refused\", or the opposite), and add one holdout case (mirrored in audit) exercising it, e.g. {\"principal_cents\":..., \"annual_rate_bp\":..., \"months\":..., \"extra\": 1}.",
 "kind": "ambiguity",
 "severity": "should-fix"
}
```

**Disposition: accepted.** I resolved it by stating that extra fields are ignored. I confirmed the
gap first: a probe that refuses any extra field passed every V, H and X check.

I chose "ignored" rather than "refused" for three reasons:
- C3's list of what counts as invalid does not mention extra fields, so "ignored" is the closer
  reading of the current text.
- The reference and all seven broken implementations already ignore extra fields. Each broken
  implementation therefore still breaks exactly the one promise it is named after, and
  `broken/README.md` stays accurate.
- It adds nothing to the build, which matters given issue 3.

Changes:
- `intent.md`, C1: after the three request fields, added "Any other field in the request is
  ignored: the loan is scheduled as if it were not there."
- H1 (`checks/holdout/interface.py`, covers C1): sends one loan (480000 cents, 399 bp, 60 months)
  five more times, each with extra fields added: a currency string, a null note, a fee with a list of
  tags, a field named `Months` with value 999, and a nested object. Some copies put the extra fields
  before the real ones. Each must exit 0 with exactly the response the command gives for the plain
  loan. The statement is updated to match.
- X1 (`audit/interface.py`, covers C1): written separately from H1, from the intent alone. It uses a
  different loan (2718281 cents, 314 bp, 120 months) sent as raw JSON text. The extra values are
  text, `true`, `null`, a fraction (`annual_rate_percent`), a nested object that holds `months` and
  `principal_cents`, a `months_label`, and fields named like response fields (`payment_cents`,
  `total_interest_cents`, `rows`). Each must exit 0 with exactly the plain loan's schedule. The
  statement is updated to match.

After the change, the strict probe fails both H1 and X1, and the reference passes both. This does not
conflict with the existing refusal cases: the X7 case with a misspelled `month` is still refused,
because `months` is missing from it.

## Issue 3: rejected

Verbatim:

```json
{
 "where": "intent.md as a whole (G1's exact-fraction requirement stacked on C3's full type/range validation matrix and G3's early-termination loop)",
 "problem": "Meeting G1's \"computed exactly\" level-payment formula without floating-point drift, on top of C3's exhaustive type discrimination (reject bool, null, float-with-.0, out-of-range, non-JSON, non-object, missing field) and G3's early-finish amortization logic, is a meaningfully bigger build than a typical under-an-hour task, even though Python's fractions.Fraction makes the exact math easy once a solver reaches for it.",
 "suggestion": "Either accept this sits at the upper end of the intended difficulty band, or nudge intent.md's opening paragraph to more explicitly foreshadow that exact rational arithmetic (not floating point) is required, so a builder doesn't spend part of the hour discovering that the hard way.",
 "kind": "difficulty",
 "severity": "minor"
}
```

**Disposition: rejected. No change was made.** I agree with the reviewer's first option: the task
sits at the upper end of the band but inside it. It stays unchanged for these reasons:
- G1 already says the payment "is computed exactly and rounded up to the next whole cent". The
  requirement is stated, not left for the builder to find.
- C3 lists every invalid input explicitly, so the validation cases are enumerated for the builder,
  not hidden.
- The complete reference is under 100 lines of standard-library Python. The exact payment and the
  interest rounding each take one integer expression.
- Adding "use rational arithmetic, not floating point" to the intent would turn a behavioural
  promise into an implementation instruction. It would also blunt what G1's near-whole-cent cases in
  H2 and X2 are meant to measure.
- The reviewer's own overall view was that "this task is not clearly oversized".

Resolving issue 2 as "ignored" adds no work for the builder.

## Reviewer's scope disclosure

The reviewer reported that it ran `ls` on `broken/` and read `broken/README.md`, both outside its
allowed reading scope. It said it did not use either as evidence and did not open `reference/` or any
broken implementation. None of the three issues depends on that file. Issues 1 and 2 were
reproduced independently here with probe implementations.

## Files changed

- `intent.md` (C1)
- `checks/public/_cmd.py`, `checks/public/contract.py`, `checks/public/checks.toml` (P1)
- `checks/holdout/_cmd.py`, `checks/holdout/interface.py`, `checks/holdout/refusals.py`,
  `checks/holdout/checks.toml` (H1, H7)
- `audit/interface.py`, `audit/checks.toml` (X1)
- `gates_report.json` (regenerated by `harness/gates.py`)
