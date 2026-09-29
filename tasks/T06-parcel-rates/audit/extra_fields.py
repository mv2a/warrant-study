"""X02 (C1): other fields in the request are ignored, whatever their name, type or value, including
names that look like the answer's fields or like the request fields in another case. Each parcel
with extra fields must get exactly the answer (status and output) that the same command gives the
parcel without them; what that answer should be is left to the other promises."""

from _audit import finish, parcel, parse, run_many

BASES = (
    parcel(3, 2750, 24, 18, 12),     # weight-billed, no surcharge
    parcel(2, 900, 105, 20, 15),     # dimension-billed, oversize
    parcel(4, 12345, 40, 30, 20),    # over 10 kg
    parcel(1, 30001, 10, 10, 10),    # refused for weight: extra fields must not rescue it
)
EXTRAS = (
    {"service": "express", "insured_value_cents": 250000},
    {"billable_g": 1, "base_cents": 0, "surcharge_cents": 0, "total_cents": 0},
    {"weight_kg": -3, "notes": None, "fragile": True},
    {"dimensions": {"length_cm": 400, "width_cm": 400, "height_cm": 400}, "tags": ["glass", 1, None]},
    {"Zone": 9, "WEIGHT_G": 0, "zone ": "x"},
    {"": "", "surcharge": 1500, "oversize": False, "discount_pct": 0.5},
)

requests, pairs = list(BASES), []
for i, base in enumerate(BASES):
    for extra in EXTRAS:
        request = {**extra, **base} if len(extra) % 2 else {**base, **extra}
        pairs.append((i, len(requests), f"{base} with extra {sorted(extra)}"))
        requests.append(request)

results = run_many(requests)
problems = []
for plain, extended, label in pairs:
    (s0, out0, _), (s1, out1, _) = results[plain], results[extended]
    same = s0 == s1 and (parse(out0) == parse(out1) if parse(out0) is not None else out0 == out1)
    if not same:
        problems.append(f"{label}: expected the answer without the extra fields (status {s0}, {out0[:80]!r}), "
                        f"got status {s1} and {out1[:80]!r}")

finish(problems, f"extra fields ignored: {len(requests)} requests")
