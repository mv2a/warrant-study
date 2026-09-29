"""Shared helpers for the audit suite (X).

The fee rules below are written from intent.md alone. They are the expected values the
audit checks compare the command against. Nothing here is taken from the reference or
from any other suite.
"""

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from _cmd import COMMAND, PATH, call

WEEK = 10080          # minutes in a week
DAY = 1440            # minutes in a 24-hour period
NIGHT = 120           # 02:00 is minute 120 of every day
HOUR_CENTS = 250      # G1: $2.50 per started hour
DAY_CAP = 1600        # G3: at most $16.00 per 24-hour period
OVERNIGHT = 600       # G4: $6.00 per 02:00 inside the stay
LOST = 2500           # G5: $25.00 for a lost ticket
FREE = 15             # G2: a stay of 15 minutes or less is free
FIELDS = ("minutes", "time_cents", "overnight_cents", "lost_ticket_cents", "total_cents")
WORKERS = 6


def stay_minutes(entry, exit):
    """C1/C2: the length of the stay; an exit before the entry is in the following week."""
    return exit - entry if exit >= entry else WEEK - entry + exit


def time_cents(minutes):
    """G1 to G3: started hours at $2.50, capped at $16.00 per 24 hours counted from entry."""
    if minutes <= FREE:
        return 0
    full, rest = divmod(minutes, DAY)
    started = -(-rest // 60)
    return full * DAY_CAP + min(started * HOUR_CENTS, DAY_CAP)


def nights(entry, minutes):
    """G4: the 02:00 moments t with entry <= t < entry + minutes (none for a free stay)."""
    if minutes <= FREE:
        return 0
    end = entry + minutes  # past WEEK for a stay that runs into the following week (C2)
    return sum(1 for t in range(NIGHT, end, DAY) if t >= entry)


def expected(entry, exit, lost=False):
    minutes = stay_minutes(entry, exit)
    t = time_cents(minutes)
    o = nights(entry, minutes) * OVERNIGHT
    l = LOST if lost else 0
    return {"minutes": minutes, "time_cents": t, "overnight_cents": o,
            "lost_ticket_cents": l, "total_cents": t + o + l}


def request(entry, exit, lost=False):
    return {"entry": entry, "exit": exit, "lost_ticket": lost}


def _require_command():
    if not os.access(PATH, os.X_OK):
        sys.exit(f"the workspace has no executable named {COMMAND}")


def run_many(requests):
    """Call the command once per request dict, in parallel. Returns [(status, body)] in order."""
    _require_command()
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        return list(pool.map(call, requests))


def run_many_raw(texts):
    """Send each text as-is on stdin. Returns [(status, stdout, stderr)] in order."""
    _require_command()

    def one(text):
        try:
            done = subprocess.run([PATH], input=text, capture_output=True, text=True, timeout=10)
        except subprocess.TimeoutExpired:
            return 124, "", "timed out"
        return done.returncode, done.stdout, done.stderr

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        return list(pool.map(one, texts))


def number(value):
    """True for a JSON number. Whether it is written as an integer is C1's business, not the money checks'."""
    return type(value) in (int, float)


def field(result, name):
    """The numeric value of one output field of a successful answer, or None.

    A field missing from a successful answer counts as 0 here: printing every field even
    when zero is C1's contract, checked by C1, and the money checks judge amounts only.
    """
    status, body = result
    if status != 0 or not isinstance(body, dict):
        return None
    value = body.get(name, 0)
    return value if number(value) else None


def show(req):
    return f"entry {req['entry']} exit {req['exit']} lost {str(req['lost_ticket']).lower()}"


def got(result, name=None):
    status, body = result
    if name is not None and status == 0 and isinstance(body, dict):
        return f"{name} {body.get(name)!r}"
    return f"status {status} and {body!r}"
