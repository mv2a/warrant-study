---
owner: the revenue office of Norvale (a fictional country)
---

# Norvale income tax

Norvale is an invented country. Its revenue office wants a small calculator that turns a
filer's yearly income and number of dependents into the income tax owed, and shows each
step so the filer can follow the arithmetic. The rules below are the whole tax. They are
made up for this calculator and follow no real country's law. Amounts are in marks,
written like 12,000.00, and the calculator counts them in whole cents.

## Goals

- G1: Taxable income is taxed in bands, and each rate applies only to the part of taxable
  income inside its band: 5% on the first 10,000.00, 15% on the part above 10,000.00 up
  to 40,000.00, 25% on the part above 40,000.00 up to 100,000.00, and 38% on the part
  above 100,000.00. The sum over the bands is the tax before credit.
- G2: Every filer has a standard allowance of 12,000.00. When the income is above
  80,000.00, the allowance shrinks by one fifth of the income above 80,000.00, so it is
  zero for incomes of 140,000.00 and above. The allowance is never less than zero.
- G3: Each dependent brings a credit of 450.00, taken off the tax before credit. The credit
  is non-refundable: it can bring the tax down to zero but never below, and any part of it
  the tax cannot absorb is lost. The credit reported is the part actually used.

## Constraints

- C1: Money is counted in whole cents. The tax before credit is worked out exactly and then
  rounded to the nearest cent, with an exact half cent rounded up. The allowance reduction
  of G2 is rounded up to the next whole cent whenever it is not already a whole cent.
- C2: The figures add up: the taxable income is the income minus the allowance, or zero
  when the allowance is larger than the income; the tax owed is the tax before credit minus
  the credit used; and the income in the response repeats the income in the request.
- C3: Invalid requests are refused, never taxed. A request is invalid when standard input
  does not hold exactly one JSON object with nothing but whitespace before or after it (so
  any other text, or a second JSON value, after the object makes it invalid); when
  `income_cents` or `dependents` is missing; when either of them is not a JSON integer (for
  example 1200.5, 1200.0, "1200", true or null); when `income_cents` is negative; or when
  `dependents` is negative or more than 20. Every other request is taxed, including an
  income of zero.
- C4: The calculator runs as a command named `tax`. It reads one JSON object on standard
  input with the fields `income_cents` (the yearly income, in cents) and `dependents` (the
  number of dependents); any other fields are ignored. On success it exits with status 0
  and writes one JSON object on standard output with exactly these fields, each a JSON
  integer: `income_cents`, `allowance_cents`, `taxable_cents`, `tax_before_credit_cents`,
  `credit_cents` and `tax_cents`. A refused request exits with status 2 and writes nothing
  on standard output.

## Scenarios

- S1: A filer with 30,000.00 of income and no dependents owes 1,700.00 (5% of 10,000.00
  plus 15% of 8,000.00): `{"income_cents": 3000000, "dependents": 0}` gives
  `{"income_cents": 3000000, "allowance_cents": 1200000, "taxable_cents": 1800000,
  "tax_before_credit_cents": 170000, "credit_cents": 0, "tax_cents": 170000}`.
- S2: A filer with 95,000.00 of income and 2 dependents has an allowance of 9,000.00
  (3,000.00 less than the standard one) and owes 15,600.00:
  `{"income_cents": 9500000, "dependents": 2}` gives
  `{"income_cents": 9500000, "allowance_cents": 900000, "taxable_cents": 8600000,
  "tax_before_credit_cents": 1650000, "credit_cents": 90000, "tax_cents": 1560000}`.
- S3: A filer with 14,000.00 of income and 3 dependents owes nothing: the 1,350.00 credit
  absorbs the 100.00 of tax and the rest of it is lost:
  `{"income_cents": 1400000, "dependents": 3}` gives
  `{"income_cents": 1400000, "allowance_cents": 1200000, "taxable_cents": 200000,
  "tax_before_credit_cents": 10000, "credit_cents": 10000, "tax_cents": 0}`.
- S4: A filer with 12,000.30 of income and no dependents has 0.30 of taxable income; 5% of
  it is 1.5 cents, which rounds up to 2 cents: `{"income_cents": 1200030, "dependents": 0}`
  gives `{"income_cents": 1200030, "allowance_cents": 1200000, "taxable_cents": 30,
  "tax_before_credit_cents": 2, "credit_cents": 0, "tax_cents": 2}`.

## Out of scope

- Other deductions and credits, joint filing, several tax years, negative income, and
  currencies other than Norvale marks.
