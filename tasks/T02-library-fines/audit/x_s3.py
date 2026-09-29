"""X17 (S3): the S3 request gets exactly the S3 response; the same case moved or reordered behaves alike."""

from _audit import finish, item, succeed

problems = []

succeed(problems, "S3 as written",
        raw='{"items": [{"id": "d7", "type": "dvd", "due_day": 5, "returned_day": 35}, '
            '{"id": "r3", "type": "reference", "due_day": 5, "returned_day": 10}]}',
        want={"items": [{"id": "d7", "days_late": 30, "fine_cents": 2000},
                        {"id": "r3", "days_late": 5, "fine_cents": 750}], "total_cents": 2500})

# A DVD 30 days late (capped at 2000) with a reference item 5 days late (750): 2750 capped to 2500.
for due in (0, 61, 4040):
    succeed(problems, f"S3 moved to day {due}", {"items": [
        item("disc", "dvd", due, due + 30), item("ref", "reference", due, due + 5)]},
        want={"items": [{"id": "disc", "days_late": 30, "fine_cents": 2000},
                        {"id": "ref", "days_late": 5, "fine_cents": 750}], "total_cents": 2500})
    succeed(problems, f"S3 reversed on day {due}", {"items": [
        item("ref", "reference", due, due + 5), item("disc", "dvd", due, due + 30)]},
        want={"items": [{"id": "ref", "days_late": 5, "fine_cents": 750},
                        {"id": "disc", "days_late": 30, "fine_cents": 2000}], "total_cents": 2500})

finish(problems, "S3 ok")
