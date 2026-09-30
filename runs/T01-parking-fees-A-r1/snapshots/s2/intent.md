# Parking garage fees

A city parking garage works out what a driver pays at the exit barrier from the entry and
exit times of the stay. A quick drop-off should cost nothing, a long stay should never cost
more than a fair amount per day, a car left in overnight pays a separate overnight fee, and
a lost ticket costs a flat penalty.

Every time is a whole number of minutes since Monday 00:00 at the start of a week: 0 is
Monday 00:00, 120 is Monday 02:00, 1440 is Tuesday 00:00, 1560 is Tuesday 02:00 and 10079
is Sunday 23:59. A week has 10080 minutes. Money is counted in whole US cents.

## Goals

- G1: Parking time is charged at $2.50 for every started hour of the stay, counted from
  the minute of entry: a stay of 60 minutes is one hour, 61 minutes is two hours and 120
  minutes is two hours. G2 and G3 limit this time charge.
- G2: The first 15 minutes are free: a stay of 15 minutes or less has no time charge and
  no overnight fee. A stay of 16 minutes or more is charged from its first minute, as in
  G1; the 15 free minutes are not deducted from it.
- G3: Daily cap: the stay is divided into 24-hour periods (1440 minutes) counted from
  entry, and the time charge for any one period is at most $16.00. Each full 24 hours
  therefore costs exactly $16.00, and the minutes left after the last full period are
  charged by started hour as in G1, again at most $16.00. Even a few leftover minutes
  count as a started hour: the free minutes of G2 apply only to a whole stay of 15 minutes
  or less.
- G4: Overnight rule: every 02:00 (on any day) that falls within the stay adds an
  overnight fee of $6.00, one per night, on top of the time charge and not limited by the
  daily cap, except for a stay that is free under G2. The stay includes a given 02:00
  when the car entered at or before 02:00 and left after it: entering at exactly 02:00
  counts for that night, and leaving at exactly 02:00 does not.
- G5: A lost ticket adds a flat lost-ticket fee of $25.00, whatever the stay: it is
  charged even when the stay is free under G2, and it is not limited by the daily cap.

## Constraints

- C1: The fee is computed by an executable command named `fee`. It reads one JSON object
  on standard input with three fields: `entry` and `exit`, JSON integers (written without
  a decimal point or exponent) from 0 to 10079, meaning minutes since Monday 00:00, and
  `lost_ticket`, true or false. On success it exits with status 0 and writes one JSON
  object on standard output with five integer fields, all present even when zero:
  `minutes` (the length of the stay), `time_cents` (G1 to G3), `overnight_cents` (G4),
  `lost_ticket_cents` (G5) and `total_cents`, which is the sum of the three charges. A
  refused request (C3) exits with status 2, writes nothing on standard output and
  explains the problem on standard error.
- C2: A stay can run past the end of the week. An exit earlier than the entry is in the
  following week, so the stay lasts 10080 - entry + exit minutes, and the 02:00 moments of
  that following week count for G4 (Monday 02:00 is minute 120 of the new week). An exit
  equal to the entry is a stay of zero minutes.
- C3: Invalid requests are refused, never charged: input that is not a JSON object; a
  missing `entry`, `exit` or `lost_ticket`; an `entry` or `exit` that is not a JSON
  integer (including true, false, null, 1.5, 600.0, 6e2 and "600") or is outside 0 to
  10079; and a `lost_ticket` that is not true or false (including 0, 1, null and "no").
  An `entry` or `exit` written `-0` is the integer 0 and is accepted. Fields other than
  `entry`, `exit` and `lost_ticket` do not make a request invalid: they are ignored, and
  the request gets the same answer as without them.

## Scenarios

- S1: Tuesday 09:10 to 11:40 with the ticket, three started hours:
  `{"entry": 1990, "exit": 2140, "lost_ticket": false}` gives
  `{"minutes": 150, "time_cents": 750, "overnight_cents": 0, "lost_ticket_cents": 0, "total_cents": 750}`.
- S2: A 15-minute stop on Friday from 12:00 to 12:15 with a lost ticket is free of time
  charges but still pays the lost-ticket fee:
  `{"entry": 6480, "exit": 6495, "lost_ticket": true}` gives
  `{"minutes": 15, "time_cents": 0, "overnight_cents": 0, "lost_ticket_cents": 2500, "total_cents": 2500}`.
- S3: Sunday 20:00 to the following Monday 08:30 with the ticket: 750 minutes, whose 13
  started hours are capped at $16.00, plus one night (Monday 02:00):
  `{"entry": 9840, "exit": 510, "lost_ticket": false}` gives
  `{"minutes": 750, "time_cents": 1600, "overnight_cents": 600, "lost_ticket_cents": 0, "total_cents": 2200}`.
- S4: Wednesday 08:00 to Friday 10:30 with the ticket: two full 24-hour periods at the cap,
  150 more minutes as three started hours, and two nights (Thursday and Friday 02:00):
  `{"entry": 3360, "exit": 6390, "lost_ticket": false}` gives
  `{"minutes": 3030, "time_cents": 3950, "overnight_cents": 1200, "lost_ticket_cents": 0, "total_cents": 5150}`.

## Out of scope

- Public holidays, weekend rates, monthly permits, validated tickets, payment and
  receipts, currencies other than US dollars, and stays of a week or longer.
