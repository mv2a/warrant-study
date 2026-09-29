"""G2: a group sits together whenever it can, in the frontmost row with a free block of its
size and, in that row, the lowest-numbered such block. Expected answers worked out by hand."""

from _cases import group as g, response, row, run_cases, seated
from _cmd import finish

CASES = [
    (
        "gap before the block (free 1,2,5,6,7,8)",
        {"rows": [8], "blocked": ["A3", "A4"], "groups": [g("Ferreira", 3), g("Gallo", 2), g("Hart", 1)]},
        response(seated("Ferreira", "A5", "A6", "A7"), seated("Gallo", "A1", "A2"), seated("Hart", "A8")),
    ),
    (
        "frontmost row with a block, not the row with most free seats",
        {
            "rows": [6, 6, 6],
            "blocked": ["A2", "A5", "B3", "B4"],
            "groups": [g("Ibsen", 3), g("Jansen", 2), g("Kahn", 2), g("Lowe", 2), g("Moss", 1), g("Nunez", 3), g("Orr", 1)],
        },
        response(
            seated("Ibsen", "C1", "C2", "C3"), seated("Jansen", "A3", "A4"), seated("Kahn", "B1", "B2"),
            seated("Lowe", "B5", "B6"), seated("Moss", "A1"), seated("Nunez", "C4", "C5", "C6"), seated("Orr", "A6"),
        ),
    ),
    (
        "lowest-numbered block, not the best-fitting block",
        {"rows": [10], "blocked": ["A7"], "groups": [g("Tate", 3), g("Ueno", 3), g("Vos", 3)]},
        response(seated("Tate", "A1", "A2", "A3"), seated("Ueno", "A4", "A5", "A6"), seated("Vos", "A8", "A9", "A10")),
    ),
    (
        "lowest-numbered blocks one after another",
        {"rows": [10], "blocked": ["A3", "A6"], "groups": [g("Pace", 2), g("Quill", 2), g("Rhee", 2), g("Sousa", 2)]},
        response(seated("Pace", "A1", "A2"), seated("Quill", "A4", "A5"), seated("Rhee", "A7", "A8"), seated("Sousa", "A9", "A10")),
    ),
    (
        "front row beats a lower number further back",
        {"rows": [5, 5], "blocked": ["A1"], "groups": [g("Ueda", 2), g("Vance", 3), g("Wynn", 2)]},
        response(seated("Ueda", "A2", "A3"), seated("Vance", "B1", "B2", "B3"), seated("Wynn", "A4", "A5")),
    ),
    (
        "a group as long as a whole row",
        {"rows": [4, 6, 6], "groups": [g("Xavier", 6), g("Young", 4), g("Zuber", 6)]},
        response(seated("Xavier", *row("B", 1, 6)), seated("Young", *row("A", 1, 4)), seated("Zuber", *row("C", 1, 6))),
    ),
    (
        "seat numbers past 9",
        {"rows": [14], "blocked": row("A", 1, 7), "groups": [g("Adler", 5), g("Brandt", 2)]},
        response(seated("Adler", *row("A", 8, 12)), seated("Brandt", "A13", "A14")),
    ),
    (
        "a later row when the front rows are too short",
        {"rows": [3, 3, 3, 5], "groups": [g("Bauer", 4), g("Cano", 3), g("Dietz", 1)]},
        response(seated("Bauer", *row("D", 1, 4)), seated("Cano", "A1", "A2", "A3"), seated("Dietz", "B1")),
    ),
    (
        "sold seats break a row into blocks",
        {"rows": [6, 6], "blocked": ["A4"], "groups": [g("Duval", 2), g("Ekman", 2), g("Fry", 2), g("Gill", 1)]},
        response(seated("Duval", "A1", "A2"), seated("Ekman", "A5", "A6"), seated("Fry", "B1", "B2"), seated("Gill", "A3")),
    ),
    (
        "a group that may split still sits together when it can",
        {"rows": [2, 5], "groups": [g("Holt", 1), g("Ivey", 3, True), g("Jiang", 2, True), g("Kerr", 1, True)]},
        response(seated("Holt", "A1"), seated("Ivey", "B1", "B2", "B3"), seated("Jiang", "B4", "B5"), seated("Kerr", "A2")),
    ),
    (
        "the back row Z",
        {"rows": [2] * 25 + [9], "blocked": ["Z5"], "groups": [g("Lamb", 4), g("Marsh", 4, False), g("Nagy", 2)]},
        response(seated("Lamb", *row("Z", 1, 4)), seated("Marsh", *row("Z", 6, 9)), seated("Nagy", "A1", "A2")),
    ),
    (
        "one person takes the first free seat",
        {"rows": [3, 3], "blocked": ["A1", "A2", "A3", "B1"], "groups": [g("Nash", 1), g("Ono", 1)]},
        response(seated("Nash", "B2"), seated("Ono", "B3")),
    ),
    (
        "wide theatre, blocks at the right end",
        {
            "rows": [50, 50],
            "blocked": row("A", 1, 44) + ["A47"] + row("B", 3, 50),
            "groups": [g("Ruth", 2), g("Soto", 3), g("Uhl", 2)],
        },
        response(
            seated("Ruth", "A45", "A46"), seated("Soto", "A48", "A49", "A50"), seated("Uhl", "B1", "B2"),
        ),
    ),
]

finish(run_cases(CASES, "G2"), f"together ok: {len(CASES)} requests")
