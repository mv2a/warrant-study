"""X7 (C2): the valid edges are priced, not refused: empty days, same-minute trips, and every range limit."""

from _audit import check_cases, trip
from _cmd import finish

cases = [
    # An empty trips list is valid and costs nothing, for every band and at the age limits.
    ("empty day, age 0", {"age": 0, "trips": []}, []),
    ("empty day, age 13", {"age": 13, "trips": []}, []),
    ("empty day, age 36", {"age": 36, "trips": []}, []),
    ("empty day, age 120", {"age": 120, "trips": []}, []),
    # Range limits are inclusive: age 0 and 120, minute 0 and 1439, zones 1 and 6.
    ("age 0, minute 0, zones 1 to 6", {"age": 0, "trips": [trip(0, 1, 6)]}, [0]),
    ("age 120, minute 1439, zones 6 to 1", {"age": 120, "trips": [trip(1439, 6, 1)]}, [295]),
    ("minute 0 and 1439", {"age": 26, "trips": [trip(0, 6, 6), trip(1439, 1, 1)]}, [270, 270]),
    ("zone 1 and zone 6 alone", {"age": 58, "trips": [trip(90, 1, 1), trip(900, 6, 6)]}, [270, 270]),
    # Trips boarding in the same minute are in order.
    ("same minute, adult", {"age": 36, "trips": [trip(720, 1, 2), trip(720, 2, 2), trip(720, 2, 1)]}, [365, 0, 0]),
    ("same minute, then later", {"age": 36, "trips": [trip(10, 1, 1), trip(10, 1, 1), trip(200, 1, 1), trip(200, 1, 1)]}, [270, 0, 270, 0]),
    ("same minute at 0", {"age": 9, "trips": [trip(0, 3, 5), trip(0, 5, 3)]}, [230, 0]),
    ("same minute at 1439", {"age": 71, "trips": [trip(1439, 2, 6), trip(1439, 6, 2)]}, [260, 0]),
    ("non-decreasing long day", {"age": 3, "trips": [trip(m, 1, 6) for m in (0, 0, 5, 5, 5, 700, 1439, 1439)]}, [0] * 8),
]

finish(check_cases(cases), f"valid edges ok: {len(cases)} requests priced")
