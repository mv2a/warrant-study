# Review of T12-course-grade

- Reviewer: an AI model, Claude Sonnet, not a human.
- Resolver: an AI model (Claude Opus), acting as the resolver for this task.
- Outcome: 3 issues raised, 3 accepted, 0 rejected. Gates re-run after the changes: PASS.

## Reviewer's overall view (verbatim)

> This is a carefully built task: every promise (G1-G4, C1-C3, S1-S3) has holdout and audit coverage with independently-styled oracles (checks/holdout/_oracle.py vs audit/_grade.py) that I hand-verified against intent.md's stated rules (weighting, drop-lowest-quiz, late penalty table, exact-fraction rounding with half-up, letter bands on the rounded percent) and found correct. Check statement counts (e.g. '37 kinds ... 4 valid edge cases', '17 kinds ... 13 kinds', '84 generated students, twelve in each band') match the code by direct count. No public-check or intent.md leakage of holdout/audit-specific edge values was found beyond the intent's own worked examples, which the builder is meant to know. Scope and difficulty look appropriate for an hour, given C1 explicitly warns against early/float rounding. I found one concrete scoring-consistency bug worth fixing before sealing (a stricter, inconsistent definition of 'writes nothing on standard output' in one audit check versus the rest of the suite), plus two minor clarity/documentation nits. None of these are blocking design flaws.

## Issue 1: accepted

Verbatim:

```json
{
 "where": "audit/interface.py:94 (X1, the REFUSED loop) vs. checks/holdout/invalid.py, checks/holdout/interface.py (H6/H7), audit/invalid_shape.py (X10), audit/invalid_values.py (X11)",
 "problem": "The audit's ground-truth check for the refusal shape (X1) uses `raw_call`, which does not strip stdout, and requires `out != \"\"` byte-for-byte for its 5 REFUSED cases. Every other refusal check in the whole suite (H6, H7, X10, X11 — 90+ refusal cases total) goes through `_cmd.call()`, which does `done.stdout.strip()` first and treats stdout that is pure whitespace (e.g. one trailing newline) as 'nothing'. So a `grade` implementation that emits a single trailing newline on refusal (very common, e.g. from a stray `print()`) would pass every visible and holdout refusal check but fail 5 specific cases in the audit (the only layer that is ground truth for scoring), for behavior the rest of the same audit suite treats as compliant with C3's 'writes nothing on standard output'.",
 "suggestion": "In audit/interface.py's REFUSED loop, change `out != \"\"` to `out.strip() != \"\"` (or route it through `_cmd.call()` / check `body is None`, like X10 and X11 do), so 'writes nothing' means the same thing everywhere in H and X for promise C3.",
 "kind": "wrong-check",
 "severity": "should-fix"
}
```

Disposition: accepted. Confirmed by reading the code: V (`checks/public/interface.py`), H6/H7
and X10/X11 all judge "no output" after stripping whitespace, and only X1's refusal loop
compared raw bytes. The decision rests on the intent, not on H: C3 defines standard output
as JSON text, and X1 itself already judges a success answer with surrounding whitespace
ignored (it parses the raw output with `json.loads`). Whitespace carries no JSON value, so
whitespace alone on a refusal is "nothing" in the same sense, and the audit layer should
not count a trailing newline as a broken C3 while its own X10/X11 accept it.

Change made:
- `audit/interface.py`: the refusal test is now `status != 2 or out.strip() != ""`, with a
  comment giving the reason. X1 still reads output through its own `raw_call`; nothing was
  copied from H.
- `audit/checks.toml` (X1 statement): "exits 2 with standard output completely empty" now
  reads "exits 2 with nothing but whitespace on standard output", so the statement says
  exactly what is checked.

Verified with throwaway copies of the reference outside the task: a copy that prints a bare
newline on refusal now passes X1 (and X10, X11); a copy that prints "refused" on refusal
still fails X1, X10 and X11. `broken/C3` (percent written as a string) is still caught by X1.

## Issue 2: accepted

Verbatim:

```json
{
 "where": "intent.md:35-40 (C2)",
 "problem": "C2 lists 'a score that is not a JSON integer from 0 to 100 (such as -1, 101, 87.5, 90.0, \"90\" or true)' as one invalidity condition in a list whose neighboring items are explicitly scoped ('a quiz or homework list', 'a homework entry'). Read on its own, it doesn't say whose score this covers; it only becomes clear that midterm and final are included by cross-referencing C3, which separately labels those fields 'a score'. Two competent engineers skimming C2 alone could disagree about whether midterm/final need the same integer-0-100/no-boolean validation as quiz and homework scores.",
 "suggestion": "Reword the C2 clause to name all four score sites explicitly, e.g. 'a quiz score, a homework score, a midterm or a final that is not a JSON integer from 0 to 100 (...)', so the scope doesn't depend on inferring it from C3.",
 "kind": "ambiguity",
 "severity": "minor"
}
```

Disposition: accepted. The meaning is unchanged (the reference, H and X already validate all
four sites the same way), but C2 should state its scope on its own.

Change made in `intent.md` (C2): "a score that is not a JSON integer from 0 to 100 (...)"
now reads "a quiz score, homework score, midterm or final that is not a JSON integer from
0 to 100 (such as -1, 101, 87.5, 90.0, "90" or true)". No check needed changing.

## Issue 3: accepted

Verbatim:

```json
{
 "where": "audit/checks.toml:87 (X11 statement) vs. audit/invalid_values.py `RAW` list",
 "problem": "X11's one-line statement says the check refuses 'NaN, Infinity and 7e1' as the extra raw-text cases, but the code's `RAW` list has four such cases, including a `days_late` of `-Infinity`, which the statement omits. TASK_SPEC.md asks a check's statement to say 'exactly what is checked'.",
 "suggestion": "Update the X11 statement in audit/checks.toml to '... and NaN, Infinity, -Infinity and 7e1 are refused ...' to match the code.",
 "kind": "gap",
 "severity": "minor"
}
```

Disposition: accepted. Confirmed: `RAW` in `audit/invalid_values.py` has four cases (a quiz
of NaN, a final of Infinity, a days_late of -Infinity, a midterm written as 7e1).

Change made in `audit/checks.toml` (X11 statement): "and NaN, Infinity and 7e1 are
refused" now reads "and NaN, Infinity, -Infinity and 7e1 are refused".

## Gates after the changes

`python3 harness/gates.py tasks/T12-course-grade`: PASS. Promises 10; checks V 2, H 9, X 15;
the reference passes every V, H and X check; `warrant check` exits 0; 7 broken
implementations, each caught by an X check covering its promise (G1 by X3, G2 by X4, G3 by
X5, G4 by X6 and X7, C1 by X8 and X9, C2 by X11, C3 by X1); 2 of them (G2, C2) pass V.
