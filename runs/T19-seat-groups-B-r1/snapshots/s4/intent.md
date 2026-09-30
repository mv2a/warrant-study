# Theatre seat groups

A small community theatre sells tickets to booking groups: a family, a school class, a
group of friends. Before each show the box office runs the night's bookings through one
command that gives every group its seats. People who book together want to sit together,
the front rows fill first, and a group that cannot be seated is told why instead of being
quietly scattered around the hall.

The theatre has up to 26 rows, lettered A (the front) to Z, and each row has up to 50
seats, numbered from 1 at the left. A seat is named by its row letter and number, such as
`B7`. Some seats can be blocked (broken, or kept clear for a wheelchair). A group *sits
together* when all its seats are in one row with consecutive numbers, so no blocked or
already sold seat lies between them. *Seating order* is row A first and, within a row, the
lowest seat number first.

## Goals

- G1: Groups are handled one at a time in booking order, the order of `groups` in the
  request. Each group is seated or refused using only the seats left free by the groups
  before it, so a group's result never depends on groups booked after it. A refused group
  takes no seats, so a later, smaller group can still be seated.
- G2: A group sits together whenever the free seats allow it. It gets the frontmost row
  that has enough free seats in a block of consecutive numbers, and in that row the
  lowest-numbered such block: a group of 3 in a row whose free seats are 1, 2, 5, 6, 7
  and 8 gets seats 5, 6 and 7.
- G3: Splitting a group is the last resort. A group is split only when its request says
  `"may_split": true`, it cannot sit together, and at least as many seats are free as it
  has members. A split group takes the first free seats in seating order until everyone
  has a seat. A group without `"may_split": true` is never split.
- G4: A group that cannot be seated under G2 and G3 is refused as a whole, never partly
  seated. The reason is `"not_enough_seats"` when fewer seats are free than the group has
  members, and `"not_together"` otherwise (enough seats are free, but the group cannot sit
  together and may not be split).

## Constraints

- C1: The allocator is a command named `seats`. It reads one JSON object on standard input
  and writes one JSON object on standard output. The request has `rows`, a list of whole
  numbers giving the number of seats in each row, row A first; `groups`, a list of booking
  groups in booking order, each an object with `id` (text), `size` (a whole number, the
  number of people) and optionally `may_split` (true or false, false when left out); and
  optionally `blocked`, a list of seat names. Fields not named here, in the request or in
  a group, are ignored. The response has exactly three fields: `seated`, a list with one
  object per seated group in booking order, holding exactly `id` and `seats` (the group's
  seat names in seating order); `refused`, a list with one object per refused group in
  booking order, holding exactly `id` and `reason`; and `free`, a whole number. The exit
  status is 0 when the request is handled, even if some or all groups are refused, and 2
  when the request itself is refused (see C3), in which case nothing is written to
  standard output.
- C2: Seats are never oversold. Every seat sold exists in the theatre, no seat goes to two
  groups, no blocked seat is sold, each seated group gets exactly as many seats as its
  `size`, and `free` is the number of seats that are neither blocked nor sold.
- C3: A malformed request is refused as a whole, as C1 describes, and no group is
  seated. A request is malformed when standard input is not JSON or not a JSON object;
  when `rows` is missing, is not a list, is empty, has more than 26 entries, or holds
  anything but whole numbers from 1 to 50; when `groups` is missing or is not a list (an
  empty list is fine); when a group is not an object, its `id` is missing, not text,
  empty, or the same as an earlier group's `id`, its `size` is missing or not a whole
  number of at least 1, or its `may_split` is present (null included) but not true or
  false; or when `blocked` is present (null included) but not a list, holds anything but
  names of seats in this theatre written exactly as responses write them (`B7`, never
  `b7`, `B07` or `B 7`), or names the same seat twice. Whole numbers are JSON numbers with
  no decimal point or exponent: true, false, 3.0 and 1e1 are not whole numbers. Standard
  input is JSON only when it is valid JSON as RFC 8259 defines it: the bare words `NaN`,
  `Infinity` and `-Infinity`, which some JSON readers accept by default, make it not
  JSON, even where they stand in a field that would otherwise be ignored.

## Scenarios

- S1: The request `{"rows": [6, 6], "groups": [{"id": "Ruiz", "size": 4}, {"id": "Chen",
  "size": 3}, {"id": "Patel", "size": 2}]}` gets exit status 0 and the response
  `{"seated": [{"id": "Ruiz", "seats": ["A1", "A2", "A3", "A4"]}, {"id": "Chen", "seats":
  ["B1", "B2", "B3"]}, {"id": "Patel", "seats": ["A5", "A6"]}], "refused": [], "free": 3}`.
  Chen moves to row B because row A has only two seats left, and Patel then takes them.
- S2: The request `{"rows": [5, 5], "blocked": ["A3", "B3"], "groups": [{"id": "Novak",
  "size": 3}, {"id": "Okafor", "size": 2}, {"id": "Lind", "size": 2}]}` gets exit status 0
  and the response `{"seated": [{"id": "Okafor", "seats": ["A1", "A2"]}, {"id": "Lind",
  "seats": ["A4", "A5"]}], "refused": [{"id": "Novak", "reason": "not_together"}], "free":
  4}`. The blocked seats leave no three free seats side by side, and Novak may not split.
- S3: The request `{"rows": [4, 4], "groups": [{"id": "Ito", "size": 3}, {"id": "Berg",
  "size": 3}, {"id": "Kim", "size": 3}, {"id": "Diaz", "size": 2, "may_split": true}]}`
  gets exit status 0 and the response `{"seated": [{"id": "Ito", "seats": ["A1", "A2",
  "A3"]}, {"id": "Berg", "seats": ["B1", "B2", "B3"]}, {"id": "Diaz", "seats": ["A4",
  "B4"]}], "refused": [{"id": "Kim", "reason": "not_enough_seats"}], "free": 0}`. Only two
  seats are left for Kim's three people, and Diaz, who may split, takes them.

## Out of scope

- Prices, seat categories, cancellations, and bookings across more than one show.
