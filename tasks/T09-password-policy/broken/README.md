# Deliberately broken implementations

Each folder holds a copy of `reference/policy` with one honest-looking mistake. Every
promise in `intent.md` has one, so no promise is missing a broken implementation.

| ID | The mistake | Passes V? |
|----|-------------|-----------|
| G1 | Measures the password in UTF-8 bytes instead of code points, so `é`, CJK and emoji count two to four times. | yes |
| G2 | Counts a symbol only when it is ASCII punctuation (`string.punctuation`), so the space, a tab and non-ASCII letters and digits count as no class at all. | yes |
| G3 | Off by one in the loop over username windows: the last four-character window is never checked, and a four-character username forbids nothing. | yes |
| G4 | Looks for repeats in the case-folded password, so `aAa` counts as a repeat. | yes |
| G5 | Compares banned entries case-sensitively, so `LAMP` does not ban `Harbor-Lamp-42`. | yes |
| C1 | Exits with status 1 whenever the password breaks a rule, like a linter, instead of 0. | no |
| C2 | Appends `banned` once for every matching banned entry, so the code can appear more than once. | yes |
| C3 | Checks only that the three fields are present, so a request with extra fields is judged instead of refused. | yes |
| S1 | Uses `<=` for the minimum length, so a 12-character password such as `Bell-Book-77` is called too short. | no |
| S2 | Case-folds the password but not the username, so an upper-case username such as `MSILVA` never matches. | no |
| S3 | Shrinks the window to the username's length when the username is shorter than four characters, so `kim` forbids `kim`. | no |
| S4 | Checks the username's length but not its characters, so `ana smith` is judged instead of refused. | no |

Scenarios are worked instances of the goals and constraints, so no implementation can get
a scenario wrong while keeping every G and C promise. Each S implementation is therefore
wrong in its scenario and, necessarily, in one other promise as well: S1 in G1, S2 and S3 in
G3, S4 in C3. The mistakes behind them are different from those in the G and C folders.
