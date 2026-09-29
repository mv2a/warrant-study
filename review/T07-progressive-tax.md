# Review of T07-progressive-tax

- Reviewer: an AI model, Claude Sonnet, not a human.
- Reviewer's scope, as the reviewer reported it: intent.md, checks/public, checks/holdout and
  audit, all read in full. It did not open reference/ or broken/ and changed no files.
- Resolver: the task's resolver role, working only inside tasks/T07-progressive-tax.
- Result: 1 issue raised. 1 accepted, 0 rejected.

## Reviewer's overall view (verbatim)

> I reviewed T07-progressive-tax as the independent reviewer role: read intent.md in full, all of checks/public (contract.py, scenarios.py, checks.toml), all of checks/holdout (_model.py, bands.py, allowance.py, credit.py, rounding.py, figures.py, refusals.py, interface.py, scenarios.py, checks.toml), and all of audit (_model.py, _invalid.py, bands_edges.py, bands_random.py, allowance.py, credit.py, rounding_edges.py, rounding_random.py, figures.py, refusals.py, interface.py, accepted.py, scenario.py, checks.toml). I did not open reference/ or broken/, and made no changes to any file.
>
> Overall this task is high quality and close to ready to seal. The holdout and audit check suites were clearly built from two independently written models of intent.md (checks/holdout/_model.py and audit/_model.py), and every hand-computed table row I spot-checked (band edges, allowance-taper edges, half-cent rounding edges including 2**53+1 and 10**18-scale incomes, the S1-S4 scenarios) matches both models exactly, which is strong evidence the arithmetic promises (G1/G2/G3/C1/C2) are unambiguous and correctly encoded on all sides. Coverage looks complete: every promise (G1-G3, C1-C4, S1-S4) has at least one H check and at least one X check, check-count claims in checks.toml statements matched the actual generated case counts wherever I verified them (H1's 84, H2's 89, H3's 80, H4's 118/93/49, H6's 28/5, X9's 69), and I found no case where a visible/public check or intent.md leaks the specific seeds or generated values used by the hidden holdout or audit checks. The task's scope (four marginal tax bands, a linearly tapering allowance with ceiling rounding, a non-refundable per-dependent credit, half-up rounding, and a strict validate-or-refuse JSON contract) is meaningfully more involved than the example pricing task but still a single pure function with no state or I/O beyond stdin/stdout - I judge it solvable by a competent engineer within an hour, neither trivial nor oversized.
>
> The one concrete problem I found is a genuine ambiguity in intent.md's refusal rule (C3/C4) around JSON input with trailing content after the object, which only the audit suite (X1, X9) resolves one particular way, with no holdout or public check to let a builder discover that expectation earlier. See the filed issue for the exact lines and the smallest fix. I did not find any other must-fix ambiguities, mistested promises, over-reaching checks, or leaks in the three suites.

## Issue 1 (verbatim)

```json
{
 "where": "intent.md lines 34-45 (C3, C4) vs audit/_invalid.py lines 15-16 (used by audit/refusals.py = X9, and audit/interface.py = X1)",
 "problem": "Intent never states whether trailing content on standard input after a well-formed JSON object invalidates the request. C4 says the command \"reads one JSON object on standard input\" and C3 defines invalidity as a closed list (not a JSON object; missing/wrong-typed income_cents or dependents; negative income; dependents <0 or >20) ending with \"Every other request is taxed.\" Two of audit's 69 invalid texts are a syntactically valid JSON object followed by extra content: '{\"income_cents\": 4750000, \"dependents\": 3} {\"income_cents\": 1, \"dependents\": 0}' and '{\"income_cents\": 4750000, \"dependents\": 3} x'. X9 requires these be refused (status 2) and X1 additionally requires silent stdout for them. A competent engineer reading C3 literally could argue the opposite: the embedded object is well-formed with valid fields, so under \"Every other request is taxed\" it should be taxed, with anything after it on stdin simply unread/ignored (analogous to how C4 already says unknown JSON *fields* inside the object are ignored). Neither the public suite nor any holdout check (H6/refusals.py, H7/interface.py) exercises trailing data, so a builder gets no feedback on this specific expectation until the sealed audit run — the only place this interpretation is enforced.",
 "suggestion": "Add one explicit clause to C3 or C4, e.g. in C4 after \"reads one JSON object on standard input\": \"; any non-whitespace bytes after that object also make the request invalid.\" (or, if the intended behavior is actually to ignore trailing bytes, change X1/X9 and _invalid.py to drop those two cases). Also add one matching case to checks/holdout/refusals.py so builders can self-check this before the audit.",
 "kind": "ambiguity",
 "severity": "must-fix"
}
```

### Disposition: accepted, with changes

The issue is correct. "Not a JSON object" can reasonably be read as applying to the object
alone, so C3's closed list followed by "Every other request is taxed" did not clearly settle
what happens to input that has more after the object. The intended behavior is to refuse it.
The reference already does this (`json.loads` rejects extra data), and X1 and X9 already
expected it, so the fix is to make the intent say it and to let H check it. X keeps its
inputs.

Changes made:

1. `intent.md`, C3: the first invalidity case now reads "when standard input does not hold
   exactly one JSON object with nothing but whitespace before or after it (so any other text,
   or a second JSON value, after the object makes it invalid)". The rest of C3 and all other
   promises are unchanged. C4 still says the command reads one JSON object on standard input,
   which agrees with this.
2. `checks/holdout/refusals.py` (H6): added two invalid requests, a second object after the
   request and the word `end` after the request, and one valid request with whitespace before
   and after the object, so the rule is checked in both directions. These inputs (income
   3000000 with 0 dependents, then a second object or `end`, and income 3000000 with 1
   dependent surrounded by spaces, tabs and newlines) were written for H. They are not copied
   from X, which uses income 4750000 with 3 dependents followed by a second object or `x`.
3. `checks/holdout/checks.toml`: the H6 statement now says 30 invalid requests (was 28) and
   names the object followed by a second object or by text, plus whitespace around the
   object among the taxed cases.
4. `audit/checks.toml`: the X9 statement now names "one object followed by a second object
   or by other text" among its 69 invalid requests. `audit/_invalid.py` has a comment on
   those two existing cases pointing to the C3 rule. No X input, seed or count changed, and X
   was not edited to match H.

Not changed: the public suite (V) stays deliberately incomplete, as TASK_SPEC.md asks. It
has 2 checks and neither covers trailing input.

Verification: a throwaway copy of the reference that parses only the first JSON value
(`raw_decode`) and ignores the rest now fails both H6 (the two new cases) and X9 (its two
existing cases). The unmodified reference passes both.

## Gate result after the change

`python3 harness/gates.py tasks/T07-progressive-tax`:
`T07-progressive-tax: PASS | promises 11 | V 2 H 8 X 14 checks | broken 7 (6 pass V)`.
The reference passes every V, H and X check. Each of the 7 broken implementations (G1, G2,
G3, C1, C2, C3, C4) fails at least one X check that covers its promise. `warrant check`
returns 0.
