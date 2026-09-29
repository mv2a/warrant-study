# Deliberately broken implementations

Each folder holds a copy of `reference/seats` with one honest-looking mistake that breaks
exactly one promise.

| Folder | Promise | Mistake |
| --- | --- | --- |
| `G1` | G1 | Seats the biggest groups first "so they can stay together", then reports the results in booking order. An earlier small group can lose its seats to a later big one. |
| `G2` | G2 | Picks the tightest block that fits anywhere in the theatre (best fit) instead of the frontmost row and lowest-numbered block. |
| `G3` | G3 | A split group fills the biggest free blocks first, to keep as many people together as possible, instead of taking the first free seats in seating order. |
| `G4` | G4 | Checks "can it sit together?" before counting free seats, so a group that may not split and is too big for the free seats is refused as `not_together` instead of `not_enough_seats`. |
| `C1` | C1 | A refused request exits with status 1, the usual error status, instead of 2. |
| `C2` | C2 | `free` counts every unsold seat, blocked seats included. |
| `C3` | C3 | Uses `isinstance(value, int)`, so `true` and `false` pass as whole numbers for sizes and row lengths, and never checks for repeated group ids. |

On valid requests, `C1` and `C3` behave exactly like the reference, `C2` differs only in
`free`, and `G4` differs only in refusal reasons.

## Promises without a broken implementation

- S1, S2 and S3 are concrete instances of G1 to G4 and C1 to C2: each scenario's response
  follows from those rules. An honest mistake that gets a scenario wrong always breaks
  the general rule behind it too, so a broken implementation for a scenario alone would
  have to special-case the scenario's exact input, which is not a plausible mistake.
  The scenarios are still exercised by the broken implementations above: `G4` gets S3
  wrong (Kim is refused as `not_together`), and `C2` gets S2 wrong (`free` counts the two
  blocked seats).
