"""X16 (S2): the S2 request gets exactly the S2 response; the same case moved or reordered behaves alike."""

from _audit import finish, item, succeed

problems = []

succeed(problems, "S2 as written",
        raw='{"items": [{"id": "r1", "type": "reference", "due_day": 40, "returned_day": 42}, '
            '{"id": "d1", "type": "dvd", "due_day": 40, "returned_day": 42}]}',
        want={"items": [{"id": "r1", "days_late": 2, "fine_cents": 300},
                        {"id": "d1", "days_late": 2, "fine_cents": 0}], "total_cents": 300})

# The same pair, two days late each, on other days and in the other order.
for due in (0, 1, 512):
    succeed(problems, f"S2 moved to day {due}", {"items": [
        item("ref", "reference", due, due + 2), item("disc", "dvd", due, due + 2)]},
        want={"items": [{"id": "ref", "days_late": 2, "fine_cents": 300},
                        {"id": "disc", "days_late": 2, "fine_cents": 0}], "total_cents": 300})
    succeed(problems, f"S2 reversed on day {due}", {"items": [
        item("disc", "dvd", due, due + 2), item("ref", "reference", due, due + 2)]},
        want={"items": [{"id": "disc", "days_late": 2, "fine_cents": 0},
                        {"id": "ref", "days_late": 2, "fine_cents": 300}], "total_cents": 300})

finish(problems, "S2 ok")
