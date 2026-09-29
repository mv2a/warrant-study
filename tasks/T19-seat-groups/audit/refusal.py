"""G4: a group that cannot be seated is refused whole, with "not_enough_seats" when fewer
seats are free than it has members and "not_together" otherwise. Expected answers worked
out by hand. Each group must be answered exactly once, so a refused group holds no seats."""

from _cases import group as g, refused, response, row, run_cases, seated
from _cmd import finish

CASES = [
    (
        "one more person than the hall holds",
        {"rows": [4], "groups": [g("Ivo", 5), g("Jae", 5, True), g("Kit", 4)]},
        response(refused("Ivo", "not_enough_seats"), refused("Jae", "not_enough_seats"), seated("Kit", *row("A", 1, 4))),
    ),
    (
        "enough seats in total but no block",
        {
            "rows": [3, 3],
            "blocked": ["A2", "B2"],
            "groups": [g("Lars", 4), g("Mei", 5), g("Nils", 5, True), g("Otto", 3), g("Pia", 2, False), g("Rui", 1)],
        },
        response(
            refused("Lars", "not_together"), refused("Mei", "not_enough_seats"), refused("Nils", "not_enough_seats"),
            refused("Otto", "not_together"), refused("Pia", "not_together"), seated("Rui", "A1"),
        ),
    ),
    (
        "a group longer than every row",
        {"rows": [3, 3], "groups": [g("Sade", 4), g("Tove", 4, False), g("Uma", 3), g("Vik", 3)]},
        response(
            refused("Sade", "not_together"), refused("Tove", "not_together"),
            seated("Uma", "A1", "A2", "A3"), seated("Vik", "B1", "B2", "B3"),
        ),
    ),
    (
        "refusals after earlier sales",
        {"rows": [5], "groups": [g("Wen", 3), g("Xia", 3), g("Yul", 3, True), g("Zed", 2), g("Amos", 1, True)]},
        response(
            seated("Wen", "A1", "A2", "A3"), refused("Xia", "not_enough_seats"), refused("Yul", "not_enough_seats"),
            seated("Zed", "A4", "A5"), refused("Amos", "not_enough_seats"),
        ),
    ),
    (
        "every seat blocked",
        {"rows": [2], "blocked": ["A2", "A1"], "groups": [g("Bly", 1), g("Cai", 1, True)]},
        response(refused("Bly", "not_enough_seats"), refused("Cai", "not_enough_seats")),
    ),
    (
        "free seats equal to the group, split by a blocked seat",
        {"rows": [2, 3], "blocked": ["B2"], "groups": [g("Dov", 4), g("Eli", 3), g("Fay", 2), g("Gus", 2), g("Hal", 3)]},
        response(
            refused("Dov", "not_together"), refused("Eli", "not_together"), seated("Fay", "A1", "A2"),
            refused("Gus", "not_together"), refused("Hal", "not_enough_seats"),
        ),
    ),
    (
        "full theatre sizes",
        {"rows": [50] * 26, "groups": [g("Iris", 1301), g("Joel", 1300), g("Lena", 10**9, True), g("Mona", 51, False), g("Ned", 50)]},
        response(
            refused("Iris", "not_enough_seats"), refused("Joel", "not_together"), refused("Lena", "not_enough_seats"),
            refused("Mona", "not_together"), seated("Ned", *row("A", 1, 50)),
        ),
    ),
    (
        "exactly one seat short, split allowed",
        {"rows": [4, 4], "blocked": ["A1", "B4"], "groups": [g("Opal", 7, True), g("Pim", 6, True)]},
        response(refused("Opal", "not_enough_seats"), seated("Pim", "A2", "A3", "A4", "B1", "B2", "B3")),
    ),
]

finish(run_cases(CASES, "G4"), f"refusal ok: {len(CASES)} requests")
