# Deliberately broken implementations of `pay`

Every promise has one. Each is the reference with one plausible, honest mistake.

| ID | Mistake |
|----|---------|
| G1 | Double time starts after 12 hours instead of 11 (a habit carried over from other overtime rules). |
| G2 | The 40-hour weekly total is checked only at the start of each day, so the day on which the week passes 40 hours keeps all of its regular time. |
| G3 | Day 7 is treated as a seventh consecutive day whenever it is worked, even when an earlier day of the week was off. |
| C1 | Each day is priced and rounded on its own and the days are added up, instead of rounding each category once for the week. |
| C2 | Amounts are computed with `Decimal` and converted to floats for JSON, so the cent fields come out as `95000.0` rather than integers. |
| C3 | `isinstance(value, int)` accepts `true` and `false` as 1 and 0, so boolean days and rates are paid instead of refused. |
| S1 | Every minute worked, overtime included, counts toward the 40 hours. |
| S2 | Regular time is capped at 40 hours, but the minutes beyond it are dropped instead of being paid as overtime. |
| S3 | The seventh consecutive day is paid entirely as overtime, with no double time after 8 hours. |
| S4 | Python's `round()` rounds exact halves to the even cent (500.5 becomes 500). |
| S5 | Premiums are not stacked: when days 1 to 6 already hold more than 40 hours of regular time, day 7 is treated as an ordinary day, so its time goes through the daily and weekly rules instead of the seventh-day rule. |

A scenario is a concrete instance of the goals and constraints, so a mistake that breaks a
scenario necessarily also breaks the promise the scenario illustrates: S1 and S2 also
break G2 (and S2 the minute total in C2), S3 and S5 also break G3, and S4 also breaks C1. Each
scenario's mistake is a different one from the mistake chosen for that goal or constraint,
and the goal and constraint mistakes are chosen so that none of them changes the values in
the five scenario outputs (C2 changes only their JSON type).
