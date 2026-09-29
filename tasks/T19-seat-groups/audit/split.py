"""G3: a group is split only as a last resort, only with "may_split": true and enough free
seats, and then takes the first free seats in seating order. Expected answers worked out
by hand."""

from _cases import group as g, refused, response, row, run_cases, seated
from _cmd import finish

CASES = [
    (
        "split around blocked seats, first free seats first",
        {"rows": [3, 3, 3], "blocked": ["A2", "B2", "C2"], "groups": [g("Olmo", 3, True), g("Park", 2, True), g("Quinn", 1)]},
        response(seated("Olmo", "A1", "A3", "B1"), seated("Park", "B3", "C1"), seated("Quinn", "C3")),
    ),
    (
        "split over the leftover seats of earlier groups",
        {"rows": [5, 5, 2], "groups": [g("Reyes", 4), g("Stahl", 4), g("Toth", 3, True), g("Udall", 1)]},
        response(
            seated("Reyes", *row("A", 1, 4)), seated("Stahl", *row("B", 1, 4)),
            seated("Toth", "A5", "B5", "C1"), seated("Udall", "C2"),
        ),
    ),
    (
        "splitting is the last resort",
        {"rows": [3, 4], "blocked": ["A2"], "groups": [g("Vidal", 3, True), g("Wade", 2, True)]},
        response(seated("Vidal", "B1", "B2", "B3"), seated("Wade", "A1", "A3")),
    ),
    (
        "never split without may_split true",
        {
            "rows": [3, 3],
            "blocked": ["A2", "B2"],
            "groups": [g("Xu", 3), g("Yates", 3, False), g("Zamora", 3, True), g("Arndt", 1)],
        },
        response(
            refused("Xu", "not_together"), refused("Yates", "not_together"),
            seated("Zamora", "A1", "A3", "B1"), seated("Arndt", "B3"),
        ),
    ),
    (
        "split seats past 9",
        {"rows": [12], "blocked": row("A", 1, 8) + ["A11"], "groups": [g("Bose", 3, True)]},
        response(seated("Bose", "A9", "A10", "A12")),
    ),
    (
        "split down a column of one-seat rows",
        {"rows": [1] * 26, "groups": [g("Cho", 5, True), g("Dunn", 21, True), g("Egan", 1, True)]},
        response(
            seated("Cho", "A1", "B1", "C1", "D1", "E1"),
            seated("Dunn", *[f"{letter}1" for letter in "FGHIJKLMNOPQRSTUVWXYZ"]),
            refused("Egan", "not_enough_seats"),
        ),
    ),
    (
        "split takes every free seat when it needs them all",
        {"rows": [4, 4], "blocked": ["A2", "B3"], "groups": [g("Eads", 6, True), g("Fox", 1, True)]},
        response(seated("Eads", "A1", "A3", "A4", "B1", "B2", "B4"), refused("Fox", "not_enough_seats")),
    ),
    (
        "no split when too few seats are free",
        {"rows": [3, 3], "blocked": ["A2"], "groups": [g("Gao", 6, True), g("Hahn", 5, True)]},
        response(refused("Gao", "not_enough_seats"), seated("Hahn", "A1", "A3", "B1", "B2", "B3")),
    ),
    (
        "first free seats, not the fewest pieces",
        {"rows": [4, 4, 4], "blocked": ["A2", "B1", "B4", "C2", "C3"], "groups": [g("Ivers", 5, True), g("Juno", 2, True)]},
        response(seated("Ivers", "A1", "A3", "A4", "B2", "B3"), seated("Juno", "C1", "C4")),
    ),
    (
        "a group longer than any row splits across rows",
        {"rows": [3, 3, 3], "groups": [g("Kane", 1), g("Lutz", 7, True), g("Moro", 1)]},
        response(seated("Kane", "A1"), seated("Lutz", "A2", "A3", "B1", "B2", "B3", "C1", "C2"), seated("Moro", "C3")),
    ),
]

finish(run_cases(CASES, "G3"), f"split ok: {len(CASES)} requests")
