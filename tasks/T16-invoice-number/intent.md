---
owner: rui, finance operations
---

# Invoice numbering

We invoice from four branches. Every invoice needs a number that tells at a glance which
branch issued it and in which year, and the numbers of one branch must run without gaps
or repeats within a year. The numbering service is given the branch, the current year
and the branch's previous invoice number, and works out the next one. A previous number
it cannot read with certainty is refused, never guessed at.

## Goals

- G1: Each branch numbers its invoices with its own prefix: `lisbon` uses `LIS`, `porto`
  uses `OPO`, `faro` uses `FAO` and `braga` uses `BRG`.
- G2: When the previous number is from the request's year, the next number continues its
  sequence by exactly one: after sequence 41 comes 42, after 999 comes 1000.
- G3: Numbering restarts every year. When the branch has no previous number, or its
  previous number is from an earlier year (however many years earlier), the sequence is 1.

## Constraints

- C1: An invoice number is written `PREFIX-YYYY-NNNNN`: the branch prefix, a hyphen, the
  request's year in four digits, a hyphen and the sequence padded with zeros to exactly
  five digits. The response's `sequence` is that same sequence as a whole number.
- C2: A malformed previous number is refused, never continued. Well-formed means exactly
  the prefix of the request's branch, a hyphen, a year from 2000 to 9999 in four digits, a
  hyphen and five digits that are not all zeros, with nothing before, after or in between.
  Every character must be its exact ASCII character, not only the digits: the prefix's
  capital letters, the hyphen-minus `-` and the digits 0 to 9. Look-alikes, such as
  letters from another alphabet, fullwidth forms or Unicode dashes, are refused, never
  normalized. So another branch's number, `LIS-2026-42`, `LIS-2026-000042`,
  `lis-2026-00041`, `LIS-26-00041`, `LIS-1999-00041`, `LIS-2026-00000` and
  `LIS-2026-00041 ` (with a trailing space) are all refused for `lisbon`.
- C3: Numbering never goes backwards and never outgrows its five digits. A previous number
  from a later year than the request is refused, and so is a previous number from the
  request's year with sequence 99999, because the next one would need six digits.
- C4: Invalid requests are refused: standard input that isn't valid UTF-8 (anywhere in it,
  even inside a field that would otherwise be ignored), text that isn't JSON, JSON that
  isn't an object, a missing `branch`, `year` or `previous` field, a branch that isn't
  exactly one of the four names in G1 (so `Lisbon`, `LIS` and `coimbra` are refused), a
  year that isn't a whole number from 2000 to 9999 (so `"2026"`, `2026.0` and `true` are
  refused), and a previous number that is neither text nor null.
- C5: The service runs as a command named `next`. It reads one JSON object, written in
  UTF-8, on standard input with the fields `branch` (text), `year` (whole number) and
  `previous` (text, or null when the branch has never issued an invoice), and ignores any
  other fields. On success it exits with status 0 and writes one JSON object on standard
  output with exactly the fields `number` (text) and `sequence` (whole number). A refused
  request exits with status 2 and writes nothing on standard output; a reason may go to
  standard error.

## Scenarios

- S1: `{"branch": "lisbon", "year": 2026, "previous": "LIS-2026-00041"}` gets
  `{"number": "LIS-2026-00042", "sequence": 42}`.
- S2: `{"branch": "porto", "year": 2027, "previous": "OPO-2026-01873"}` gets
  `{"number": "OPO-2027-00001", "sequence": 1}`, because a new year restarts the count.
- S3: `{"branch": "faro", "year": 2026, "previous": null}` gets
  `{"number": "FAO-2026-00001", "sequence": 1}`.
- S4: `{"branch": "braga", "year": 2026, "previous": "LIS-2026-00041"}` is refused with
  status 2 and no output, because that is a Lisbon number, not a Braga one.

## Out of scope

- Storing numbers, reserving them concurrently, credit notes and branches other than the
  four above.
