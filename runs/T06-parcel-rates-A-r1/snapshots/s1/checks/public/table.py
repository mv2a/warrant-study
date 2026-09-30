"""P3: a few parcels in the middle of their weight bracket pay the table price."""

from _cmd import call, finish

CASES = [  # (zone, actual weight in grams, expected base price in cents); every parcel is 10 x 10 x 10 cm
    (1, 300, 450),
    (2, 750, 630),
    (3, 1600, 960),
    (4, 3200, 1700),
]
problems = []
for zone, weight, expected in CASES:
    request = {"zone": zone, "weight_g": weight, "length_cm": 10, "width_cm": 10, "height_cm": 10}
    status, body = call(request)
    base = body.get("base_cents") if isinstance(body, dict) else None
    if status != 0 or base != expected:
        problems.append(f"zone {zone}, {weight} g: expected base_cents {expected}, got status {status} and {base!r}")

finish(problems, f"rate table ok: {len(CASES)} parcels")
