---
owner: office coordinator
---

# Common free slots

We book meetings for small groups. Not everyone has to come: a meeting can go ahead when
enough of the group can attend. Each person keeps a list of the times of day they are
busy. Given everyone's busy times, the working hours and how many people must be there, we
want the stretches of the day when at least that many of them are free and that are long
enough for the meeting we have in mind, listed so that whoever books the room can pick one
at a glance.

A free minute below is a minute of the working hours when enough people are free (G1). A
free stretch is a run of free minutes that is as long as it can be: on each side it meets
a minute that is not free or the edge of the working hours.

## Goals

- G1: A slot is time when enough people are free. A minute inside the working hours is
  free when at least `quorum` of the listed people are free at that minute, however many
  people are listed; with `quorum` equal to the number of people, that means everyone. A
  person is busy at a minute when one of their own busy intervals covers it and free
  otherwise, so a person with no busy intervals is free all day and counts toward the
  quorum.
- G2: A free stretch is returned when it lasts at least `min_length` minutes, including one
  that lasts exactly `min_length` minutes, and never when it is shorter. When no stretch
  is long enough, `slots` is an empty list.
- G3: Each free stretch comes back whole, as one slot from the minute it starts to the
  minute it ends, even when the people who are free change partway through it. It is never
  cut into pieces, so no two slots overlap or touch. Slots are listed in time order,
  earliest first.

## Constraints

- C1: Time is counted in whole minutes after midnight, from 0 to 1440. An interval
  `[start, end]` runs from minute `start` up to minute `end`: it lasts `end - start`
  minutes and does not include minute `end` itself. So a person whose meeting ends at
  minute 660 is free at minute 660, a slot can start at the very minute a meeting ends and
  end at the very minute the next one starts, and a person with the meetings `[600, 660]`
  and `[660, 720]` is busy from 600 to 720 with no free minute between them.
- C2: Busy intervals can come in any order, and they can overlap, sit entirely inside one
  another or repeat, within one person's list and across people. A person counts once
  however many of their own intervals cover a minute: overlapping or repeated intervals of
  one person make one busy person, never several, while the same meeting in two people's
  lists makes two busy people. The answer does not depend on the order of the intervals
  within a person's list, nor on the order of the people.
- C3: Slots lie within the working hours. A meeting that runs past the start or end of the
  working hours still makes its person busy for the part inside them, a meeting entirely
  outside them changes nothing (it must still be a valid interval, see C4), and free time
  that reaches the start or end of the working hours ends there.
- C4: Invalid requests are refused, never answered. That includes input that isn't JSON or
  isn't a JSON object; a missing `workday`, `min_length`, `quorum` or `busy`; a `workday`
  or busy interval that isn't a list of exactly two whole numbers `[start, end]` with
  0 <= start < end <= 1440, so an empty or reversed interval is refused; a `min_length`
  that isn't a whole number of at least 1; a `busy` that isn't a list naming at least one
  person; a person's entry that isn't a list; and a `quorum` that isn't a whole number from
  1 up to the number of people in `busy`. The bound on intervals applies to every busy
  interval, even one that touches or lies entirely outside the working hours. True, false,
  text, and numbers written with a decimal point, such as 600.5 or 600.0, are not whole
  numbers.
- C5: The command is named `slots`. It reads one JSON object on standard input with the
  fields `workday` (the working hours, `[start, end]`), `min_length` (the shortest slot
  wanted, in minutes), `quorum` (the fewest of the listed people who must be free at every
  minute of a slot) and `busy` (a list with one entry per person, each entry a list of that
  person's busy intervals `[start, end]`, possibly empty); other fields are ignored. On
  success it writes one JSON object with exactly one field, `slots`, a list of
  `[start, end]` pairs of whole numbers, and exits with status 0. A refused request exits
  with status 2, writes nothing to standard output and gives a reason on standard error.

## Scenarios

- S1: The request
  `{"workday": [540, 1020], "min_length": 30, "quorum": 2, "busy": [[[600, 660], [840, 900]], [[630, 720], [735, 780]]]}`
  gets `{"slots": [[540, 600], [780, 840], [900, 1020]]}`. Both people must be free; their
  overlapping meetings block 600 to 720 together, and the 15 minutes from 720 to 735 are
  too short.
- S2: The request
  `{"workday": [480, 960], "min_length": 45, "quorum": 2, "busy": [[[540, 600], [600, 630], [700, 760]], [[630, 700], [900, 960]]]}`
  gets `{"slots": [[480, 540], [760, 900]]}`. The touching meetings block 540 to 760
  without a gap, and nothing is free after 900.
- S3: The request
  `{"workday": [540, 1020], "min_length": 90, "quorum": 3, "busy": [[], [[570, 660], [930, 990]], [[720, 870]]]}`
  gets `{"slots": []}`. The first person is free all day, but the longest stretch when all
  three are free lasts 60 minutes.
- S4: The request
  `{"workday": [540, 1020], "min_length": 45, "quorum": 3, "busy": [[], [[600, 720]], [[660, 780], [900, 960]], [[700, 750], [930, 1020]]]}`
  gets `{"slots": [[540, 660], [750, 930], [960, 1020]]}`. At most one of the four people
  may be busy; the first person, free all day, counts toward the three. The stretch from
  750 to 930 is one slot although the third person is busy at its start and at its end.
  The same request with `"quorum": 4` gets `{"slots": [[540, 600], [780, 900]]}`.

## Out of scope

- Dates, time zones, recurring meetings, people with different working hours, choosing
  which slot is best, and saying which people are free in a slot.
