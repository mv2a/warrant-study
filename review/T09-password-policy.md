# Review of T09-password-policy

- Reviewer: an AI model, Claude Sonnet, not a human. It worked as the independent reviewer under protocol §4.
- Resolver: an AI model, Claude Opus 5.5, not a human.
- Outcome: 3 issues accepted and fixed, 1 rejected. The gates were re-run after the fixes:
  `T09-password-policy: PASS | promises 12 | V 3 H 10 X 13 checks | broken 12 (7 pass V)`.
- The audit suite (X), the public suite (V), the reference and the broken implementations are
  unchanged. The changes are in `intent.md` and the holdout suite (H).

## How the issues were tested

Before changing anything, I wrote probe implementations in the scratchpad, not in the task. Each
probe is a copy of `reference/policy` changed in one way. I ran every V, H and X check against each
one. The probes were:

- Whole-request normalization: the password, username and banned entries are normalized to NFC,
  NFD or NFKC as soon as they are read.
- Rule-only normalization: length is counted on the raw text, but the text is normalized to NFC,
  NFD or NFKC before the other rules. There is one probe per rule (`classes`, `username`, `repeat`,
  `banned`) and one that normalizes for all four.
- Python case mapping: `str.lower()` or `str.casefold()` instead of ASCII-only folding. This is done
  in the username rule only, in the banned rule only, and in both.
- Trailing content: parse the first JSON value with `raw_decode` and ignore anything after it.
- Leading content: drop everything before the first `{`.
- Wide strip: call Python's `str.strip()` before `json.loads`, which also removes a form feed and
  other non-JSON whitespace.

## Issue 1: accepted

Verbatim:

```json
{
 "where": "tasks/T09-password-policy/intent.md — G1 (\"Characters are counted as Unicode code points, not bytes\"), read against G2/G3/G4",
 "problem": "The code-point counting rule, and the (never-stated) no-normalization rule, appear once, attached to the too_short/too_long sentence in G1. \"Character\" is used again in G2 (\"every character belongs to exactly one of four classes\"), G3 (\"four consecutive characters of the username\") and G4 (\"the same character appears three or more times in a row\") without repeating or cross-referencing that convention. Two competent engineers could disagree on whether G3/G4 also operate strictly on raw code points, and whether input should be NFC-normalized before matching/counting (a common real-world password-hygiene step). The hidden and audit suites commit to one specific answer — raw code points, no normalization — via combining-mark cases: holdout/length.py's \"12 code points ending in a combining accent\", audit/length.py's DECOMPOSED cases, audit/username.py's \"combining accent splits/joins the run\", and audit/repeat.py's combining-mark and emoji-run cases. A builder who reasonably chose to NFC-normalize would fail several hidden/audit checks even though intent.md never rules that choice out, which directly conflicts with \"ground truth is intent.md\" since the intent itself under-specifies the behavior being scored.",
 "suggestion": "Move (or duplicate) the code-point sentence into the document's opening paragraph, before \"## Goals\", so it reads as a definition governing every later use of \"character\", and add an explicit no-normalization clause, e.g.: \"Throughout, a character is one Unicode code point; input is taken exactly as received and is never Unicode-normalized (NFC/NFD) before it is measured or compared.\"",
 "kind": "ambiguity",
 "severity": "should-fix"
}
```

**Disposition: accepted.** The intent never said whether text is normalized, and the scoring depends
on it. All 16 normalization probes fail X: X2 catches them for length, and X3 to X6 catch them for
the other rules. So X already scores a normalizing builder as wrong, but the intent never ruled that
choice out.

The probes also exposed a gap in H. Before the change:
- The rule-only NFC probe passed every V and H check and failed X3, X4, X5 and X6.
- The rule-only NFC probes for `classes`, `username`, `repeat` and `banned`, the NFKC probes for
  `repeat` and `username`, and the NFD probe for `username` each passed every H check.
- The whole-request NFC probe failed only H1, the length check.

Under conditions B and C, a builder who counted length on raw text but normalized for the other
rules would have passed Warrant's gate. X would still have scored the promises as broken.

Changes:
- `intent.md`: a new paragraph between the purpose paragraph and `## Goals`, so it governs every
  later use of "character":
  "Throughout, a character is one Unicode code point, and two characters are the same only when
  they are the same code point. Every rule judges the password, the username and the banned
  entries exactly as the request gives them: nothing is Unicode-normalized (to NFC, NFD, NFKC or
  NFKD), trimmed or otherwise rewritten before it is counted or compared. The only difference any
  rule ignores is the one G3 and G5 name, between upper and lower case ASCII letters."
  G1 keeps its own sentence and its `é` and `😀` examples, so the one promise that is scored on
  counting still states the rule itself. "Trimmed" is included because it follows from "exactly as
  the request gives them". The existing checks already require it: X2 counts leading and trailing
  spaces and tabs, X8 refuses a username with a trailing newline, and H5 and X6 treat spaces in
  banned entries as ordinary characters.
- H2 (`checks/holdout/classes.py`): 3 new passwords: an uppercase `E` followed by a separate
  combining accent (3 classes as given, 2 after NFC), a precomposed `É` (2 classes as given, 3 after
  NFD), and fullwidth `Ａ` and `１` (2 classes as given, 3 after NFKC).
- H3 (`checks/holdout/username.py`): 3 new requests with username `lopez`: `lope` followed by a
  separate accent (breaks the rule; NFC hides the match), a precomposed `é` (does not break it; NFD
  creates a match), and fullwidth letters (does not break it; NFKC creates a match).
- H4 (`checks/holdout/repeat.py`): 4 new passwords: `ööö` precomposed (a repeat; NFD removes it),
  `o` with a separate diaeresis three times (not a repeat; NFC creates one), three combining accents
  after an `a` (a repeat; NFC composes one of them), and fullwidth `ｘ`, `x`, fullwidth `ｘ` (not a
  repeat; NFKC creates one).
- H5 (`checks/holdout/banned.py`): 4 new requests: `Cre` with a separate grave accent against
  `cre` (breaks the rule; NFC hides the match), a precomposed `è` against `CRE` and against `cre`
  with a separate grave (neither breaks it; NFD and NFC create matches), and fullwidth `Ｌａｍｐ`
  against `lamp` (does not break it; NFKC creates a match).
- The H2, H3, H4 and H5 statements in `checks/holdout/checks.toml` now say that text is judged as
  given, without Unicode normalization.
- X is unchanged. It already enforces the rule for every probe. One detail of the reviewer's
  evidence is inaccurate. `audit/repeat.py` has no combining-mark case, and the combining-accent
  cases in `audit/username.py` give the same answer with or without NFC. X3 to X6 catch NFC through
  the Kelvin sign (U+212A), which NFC maps to ASCII `K`, and through generated cases. X2 catches it
  through its decomposed-accent length cases. This is enough, so X was not edited.

After the change, every normalization probe fails the H check for each rule it changes: H2, H3, H4
or H5, and H1 for the whole-request probes. The reference passes all of them.

## Issue 2: accepted

Verbatim:

```json
{
 "where": "tasks/T09-password-policy/intent.md — C1 (\"reads one JSON object on standard input\")",
 "problem": "The sentence doesn't say the whole of standard input must be exactly that one JSON object (surrounding whitespace aside). It could plausibly be read as \"parse the first JSON value found on stdin\", ignoring bytes after it (e.g. via a streaming/`raw_decode`-style parser). Holdout (checks/holdout/interface.py: \"two JSON objects\") and audit (audit/refusals.py: \"text after the object\", \"two objects\", \"two objects on two lines\") all treat trailing content as a refusal — the correct ground truth per the checks — but intent.md doesn't say so explicitly.",
 "suggestion": "Reword C1 to something like \"reads standard input as exactly one JSON object, with nothing else before or after it besides surrounding whitespace.\"",
 "kind": "ambiguity",
 "severity": "minor"
}
```

**Disposition: accepted.** I confirmed the gap first. The `raw_decode` probe, which accepts text
after the object, fails only H8 and X8. The probe that drops text before the first `{` passed every
V and H check. In X it failed only X8, through its "a comment before the object" case. (The reviewer placed the
"two JSON objects" case in `checks/holdout/interface.py`. It is in `checks/holdout/invalid.py`,
which is H8.)

Changes:
- `intent.md`, C1: "It reads exactly one JSON object on standard input, with nothing before or
  after it except whitespace (spaces, tabs, carriage returns and line feeds). The object has exactly
  three fields: ..." The rest of C1 is unchanged. The whitespace list is JSON's own definition of
  whitespace, so the sentence does not depend on how any language defines whitespace.
- `intent.md`, C3: the list of invalid inputs now begins "input that is not JSON, is not a JSON
  object, or holds anything but whitespace before or after the object". This makes it explicit that
  such input is refused.
- H8 (`checks/holdout/invalid.py`): 3 new refusals: the object followed by a comma and a second
  object, the object followed by a word on the next line, and a label before the object. The count
  in the H8 statement changes from forty-two to forty-five, and the statement now mentions text
  before or after the object.
- X is unchanged. X8 already refuses "text after the object", "two objects", "two objects on two
  lines" and "a comment before the object". X9 and H6 already require whitespace around the object,
  including CRLF, to be accepted.

After the change, both probes fail H8 and X8. The reference passes both.

One edge is still untested, on purpose. A builder who calls Python's `str.strip()` before parsing
accepts a form feed or a no-break space around the object, which the new C1 wording refuses. That
probe passes every V, H and X check. I did not add a check for it. It is an obscure corner, the
issue did not ask for it, and a check would add a trap that no reviewer found.

## Issue 3: accepted

Verbatim:

```json
{
 "where": "tasks/T09-password-policy/intent.md — G3/G5 (\"ignoring the difference between upper and lower case ASCII letters\"), tested by checks/holdout/username.py, checks/holdout/banned.py, audit/username.py, audit/banned.py",
 "problem": "The rule text is precise and the hidden/audit suites correctly probe it with non-ASCII look-alikes (Kelvin sign U+212A, long s U+017F, dotless/dotted i, sharp s, ligatures). But since the task's language is fixed to Python, this is a real implementation trap: Python's built-in `str.lower()`/`str.upper()`/`str.casefold()` are Unicode-aware and silently fold exactly these look-alikes to ASCII (verified interactively: `\"K\".lower() == \"k\"`, `\"ſ\".upper() == \"S\"`, `\"ẞ\".casefold() == \"ss\"`). A competent engineer reaching for the idiomatic `.lower()`/`.casefold()` to implement \"ignore case\" will silently fail several hidden/audit cases, and the public (V) suite (checks/public/*.py) never touches a single non-ASCII character, so the trap is invisible until the hidden gate.",
 "suggestion": "No wording change is strictly required (the rule as written is correct), but consider adding a clarifying clause such as \"(fold only A-Z to a-z; leave every other code point — including look-alikes such as the Kelvin sign — exactly as it is)\", or add one non-ASCII look-alike case to checks/public so builders can discover the requirement before the hidden gate rather than only from a failed run.",
 "kind": "difficulty",
 "severity": "minor"
}
```

**Disposition: accepted, using the first suggestion in different words. The second suggestion is
rejected.**

What changed in the intent:
- G3 and G5 now say "ignoring **only** the difference between upper and lower case ASCII letters".
- The definition paragraph added for issue 1 says that two characters are the same only when they
  are the same code point, and that the ASCII case difference is the only difference any rule
  ignores.

Together these state the rule as behaviour. A non-ASCII character that looks like an ASCII letter,
or maps to one under Unicode case mapping, is a different code point, so it matches only itself.

I did not use the reviewer's exact clause, for two reasons:
- "Fold only A-Z to a-z" is an instruction about implementation, not a behavioural promise.
- Naming the Kelvin sign would give builders one of the specific values that H and X probe.

I rejected adding a non-ASCII look-alike case to V. TASK_SPEC.md says V is deliberately
incomplete, so that a builder who satisfies only V can still break promises. The reviewer's own
overall view credits V for not leaking the hidden suites' look-alike characters. A V case would give
every builder, in every condition, the exact trap that H and X are there to measure.

The probes found a related gap in H, which I fixed:
- Before the change, H caught `str.lower()` and `str.casefold()` only in the banned rule (H5,
  through `cafÉ` and `STRASSE`).
- Probes that used them in the username rule only passed every H check and failed only X4.
- H3 (`checks/holdout/username.py`) gains 3 new requests. Username `kestrel` against `KEST` breaks
  the rule. Username `kestrel` against the Kelvin sign followed by `est` does not break it, which
  catches `str.lower()`. Username `castle` against `ca` + long s + `tl` does not break it, which
  catches `str.casefold()`.
- H5 (`checks/holdout/banned.py`) gains 1 new request: the Kelvin sign followed by `elp` against the
  entry `KELP` does not break the rule.
- The H3 and H5 statements name these cases.
- After the change, every case-mapping probe fails H3, H5 or both, according to the rule it
  changes, and still fails X4 or X6.

Disclosure: I wrote these H cases after reading X. X4 and X6 also use the Kelvin sign and the
long s, which are the standard examples of Python's Unicode case mapping. The H inputs (usernames,
passwords and entries) are different from X's. X was not changed.

## Issue 4: rejected

Verbatim:

```json
{
 "where": "tasks/T09-password-policy/intent.md and task.json — overall scope (12 promises: G1-G5, C1-C3, S1-S4)",
 "problem": "12 promises is the maximum TASK_SPEC.md allows (\"5 to 12\"), and a correct solution must simultaneously get right: code-point-vs-byte counting, a 4-way character classification, two separate ASCII-only case-folding rules (distinct from Python's own Unicode folding — see the prior finding), contiguous run-length detection, and a five-part JSON validation surface (type checks, missing/extra fields, username charset/length, banned-list shape/size) before combining five content rules into a sorted, de-duplicated output. This sits at the harder end of \"solvable by a competent engineer in under an hour,\" particularly to get every Unicode edge case right on a from-scratch implementation.",
 "suggestion": "Time an actual pilot solve before sealing the task. If it runs long, the lowest-risk trim is documentation, not scope: state the G1 code-point/no-normalization convention once at the top (finding 1) so implementers don't waste time guessing, rather than dropping a promise (dropping one would require re-deriving checks/coverage).",
 "kind": "difficulty",
 "severity": "minor"
}
```

**Disposition: rejected. No change was made for this issue.** The scope stays at 12 promises, for
these reasons:
- 12 is inside the protocol's band of 5 to 12. Four of the 12 are scenarios, which are worked
  instances of the goals and constraints, not extra work.
- The documentation trim the reviewer calls lowest-risk is done under issue 1. The convention is now
  stated once at the top, and G3 and G5 say exactly which case difference they ignore (issue 3).
- The work is small once the rules are read. The reference is 91 lines of standard-library Python,
  including its docstring. Each content rule takes one to three lines. C3 lists every invalid input
  explicitly, so no validation case is hidden from the builder.
- None of the added text creates new behaviour for the builder to implement. It only rules out
  readings the checks already scored as wrong.

I could not honestly supply the pilot solve the reviewer asks for. I have read the reference and the
H and X suites, so any time I measured would not be a builder's time. If the operator wants a pilot
before sealing, it needs a fresh builder that has seen only `intent.md` and `checks/public`. That is
left open for the operator. It is not a change to the task.

## Reviewer's overall view (verbatim)

> T09-password-policy is a well-built task. All 12 promises (G1-G5, C1-C3, S1-S4) are covered by at least one holdout and one audit check; the audit suite is genuinely independent (different seeds, different hand-picked cases, its own oracle in _audit.py) and each script self-validates its hand-written expectations against that oracle before running. checks.toml "statement" counts were spot-checked against the actual scripts (e.g. X8's "76 hand-written objects ... 21 texts ... 90 seeded mutations", X3-X6's hand-picked counts) and all matched exactly. The public (V) suite is appropriately thin and doesn't leak any of the hidden suites' specific edge-case values (look-alike characters, seeds, generation strategies). I did not find a "wrong check" — no holdout/audit check contradicts intent.md as written. The main finding is that intent.md's Unicode conventions (code points vs. bytes, and implicitly, no normalization) are stated once under G1 but silently relied on by G2-G4 and by many hidden/audit combining-character cases, which is a genuine ambiguity risk given "ground truth is intent.md." A second, smaller ambiguity concerns whether trailing content after the JSON object should cause a refusal. Two further notes (ASCII-only case folding being a Python `str.lower()` trap, and the task sitting at the upper end of the allowed promise count) are flagged as minor difficulty/fairness considerations rather than defects — the checks correctly enforce the letter of the spec in both cases, so no test needs to change, but intent.md could be a little more explicit to reduce illegitimate builder penalization.

Two corrections to the evidence the reviewer cited. Neither changes the findings:
- `checks/holdout/username.py` had no non-ASCII look-alike case before this resolution. It had
  only `é` between letters. H5 had `É` against `é` and `ß` against `SS`, but no Kelvin sign or long s.
- `audit/repeat.py` has no combining-mark case. Its non-ASCII cases are precomposed letters, the
  Kelvin sign, the dotless i, the no-break space, an Arabic-Indic digit, CJK characters and emoji.

## Files changed

- `intent.md`: a new definition paragraph before `## Goals`, plus changes to G3, G5, C1 and C3.
- `checks/holdout/classes.py` (H2), `checks/holdout/username.py` (H3), `checks/holdout/repeat.py`
  (H4), `checks/holdout/banned.py` (H5), `checks/holdout/invalid.py` (H8), and
  `checks/holdout/checks.toml` (the H2, H3, H4, H5 and H8 statements).
- `gates_report.json`, regenerated by `harness/gates.py`.
- Unchanged: `audit/`, `checks/public/`, `reference/`, `broken/`, `task.json`, `warrant.toml`.
