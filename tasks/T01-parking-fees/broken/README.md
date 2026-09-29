# Broken implementations for T01-parking-fees

Every goal and constraint (G1 to G5, C1 to C3) has a broken implementation in the folder of
the same name. Each is the reference with one plausible mistake that breaks that promise.

The scenarios S1, S2, S3 and S4 have none. Each scenario is one exact request and its
exact output, and every rule it exercises is already a goal or a constraint. A program
that is wrong in a scenario but right in every goal and constraint would have to
special-case that one request, which is not an honest mistake. The broken implementations
for the goals and constraints already get scenarios wrong: C1 breaks all four, G5 breaks
S2, and C2 breaks S3.
