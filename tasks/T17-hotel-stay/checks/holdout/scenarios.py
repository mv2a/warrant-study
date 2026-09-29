"""H8: the four scenarios in the intent, every field, and the exact form of the S3 refusal."""

from _cmd import call, finish

PRICED = [
    ("S1", {"check_in": "wed", "nights": 2, "rate_cents": 12000},
     {"room_cents": 24000, "discount_cents": 0, "tax_cents": 550, "total_cents": 24550}),
    ("S2", {"check_in": "thu", "nights": 3, "rate_cents": 12000},
     {"room_cents": 42000, "discount_cents": 0, "tax_cents": 825, "total_cents": 42825}),
    ("S4", {"check_in": "sun", "nights": 14, "rate_cents": 8000},
     {"room_cents": 120000, "discount_cents": 18000, "tax_cents": 2750, "total_cents": 104750}),
]
problems = []
for scenario, request, expected in PRICED:
    status, body = call(request)
    if status != 0 or body != expected:
        problems.append(f"{scenario}: expected {expected} with status 0, got {body!r} (status {status})")

status, body = call({"check_in": "sat", "nights": 2, "rate_cents": 12000})
if status != 2 or body is not None:
    problems.append(f"S3: should be refused with status 2 and nothing on standard output, got {body!r} (status {status})")

finish(problems, "scenarios ok: S1, S2, S3, S4")
