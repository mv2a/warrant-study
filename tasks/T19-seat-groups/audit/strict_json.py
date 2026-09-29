"""C3: standard input that is not JSON is refused, including text that Python's json module
accepts by default but JSON (RFC 8259) does not: the bare words NaN, Infinity and
-Infinity, even inside a field that would otherwise be ignored."""

from _audit import raw_all
from _cmd import finish

CASES = [
    '{"rows": [5], "groups": [], "note": NaN}',
    '{"rows": [5], "groups": [{"id": "Ames", "size": 1, "weight": Infinity}]}',
    '{"rows": [5], "groups": [], "limits": [-Infinity]}',
]

problems = []
for text, (status, out) in zip(CASES, raw_all(CASES)):
    if status != 2 or out != "":
        problems.append(f"not JSON, so expected status 2 and no output, got {status} and {out[:60]!r} | sent {text!r}")

finish(problems, f"non-JSON number words refused: {len(CASES)}")
