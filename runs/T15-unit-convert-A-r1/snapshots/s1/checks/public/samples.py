"""P3: a few everyday conversions, one or two for each kind of measure."""

from _cmd import call, finish

SAMPLES = [
    ("1", "yd", "in", 0, "36"),
    ("1", "km", "cm", 0, "100000"),
    ("1", "kg", "g", 1, "1000.0"),
    ("2", "st", "lb", 0, "28"),
    ("1", "l", "ml", 0, "1000"),
    ("1", "gal", "pt", 0, "8"),
]
problems = []
for value, source, target, places, expected in SAMPLES:
    status, body = call({"value": value, "from": source, "to": target, "places": places})
    got = body.get("value") if isinstance(body, dict) else None
    if status != 0 or got != expected:
        problems.append(f"{value} {source} to {target} at {places} places: expected {expected!r}, got {got!r} (status {status})")

finish(problems, f"samples ok: {len(SAMPLES)} conversions")
