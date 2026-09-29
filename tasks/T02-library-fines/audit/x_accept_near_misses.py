"""X08 (C3, C1): requests that look close to a refusal but break no rule in C3 are answered, not refused."""

from _audit import finish, item, succeed

problems = []

# Day 0 is allowed for both fields.
succeed(problems, "due and returned on day 0", {"items": [item("h1", "reference", 0, 0)]})
succeed(problems, "due on day 0", {"items": [item("h2", "book", 0, 9)]})
succeed(problems, "returned on day 0 (early)", {"items": [item("h3", "dvd", 14, 0)]})

# Large whole day numbers are JSON integers of 0 or more.
succeed(problems, "large day numbers", {"items": [
    item("h4", "book", 10 ** 12, 10 ** 12 + 5),
    item("h5", "dvd", 0, 10 ** 15),
    item("h6", "reference", 999999999, 1000000000),
]})

# Ids that differ only in case, or by surrounding spaces, are different ids.
succeed(problems, "ids differing in case", {"items": [item("abc", "book", 1, 9), item("ABC", "book", 1, 9)]})
succeed(problems, "ids differing by a space", {"items": [item("x", "dvd", 1, 9), item("x ", "dvd", 1, 9)]})

# A one-character id and an id made of a single space are non-empty strings.
succeed(problems, "one-character id", {"items": [item("q", "reference", 3, 4)]})
succeed(problems, "id of one space", {"items": [item(" ", "book", 3, 40)]})

# Same due and returned days on items with different ids are fine.
succeed(problems, "identical items but ids", {"items": [
    item("s1", "dvd", 5, 9), item("s2", "dvd", 5, 9), item("s3", "dvd", 5, 9)]})

# Numbers written as JSON integers with surrounding whitespace in the text.
succeed(problems, "integers with whitespace",
        raw='{ "items" : [ { "id" : "w1" , "type" : "book" , "due_day" :  6 , "returned_day" : 16 } ] }',
        want={"items": [{"id": "w1", "days_late": 10, "fine_cents": 175}], "total_cents": 175})

finish(problems, "near misses ok: valid requests close to the refusal rules are answered")
