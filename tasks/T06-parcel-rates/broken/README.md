# Deliberately broken implementations of `rate`

Each folder holds a copy of the reference with one plausible, honest mistake in the rule for
the promise it is named after. Everything else matches the reference.

| Folder | Mistake |
|--------|---------|
| G1 | Dimensional weight uses integer division, so it is rounded down instead of up to a whole gram. |
| G2 | Bracket limits are treated as exclusive, so a parcel of exactly 500, 1,000, 2,000 or 5,000 g is priced in the next bracket. |
| G3 | Above 10,000 g only whole extra kilograms are charged, not every started kilogram. |
| G4 | The surcharge rule takes the `length_cm` field as the parcel's length instead of its longest side, so the result depends on the order the sides are given in. |
| C1 | A refusal writes a JSON error object on standard output instead of writing nothing there. |
| C2 | The 30,000 g limit is applied to the actual weight instead of the billable weight, so light parcels with a dimensional weight over the limit are priced. |
| C3 | Weights and sides only have to be zero or more, so a zero weight or a zero side is priced. |

## Promises without a broken implementation

S1, S2, S3 and S4 have none. Each scenario is a worked instance of the goals and constraints
(S1 of G1 and G2, S2 of G1 and G3, S3 of G1, G2 and G4, S4 of C2), and those promises fully
determine the response to every request. So any honest mistake that gets a scenario wrong
also breaks one of G1 to G4 or C1 to C3, and that promise already has its own broken
implementation above. An implementation wrong in a scenario and in nothing else would have to
special-case that exact request, which is not a plausible honest mistake.

The broken implementations above were chosen so that all four scenarios still come out right,
so each one is wrong in its own promise and in no scenario.
