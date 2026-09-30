---
owner: lending desk, consumer loans
---

# Loan repayment schedule

We lend fixed amounts at a fixed yearly rate, repaid in equal monthly payments. Before a
customer signs, we show them the whole repayment schedule: what they pay each month, how
much of it is interest and how much pays down the loan, and what they still owe
afterwards. Every figure is in whole cents, the rounding is stated in advance, and the
last payment leaves the customer owing exactly nothing.

The monthly rate `i` is the yearly rate divided by 12. Rates are given in basis points,
so `i` is `annual_rate_bp / 120000` (650 basis points is 6.50% a year).

## Goals

- G1: For a yearly rate above zero, the regular monthly payment is the level payment
  P × i ÷ (1 − (1 + i)^−n), where P is the amount borrowed and n the number of months. It
  is computed exactly and rounded up to the next whole cent; a result that is already a
  whole number of cents is not changed.
- G2: Each month's interest is the balance owed at the start of that month times i,
  rounded to the nearest cent, with an exact half cent rounded up. The rest of that
  month's payment is principal, and the balance after the payment is the starting balance
  minus that principal. Month 1 starts from the amount borrowed; every later month starts
  from the balance the month before left.
- G3: The last payment clears the loan exactly: it is that month's starting balance plus
  that month's interest, and leaves a balance of 0. The schedule ends in the first month
  whose starting balance plus interest is at most the regular payment, or in month n if
  no earlier month qualifies, so a loan can finish before month n. Every month before the
  last pays exactly the regular payment and leaves a balance above 0.
- G4: Interest-free loans (a yearly rate of 0) are scheduled too: every month's interest
  is 0, and the regular payment is the amount borrowed divided by the number of months,
  rounded up to the next whole cent.

## Constraints

- C1: The schedule is produced by a command named `schedule` that reads one JSON object
  on standard input and writes one JSON object on standard output. The request has three
  whole-number fields: `principal_cents` (the amount borrowed), `annual_rate_bp` (the
  yearly rate in basis points) and `months` (n, the number of monthly payments). Any other
  field in the request is ignored: the loan is scheduled as if it were not there. The
  response has exactly the fields `payment_cents` (the regular payment),
  `total_interest_cents` and `rows`, and the command exits with status 0. `rows` is a
  list with one object per payment, in order, each with exactly the whole-number fields
  `month` (1, 2, 3, ...), `payment_cents`, `interest_cents`, `principal_cents` and
  `balance_cents` (what is still owed after that payment). A refused request exits with
  status 2 and writes nothing on standard output.
- C2: The totals add up: `total_interest_cents` is the sum of every row's interest, the
  rows' principal amounts add up to exactly the amount borrowed, and the rows' payments
  add up to the amount borrowed plus the total interest.
- C3: Invalid requests are refused, never scheduled. That includes text that is not JSON,
  JSON that is not an object, a missing field, a field that is not written as a whole
  number (such as true, false, null, "12", 12.5 or 12.0), `principal_cents` below 1 or
  above 1000000000, `annual_rate_bp` below 0 or above 5000, and `months` below 1 or
  above 480.

## Scenarios

- S1: Borrowing 1000000 cents at 600 basis points for 12 months gives a regular payment
  of 86067 cents. Month 1 is 5000 cents of interest and 81067 of principal, leaving
  918933. The 12th and last payment is 86059 cents, and the total interest is 32796.
- S2: Borrowing 100000 cents at 0 basis points for 7 months gives a regular payment of
  14286 cents. Months 1 to 6 pay 14286 each with no interest, and the 7th and last
  payment is 14284 cents, leaving 0. The total interest is 0.
- S3: Borrowing 700000 cents at 500 basis points for 24 months gives a regular payment
  of 30710 cents. Month 1 is 2917 cents of interest and 27793 of principal. The 24th and
  last payment is 30714 cents, more than the regular payment, of which 127 is interest.
  The total interest is 37044.

## Out of scope

- Fees, variable rates, payment holidays, extra or missed payments, and currencies.
