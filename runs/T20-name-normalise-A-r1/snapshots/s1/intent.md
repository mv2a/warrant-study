---
owner: the newsletter team
---

# Mailing-list names

Our newsletter sign-up form lets people type their name however they like, so the list
is full of stray spaces, shouting capitals, titles and the same person signed up twice
with different spellings. Before we print a greeting or an address label we want one
tidy way of writing every name, and a key that stays the same across the usual spelling
differences so we can spot duplicates.

## Goals

- G1: Whitespace is tidied. Whitespace at the start and end of the name is dropped, and
  every run of whitespace inside it becomes a single space. Whitespace means any of the 25
  characters with the Unicode White_Space property, including space, tab, line feed,
  carriage return and no-break space (U+00A0). The words of the name are what is left
  between those single spaces.
- G2: Honorifics are removed from the start of the name. The honorifics are Mr, Mrs, Ms,
  Miss, Mx, Dr, Prof, Rev, Sir and Dame, each matched as a whole word in any mix of upper
  and lower case, with or without one full stop after it ("DR." and "dr" both count;
  "Dr..", "Drs" and "Doctor" do not). Several honorifics in a row at the start are all
  removed, so "Prof. Dr. Anna Weber" becomes "Anna Weber". The same words later in the
  name are ordinary words and are kept: "Anna Dr. Weber" stays "Anna Dr. Weber".
- G3: Every word is capitalised, apart from the particles that G4 keeps in lower case.
  Within a word, a character is upper-cased when it is the first character of the word
  or comes directly after a hyphen (-), an apostrophe (' or ’) or a full stop (.); every
  other character is lower-cased. So "anna-MARIA" becomes "Anna-Maria", "o'neil" becomes
  "O'Neil", "j.r.r." becomes "J.R.R.", "mcdonald" becomes "Mcdonald", "3RD" becomes
  "3rd" and "élodie" becomes "Élodie".
- G4: Particles stay in lower case inside a name. The particles are da, de, del, della,
  der, di, du, la, le, van and von, each matched as a whole word in any case. A particle
  that is neither the first nor the last word of the name, counted after honorifics are
  removed, is written entirely in lower case. A particle that is the first or the last
  word is capitalised like any other word ("van gogh" becomes "Van Gogh", "Dr. van Gogh"
  becomes "Van Gogh" and "Anna van" becomes "Anna Van"). The parts of a hyphenated word
  are never particles: "anna-de-la-cruz" becomes "Anna-De-La-Cruz".
- G5: Every name gets a stable key for spotting duplicates. The key is made from the
  display name: it is put into Unicode compatibility decomposition (NFKD), lower-cased
  character by character (so ß stays ß), and every character that is not a letter is
  dropped. That removes digits, spaces, hyphens, apostrophes, full stops and the accent
  marks that NFKD splits off (é, ü, ñ and å become e, u, n and a), while letters that do
  not decompose, such as ø, ł, æ and ß, and letters of other alphabets, such as д, are
  kept. So names that differ only in whitespace, case, leading honorifics, such accents,
  hyphens, apostrophes or full stops get the same key, and normalising a display name
  again gives the same key.

## Constraints

- C1: The normaliser runs as a command named `normalise`. It reads one JSON object on
  standard input with a field "name" whose value is a string; any other fields are
  ignored. On success it exits with status 0 and writes one JSON object on standard
  output with exactly two fields, both strings: "display" (the tidied name from G1 to G4)
  and "key" (the duplicate key from G5). A refused request exits with status 2 and writes
  nothing on standard output.
- C2: Invalid requests are refused, never normalised. That covers input that is not
  JSON, JSON that is not an object, a missing "name", a "name" that is not a string, a
  name longer than 100 characters (Unicode code points, counted before any tidying), and
  a name with no letters left once whitespace is tidied and leading honorifics are
  removed, such as "", "   ", "Dr.", "Mr. Mrs." or "Mr. 42". A name of exactly 100
  characters is accepted.

## Scenarios

- S1: `{"name": "  prof. DR.  anna-maria   o'neil "}` gives
  `{"display": "Anna-Maria O'Neil", "key": "annamariaoneil"}`.
- S2: `{"name": "LUDWIG VAN BEETHOVEN"}` gives
  `{"display": "Ludwig van Beethoven", "key": "ludwigvanbeethoven"}`.
- S3: `{"name": "van der berg"}` gives `{"display": "Van der Berg", "key": "vanderberg"}`,
  because a particle at the start of a name is capitalised.
- S4: `{"name": "Mr José García"}` gives `{"display": "José García", "key": "josegarcia"}`,
  and `{"name": "jose  GARCIA"}` gives `{"display": "Jose Garcia", "key": "josegarcia"}`:
  the same key, so the two sign-ups are flagged as one person.

## Out of scope

- Reordering names written surname first, or with a comma ("Weber, Anna").
- Special treatment of suffixes such as Jr or III, or of prefixes such as Mc and Mac:
  they are capitalised by G3 like any other word.
- Deciding which of two duplicate sign-ups to keep.
- Names containing the control characters U+001C to U+001F, which some programming
  libraries count as whitespace although they lack the Unicode White_Space property.
- Names in which G3 would change the case of a character whose other case is more than
  one character or depends on the letters around it, such as upper-casing ß (some
  libraries give SS, others keep ß), lower-casing İ, or lower-casing a Greek capital
  sigma (σ, or ς at the end of a word). Lower-casing ẞ to ß, and keeping ß in the key,
  are still settled by G3 and G5.
