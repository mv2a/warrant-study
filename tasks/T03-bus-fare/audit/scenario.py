"""X9-X11 (S1, S2, S3): one example day from the intent, exactly, plus the partial days its
explanation relies on. Usage: python3 scenario.py S1|S2|S3"""

import sys

from _audit import check_cases, trip
from _cmd import finish

SCENARIOS = {
    "S1": [
        ("S1 as written", {"age": 40, "trips": [trip(450, 2, 5), trip(490, 5, 6), trip(600, 6, 6)]}, [555, 0, 270]),
        ("S1 first trip alone", {"age": 40, "trips": [trip(450, 2, 5)]}, [555]),
        ("S1 first two trips", {"age": 40, "trips": [trip(450, 2, 5), trip(490, 5, 6)]}, [555, 0]),
        ("S1 fields in another order", {"trips": [{"to_zone": 5, "from_zone": 2, "board_minute": 450}, {"to_zone": 6, "board_minute": 490, "from_zone": 5}, {"from_zone": 6, "to_zone": 6, "board_minute": 600}], "age": 40}, [555, 0, 270]),
    ],
    "S2": [
        ("S2 as written", {"age": 11, "trips": [trip(480, 1, 3), trip(1000, 3, 3)]}, [230, 135]),
        ("S2 first trip alone", {"age": 11, "trips": [trip(480, 1, 3)]}, [230]),
        ("S2 second trip alone", {"age": 11, "trips": [trip(1000, 3, 3)]}, [135]),
        ("S2 fields in another order", {"trips": [{"to_zone": 3, "board_minute": 480, "from_zone": 1}, {"from_zone": 3, "board_minute": 1000, "to_zone": 3}], "age": 11}, [230, 135]),
    ],
    "S3": [
        ("S3 as written", {"age": 30, "trips": [trip(420, 1, 6), trip(480, 6, 4), trip(720, 4, 6), trip(1080, 6, 6)]}, [745, 0, 355, 0]),
        ("S3 first three trips", {"age": 30, "trips": [trip(420, 1, 6), trip(480, 6, 4), trip(720, 4, 6)]}, [745, 0, 355]),
        ("S3 third trip alone", {"age": 30, "trips": [trip(720, 4, 6)]}, [460]),
        ("S3 fields in another order", {"trips": [{"board_minute": 420, "to_zone": 6, "from_zone": 1}, {"to_zone": 4, "from_zone": 6, "board_minute": 480}, {"from_zone": 4, "board_minute": 720, "to_zone": 6}, {"to_zone": 6, "from_zone": 6, "board_minute": 1080}], "age": 30}, [745, 0, 355, 0]),
    ],
}

name = sys.argv[1] if len(sys.argv) > 1 else ""
if name not in SCENARIOS:
    sys.exit(f"usage: scenario.py {'|'.join(SCENARIOS)}")
finish(check_cases(SCENARIOS[name]), f"{name} ok: {len(SCENARIOS[name])} requests")
