# Review of T17-hotel-stay

- Reviewer: an AI model, Claude Sonnet, not a human.
- Resolver: an AI model (Claude Opus), working only inside `tasks/T17-hotel-stay`.
- Result: 2 issues accepted, 0 rejected. The gates were re-run after the changes and pass.

## Reviewer's overall view (verbatim)

> T17-hotel-stay is a well-built, internally consistent task. I hand-verified all four intent.md scenarios (S1-S4) against the room/discount/tax/total formulas by arithmetic and they match exactly; the checks.toml 'statement' fields were cross-checked against their scripts' actual logic (case counts, rate/day sets, coverage) and, with one exception, accurately describe what runs. Every promise (G1-G4, C1-C3, S1-S4) has independent, non-overlapping coverage in both H and X, the surcharge/discount rounding rules are unambiguous given the worked examples, and the task's scope (parse+validate JSON, compute per-night pricing, apply a tiered discount and capped tax, enforce one refusal rule) is appropriately sized for a competent engineer in under an hour — comparable in shape to the reference 'pricing' example. I found no promise that two competent engineers would price differently, and no case where a visible or holdout check leaks a specific hidden-check input. The two issues below are real but modest: a coverage gap between the holdout tier's claimed thoroughness and what it actually tests for malformed/non-UTF-8 input (only audited, never held out, and arguably underspecified in intent.md's C3), and a checks.toml statement that undercounts what its own script checks. Neither is large enough to block sealing on its own, but the first is worth fixing since it affects what a builder can fairly be judged on under conditions A/B versus C.

## Issue 1 (gap, should-fix): accepted

**Where (verbatim):** intent.md C3 (lines 42-46) vs. checks/holdout/invalid.py H7 (whole file) vs. audit/invalid.py X9 (lines 29-31, 62-63)

**Problem (verbatim):** Two invalid-input cases — trailing content after a complete JSON object (`json.dumps(BASE) + " trailing words"` / `+ ' {"check_in": "tue"}'`) and raw bytes that are not valid UTF-8 (the `b'\xff\xfe...'` case, deliberately run under a forced POSIX/C locale so the verdict is host-independent) — are exercised only by the audit tier (X9). Neither appears in the visible checks (V) nor, more importantly, in the holdout tier (H7's `invalid.py`), even though the protocol says H must be 'thorough: boundaries, rounding, invalid input, many generated cases' and intent.md's C3 list is only introduced with 'That includes...' (non-exhaustive, so these cases are arguably already promised by the general clause 'input that is not a JSON object'). Since a builder in conditions A/B never sees X, and H's own 'thorough' invalid-input check omits this whole class of case, the requirement to cleanly exit 2 (not crash with status 1 on an uncaught decode error, which a common `sys.stdin.read()`-then-`json.loads()` split would do under a plain UTF-8 locale) is undiscoverable before being scored against it. Two competent engineers could also disagree on whether 'not a JSON object' was meant to reach down to raw byte-decoding, since intent.md never mentions text encoding.

**Suggestion (verbatim):** Smallest fix: add one clause naming this explicitly, e.g. append to C3: '...and input that cannot be read as UTF-8 text, or that has anything besides whitespace after the JSON object, is refused the same way.' Then mirror at least one trailing-content case and one non-UTF-8-bytes case (under a fixed locale, as X9 already does) into checks/holdout/invalid.py so H actually covers what it claims to be thorough about, before X quietly audits it.

**Disposition: accepted, with a change to intent.md and to H7.** The reviewer is right that intent.md never mentioned text encoding or trailing content, while X9 scores both. Because intent.md is the ground truth, both are now stated there.

What the locale does, measured on this host with Python 3.13 before changing anything:

- The study host sets no `LANG` or `LC_*`, so Python starts in UTF-8 mode and decodes standard input with `surrogateescape`. Under that setting, and under the POSIX locale X9 forces, a program that reads standard input as text does not crash on bytes that are not UTF-8. Bytes before the object make `json.loads` fail, so the request is refused with status 2. A stray byte inside a string of an ignored field decodes to a surrogate, the JSON parses, and the request is priced.
- Under a UTF-8 locale (`LC_ALL=en_US.UTF-8`) the same program exits 1 with a `UnicodeDecodeError` traceback on both inputs. This is the crash the reviewer describes.
- So the reviewer's crash does not happen under the POSIX locale X9 uses: a text-mode reader passes X9's `b'\xff\xfe...'` case with status 2. Whether a text-mode reader met C3 therefore depended on the host's locale. That is why the new clause says the locale does not matter.

Changes made:

1. **intent.md, C3.** Appended after "and a rate below 1 cent.":

   > Input that is not valid UTF-8 text is refused the same way, whatever the locale of the system running the command, and so is input with anything other than spaces, tabs or line breaks after the JSON object.

   The clause gives no example input, so no case from H or X leaks into the intent the builder sees. It names spaces, tabs and line breaks rather than "whitespace", because Python's `str.strip()` and JSON disagree on what whitespace is. X5 and X10 to X13 already send requests followed by `"\n"` and `"\n\n"` and expect them to be priced, so the wording agrees with X.

2. **checks/holdout/invalid.py (H7).** New cases, written for H with inputs that differ from X9's:
   - Four trailing-content requests that must be refused: a second object straight after the first, a number on the next line, a word after the object, and a stray closing brace. That makes 44 refused text requests instead of 40.
   - Two valid edges that must be priced: the object followed by `"\n"`, and by `" \t\r\n "`. This covers the other side of the new clause, so an implementation that refuses anything after the closing brace is caught.
   - Two requests whose bytes are not UTF-8: a Latin-1 `\xe9` inside the string of an ignored `guest` field, and a stray `\x80` before the object. Each is sent under two fixed settings instead of the host's own: the POSIX locale (`LC_ALL=C` with `LANG`, `LC_*`, `PYTHONIOENCODING` and `PYTHONUTF8` removed), and the same with `PYTHONIOENCODING=utf-8:strict`, which makes Python decode standard input as strict UTF-8, as on a UTF-8-locale host, whatever locales the host has installed. Both settings are fixed, so the verdict does not depend on the host.
   - The byte cases require exit status 2 itself. The rest of H7 accepts any nonzero exit and leaves the exact refusal form to H5. For undecodable input, the typical failure is a crash with status 1, so here only status 2 separates a refusal from a crash.

3. **X was not changed.** X9 already tests trailing content and bytes that are not UTF-8, and it agrees with the amended C3, so nothing in X needed to change to match the intent. X stays independent of H. One limit, recorded for the study's operators: X9's byte case, bytes before the object under the POSIX locale, is also refused by a text-mode reader. So X does not score the "whatever the locale" part as strictly as H7 does. X still covers C3, and `broken/C3` is still caught by X9.

Checked against variants of the reference (kept in the resolver's scratchpad, not in the task), each with one plausible way of reading input:

| Variant | new H7 | X9 |
|---|---|---|
| reference (decodes the raw bytes itself) | pass | pass |
| `sys.stdin.read()` then `json.loads`, catching only JSON errors | fail: Latin-1 byte priced under POSIX; both byte cases exit 1 under strict UTF-8 | pass |
| `sys.stdin.read()` inside a `try` that refuses on `UnicodeDecodeError` | fail: Latin-1 byte priced under POSIX | pass |
| `json.JSONDecoder().raw_decode`, which ignores trailing content | fail: all four trailing-content cases priced | fail |
| `json.loads(text.strip())` | fail on the byte cases only; trailing whitespace is priced | pass |

## Issue 2 (wrong-check, minor): accepted

**Where (verbatim):** checks/holdout/checks.toml line 54 (H7 statement) vs. checks/holdout/invalid.py lines 61-66 (VALID_EDGES)

**Problem (verbatim):** H7's statement says 'the valid edges of 1 night, 30 nights and a 1-cent rate are priced,' but the code's `VALID_EDGES` list has a fourth case — `{"check_in": "sun", "nights": 2, "rate_cents": 10 ** 9}` (a $10,000,000.00 nightly rate) — that the statement doesn't mention. TASK_SPEC.md requires each checks.toml statement to say 'exactly what is checked.'

**Suggestion (verbatim):** Reword the H7 statement to include the fourth edge, e.g. '...while the valid edges of 1 night, 30 nights, a 1-cent rate and a $10,000,000.00 rate are priced.'

**Disposition: accepted, by rewording the statement.** 10\*\*9 cents is $10,000,000.00, as the reviewer says. The H7 statement now names that edge, and it also describes the cases added under Issue 1:

> Forty-four invalid requests are refused rather than priced, covering input that is not a JSON object or has something other than whitespace after it, each missing field, wrong weekday names, and night counts and rates that are out of range or not JSON integers (including true, 2.0 and strings); two requests containing bytes that are not UTF-8 are refused with exit status 2 both under the POSIX locale and with standard streams decoded strictly as UTF-8; and the valid edges of 1 night, 30 nights, a 1-cent rate, a $10,000,000.00 rate and trailing whitespace after the object are priced.

Against the reference, the script now prints "invalid requests ok: 44 refused, 2 non-UTF-8 inputs refused under 2 settings, 6 edge cases priced", which matches the statement.

## Gate result after the changes

`python3 harness/gates.py tasks/T17-hotel-stay`:

```
T17-hotel-stay: PASS | promises 11 | V 3 H 9 X 13 checks | broken 7 (4 pass V)
```

The reference passes all 3 V, 9 H and 13 X checks, and `warrant check` returns 0. Each of the 7 broken implementations (G1, G2, G3, G4, C1, C2, C3) fails at least one X check that covers its promise. Four of them (G2, G4, C2, C3) pass V, as intended, since V is deliberately incomplete. S1 to S4 have no broken implementation, for the reason given in `broken/README.md`. The numbers of checks, promises and broken implementations are the same as before the review. Only the content of intent.md C3 and of H7 changed.
