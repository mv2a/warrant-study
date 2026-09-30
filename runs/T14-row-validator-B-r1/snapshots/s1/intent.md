---
owner: data intake team
---

# Row validator

Teams hand us tables as JSON: a list of rows, each row an object of field values. Before a
table is loaded anywhere, we check it against a small schema that says which fields must be
filled in, what type each field holds, what range or values it may take, and which fields
must never repeat. A table with problems is not simply rejected: people need the full list
of what is wrong, row by row and field by field, in an order they can read from top to
bottom.

## Goals

- G1: A row that leaves out a required field, or holds `null` in it, gets a `missing` error
  for that field. A field that is not required may be left out or `null`; it then gets no
  error and no other check.
- G2: A value of the wrong type gets a `type` error. A `string` field takes JSON strings, a
  `boolean` field takes `true` and `false`, a `number` field takes any JSON number, and an
  `integer` field takes numbers with no fractional part, so `4` and `4.0` are integers and
  `4.5` is not. `true` and `false` are never numbers.
- G3: A number below the field's `min` or above its `max` gets a `range` error; both bounds
  are inclusive. A value that equals none of the entries in the field's `allowed` list gets
  an `allowed` error. Strings are equal only when they match exactly, case and spaces
  included: they are compared as sequences of Unicode code points and never normalized, so
  an accented letter written as one code point does not equal the same letter written as a
  base letter followed by a combining accent. Numbers are equal when their values are, so
  `2` equals `2.0`.
- G4: In a field marked `unique`, a value that equals (as in G3) a value in the same field
  of an earlier row gets a `duplicate` error; the first occurrence gets none. Only values of
  the field's type take part, so an earlier `true` never makes a later `1` a duplicate, and
  a left-out or `null` value is never a duplicate.
- G5: Every problem in every row is reported, however many there are: checking never stops
  at the first bad row or at the first bad field of a row. Fields a row has that the schema
  does not name are ignored.

## Constraints

- C1: The command is named `validate`. It reads one JSON object from standard input,
  `{"schema": [<field rule>, ...], "rows": [<object>, ...]}`, writes one JSON object to
  standard output, `{"valid": <true or false>, "errors": [{"row": <integer>, "field":
  <string>, "code": <string>}, ...]}`, and exits with status 0. `row` is the row's
  zero-based position in `rows`, `field` is the field's name, `code` is one of `missing`,
  `type`, `range`, `allowed` or `duplicate`, and `valid` is true exactly when `errors` is
  empty. A field rule is an object with a `name` (a non-empty string), a `type` (`string`,
  `integer`, `number` or `boolean`) and, optionally, `required` and `unique` (true or false;
  false when left out), `min` and `max` (numbers) and `allowed` (a list of values). A
  refused request writes nothing to standard output, says why on standard error, and exits
  with status 2.
- C2: Each field of each row gets at most one error: the first that applies in the order
  `missing`, `type`, `range`, `allowed`, `duplicate`.
- C3: Errors are listed by row position, lowest first, and within one row in the order the
  fields appear in the schema.
- C4: A malformed request is refused, never validated. That covers: text that isn't a JSON
  object; a missing `schema` or `rows`, or any other top-level key; a `schema` that isn't a
  non-empty list of field rules; a field rule with a missing, empty or repeated `name`, a
  missing or unknown `type`, or a key other than the seven named in C1; a `required` or
  `unique` that isn't true or false; a `min` or `max` that isn't a number, or that sits on
  a `string` or `boolean` field; a `min` greater than its `max`; an `allowed` that isn't a
  non-empty list of values of the field's type (as in G2); and `rows` that isn't a list of
  objects. Bad values inside rows are never refused: they are reported as errors.

## Scenarios

Every scenario uses this schema, called ROSTER:

```json
[{"name": "id", "type": "integer", "required": true, "unique": true, "min": 1},
 {"name": "email", "type": "string", "required": true, "unique": true},
 {"name": "age", "type": "integer", "min": 16, "max": 99},
 {"name": "shift", "type": "string", "allowed": ["morning", "evening"]},
 {"name": "lead", "type": "boolean"}]
```

- S1: With ROSTER and the rows `[{"id": 1, "email": "ana@example.org", "age": 34, "shift":
  "morning", "lead": true}, {"id": 2, "email": "ben@example.org", "shift": "evening",
  "badge": "B-17"}, {"id": 3, "email": "cy@example.org", "age": null, "lead": false}]`, the
  output is `{"valid": true, "errors": []}`.
- S2: With ROSTER and the rows `[{"id": 1, "email": "ana@example.org", "age": 15, "shift":
  "Morning"}, {"email": "ben@example.org", "age": "40", "lead": "yes"}, {"id": 3, "email":
  null, "age": 58, "shift": "night"}]`, the output is `{"valid": false, "errors": [{"row":
  0, "field": "age", "code": "range"}, {"row": 0, "field": "shift", "code": "allowed"},
  {"row": 1, "field": "id", "code": "missing"}, {"row": 1, "field": "age", "code": "type"},
  {"row": 1, "field": "lead", "code": "type"}, {"row": 2, "field": "email", "code":
  "missing"}, {"row": 2, "field": "shift", "code": "allowed"}]}`.
- S3: With ROSTER and the rows `[{"id": 7, "email": "ana@example.org"}, {"id": 8, "email":
  "ANA@example.org"}, {"id": 7, "email": "ana@example.org"}, {"id": 0, "email":
  "dee@example.org"}]`, the output is `{"valid": false, "errors": [{"row": 2, "field": "id",
  "code": "duplicate"}, {"row": 2, "field": "email", "code": "duplicate"}, {"row": 3,
  "field": "id", "code": "range"}]}`.

## Out of scope

- Dates, patterns, string lengths, rules that span several fields, and nested objects.
- Converting values: `"40"` is never read as the number 40.
- Input formats other than one JSON request on standard input.
