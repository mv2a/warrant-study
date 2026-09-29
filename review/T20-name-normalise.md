# Review of T20-name-normalise

Reviewer: an AI model, Claude Sonnet, not a human.

The reviewer raised two issues. Both are accepted. Each issue is quoted verbatim below,
followed by its disposition.

## Reviewer's overall view (verbatim)

> T20-name-normalise is an unusually well-built task: intent.md's five goals are each backed by explicit worked examples, the audit suite (X1-X20) is independently derived from intent.md alone (its own _model.py, word lists and seeds, distinct from checks/holdout), every promise ID is covered by both H and X, checks.toml statements match what the code actually tests (verified counts on H1, H3, H5, H8), and subtle rule interactions (honorific removal vs. particle-position counting, particles' lack of the honorifics' optional-dot leniency, hyphenated words never containing particles, NFKD quirks like Cyrillic й losing its breve or capital-ẞ lower-casing to ß) are deliberately and correctly exercised rather than glossed over. I did not find any check that tests something the intent doesn't state, nor any content in checks/public or intent.md that leaks holdout/audit's specific generated cases. I found one concrete, verified ambiguity worth fixing before sealing (the Unicode-whitespace definition diverging from Python's native isspace()/\\s on the C0 separator controls U+001C-U+001F, untested by both suites) and one minor, already-acknowledged gap (multi-character case mappings like ß, which the audit's own code comments admit are dodged rather than resolved). Task size and interface/refusal semantics look appropriately scoped for an hour and are unambiguous.

## Issue 1 (verbatim)

```json
{
 "where": "intent.md G1 (\"Whitespace means any Unicode whitespace character...\"); checks/holdout/whitespace.py (H1); audit/whitespace.py (X5); audit/_model.py WHITESPACE constant",
 "problem": "G1 says whitespace is \"any Unicode whitespace character\" but never pins down what that means, and the two most natural Python implementations disagree on four code points. I verified programmatically: Python's str.isspace() and re's \\s (Unicode mode) both treat U+001C-U+001F (the C0 'file/group/record/unit separator' controls) as whitespace, but the formal Unicode White_Space property -- which is exactly the 25-character set hard-coded in audit/_model.py's WHITESPACE constant and reused by H1/X5 -- does not include them. So a builder who writes the obvious `name.split()` or `re.sub(r'\\s+', ' ', name.strip())` will silently diverge from the reference on these four characters, and neither H1 (\"12 fixed names and 150 generated ones\") nor X5 (\"each of the 25 Unicode whitespace characters... a zero width space and a word joiner do not split a word\") ever probes U+001C-U+001F, so the disagreement is never exercised in either direction. The checks' claim of exhaustively covering 'each Unicode whitespace character' is therefore overstated.",
 "suggestion": "Smallest fix: add one clause to G1 pinning the definition to the formal Unicode White_Space property and explicitly excluding the C0 separators, e.g. \"...meaning the Unicode 'White_Space' property (25 characters); the ASCII separator controls U+001C-001F are NOT whitespace even though some libraries' isspace()/\\\\s treat them as such.\" Then add one non-splitting case to H1 and X5, e.g. `\"anna\\x1cweber\"` must stay one word (`\"Anna\\x1cWeber\"`), not two.",
 "kind": "ambiguity",
 "severity": "should-fix",
 "short_summary": "G1 whitespace def diverges from Python isspace() on U+001C-001F, untested",
 "failure_scenario": "A builder implements G1 with `name.split()` (Python's default whitespace splitting). For input containing U+001C (File Separator), their implementation splits it into two words / strips it at the ends, while the reference (using the 25-member White_Space property) keeps it inside a single word. No check in checks/holdout or audit exercises U+001C-001F, so this divergence from the reference is never caught by either suite even though the checks claim to test 'each Unicode whitespace character.'"
}
```

### Disposition: accepted, with a different fix from the one suggested

The ambiguity is real. Checked on Python 3.13 (Unicode 15.1): `str.isspace()`, `str.split()`
and `re`'s `\s` all treat 29 characters as whitespace, the 25 with the White_Space property
plus U+001C to U+001F. One detail of the report is wrong: the reference uses `name.split()`,
so it splits on U+001C to U+001F. The audit model uses the 25-character set and keeps
them inside a word. The reference and the audit model therefore disagree on these four
characters. Neither suite sends them, so the gates never caught this.

Change made:

- intent.md G1 now says "Whitespace means any of the 25 characters with the Unicode
  White_Space property, including space, tab, line feed, carriage return and no-break
  space (U+00A0)."
- intent.md "Out of scope" gains: "Names containing the control characters U+001C to
  U+001F, which some programming libraries count as whitespace although they lack the
  Unicode White_Space property."
- The X5 statement in audit/checks.toml now reads "Each of the 25 characters with the
  Unicode White_Space property ...", which is what the check tests. No X case was changed.
  The audit/_model.py docstring now notes that intent.md puts the inputs its generators
  avoid out of scope.

Why this fix and not the suggested one. The suggestion pins U+001C to U+001F as
non-whitespace and adds cases to H1 and X5. That would make the obvious `str.split()`
implementation break G1. It would also mean changing the reference, and the scored
result would then turn on a detail of CPython's whitespace table. These separator
controls mean nothing in a person's name on a sign-up form, so a rule for them would
test library trivia rather than the newsletter team's intent. The G1 wording removes the
ambiguity about which characters are whitespace. The out-of-scope line removes the one
place where natural implementations disagree. Both natural implementations (`str.split()`
and a split on the 25 White_Space characters) are now conforming. With whitespace defined
as the White_Space property, the checks' claim to cover "each of the 25" whitespace
characters is exact.

I scanned all 1,817 names sent by the V, H and X suites through a logging wrapper. None
contains U+001C to U+001F, so no existing check tests an input that is now out of scope.
The reference is unchanged.

## Issue 2 (verbatim)

```json
{
 "where": "intent.md G3 (character-by-character upper/lower rule) and G5 (\"lower-cased character by character (so ß stays ß)\"); audit/_model.py docstring lines 1-7",
 "problem": "Neither G3 nor G5 says what happens when a character's Unicode case mapping isn't a single character or is context-dependent (German ß upper-casing to \"SS\" under Python's str.upper(), Greek final sigma, Turkish dotted/dotless I). The audit's own _model.py docstring admits the generators deliberately dodge this (\"never use a final capital sigma, a dotted or dotless I, a sharp s where G3 would upper-case it...\"), and indeed only the safe direction is tested (GROẞ -> Groß, lower-casing an already-uppercase ß). Two competent engineers could reasonably differ on a name whose first letter is ß: one calling ch.upper() naively gets \"SS\" (breaking the word's length and the \"first character is upper-cased, the rest lower-cased\" framing), another might special-case it to leave ß alone. This is nowhere declared in \"Out of scope,\" so it's an acknowledged-but-unstated hole rather than a deliberate scoping decision a reviewer can point to.",
 "suggestion": "Add one line to \"Out of scope\": \"Characters whose upper-casing is not a single character (such as ß) or is context-dependent (such as Greek final sigma) are out of scope; behaviour for them is undefined.\" This matches what the audit already does in practice and just makes it an explicit intent decision instead of an implicit one.",
 "kind": "gap",
 "severity": "minor",
 "short_summary": "Multi-char case mappings (ß, final sigma) undefined and untested",
 "failure_scenario": "Input name begins with ß (e.g. as the first letter of a word). One compliant-looking implementation calls Python's char.upper(), producing a 2-character \"SS\" where G3 implies a 1-for-1 per-character transform; another implementation leaves ß untouched. Neither H3/H9 nor X8/X9 contains a case where ß would need upper-casing, so this disagreement is invisible to every check, and there is no text in intent.md that would let a reviewer say which behaviour is correct."
}
```

### Disposition: accepted

This is confirmed. The reference turns "ßeta weber" into "SSeta Weber". An
implementation that leaves ß alone, or uses `str.lower()` on the rest of a word (Python
applies the final-sigma rule there), would differ, and nothing in the intent settles it.

Change made: intent.md "Out of scope" gains "Names in which G3 would change the case of a
character whose other case is more than one character or depends on the letters around
it, such as upper-casing ß (some libraries give SS, others keep ß), lower-casing İ, or
lower-casing a Greek capital sigma (σ, or ς at the end of a word). Lower-casing ẞ to ß,
and keeping ß in the key, are still settled by G3 and G5."

The suggested wording would have made "characters such as ß" out of scope as a whole. I
narrowed it to the case change that is actually ambiguous. That keeps the checks that
H5, X8 and X14 already make on ß inside a word and in the key ("GROẞ" becomes "Groß",
"straße" keeps ß) within scope. It also adds İ, whose lower case is two characters.
Turkish casing of the dotless ı is not listed. Its default Unicode case mappings are
single characters in both directions, so the intent already settles it.

The same scan of all 1,817 names sent by V, H and X found no name in which G3 would
upper-case a character whose upper case has more than one character, and none in which
it would lower-case İ or Σ. No name contains İ, ı, Σ or ς. ß appears in three names and
is lower-cased each time. No existing check tests an input that is now out of scope,
and no check or reference change was needed.

## Result

`python3 harness/gates.py tasks/T20-name-normalise` passes after the changes. See
tasks/T20-name-normalise/gates_report.json.
