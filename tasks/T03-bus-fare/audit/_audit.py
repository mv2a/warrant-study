"""Shared helpers for the audit (X) checks: an independent fare model written from
intent.md alone, a parallel caller, and the output-shape test from C3.

The model is deliberately plain so it can be read against the intent line by line.
"""

from concurrent.futures import ThreadPoolExecutor

from _cmd import call

# G1
BASE_CENTS = 270
PER_BOUNDARY_CENTS = 95
# G2
TRANSFER_MINUTES = 90
# G4
CAP_CENTS = {"adult": 1100, "child": 550, "senior": 440}

# The fare for 0..5 boundaries crossed, written out by hand from G1, G3 and C1
# (50% or 40% of the adult fare, rounded down to a multiple of 5 cents).
ADULT_TABLE = [270, 365, 460, 555, 650, 745]
CHILD_TABLE = [135, 180, 230, 275, 325, 370]   # 182.5 -> 180, 277.5 -> 275, 372.5 -> 370
SENIOR_TABLE = [105, 145, 180, 220, 260, 295]  # 108 -> 105, 146 -> 145, 184 -> 180, 222 -> 220, 298 -> 295


def trip(minute, start, end):
    return {"board_minute": minute, "from_zone": start, "to_zone": end}


def band(age):
    """G3: which fare an age pays."""
    if age < 5:
        return "free"
    if age <= 15:
        return "child"
    if age >= 65:
        return "senior"
    return "adult"


def adult_fare(start, end):
    """G1."""
    return BASE_CENTS + PER_BOUNDARY_CENTS * abs(start - end)


def rider_fare(age, start, end):
    """G3 with C1 rounding: whole cents, rounded down to a multiple of 5."""
    full = adult_fare(start, end)
    kind = band(age)
    if kind == "free":
        return 0
    if kind == "adult":
        return full
    percent = 50 if kind == "child" else 40
    return (full * percent // 100) // 5 * 5


def price(age, trips):
    """The whole day: G2 transfers, then G3/C1 concessions, then the G4 cap."""
    cap = CAP_CENTS.get(band(age))
    opened_at = None
    spent = 0
    fares = []
    for t in trips:
        minute = t["board_minute"]
        if opened_at is not None and minute - opened_at <= TRANSFER_MINUTES:
            due = 0
        else:
            opened_at = minute
            due = rider_fare(age, t["from_zone"], t["to_zone"])
        if cap is not None:
            due = min(due, cap - spent)
        spent += due
        fares.append(due)
    return fares


def expected_body(age, trips):
    fares = price(age, trips)
    return {"fares_cents": fares, "total_cents": sum(fares)}


def call_many(requests, workers=8):
    """Call the command once per request, in parallel, results in request order."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(call, requests))


def call_many_raw(texts, workers=8):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(lambda text: call(raw=text), texts))


def shape_problem(request, status, body):
    """C3: return a description of what is wrong with a success reply, or None."""
    if status != 0:
        return f"exited with status {status}, expected 0 (output {body!r})"
    if not isinstance(body, dict):
        return f"expected one JSON object on standard output, got {body!r}"
    if set(body) != {"fares_cents", "total_cents"}:
        return f"expected exactly fares_cents and total_cents, got fields {sorted(body)}"
    fares, total = body["fares_cents"], body["total_cents"]
    if not isinstance(fares, list):
        return f"fares_cents must be a list, got {fares!r}"
    if len(fares) != len(request["trips"]):
        return f"fares_cents has {len(fares)} entries for {len(request['trips'])} trips"
    if not all(type(f) is int for f in fares) or type(total) is not int:
        return f"amounts must be JSON integers, got {body!r}"
    if total != sum(fares):
        return f"total_cents {total} is not the sum of fares_cents {fares}"
    return None


def short(request, limit=150):
    text = str(request)
    return text if len(text) <= limit else text[: limit - 3] + "..."


def check_cases(cases):
    """cases: (label, request, expected fares list). Returns a list of problems."""
    replies = call_many([request for _, request, _ in cases])
    problems = []
    for (label, request, fares), (status, body) in zip(cases, replies):
        wrong = shape_problem(request, status, body)
        if wrong:
            problems.append(f"{label}: {wrong}")
            continue
        expected = {"fares_cents": list(fares), "total_cents": sum(fares)}
        if body != expected:
            problems.append(f"{label}: expected {expected['fares_cents']} (total {expected['total_cents']}), got {body['fares_cents']} (total {body['total_cents']})")
    return problems
