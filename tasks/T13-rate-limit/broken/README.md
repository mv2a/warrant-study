# Deliberately broken implementations of `limit`

Every promise in `intent.md` has a broken implementation, so no promise is left without
one. Each is a copy of `reference/limit` with one targeted change, written to look like an
honest mistake.

| ID | The mistake |
|----|-------------|
| G1 | Keeps one clock for the whole log instead of one per client. Refill is measured from the previous request by anyone, so a busy neighbour stops another client's bucket from refilling. |
| G2 | A new client's bucket defaults to empty at time 0 (`buckets.get(client, (0, 0))`). A client whose first request comes early does not get its burst. |
| G3 | Counts whole tokens only: each request adds `rate * elapsed // 1000` and resets the clock, so progress toward a token that is not complete yet is thrown away. |
| G4 | Takes the token before looking: a rejected request still uses one up and drives the bucket below zero, so a client that keeps retrying is locked out. |
| C1 | Refuses with `sys.exit("message")`, which exits with status 1 instead of 2. |
| C2 | Keeps token counts as floating-point numbers, so rounding errors pile up. At a rate of 10, a token due at exactly 100 ms after ten 10 ms steps is not there. |
| C3 | Checks time order per client instead of across the whole log, so a log that goes back in time with a different client is replayed rather than refused. |
| C4 | Validates integers with `isinstance(value, int)`, so `true` and `false` are taken as 1 and 0 for `burst`, `rate` and `at`. |
| S1 | Accepts while any part of a token is left (`held > 0`) instead of a whole token. In S1, the request at 499 ms is accepted and the one at 500 ms rejected. |
| S2 | Builds the per-client counts with `dict.fromkeys(names, {...})`, so all clients share one counter. Decisions are right, but in S2 both "a" and "b" show 4 accepted and 2 rejected. |
| S3 | Never caps the bucket at `burst`, so a client that stays quiet saves up tokens. In S3, all three requests at 60000 ms are accepted. |

The scenarios are worked instances of the goals. A program that gets a scenario wrong must
also break the rule the scenario illustrates, so each `broken/S*` breaks a goal or
constraint as well: S1 breaks G4, S2 breaks C1 and S3 breaks G2. Each uses a different
mistake from the `broken/G*` and `broken/C*` implementations.

Some mistakes also show up under other promises, because the token arithmetic is shared.
For example, a bucket that starts empty (G2) changes almost every decision, and throwing
away partial progress (G3) is also a rounding error under C2.
