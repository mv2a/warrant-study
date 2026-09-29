# Review of T10-free-slots

Reviewer: an AI model, Claude Sonnet, not a human.
Resolver: an AI model (Claude Opus), who could read everything in the task.

Four issues were raised. All four were accepted. The issues are copied below exactly as
the reviewer wrote them, each followed by its disposition.

## Issue 1

```json
{
 "where": "intent.md — overall task concept (G1, G2, G3 together)",
 "problem": "The core promise — take each person's busy intervals, union them, take the complement inside the working hours, and keep stretches at least min_length long — is structurally the same problem as the well-known \"Employee Free Time\" kata (LeetCode 759 and its many clones/interview-prep copies). TASK_SPEC.md's own rule says a task \"must be newly written for this study: do not reproduce a known kata, textbook exercise or anything from the Warrant repository.\" The JSON stdin/stdout framing, the min_length threshold, and the large C4 validation surface are genuine additions, but the algorithmic heart is not new, which risks a builder (or a model that has memorized this kata) solving it from prior exposure rather than from the stated promises — undermining what the study is trying to measure.",
 "suggestion": "Before sealing, either (a) add a structural twist that changes the shape of the core algorithm (e.g. per-person working windows, ranking/selecting among slots, or some other change that isn't just cosmetic), or (b) explicitly record that provenance was checked and the min_length filter plus the validation rules were judged to make it sufficiently distinct, so this doesn't surface later as a study-validity objection.",
 "kind": "other",
 "severity": "must-fix"
}
```

**Disposition: accepted, option (a).** The resolver agrees that the old core (union of
busy time, complement inside the working hours, then a length filter) was LeetCode 759,
Employee Free Time, plus small additions. Option (b) was not taken because the length
filter and working-hours clipping are minor additions (LeetCode 1229, Meeting Scheduler,
already has a duration), so calling the task distinct on that basis would not hold up.

The twist is a required `quorum` field: the fewest of the listed people who must be free
at every minute of a slot. A free minute is now one when at least `quorum` people are
free, not one when nobody is busy. So the task can no longer be solved by merging
everyone's intervals. It needs a count of busy people per minute, or a sweep over
per-person busy time. The twist also brings two new traps that the kata doesn't have:

- One person's overlapping or repeated intervals must count as one busy person, while
  the same meeting in two people's lists counts as two (C2).
- A free stretch must come back as one slot even when the people who are free change
  inside it. A sweep that reports each piece between neighbouring events cuts the
  stretch into pieces (G3).

When `quorum` equals the number of people, the task reduces to the old one. So the old
promises about touching, nesting, clipping, thresholds and validation still apply
unchanged.

Changes made:

- `intent.md`:
  - The purpose and the definition of a free minute and a free stretch are rewritten.
  - G1 now says a minute is free when at least `quorum` of the listed people are free
    there. People with no busy intervals count toward the quorum.
  - G3 adds "even when the people who are free change partway through it".
  - C1 now says a person is free again at the minute their meeting ends.
  - C2 now says a person counts once however many of their own intervals cover a minute,
    and that the same meeting in two lists makes two busy people.
  - C3 now says a meeting "makes its person busy" for the part inside the working hours.
  - C4 adds a missing `quorum` and a `quorum` that isn't a whole number from 1 up to the
    number of people.
  - C5 adds the `quorum` field.
  - S1, S2 and S3 gain a `quorum` equal to the group size, so their answers are
    unchanged.
  - A new scenario, S4 (four people, quorum 3, and the same request with quorum 4), is
    added. The task now has 12 promises. S4 uses `min_length` 45, so none of its slots is
    exactly `min_length` long. Like S1 to S3, it therefore doesn't show the G2 boundary in
    the public checks, and V stays deliberately incomplete for G2.
  - "Saying which people are free in a slot" is added to the out-of-scope list.
- `task.json`: S4 is added.
- `reference/slots` is rewritten. It merges each person's busy time inside the working
  hours, then sweeps over the change points, counting busy people and joining
  neighbouring free pieces.
- `broken/`: all eight implementations were re-derived from the new reference, each as a
  small edit. Four have new mistakes:
  - G1 leaves people with empty calendars out of the count.
  - G3 reports each piece between neighbouring events as its own slot.
  - C2 counts meetings instead of people.
  - C4 also accepts a quorum larger than the group.

  The others (G2, C1, C3, C5) keep their old mistakes. `broken/README.md` is updated.
- Public checks (V): P1 now sends `quorum`, and P2 covers S1 to S4.
- Holdout checks (H):
  - The oracle now counts busy people per minute. A request written without a quorum
    means everyone is required.
  - The generated requests now use varied quorums.
  - H1, H3, H4, H5 and H6 gain hand-worked quorum cases.
  - H2 gains quorum threshold cases.
  - H7 gains 11 new invalid requests: a missing quorum and 10 bad quorum values. It also
    gains two new valid edge cases.
  - H8 gains a quorum refusal.
  - H9 covers S4.
- Audit checks (X): these were updated from the intent alone, with their own
  hand-worked cases and their own seeds, not copied from H.
  - The audit model counts free people per minute, each person once.
  - X5 is renamed to `x_enough_free.py`. It checks quorums from one person to everyone.
  - X6 to X10 gain quorum cases.
  - X9 drops its old "moved between people" rewrite, because C2 no longer promises that
    moving an interval to another person changes nothing. Its "repeats and nested
    pieces" rewrite now adds each piece to the same person.
  - X11 gains 18 bad quorum values, a missing quorum, a quorum sent under another field
    name and four valid quorum edge cases.
  - X12's generated requests use varied quorums.
  - A new check, X13, covers S4.

Provenance note: the resolver doesn't know of a well-known kata that asks for stretches
when at least k of n people are free, with each person counted once, stretches kept whole
and a minimum length. Counting how many intervals cover each point is a general technique
(as in Meeting Rooms II), not this exercise. This is the resolver's judgment. No search of
kata catalogues was run, because the study rules allow no network access.

## Issue 2

```json
{
 "where": "intent.md — C3 (\"a meeting entirely outside them changes nothing\") vs C4 (busy intervals must satisfy 0 <= start < end <= 1440)",
 "problem": "C3's plain-language framing (\"a meeting entirely outside [the working hours] changes nothing\") can read as license to ignore/tolerate a malformed or out-of-range busy interval that sits outside the working hours, when in fact C4 requires every busy interval — regardless of its position relative to the working hours — to be well-formed and within [0, 1440], or the whole request is refused. The rule is technically stated (C4's clause covers \"workday or busy interval\" generally) and is correctly tested (checks/holdout/invalid.py: \"a busy interval starting before midnight\"/\"ending after midnight\"; audit/x_refusals.py: \"an interval past 1440 after the working hours\", \"a bad interval behind many good ones\"), but a builder skimming C3 in isolation could reasonably conclude out-of-range junk outside the working hours should just be dropped rather than causing a refusal — this is exactly the kind of promise two competent engineers could read differently.",
 "suggestion": "Add one clarifying clause to C4, e.g. \"This bound applies to every busy interval, even one that touches or lies entirely outside the working hours\" — one sentence removes the ambiguity.",
 "kind": "ambiguity",
 "severity": "should-fix"
}
```

**Disposition: accepted.**

- C4 now includes the sentence: "The bound on intervals applies to every busy interval,
  even one that touches or lies entirely outside the working hours."
- C3 now says a meeting entirely outside the working hours changes nothing "(it must
  still be a valid interval, see C4)". A reader of C3 alone is therefore pointed to the
  rule.

The existing checks already tested this, so no check changed for this issue.

## Issue 3

```json
{
 "where": "checks/holdout/checks.toml — H1 statement (\"in groups of 2 to 10\") and H2 statement (\"For min_length from 1 to 120\")",
 "problem": "Both statements read as continuous ranges, but the code behind them only exercises discrete points. H1's people.py loops `for size in (2, 3, 4, 5, 7, 10)` for the \"one person's meeting blocks everyone\" case (skipping 6, 8, 9), and H2's length.py loops `for need in (1, 2, 15, 30, 45, 60, 90, 120)` (not every value in between). The prose overclaims what was actually run, which matters for a reviewer or auditor trying to judge whether a promise is really tested from the checks.toml statement alone.",
 "suggestion": "Reword to name the actual set, e.g. \"in groups of 2, 3, 4, 5, 7 and 10\" and \"for min_length values of 1, 2, 15, 30, 45, 60, 90 and 120\", so the statement matches the code.",
 "kind": "wrong-check",
 "severity": "minor"
}
```

**Disposition: accepted.**

- The H1 statement now says "in groups of 2, 3, 4, 5, 7 and 10 people".
- The H2 statement now says "For min_length values of 1, 2, 15, 30, 45, 60, 90 and 120".

Both statements were also extended to describe the quorum cases added for issue 1. Each
new part names exactly what the code runs: groups of 3, 5 or 8 with every quorum, seven
hand-worked quorum cases, and quorum 1 of 2 thresholds. The other H statements were
checked against their code at the same time, and their counts were updated: H7 has 53
invalid and 8 valid requests, and H8 has 28 valid and 5 refused requests.

## Issue 4

```json
{
 "where": "audit/x_interface.py — the \"no trailing newline\" case (`json.dumps(BASE, separators=(\",\", \":\"))`), and its X1 checks.toml statement",
 "problem": "The label \"no trailing newline\" is misleading: `json.dumps` never appends a trailing newline in any of the other cases either, so this case doesn't actually test trailing-newline handling — it tests compact JSON with no whitespace after separators, which is a different thing. Meanwhile checks.toml's X1 statement (\"pretty-printing, reordered fields and surrounding blank lines change nothing\") lists only 3 of the 4 variations actually run, omitting this one entirely, and no case in the suite ever sends input with a genuine trailing newline (e.g. `json.dumps(BASE) + \"\\n\"`), which is a very plausible thing a real caller's tooling would send.",
 "suggestion": "Rename the case to something like \"compact JSON (no extra whitespace)\", add a real trailing-newline case (`json.dumps(BASE) + \"\\n\"`), and update the X1 statement to mention both.",
 "kind": "gap",
 "severity": "minor"
}
```

**Disposition: accepted.**

- In `audit/x_interface.py`, the case is renamed "compact JSON (no extra whitespace)".
- A new case, "a trailing newline", sends `json.dumps(BASE) + "\n"`.
- The X1 statement now lists all six layout variations it runs.

One part of the problem is slightly overstated: the existing "surrounding blank lines"
case already ended with `"  \n\n"`, so some trailing newlines were sent before. No case
sent a plain single trailing newline, though, so the new case still adds coverage.

## Reviewer's overall view (verbatim)

> The task is well-formed mechanically: all 11 promise IDs (G1-G3, C1-C5, S1-S3) are covered by at least one holdout check and one independently-written audit check, the H/X "expected" models are minute-sweep implementations that correctly encode G1/C1/C3/G2/G3 and agree with each other, and I found no leakage of holdout's specific cases, seeds, or thresholds into the public checks or intent.md (the S1-S3 overlap between intent, public and holdout is intentional, since scenarios are meant to be visible). Sizing looks appropriate for under an hour — nontrivial (half-open interval semantics, multi-person union, ~40 distinct invalid-input shapes) but not sprawling. The most consequential finding is that the core algorithm duplicates the well-known "Employee Free Time" kata, which the study's own rules forbid; I'd resolve that before sealing. The remaining findings are a real but narrow ambiguity in how C3 and C4 interact for out-of-range busy intervals, and two minor checks.toml/audit documentation-accuracy nits that don't affect correctness but would mislead someone auditing coverage from the statements alone.

## Result

After the changes, `python3 harness/gates.py tasks/T10-free-slots` passes:

```
T10-free-slots: PASS | promises 12 | V 2 H 9 X 13 checks | broken 8 (4 pass V)
```

- The reference passes all V, H and X checks, and `warrant check` exits 0.
- X covers every promise.
- Each broken implementation fails an X check that covers its promise:

  | Broken | Caught by | Passes V? |
  |---|---|---|
  | G1 | X5, X12 | no |
  | G2 | X6, X12 | yes |
  | G3 | X7, X12 | no |
  | C1 | X8, X12 | no |
  | C2 | X9, X12 | yes |
  | C3 | X10, X12 | yes |
  | C4 | X11 | yes |
  | C5 | X1 | no |

- As a separate check, the resolver compared the reference's slot computation in-process
  with a brute-force minute-by-minute model on 4000 random requests. They agreed on
  every one.
