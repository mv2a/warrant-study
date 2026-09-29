"""Shared helpers for the audit checks: an oracle written from intent.md, and exact runners.

The oracle below is derived only from intent.md (G1 to G4, C2). It is not the reference.
"""

import json
import os
import subprocess
import sys

from _cmd import PATH, call, finish  # noqa: F401  (re-exported for the check scripts)

RATE = {"book": 25, "dvd": 100, "reference": 150}      # G1
GRACE = {"book": 3, "dvd": 3, "reference": 0}          # G2
ITEM_CAP = {"book": 800, "dvd": 2000, "reference": 1500}  # G3
ACCOUNT_CAP = 2500                                      # G4
REASON_LIMIT = 200                                      # C1: a refusal's reason, in characters
TYPES = ("book", "dvd", "reference")

TOP = {"items", "total_cents"}
LINE = {"id", "days_late", "fine_cents"}


def days_late(due, returned):
    """C2: returned minus due, never below zero."""
    return max(0, returned - due)


def charged_days(kind, late):
    """G2: books and DVDs forgive the first 3 late days; reference items forgive none."""
    return max(0, late - GRACE[kind])


def item_fine(kind, due, returned):
    """G1 and G3: charged days times the daily rate, stopped at the item's cap."""
    late = days_late(due, returned)
    return min(charged_days(kind, late) * RATE[kind], ITEM_CAP[kind])


def expected(request):
    """The full response intent.md promises for a valid request."""
    lines = []
    for item in request["items"]:
        lines.append({
            "id": item["id"],
            "days_late": days_late(item["due_day"], item["returned_day"]),
            "fine_cents": item_fine(item["type"], item["due_day"], item["returned_day"]),
        })
    return {"items": lines, "total_cents": min(sum(l["fine_cents"] for l in lines), ACCOUNT_CAP)}


def item(ident, kind, due, returned, /, **extra):
    entry = {"id": ident, "type": kind, "due_day": due, "returned_day": returned}
    entry.update(extra)
    return entry


def run_raw(text, timeout=10):
    """Run the command on raw stdin text. Returns (status, stdout, stderr), unstripped."""
    if not os.access(PATH, os.X_OK):
        sys.exit("the workspace has no executable named fine")
    try:
        done = subprocess.run([PATH], input=text, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, "", "timed out"
    return done.returncode, done.stdout, done.stderr


def short(value, limit=110):
    text = value if isinstance(value, str) else json.dumps(value)
    return text if len(text) <= limit else text[:limit - 3] + "..."


def refusal_problem(label, text):
    """C1 and C3: a refused request exits 2, writes nothing on stdout and a short reason on stderr.

    "Short" is what C1 states: at most REASON_LIMIT characters (surrounding whitespace aside)
    and not a traceback. Returns None when the refusal is correct, else a one-line description.
    """
    status, out, err = run_raw(text)
    if status != 2:
        return f"{label}: expected refusal with status 2, got status {status} and stdout {short(out.strip())!r}"
    if out != "":
        return f"{label}: refused but wrote on standard output: {short(out)!r}"
    reason = err.strip()
    if not reason:
        return f"{label}: refused without a reason on standard error"
    if "Traceback" in err:
        return f"{label}: standard error holds a traceback, not a short reason: {short(reason)!r}"
    if len(reason) > REASON_LIMIT:
        return f"{label}: the reason on standard error has {len(reason)} characters, over {REASON_LIMIT}: {short(reason)!r}"
    return None


def refuse(problems, label, request=None, raw=None):
    text = raw if raw is not None else json.dumps(request)
    problem = refusal_problem(label, text)
    if problem:
        problems.append(problem)


def success_problem(label, request=None, raw=None, want=None):
    """Run a valid request; compare with the oracle (or `want`) exactly, with integer types.

    Returns None when correct, else a one-line description.
    """
    if want is None:
        want = expected(request)
    text = raw if raw is not None else json.dumps(request)
    status, body = call(raw=text)
    if status != 0:
        return f"{label}: expected status 0, got status {status}"
    if not isinstance(body, dict) or set(body) != TOP:
        return f"{label}: expected an object with exactly {sorted(TOP)}, got {short(body)!r}"
    if type(body["total_cents"]) is not int:
        return f"{label}: total_cents must be a JSON integer, got {body['total_cents']!r}"
    if not isinstance(body["items"], list):
        return f"{label}: items must be a list, got {short(body['items'])!r}"
    for line in body["items"]:
        if not isinstance(line, dict) or set(line) != LINE:
            return f"{label}: each entry needs exactly {sorted(LINE)}, got {short(line)!r}"
        if type(line["days_late"]) is not int or type(line["fine_cents"]) is not int:
            return f"{label}: days_late and fine_cents must be JSON integers, got {short(line)!r}"
    if body != want:
        return f"{label}: expected {short(want, 200)}, got {short(body, 200)}"
    return None


def succeed(problems, label, request=None, raw=None, want=None):
    problem = success_problem(label, request=request, raw=raw, want=want)
    if problem:
        problems.append(problem)
