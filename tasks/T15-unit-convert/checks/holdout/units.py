"""H6: units of different kinds, and unknown units, are refused; every unit converts to itself (C3)."""

from _cmd import call, finish
from _units import KIND, UNITS

UNKNOWN = ["KG", "Kg", "M", "MM", "L", "ML", "Gal", "FLOZ", "lbs", "gallon", "meter", "metre",
           "mile", "inch", "feet", "foot", "tonne", "ton", "stone", "ounce", "fl oz", "fl_oz",
           "cc", "cm3", "dm", "um", " m", "m ", "", "furlong"]


def refused(status, body):
    return status == 2 and not (isinstance(body, dict) and "value" in body)


problems = []
count = 0
for source in UNITS:
    for target in UNITS:
        if KIND[source] == KIND[target]:
            continue
        count += 1
        status, body = call({"value": "3", "from": source, "to": target, "places": 2})
        if not refused(status, body):
            problems.append(f"{source} to {target} mixes {KIND[source]} and {KIND[target]}: expected a refusal, got status {status} and {body!r}")

for name in UNKNOWN:
    for source, target in ((name, "m"), ("kg", name)):
        count += 1
        status, body = call({"value": "3", "from": source, "to": target, "places": 2})
        if not refused(status, body):
            problems.append(f"unknown unit {name!r} ({source!r} to {target!r}): expected a refusal, got status {status} and {body!r}")

for unit in UNITS:
    for places, want in ((0, "12"), (1, "12.3"), (4, "12.3400")):
        count += 1
        status, body = call({"value": "12.34", "from": unit, "to": unit, "places": places})
        got = body.get("value") if isinstance(body, dict) else None
        if status != 0 or got != want:
            problems.append(f"12.34 {unit} to {unit} at {places} places: expected {want!r}, got {got!r} (status {status})")

finish(problems, f"units ok: {count} requests")
