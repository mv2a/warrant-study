"""Run hand-written cases whose expected answers were worked out by hand from intent.md.

A case is (label, request, expected response). The comparison is per group and lenient
about seat order inside a group, extra fields and `free` (those belong to C1 and C2).

With `promise` set (G2, G3 or G4), each group is instead judged from the seats left by the
command's own earlier answers and only differences governed by that promise are reported,
so that a fault in one placement rule is not charged to the others. For a correct command
both ways give exactly the hand-worked responses."""

from _audit import brief, call_all, compare, expected, review


def run_cases(cases, promise=None):
    for label, request, want in cases:  # the hand-worked answers must agree with the model
        mismatch = compare(request, expected(request), want)
        if mismatch:
            raise SystemExit(f"audit error in case {label!r}: {mismatch[0]}")
    problems = []
    results = call_all([request for _, request, _ in cases])
    for (label, request, want), (status, body) in zip(cases, results):
        if status != 0:
            problems.append(f"{label}: exit status {status}, expected 0 | {brief(request)}")
            continue
        if promise is None:
            problems.extend(f"{label}: {message}" for message in compare(request, body, want))
        else:
            problems.extend(f"{label}: {message}" for p, message in review(request, status, body) if p in (promise, "*"))
    return problems


def seated(gid, *seats):
    return {"id": gid, "seats": list(seats)}


def refused(gid, reason):
    return {"id": gid, "reason": reason}


def response(*entries):
    return {
        "seated": [e for e in entries if "seats" in e],
        "refused": [e for e in entries if "reason" in e],
    }


def group(gid, size, may_split=None):
    g = {"id": gid, "size": size}
    if may_split is not None:
        g["may_split"] = may_split
    return g


def row(letter, first, last):
    return [f"{letter}{n}" for n in range(first, last + 1)]
