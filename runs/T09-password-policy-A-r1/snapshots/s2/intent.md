---
owner: identity team
---

# Password policy

Our sign-up and password-change screens ask one small program whether a new password meets
the organisation's password policy. It answers with the list of rules the password breaks,
so the screen can explain each one to the person typing it. Every password must be judged
by the same written rules, and a malformed request must be refused rather than guessed at.

Throughout, a character is one Unicode code point, and two characters are the same only when
they are the same code point. Every rule judges the password, the username and the banned
entries exactly as the request gives them: nothing is Unicode-normalized (to NFC, NFD, NFKC
or NFKD), trimmed or otherwise rewritten before it is counted or compared. The only
difference any rule ignores is the one G3 and G5 name, between upper and lower case ASCII
letters.

## Goals

- G1: A password shorter than 12 characters breaks `too_short`, and one longer than 64
  characters breaks `too_long`. Characters are counted as Unicode code points, not bytes:
  `é` (U+00E9) and `😀` (U+1F600) each count as one character.
- G2: Every character belongs to exactly one of four classes: lowercase (ASCII `a` to `z`),
  uppercase (ASCII `A` to `Z`), digit (ASCII `0` to `9`) and symbol (every other character,
  including the space and letters or digits outside ASCII, such as `é` or `٣`). A password
  that uses fewer than three of the four classes breaks `classes`.
- G3: A password that contains any four consecutive characters of the username breaks
  `username`, ignoring only the difference between upper and lower case ASCII letters. A
  username shorter than four characters forbids nothing.
- G4: A password in which the same character appears three or more times in a row breaks
  `repeat`. Case matters: `aaa` is a repeat, `aAa` is not.
- G5: A password that contains any entry of the request's banned list breaks `banned`,
  ignoring only the difference between upper and lower case ASCII letters.

## Constraints

- C1: The checker is a command named `policy`. It reads exactly one JSON object on standard
  input, with nothing before or after it except whitespace (spaces, tabs, carriage returns
  and line feeds). The object has exactly three fields: `password` (a string), `username`
  (a string) and `banned` (a list of strings). For every valid request it writes one JSON
  object on standard output with exactly two fields, `ok` (true or false) and `violations`
  (a list of strings), and exits with status 0, whether or not the password breaks a rule.
  A refused request exits with status 2 and writes nothing on standard output.
- C2: `violations` names each broken rule exactly once, using only the six codes `banned`,
  `classes`, `repeat`, `too_long`, `too_short` and `username`, in ascending alphabetical
  order. `ok` is true exactly when `violations` is empty.
- C3: Invalid requests are refused, never judged. That includes input that is not JSON, is
  not a JSON object, or holds anything but whitespace before or after the object; a missing
  field, or any field besides the three; a password that is not a string; a username that
  is not a string, is empty, is longer than 32 characters or holds anything other than
  ASCII letters, digits, `.`, `_` and `-`; and a banned value that is not a list, has more
  than 20 entries, or has an entry that is not a string or is empty.

## Scenarios

- S1: `{"password": "Bell-Book-77", "username": "rebel", "banned": ["books"]}` gives
  `{"ok": true, "violations": []}`: 12 characters are enough, doubled characters are
  allowed, sharing only three letters (`bel`) with the username is allowed, and `books`
  does not appear in the password.
- S2: `{"password": "maria.silva2024", "username": "MSILVA", "banned": ["2024"]}` gives
  `{"ok": false, "violations": ["banned", "username"]}`: the password holds `silv`, four
  consecutive characters of the username in lower case, and the banned entry `2024`.
- S3: `{"password": "kim111", "username": "kim", "banned": ["11"]}` gives
  `{"ok": false, "violations": ["banned", "classes", "repeat", "too_short"]}`; the
  three-letter username forbids nothing.
- S4: `{"password": "Harbor-Lamp-42", "username": "ana smith", "banned": []}` is refused
  because the username holds a space: exit status 2 and nothing on standard output.

## Out of scope

- Storing or hashing passwords, comparing them with earlier passwords, breach databases,
  strength scores, and any rule not listed above.
