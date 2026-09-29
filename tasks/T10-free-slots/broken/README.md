# Deliberately broken implementations

Each folder holds a `slots` command that is wrong in one promise, in a way an honest
builder could plausibly get wrong. Each one differs from `reference/slots` by a small edit.

| Folder | The mistake |
|---|---|
| G1 | Leaves people with no busy intervals out before counting ("they never block anyone"), so they no longer count toward the quorum. With everyone required and no empty calendars it is right; otherwise it asks for more free people than there are. |
| G2 | Keeps a free stretch only when it is longer than `min_length` (`>` instead of `>=`), so a stretch of exactly `min_length` minutes is dropped. |
| G3 | Reports each piece of time between two neighbouring meeting starts or ends as its own slot instead of joining neighbouring free pieces, so a stretch during which the people who are free change is cut into pieces (and pieces shorter than `min_length` are dropped). With everyone required it is right. |
| C1 | Treats a meeting as still occupying its end minute, so a person is free one minute late after each meeting and a one-minute gap disappears. |
| C2 | Counts meetings instead of people: one person's overlapping or repeated intervals count as several busy people. With everyone required it is right. |
| C3 | Ignores every meeting that is not wholly inside the working hours instead of cutting it at the edges, so a meeting that runs past the start or end of the day doesn't make anyone busy. |
| C4 | Lenient validation: `isinstance(value, int)` lets true and false through as numbers, busy intervals are checked only for shape (reversed, empty and out-of-range intervals are accepted), an empty `busy` list is accepted, and a `quorum` larger than the group is accepted. |
| C5 | Refuses with `sys.exit(message)`, which exits with status 1 instead of 2. The request is still refused, but checks can only see a refusal through the exit status, so C4 checks fail for it too. |

## Promises without a broken implementation

- S1, S2, S3, S4: each scenario is one worked instance of the goals and constraints. S1
  shows overlapping meetings (C2) and a stretch that is too short (G2), in time order (G3);
  S2 shows touching meetings (C1); S3 shows three people, one with no meetings (G1), and an
  empty answer (G2); S4 shows a quorum below the whole group (G1), a person with no
  meetings counting toward it (G1) and a stretch that stays whole while the people who are
  free change (G3).
  An implementation that gets a scenario wrong necessarily breaks at least one of those
  general promises at that input, so no plausible mistake breaks a scenario alone. The
  broken implementations for G1 (S4), G3 (S4) and C1 (S1, S2) already get scenarios wrong.
