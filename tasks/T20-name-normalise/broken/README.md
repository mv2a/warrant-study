# Broken implementations

Each folder holds a copy of the reference with one plausible, honest mistake that breaks
exactly the promise it is named after:

- G1: splits the name on spaces, tabs and line feeds only, so a carriage return or a
  no-break space stays inside a word.
- G2: drops every honorific word wherever it appears, instead of only the ones at the
  start ("Anna Dr. Weber" becomes "Anna Weber").
- G3: starts a new capitalised part after a hyphen or an apostrophe but forgets the full
  stop ("j.r.r." becomes "J.r.r.").
- G4: lower-cases every particle after the first word, forgetting that a particle in the
  last position is capitalised ("Anna van" stays "Anna van").
- G5: keeps only the letters a to z in the key, so letters that do not decompose, such as
  ø, ł, æ, ß and Cyrillic or Chinese letters, are lost ("Søren" gets the key "sren").
- C1: refuses any request that has a field other than "name", instead of ignoring it.
- C2: refuses only names that are blank, so a name with no letters once honorifics are
  removed ("Dr.", "Mr. 42") is normalised to an empty or letterless display and an empty
  key instead of being refused.

## Promises without a broken implementation

- S1, S2, S3 and S4 are concrete scenarios: each is one fixed request whose expected
  output follows from the goals G1 to G5. Any honest mistake that gets a scenario wrong
  also breaks the goal behind it (S1 exercises G1, G2 and G3, S2 and S3 exercise G4, S4
  exercises G2 and G5), and the broken implementations above already cover those goals.
  A variant wrong in a scenario but in no goal could only be written by special-casing
  that exact input, which would not be a plausible mistake.
