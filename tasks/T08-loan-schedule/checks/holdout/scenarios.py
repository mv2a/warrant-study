"""H8: the three example loans in the intent (S1, S2, S3) match the promised schedule row by row."""

from _cmd import call, finish
from _model import schedule

SCENARIOS = {
    "S1": ((1000000, 600, 12), {"payment_cents": 86067, "total_interest_cents": 32796, "rows": 12,
                                "first": (86067, 5000, 81067, 918933), "last": 86059}),
    "S2": ((100000, 0, 7), {"payment_cents": 14286, "total_interest_cents": 0, "rows": 7,
                            "first": (14286, 0, 14286, 85714), "last": 14284}),
    "S3": ((700000, 500, 24), {"payment_cents": 30710, "total_interest_cents": 37044, "rows": 24,
                               "first": (30710, 2917, 27793, 672207), "last": 30714}),
}
KEYS = ("payment_cents", "interest_cents", "principal_cents", "balance_cents")
problems = []
for name, ((principal, rate, months), stated) in SCENARIOS.items():
    wanted = schedule(principal, rate, months)
    # The model must agree with the figures the intent states before it is used as the answer key.
    rows = wanted["rows"]
    assert (wanted["payment_cents"], wanted["total_interest_cents"], len(rows), tuple(rows[0][k] for k in KEYS),
            rows[-1]["payment_cents"]) == (stated["payment_cents"], stated["total_interest_cents"], stated["rows"],
                                           stated["first"], stated["last"]), ("check setup", name)
    status, body = call({"principal_cents": principal, "annual_rate_bp": rate, "months": months})
    if status != 0 or not isinstance(body, dict):
        problems.append(f"{name}: expected a schedule, got status {status}")
        continue
    for key in ("payment_cents", "total_interest_cents"):
        if body.get(key) != wanted[key]:
            problems.append(f"{name}: expected {key} {wanted[key]}, got {body.get(key)!r}")
    got_rows = body.get("rows")
    if not isinstance(got_rows, list) or len(got_rows) != len(rows):
        problems.append(f"{name}: expected {len(rows)} rows, got {len(got_rows) if isinstance(got_rows, list) else got_rows!r}")
        continue
    for want, got in zip(rows, got_rows):
        if not isinstance(got, dict) or any(got.get(k) != want[k] for k in ("month",) + KEYS):
            problems.append(f"{name}, month {want['month']}: expected {want}, got {got!r}")
            break

finish(problems, "scenarios ok: S1, S2, S3 match row by row")
