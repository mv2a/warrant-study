# Review of T01-parking-fees

Reviewer: an AI model, Claude Sonnet, not a human.

Resolver: an AI model (Claude), acting in the resolver role for this task only.

Outcome: 4 issues raised, 4 accepted, 0 rejected. After the changes,
`python3 harness/gates.py tasks/T01-parking-fees` passes: 12 promises, V 3, H 10 and X 12
checks, 8 broken implementations, 5 of which pass V.

## Reviewer's overall view (verbatim)

> This is a well-built, internally consistent task. I hand-verified the four S1-S4 worked examples against the prose rules (G1-G5, C2) and they check out; the holdout oracle (_oracle.py, a minute-by-minute walk) and the audit oracle (_audit.py, closed-form arithmetic) are two genuinely independent restatements of the tariff and they agree on every case I traced, including the G4 boundary ("entering at exactly 02:00 counts, leaving at exactly 02:00 does not"). checks.toml statements accurately describe what their scripts do (I hand-counted several claimed case counts - H1's 16-130/2-6 hours/30 random, H2's twelve free/eleven charged, H8's thirty invalid/four valid - and they all matched the code). All 13 promises are covered by at least one V, H, and X check as required, and gates_report.json confirms the reference passes everything and every promise has a broken variant caught by its X check. The task is appropriately scoped for an hour: nontrivial (modular week arithmetic, daily cap, overnight counting, JSON validation) but bounded. I found one real spec ambiguity (unrecognized extra input fields are never addressed or tested), one test-design weakness (two holdout cases duplicate public ones verbatim, adding no hidden coverage), and two minor/cosmetic nits. None of these are severe enough to block sealing on their own, but the extra-fields gap is worth closing since it's a genuine two-readings ambiguity with zero check coverage either way.

Resolver's notes on the overall view: the task has 12 promises (G1 to G5, C1 to C3, S1 to
S4), not 13. The scenarios have no broken implementation, as `broken/README.md` explains, so
"every promise has a broken variant" holds for the eight goals and constraints only.

## Issue 1 (verbatim)

- where: intent.md C3 (line 49) and every refusal/interface check (checks/public/refusals.py, checks/public/contract.py, checks/holdout/refusals.py, checks/holdout/interface.py, audit/refusals.py, audit/contract.py)
- problem: C3's list of invalid requests reads as exhaustive (not a JSON object; missing entry/exit/lost_ticket; wrong type or out-of-range entry/exit; non-boolean lost_ticket) but never says what happens when the input object has an extra, unrecognized key alongside valid entry/exit/lost_ticket, e.g. {"entry":600,"exit":700,"lost_ticket":false,"note":"x"}. One competent engineer reads the C3 list as exhaustive and silently ignores unknown keys; another defensively refuses any object with an unexpected shape. No check in V, H, or X ever sends a request with an extra field, so neither reading is confirmed, and the audit (ground truth) cannot catch a wrong implementation of either choice.
- suggestion: Add one clause to C3 stating the intended behavior for unrecognized fields (e.g. "an object with extra fields beyond entry/exit/lost_ticket is accepted and the extra fields are ignored"), then add one holdout case and one audit case that sends such a request and asserts the chosen behavior.
- kind: ambiguity
- severity: should-fix

**Disposition: accepted.** Changes:

- `intent.md` C3 now ends: "Fields other than `entry`, `exit` and `lost_ticket` do not make a
  request invalid: they are ignored, and the request gets the same answer as without them."
  Ignoring was chosen because it is the reading of C3's list as exhaustive and it is what the
  reference already did, so the reference is unchanged.
- `checks/holdout/refusals.py` (H8): two requests with extra fields (extra text and number
  fields; extra fields placed first, including a nested object holding `entry` and `exit`, a
  null and a list) must get status 0 and exactly the answer of the same request without them.
- `audit/refusals.py` (X-C3), written from the new clause with its own inputs: five requests
  with extra fields (a text field; fields of every JSON type placed first and in between;
  fields named like the output fields; differently cased or spelled copies of the three
  fields holding invalid values; an extra field with a lost ticket) must each get the same
  status and output as the plain request. The comparison is the command against itself, so
  a fault in a money rule cannot fail X-C3.
- The H8 and X-C3 statements in `checks.toml` now say this.
- Checked with throwaway mutants outside the task: a command that refuses unknown fields
  fails both H8 and X-C3 and still passes V. X-C3 still fails only `broken/C3` among the
  broken implementations.

## Issue 2 (verbatim)

- where: checks/holdout/refusals.py lines 14 and 29 vs checks/public/refusals.py lines 7 and 9
- problem: Two of holdout H8's roughly thirty invalid-request cases are byte-for-byte identical to two of public P3's four cases: ("a missing lost_ticket", '{"entry": 600, "exit": 700}') and ("an exit of 10080", '{"entry": 600, "exit": 10080, "lost_ticket": false}'). Nothing secret leaks since the values are already public, but those two H8 entries add zero discriminating coverage beyond P3: a builder who special-cased P3's exact literal inputs, without generalizing the rule, would incidentally pass them too.
- suggestion: Change the entry/exit numbers in those two H8 cases to values that differ from P3's (e.g. a different entry/exit pair for the missing-lost_ticket and exit-10080 cases), keeping the same fault category so H8 still tests the same promise but with genuinely unseen inputs.
- kind: wrong-check
- severity: should-fix

**Disposition: accepted.** Changes in `checks/holdout/refusals.py` (H8): the missing
lost_ticket case is now `{"entry": 2300, "exit": 2475}` and the exit-of-10080 case is now
`{"entry": 4100, "exit": 10080, "lost_ticket": true}`. While checking this, the resolver found
two more holdout refusals that repeated public ones word for word, and changed them the
same way:

- H8's missing-exit case repeated P1's refusal (`{"entry": 600, "lost_ticket": false}`). It is
  now `{"entry": 3150, "lost_ticket": false}`.
- H6 (`checks/holdout/interface.py`) sent P3's missing-lost_ticket request
  (`{"entry": 600, "exit": 700}`) as one of its three refusals. It is now
  `{"entry": 4710, "exit": 4800}`.

Each keeps its fault category. No holdout refusal now repeats a public request.

## Issue 3 (verbatim)

- where: checks/holdout/checks.toml line 14 (H2 statement) vs checks/holdout/grace.py CHARGED entry (1000, 1000+1455, 1850, 600)
- problem: The H2 statement says the '24 hours 15 minutes' case checks '1850 cents' but doesn't mention the check also asserts overnight_cents == 600 at that same data point (the code compares the (time_cents, overnight_cents) pair). The prose under-describes what the check verifies; purely a documentation-precision gap, not a functional one.
- suggestion: Reword the H2 statement to '...and 24 hours 15 minutes at 1850 cents plus one night' so the statement matches what grace.py actually asserts.
- kind: other
- severity: minor

**Disposition: accepted.** The H2 statement now ends "and 24 hours 15 minutes at 1850 cents
plus one night." The resolver confirmed the stay (Monday 16:40 to Tuesday 16:55) contains
Tuesday 02:00, so one night is correct.

## Issue 4 (verbatim)

- where: intent.md C3 (line 49): "a JSON integer (written without a decimal point or exponent)"
- problem: By C3's own literal definition, the token "-0" is a legal JSON integer (no decimal point or exponent) numerically equal to 0, i.e. in range. No check in V, H, or X ever sends -0 for entry or exit, so this boundary token is untested, even though audit/refusals.py's NOT_INTEGER list is otherwise very thorough (it includes -0.0 but not -0).
- suggestion: Add "-0" as one more valid-extreme case (expect it treated as 0) in a holdout or audit interface/refusals check, or state explicitly in C3 that -0 is accepted as zero, to close the boundary rather than leave it implicit.
- kind: gap
- severity: minor

**Disposition: accepted, with both remedies.** A check against an unstated reading would be
unfair to the builder, so the rule is stated first and then tested:

- `intent.md` C3 now says: "An `entry` or `exit` written `-0` is the integer 0 and is
  accepted." This follows from C3's own definition of a JSON integer, and the reference
  already did it (Python's `json` reads `-0` as the integer 0). `-0.0` stays refused as a
  non-integer.
- H8 now sends `-0` as the entry (`{"entry": -0, "exit": 45, ...}`) and as the exit
  (`{"entry": 8000, "exit": -0, ...}`). Each must get status 0 and exactly the answer of the
  same request with 0.
- X-C3 sends `-0` as the entry, as the exit and as both. Each must get the same status and
  output as the request with 0. This holds even where 0 wraps into the following week (C2),
  so a C2 fault cannot fail X-C3.
- Checked with a throwaway mutant that refuses `-0`: it fails H8 and X-C3 and passes V.

## Gate result after the changes

`python3 harness/gates.py tasks/T01-parking-fees`: **PASS**. There are 12 promises, with V 3,
H 10 and X 12 checks. The reference passes every V, H and X check. Each of the 8 broken
implementations (G1 to G5, C1 to C3) is caught by the X check for its own promise. 5 of them
(G1, G2, G3, G4, C3) pass V. `warrant check` exits 0.
