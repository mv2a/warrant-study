# Broken implementations for T03-bus-fare

Each folder holds a copy of `reference/fare` with one plausible, honest mistake that breaks
exactly the promise it is named after.

| Folder | Mistake |
| --- | --- |
| `G1/` | Counts zones crossed as `to_zone - from_zone` without taking the absolute value, so trips towards a lower zone number are undercharged (and can even come out negative). |
| `G2/` | Measures the 90-minute window from the previous trip instead of from the trip that opened the window, so each transfer extends the window. |
| `G3/` | Starts the senior fare at 66 instead of 65 (`age > 65`), so 65-year-olds pay the adult fare. |
| `G4/` | Applies the adult daily cap of 1100 cents to every rider, instead of 550 for children and 440 for seniors. |
| `C1/` | Rounds concession fares down to the whole cent only, not to a multiple of 5 cents (a child on a 365-cent trip pays 182, not 180). |
| `C2/` | Does not check that trips are in boarding order, so out-of-order trips are priced instead of refused. |
| `C3/` | Reports a refusal as a JSON `{"error": ...}` object on standard output, which the interface forbids; the exit status 2 is still right. |

## Promises without a broken implementation

- S1, S2 and S3 have no broken implementation. Each scenario is a fixed instance of the
  general rules (S1 of G1 and G2, S2 of G1 and G3, S3 of G1, G2 and G4), so any
  implementation that gets a scenario wrong also breaks one of those general promises.
  An implementation wrong in a scenario and in nothing else would have to special-case
  the scenario's exact input, which is not an honest mistake. The broken implementations
  for the general promises already show how scenario checks behave: for example,
  `broken/C3` fails the public contract check, while the others pass all public checks.
