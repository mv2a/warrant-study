---
owner: payroll lead, a small staffing agency
---

# Weekly overtime pay

We pay hourly staff once a week. For each person we know how many minutes they worked on
each of the seven days of the workweek and their hourly rate. The `pay` command splits the
week's time into regular time, overtime and double time and prices each part in cents, so
that long days, long weeks and working every day of the week all earn a premium, and
nobody is ever paid a wrong or impossible amount.

## Goals

- G1: Daily thresholds. On an ordinary day, the first 8 hours (480 minutes) worked are
  regular time, the minutes after 8 hours up to 11 hours (minutes 481 to 660 of the day)
  are overtime, and every minute after 11 hours is double time. Every day is an ordinary
  day except a seventh consecutive day (G3).
- G2: Weekly threshold. A week holds at most 40 hours (2400 minutes) of regular time. When
  the regular minutes from G1 add up to more than 2400 over the week, the minutes beyond
  2400 are overtime instead. Overtime and double-time minutes from G1 and G3 do not count
  toward the 40 hours, and no minute ever moves between overtime and double time.
- G3: Seventh consecutive day. Days 1 to 7 are consecutive calendar days. When all seven
  days have more than 0 minutes worked, day 7 is a seventh consecutive day: its first 8
  hours (480 minutes) are overtime, every minute after 8 hours is double time, and none of
  its minutes are regular. When any day of the week has 0 minutes, day 7 is an ordinary
  day.

## Constraints

- C1: Money is counted in whole cents. Regular time pays the hourly rate, overtime 1.5
  times the rate and double time 2 times the rate. Each category's pay is worked out once,
  from the week's total minutes in that category, as rate_cents × multiplier × minutes ÷ 60,
  and rounded to the nearest cent with exact halves rounded up. `total_cents` is the sum of
  the three rounded amounts.
- C2: The command is named `pay`. It reads one JSON object on standard input with the
  fields `minutes`, a list of 7 integers giving the minutes worked on days 1 to 7 in
  order, and `rate_cents`, an integer hourly rate in cents; any other fields are ignored.
  On success it exits with status 0 and writes one JSON object with exactly the integer
  fields `regular_minutes`, `overtime_minutes`, `double_minutes`, `regular_cents`,
  `overtime_cents`, `double_cents` and `total_cents`, where the three minute fields add up
  to the minutes worked in the week. A refused request exits with status 2 and writes
  nothing on standard output.
- C3: Invalid requests are refused, never paid: input that is not JSON or not a JSON
  object; a missing `minutes` or `rate_cents`; a `minutes` that is not a list of exactly 7
  entries; a day's minutes that are not a whole number from 0 to 1440; and a `rate_cents`
  that is not a whole number from 1 to 100000. true and false are not numbers, and a
  number written with a decimal point or an exponent, such as 480.5, 480.0 or 4.8e2, is
  not a whole number. For example, the request
  `{"minutes": [480, -30, 0, 0, 0, 0, 0], "rate_cents": 1500}` is refused because day 2 is
  below 0: the command exits with status 2 and writes nothing on standard output.

## Scenarios

- S1: Five 9-hour days at $20.00 an hour. The request
  `{"minutes": [540, 540, 540, 540, 540, 0, 0], "rate_cents": 2000}` gets
  `{"regular_minutes": 2400, "overtime_minutes": 300, "double_minutes": 0, "regular_cents": 80000, "overtime_cents": 15000, "double_cents": 0, "total_cents": 95000}`.
  The daily overtime does not count toward the 40 hours.
- S2: Five 8-hour days and a 6-hour sixth day at $18.00 an hour. The request
  `{"minutes": [480, 480, 480, 480, 480, 360, 0], "rate_cents": 1800}` gets
  `{"regular_minutes": 2400, "overtime_minutes": 360, "double_minutes": 0, "regular_cents": 72000, "overtime_cents": 16200, "double_cents": 0, "total_cents": 88200}`.
  The sixth day is all past the 40 hours.
- S3: Six 4-hour days and a 10-hour seventh day at $25.00 an hour. The request
  `{"minutes": [240, 240, 240, 240, 240, 240, 600], "rate_cents": 2500}` gets
  `{"regular_minutes": 1440, "overtime_minutes": 480, "double_minutes": 120, "regular_cents": 60000, "overtime_cents": 30000, "double_cents": 10000, "total_cents": 100000}`.
- S4: One day of 8 hours 20 minutes at $10.01 an hour. The request
  `{"minutes": [500, 0, 0, 0, 0, 0, 0], "rate_cents": 1001}` gets
  `{"regular_minutes": 480, "overtime_minutes": 20, "double_minutes": 0, "regular_cents": 8008, "overtime_cents": 501, "double_cents": 0, "total_cents": 8509}`.
  The overtime works out to 500.5 cents, which rounds up.
- S5: Six 8-hour days and a 12-hour seventh day at $22.50 an hour. The request
  `{"minutes": [480, 480, 480, 480, 480, 480, 720], "rate_cents": 2250}` gets
  `{"regular_minutes": 2400, "overtime_minutes": 960, "double_minutes": 240, "regular_cents": 90000, "overtime_cents": 54000, "double_cents": 18000, "total_cents": 162000}`.
  Days 1 to 6 have 2880 regular minutes under G1, so the 480 beyond 2400 are overtime. Day
  7 is a seventh consecutive day: its first 480 minutes are overtime and the other 240
  double time, and none of them count toward the 40 hours.

## Out of scope

- Consecutive days carried over from the previous week, meal and rest breaks, holidays,
  pay periods longer than one week, and currencies other than US dollars.
