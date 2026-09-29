# Review of T04-bill-split

- Task: `tasks/T04-bill-split`
- Reviewer: an AI model, Claude Sonnet, not a human.
- Resolver: an AI model, Claude Opus, not a human.
- Outcome: 4 issues raised, 4 accepted, 0 rejected. For issue 3 the notes went into the hidden manifests only, and the public manifest was left as it was on purpose (reason below). The gates were re-run after the changes. See the end of this file.

## Issue 1 (ambiguity, should-fix): accepted

Verbatim from the reviewer:

```json
{
 "where": "tasks/T04-bill-split/intent.md, C3 (\"two diners with the same name (names are compared exactly)\")",
 "problem": "The intent only states \"compared exactly\" in the duplicate-diner-name clause. It never restates that an item's `diner` field must match a listed diner's name exactly (same case, no trimming). Two competent engineers could read the qualifier as scoped only to duplicate detection and choose a looser match (case-fold or trim) when resolving an item's `diner` to a listed diner — which checks/holdout/invalid.py (\"an item whose diner differs only in case\") and audit/refusals.py's `for who in [\"galo\", \"GALO\", \"Galo \", \" Galo\", ...]` loop would then correctly fail, but only because the hidden suite enforces a rule the visible intent text doesn't clearly extend to this case.",
 "suggestion": "Reword the item clause in C3 to repeat the exactness rule, e.g.: \"...or whose `diner` does not exactly match (same case, no trimming) the name of a listed diner; two diners with the same name, compared the same way, ...\". A two-clause edit removes the doubt.",
 "kind": "ambiguity",
 "severity": "should-fix"
}
```

Disposition: accepted. The finding is correct. The parenthesis "(names are compared exactly)" was attached only to the duplicate-name clause. H7 and X7 both require an exact match for an item's `diner` too, and X8 requires that names differing only by case, a trailing space or Unicode form are accepted as different diners. The reference already compared plain strings, so its behaviour did not change.

Changes made:

- `intent.md` C3: the parenthesis is removed from the duplicate clause. The item clause now reads "whose `diner` is not exactly the name of a listed diner". One sentence was added that governs both uses: "Names are compared exactly as written, both when looking for two diners with the same name and when matching an item's `diner` to a listed diner: case, spaces and every other character count, and nothing is trimmed or normalized, so an item for `"ana"` or `"Ana "` does not belong to a diner named `"Ana"`." The words "nothing is ... normalized" also state in the text what X8 already assumed about Unicode forms.
- `checks/holdout/invalid.py` (H7): one case added, "an item whose diner has a trailing space" (`"Omar "` for the listed diner `Omar`). Before this, H7 tested only a case difference, so an implementation that trimmed but did not case-fold would have passed H and failed only X.
- Audit: no code change was needed, because X7 already tests `"galo"`, `"GALO"`, `"Galo "` and `" Galo"`. The X7 statement now names these ("an item for an unlisted diner or for a listed name differing only in case or a leading or trailing space") instead of the vaguer "differently-spelled diner".
- Verification: a scratch mutant of the reference that trims an item's `diner` before matching it now fails H7 (the new case) and X7. A scratch mutant that case-folds fails both too. The mutants were kept outside the task and deleted afterwards.

## Issue 2 (gap, minor): accepted

Verbatim from the reviewer:

```json
{
 "where": "tasks/T04-bill-split/checks/holdout/invalid.py and audit/refusals.py (both refusal suites' \"not an object\" cases)",
 "problem": "Intent C3 makes the \"is not an object\" rule symmetric between diners and items (\"a diner or an item that is not an object\"). The checks are not symmetric: both H7 and X7 test `(\"a diner that is true\", ...)` but neither ever tests an item that is `true`/`false`, nor a diner that is `false`. So one side of a symmetric promise has a small coverage gap versus the other. Risk is low in practice (a plain `isinstance(x, dict)` check rejects booleans for free, unlike the price/tip int-vs-bool cases which need special-casing), but it's an inconsistency worth closing for full parity before sealing.",
 "suggestion": "Add an `(\"an item that is true\", extra(\"items\", True))` case (and optionally a boolean-false diner/item case) to both invalid.py and refusals.py so items get the same boolean coverage diners already have.",
 "kind": "gap",
 "severity": "minor"
}
```

Disposition: accepted. One factual correction: H7 did not have a "diner that is true" case. Only X7 did. H7's entries that were not objects were a string diner and a number item. So H had no boolean entry case at all, and the gap was a little wider than the reviewer said. The reference already refused every one of these cases, because it tests entries with `isinstance(..., dict)`.

Changes made:

- `checks/holdout/invalid.py` (H7): two cases added, "a diner that is false" and "an item that is true". Each is placed as the second entry of H7's own Zara/Omar request.
- `audit/refusals.py` (X7): three cases added, "a diner that is false" (placed first in the list), "an item that is true" (placed second) and "an item that is false" (placed last). Together with the existing "a diner that is true", X7 now tests `true` and `false` for both diners and items. The inputs come from C3's "a diner or an item that is not an object" and "True and false are not numbers". Each is one change away from X7's own Galo/Suvi/Pim request, so no X request is the same as an H request, and X stays independent of H.
- Statements: H7 now counts 42 kinds of invalid request (39, plus these two, plus the one from issue 1) and names the boolean entries. X7 now counts 115 invalid requests (112 plus 3) and says "true and false included for both".
- Verification: a scratch mutant that silently drops boolean entries from `diners` and `items` now fails H7 and X7.

## Issue 3 (gap, minor): accepted, with the note placed in the hidden manifests only

Verbatim from the reviewer:

```json
{
 "where": "tasks/T04-bill-split/intent.md Scenarios S1-S3, replayed by checks/public/scenarios.py (P2), checks/holdout/scenarios.py (H9), audit/scenario.py (X10-X12)",
 "problem": "S1's diners are Ana, Ben; S2's are Ana, Ben, Cy; S3's are Ana, Ben, Cy, Dee — every scenario happens to list diners in alphabetical order. So the tie-broken cent in S2 and S3 goes to the same diner whether an implementation correctly uses \"listed earlier in `diners`\" (C2) or incorrectly sorts by name. The three scenario-replay checks (P2/H9/X10-12) therefore cannot, on their own, catch an alphabetical-order tie-break bug. This is not a hole in the overall suite — checks/holdout/leftover.py (H6) and audit/leftover.py (X6) both include hand-built cases with diners deliberately out of alphabetical order that do catch it — but a reviewer skimming only the scenario checks could mistakenly credit them with testing the tie-break rule.",
 "suggestion": "No code change needed given H6/X6 already cover it; consider a one-line note in checks.toml's P2/H9/X10-12 statements (or in a task-notes file) clarifying that the tie-break rule is exercised elsewhere, so a future auditor doesn't need to re-derive this.",
 "kind": "gap",
 "severity": "minor"
}
```

Disposition: accepted. The observation is correct. I confirmed that H6 fails the name-order tie-break (for example `['Zara', 'Beth', 'Mei']`), and that P2 passes it. The scenarios themselves were not changed. If S2 or S3 listed diners out of alphabetical order, the visible check P2 would start to catch the tie-break mistake. That would change what V reveals, and V is meant to be incomplete.

Changes made:

- `checks/holdout/checks.toml`: a comment above H9 says that S1 to S3 list their diners in alphabetical order, so H9 cannot tell a tie broken by listing order from one broken by name, and that H6 tests that rule.
- `audit/checks.toml`: the same comment above X10 to X12, pointing to X6. It names only X checks, so the audit manifest stays independent of H.
- The notes are TOML comments rather than extra words in the `statement` fields. A statement is meant to say exactly what the check does, and these checks do exactly what their statements say.
- `checks/public/checks.toml` (P2) is left unchanged, on purpose. The builder reads that file. A note there would point the builder at a gap in V and name the rule that V does not test, which would weaken the "deliberately incomplete" property the protocol requires of V. P2's statement already claims only that the three example requests get the intent's responses.

## Issue 4 (ambiguity, minor): accepted

Verbatim from the reviewer:

```json
{
 "where": "tasks/T04-bill-split/intent.md, C4 (interface)",
 "problem": "C4 never states the text encoding for stdin/stdout, yet audit/interface.py (X9) sends \"raw UTF-8\" non-ASCII names and several checks (X5, X8, H8) use non-Latin names (李雷, Ζωή, Zoë, Björn) and NFC/NFD Unicode forms. A competent engineer on a system with a non-UTF-8 default locale reading `sys.stdin` in text mode could plausibly mis-decode these and fail checks for reasons unrelated to the split logic itself.",
 "suggestion": "Add one clause to C4: \"input and output are UTF-8.\" Removes any locale-dependent ambiguity.",
 "kind": "ambiguity",
 "severity": "minor"
}
```

Disposition: accepted. H8, X5 and X8 send their non-Latin names as `\u` escapes, so the bytes on the wire are pure ASCII and the locale does not affect them. X9's pretty-printed request, however, is sent without escapes. Before this change it went through the shared `_cmd.py` helper in text mode, which encodes with the locale's encoding. So both the check and the reference depended on the machine's locale, and the intent said nothing about encoding.

Changes made:

- `intent.md` C4: "reads one JSON object on standard input and writes one JSON object on standard output, both as UTF-8 text".
- `audit/interface.py` (X9): the pretty-printed request with raw non-ASCII names is now sent as explicit UTF-8 bytes, and standard output is decoded as UTF-8, whatever the locale. This uses a small local helper next to the existing raw-bytes runner. The X9 statement and docstring now say so. Only the intent drove this change. H8 was not consulted for it and was not changed.
- `reference/split`: standard input is now read as `sys.stdin.buffer.read().decode("utf-8")` instead of in the locale's text mode. Invalid UTF-8 is refused as before, because `UnicodeDecodeError` was already caught. The output was already ASCII, which is valid UTF-8, because `json.dump` escapes non-ASCII by default. On a UTF-8 locale the behaviour is the same as before.
- `broken/*/split`: the same one-line change, so each broken implementation still differs from the reference only by its named mistake. The diff sizes against the reference are the same as before.
- `_cmd.py` in each suite was not changed. It stays a copy of `harness/_cmd.py.template`, which is shared by every task. It uses the locale's encoding, which is UTF-8 on the study machines, and Python uses UTF-8 under the C/POSIX locale too.
- Verification: under an ISO-8859-1 locale, the reference passes X9. A scratch mutant that reads standard input in the locale's text mode (the old reference) fails X9 there, and passes under the normal UTF-8 locale, as it should.

## Gates after the changes

`python3 harness/gates.py tasks/T04-bill-split` printed:

```
T04-bill-split: PASS | promises 11 | V 3 H 9 X 14 checks | broken 8 (4 pass V)
```

- The reference passes every V, H and X check.
- `warrant check` exits 0.
- Every broken implementation fails at least one X check that covers its promise:
  - G1: X1, X13
  - G2: X2
  - G3: X3
  - G4: X4, X14
  - C1: X5
  - C2: X6, X14
  - C3: X7
  - C4: X9
- The broken G1, G2, C2 and C3 implementations pass V.
- The number of checks in each suite did not change. H7 and X7 gained cases, and their statements now give the new counts (42 and 115).
