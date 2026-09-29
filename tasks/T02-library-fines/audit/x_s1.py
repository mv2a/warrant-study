"""X15 (S1): the S1 request gets exactly the S1 response; the same case moved to other days behaves alike."""

from _audit import finish, item, succeed

problems = []

# The scenario exactly as written in the intent.
succeed(problems, "S1 as written",
        raw='{"items": [{"id": "b1", "type": "book", "due_day": 10, "returned_day": 17}]}',
        want={"items": [{"id": "b1", "days_late": 7, "fine_cents": 100}], "total_cents": 100})

# The same situation (a book 7 days late, 4 charged at 25 cents) on other day numbers and ids.
for due in (0, 3, 250, 99999):
    succeed(problems, f"S1 moved to day {due}", {"items": [item("book-7", "book", due, due + 7)]},
            want={"items": [{"id": "book-7", "days_late": 7, "fine_cents": 100}], "total_cents": 100})

finish(problems, "S1 ok")
