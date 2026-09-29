# Review of T16-invoice-number

Reviewer: an AI model, Claude Sonnet, not a human.

Resolver: an AI model (Claude Opus), working only inside `tasks/T16-invoice-number`.

Outcome: 3 issues raised, 3 accepted, 0 rejected. After the changes,
`python3 harness/gates.py tasks/T16-invoice-number` reports
`PASS | promises 12 | V 2 H 9 X 16 checks | broken 8 (7 pass V)`.

## Reviewer's overall view (verbatim)

> intent.md is precise and well-scoped (exhaustive continue/restart/refuse logic, explicit format grammar, concrete malformed examples, exact scenarios), and the holdout/audit suites cover all 12 promises with strong binary assertions and no leakage from public checks into hidden ones. Two clarifications should be made before sealing: intent.md is silent on how to handle non-UTF-8 stdin even though the audit (X12) enforces specific behavior there with no holdout check to surface it during development, and C2's ASCII requirement is stated only for digits even though the audit also demands ASCII-exact hyphens/letters. A minor documentation nit: H7's checks.toml statement omits that the script also re-verifies three valid requests. None of these are severe enough to indicate the task is broken (gates_report.json shows all gates already pass), but each is a place where a careful, spec-literal builder could reasonably diverge from what the hidden checks assume.

## Issue 1

- where: intent.md C4/C5 (silent on stdin encoding) vs. audit/undecodable.py (X12)
- problem: X12 (ground truth for scoring) requires that standard input which is not valid UTF-8 be refused with status 2 under both strict and surrogate-escape decoding (pinned via PYTHONIOENCODING). Nothing in intent.md says the input must be UTF-8, or that undecodable bytes must be treated as an ordinary refusal rather than left to crash; C4 only says 'text that isn't JSON' is refused, which presupposes you already have text. No holdout check exercises this case either (H1-H9 has no undecodable-input check), so the requirement is invisible during development and surfaces only in the hidden audit.
- suggestion: Add one clause to C4 (or C5), e.g. "standard input that cannot be decoded as UTF-8 text is refused the same way as text that isn't JSON," so the promise explicitly covers this. Optionally add a single holdout case (checks/holdout) exercising one invalid-UTF-8 payload so a builder can discover and verify this behavior before the audit runs.
- kind: wrong-check
- severity: should-fix

**Disposition: accepted.** X12 enforced a rule the intent never stated. Changes:

- `intent.md` C4 now begins "Invalid requests are refused: standard input that isn't valid
  UTF-8 (anywhere in it, even inside a field that would otherwise be ignored), text that
  isn't JSON, ...". C5 now says the command "reads one JSON object, written in UTF-8, on
  standard input". The "even inside a field that would otherwise be ignored" wording
  settles a question the clause would otherwise leave open, given that C5 says extra
  fields are ignored.
- `reference/next` read standard input in text mode, so its answer depended on the
  locale. In the C locale (surrogate escapes), a request that was valid apart from a
  non-UTF-8 byte in an ignored field was answered with status 0. That breaks the amended
  C4. X12 never sent that case, because every X12 payload is also invalid for another
  reason. The reference now reads `sys.stdin.buffer` and decodes it strictly as UTF-8,
  refusing with status 2 on failure. The same edit was made in all eight
  `broken/<ID>/next` copies. Each copy therefore still differs from the reference by its
  one named mistake only, which I confirmed with diff. `broken/README.md` needed no
  change.
- `checks/holdout/invalid.py` (H7) now sends six inputs that are not valid UTF-8 as raw
  bytes, under both `PYTHONIOENCODING=utf-8:strict` and `utf-8:surrogateescape`:
  - a broken two-byte sequence
  - the request in UTF-16 with a byte order mark
  - an overlong-encoded hyphen in `previous`
  - a stray continuation byte in `previous`
  - an encoded surrogate in `branch`
  - a Latin-1 byte in an ignored extra field

  Each one must be refused with status 2 and no output. The payloads come from the
  amended intent and differ from X12's. The old reference fails the ignored-field case
  under surrogate escapes, and the new reference passes all of them.
- The audit (X) was not changed. X12 already matches the amended intent, so nothing in X
  needed fixing, and X stays independent of H.

## Issue 2

- where: intent.md C2, lines 24-33
- problem: C2 explicitly restricts only the digits to ASCII ("Digits are only the ASCII characters 0 to 9") but says nothing equivalent for the hyphen or the three prefix letters. audit/malformed.py (X7) nonetheless refuses look-alike Unicode hyphens (–, ‐, −) and look-alike Unicode letters (Cyrillic/fullwidth homoglyphs for LIS/OPO/FAO/BRG) as malformed. A competent engineer could reasonably read C2 as scoping the ASCII requirement to digits only (since that's the only place it's stated) and, e.g., apply Unicode normalization or a lenient separator match without realizing that violates intent.
- suggestion: Broaden the ASCII sentence in C2 to the whole pattern, e.g. "Every character of a well-formed number -- the prefix letters and both hyphens, not only the digits -- must be its exact ASCII character; look-alikes are refused."
- kind: ambiguity
- severity: should-fix

**Disposition: accepted.** Changes:

- `intent.md` C2: "Digits are only the ASCII characters 0 to 9." now reads "Every
  character must be its exact ASCII character, not only the digits: the prefix's capital
  letters, the hyphen-minus `-` and the digits 0 to 9. Look-alikes, such as letters from
  another alphabet, fullwidth forms or Unicode dashes, are refused, never normalized."
  The list of lisbon examples was left as it was, so X7's statement ("every malformed
  previous number the intent lists for lisbon") is still true without editing X.
- `checks/holdout/malformed.py` (H5) now also sends seven look-alike spellings for lisbon
  2026:
  - a Greek capital iota
  - a fullwidth S
  - a non-breaking hyphen (U+2011)
  - fullwidth hyphen-minus separators (U+FF0D)
  - a small hyphen-minus (U+FE63)
  - a figure dash (U+2012)
  - a soft hyphen (U+00AD)

  None of these characters is used in X7, which uses Cyrillic and all-fullwidth prefixes
  and U+2013, U+2010 and U+2212. The H5 statement in `checks/holdout/checks.toml` now
  lists look-alike prefix letters and dashes. As a sanity test, a copy of the reference
  that NFKC-normalizes `previous` fails both the new H5 cases and X7.
- The reference already refused all of these, because its pattern uses `[A-Z]`, a literal
  `-` and `[0-9]` with `fullmatch`. X was not changed.

## Issue 3

- where: checks/holdout/checks.toml, H7 statement vs. checks/holdout/invalid.py
- problem: TASK_SPEC requires each checks.toml statement to say 'exactly what is checked.' H7's script also re-verifies three specific valid requests (lisbon at year 2000, year 9999, and a continuation to sequence 42) still succeed after running the invalid-input list, but the one-sentence statement only describes the refusals, not this sanity check on the valid path. A reader of checks.toml alone would miss that H7 also asserts something about valid requests.
- suggestion: Append a clause to H7's statement, e.g. "...; three known-good requests (year 2000, year 9999, and a continuation) still succeed."
- kind: other
- severity: minor

**Disposition: accepted.** The H7 statement now also describes the six undecodable inputs
added under issue 1, and it ends with "...; and three known-good lisbon requests (year
2000, year 9999, and a continuation from 41 to 42) still succeed."

## Verification

- `python3 harness/gates.py tasks/T16-invoice-number`: PASS. The reference passes V (P1,
  P2), H (H1 to H9) and X (X1 to X16). `warrant check` exits 0.
- Every broken implementation is still caught by an X check that covers its promise:

  | Broken | Caught by |
  | --- | --- |
  | G1 | X3 |
  | G2 | X4 |
  | G3 | X5 |
  | C1 | X6 |
  | C2 | X7, X8, X9 |
  | C3 | X10 |
  | C4 | X11 |
  | C5 | X2 |

  Seven of the eight pass V. broken/C1 does not.
- H7, H5, X12 and X2 were also run against the reference with `LANG`/`LC_ALL` set to
  `en_US.UTF-8` and to `C`. All pass under both locales.
