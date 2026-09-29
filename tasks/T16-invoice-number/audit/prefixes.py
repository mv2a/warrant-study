"""X3 (G1): every number a branch gets starts with that branch's own prefix and a hyphen
(lisbon LIS, porto OPO, faro FAO, braga BRG), whether it starts, continues or restarts."""

from _x import PREFIX, encode, finish, invoke_all, parse, show

cases = []
for branch, prefix in PREFIX.items():
    for year in (2000, 2039, 5170, 9999):
        cases.append((branch, {"branch": branch, "year": year, "previous": None}))
    cases.append((branch, {"branch": branch, "year": 2062, "previous": f"{prefix}-2062-00808"}))
    cases.append((branch, {"branch": branch, "year": 4410, "previous": f"{prefix}-4410-31415"}))
    cases.append((branch, {"branch": branch, "year": 2063, "previous": f"{prefix}-2019-05500"}))
    cases.append((branch, {"branch": branch, "year": 9999, "previous": f"{prefix}-2000-99999"}))

problems = []
results = invoke_all([encode(r) for _, r in cases])
for (branch, request), (status, out) in zip(cases, results):
    body = parse(out)
    number = body.get("number") if body else None
    want = PREFIX[branch] + "-"
    if status != 0:
        problems.append(f"{show(request)}: status {status}, expected 0")
    elif not isinstance(number, str) or not number.startswith(want):
        problems.append(f"{show(request)}: number {show(number)} should start with {want}")

finish(problems, f"prefixes ok: {len(cases)} requests over 4 branches")
