"""Shared helpers for the audit suite X, written from intent.md alone.

- a small model of the promises (`decide`, `expected`), used as the oracle;
- readers that turn a response into per-group answers;
- a request generator driven by a seeded random.Random (never the global one);
- `call_all`, which runs many requests in parallel through _cmd.call.
"""

import concurrent.futures
import json
import random
import sys

from _cmd import call

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"
WORKERS = 12


# ---------------------------------------------------------------- seats

def name(row, number):
    return f"{LETTERS[row]}{number}"


def parse(seat):
    """A seat name written exactly as responses write it -> (row index, number); else None."""
    if not isinstance(seat, str) or len(seat) < 2 or seat[0] not in LETTERS:
        return None
    digits = seat[1:]
    if any(c not in DIGITS for c in digits) or digits[0] == "0":
        return None
    return LETTERS.index(seat[0]), int(digits)


def seats_of(rows):
    """Every seat of the theatre, in seating order."""
    return [(r, n) for r, length in enumerate(rows) for n in range(1, length + 1)]


def exists(rows, seat):
    return seat is not None and seat[0] < len(rows) and 1 <= seat[1] <= rows[seat[0]]


def together(parsed):
    """True when the seats are in one row with consecutive numbers."""
    if not parsed or None in parsed:
        return False
    parsed = sorted(parsed)
    return all(s[0] == parsed[0][0] for s in parsed) and all(
        b[1] == a[1] + 1 for a, b in zip(parsed, parsed[1:])
    )


# ---------------------------------------------------------------- model

def decide(rows, taken, size, may_split):
    """One group's outcome from the seats already taken (blocked or sold).

    Returns ("together", seats), ("split", seats) or ("refused", reason)."""
    for r, length in enumerate(rows):
        for start in range(1, length - size + 2):
            block = [(r, n) for n in range(start, start + size)]
            if taken.isdisjoint(block):
                return "together", block
    free = [s for s in seats_of(rows) if s not in taken]
    if len(free) < size:
        return "refused", "not_enough_seats"
    if may_split:
        return "split", free[:size]
    return "refused", "not_together"


def expected(request):
    """The full response the intent prescribes for a valid request."""
    rows = request["rows"]
    taken = {parse(s) for s in request.get("blocked", [])}
    seated, refused = [], []
    for group in request["groups"]:
        kind, value = decide(rows, taken, group["size"], group.get("may_split") is True)
        if kind == "refused":
            refused.append({"id": group["id"], "reason": value})
        else:
            taken.update(value)
            seated.append({"id": group["id"], "seats": [name(*s) for s in value]})
    return {"seated": seated, "refused": refused, "free": sum(rows) - len(taken)}


# ---------------------------------------------------------------- reading responses

def answers(body):
    """Response -> {id: [answer, ...]} where an answer is ("seated", [names]) or
    ("refused", reason). Lenient about extra fields and seat order; None when the
    response cannot be read as seated and refused lists at all."""
    if not isinstance(body, dict):
        return None
    seated, refused = body.get("seated"), body.get("refused")
    if not isinstance(seated, list) or not isinstance(refused, list):
        return None
    out = {}
    for entry in seated:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not isinstance(entry.get("seats"), list):
            return None
        out.setdefault(entry["id"], []).append(("seated", entry["seats"]))
    for entry in refused:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            return None
        out.setdefault(entry["id"], []).append(("refused", entry.get("reason")))
    return out


def normal(answer):
    """Comparable form of one answer: seats as a sorted list of parsed seats."""
    kind, value = answer
    if kind == "seated":
        parsed = [parse(s) for s in value]
        return ("seated", None if None in parsed else sorted(parsed))
    return ("refused", value)


def show(answer):
    kind, value = answer
    if kind == "seated":
        return "seats " + ",".join(str(s) for s in value)
    return f"refused {value!r}"


def compare(request, body, want):
    """Per-group comparison of a response with the expected response `want`
    (lenient about seat order inside a group, extra fields and `free`)."""
    got = answers(body)
    if got is None:
        return [f"unreadable response {str(body)[:120]}"]
    exp = answers(want)
    problems = []
    for group in request["groups"]:
        gid = group["id"]
        (w,) = exp[gid]
        g = got.get(gid, [])
        if len(g) != 1:
            problems.append(f"{gid}: expected {show(w)}, got {len(g)} answers")
        elif normal(g[0]) != normal(w):
            problems.append(f"{gid}: expected {show(w)}, got {show(g[0])}")
    return problems


PROMISE = {"together": "G2", "split": "G3", "refused": "G4"}


def review(request, status, body):
    """Replay the command's own answers in booking order and compare each group's answer
    with the model's decision from the same free seats.

    Returns a list of (promise, message); promise "*" means the response could not be
    judged at all (bad exit status or unreadable), which fails every mode."""
    if status != 0:
        return [("*", f"exit status {status} for a valid request")]
    got = answers(body)
    if got is None:
        return [("*", f"unreadable response {str(body)[:120]}")]
    rows = request["rows"]
    taken = {parse(s) for s in request.get("blocked", [])}
    problems = []
    for group in request["groups"]:
        gid, size = group["id"], group["size"]
        may = group.get("may_split") is True
        kind, value = decide(rows, taken, size, may)
        want = ("refused", value) if kind == "refused" else ("seated", [name(*s) for s in value])
        tag = f"{gid} (size {size}{', may split' if may else ''})"
        entries = got.get(gid, [])
        if len(entries) != 1:
            problems.append((PROMISE[kind], f"{tag}: expected {show(want)}, got {len(entries)} answers"))
            continue
        have = entries[0]
        if normal(have) != normal(want):
            problems.append((PROMISE[kind], f"{tag}: expected {show(want)}, got {show(have)}"))
        if have[0] == "seated":
            parsed = [parse(s) for s in have[1]]
            if not may and not together(parsed):
                problems.append(("G3", f"{tag}: may not split but got {show(have)}"))
            elif kind == "together" and not together(parsed):
                problems.append(("G3", f"{tag}: split although it can sit together, got {show(have)}"))
            taken.update(p for p in parsed if p is not None)
    return problems


# ---------------------------------------------------------------- generation

NAMES = [
    "Abara", "Brisco", "Cyrus", "Delacroix", "Eze", "Falk", "Grieve", "Hollis", "Ines",
    "Jaramillo", "Kowal", "Lustig", "Mwangi", "Nordin", "Oyelaran", "Pruitt", "Quade",
    "Rasmussen", "Stoica", "Tamura", "Umberg", "Varga", "Whitlock", "Xiong", "Yilmaz", "Zeller",
]


def generate(rng):
    """One valid request. `rng` is a seeded random.Random."""
    shape = rng.random()
    if shape < 0.6:
        rows = [rng.randint(1, 9) for _ in range(rng.randint(1, 4))]
        count = rng.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12])
    elif shape < 0.9:
        rows = [rng.randint(3, 16) for _ in range(rng.randint(2, 9))]
        count = rng.randint(3, 24)
    else:
        rows = [rng.randint(1, 50) for _ in range(rng.randint(8, 26))]
        count = rng.randint(10, 80)
    density = rng.choice([0.0, 0.0, 0.08, 0.15, 0.25, 0.4, 0.6])
    blocked = [name(*s) for s in seats_of(rows) if rng.random() < density]
    rng.shuffle(blocked)
    widest = max(rows)
    groups = []
    for i in range(count):
        roll = rng.random()
        if roll < 0.07:
            size = rng.randint(widest, widest + 4)
        elif roll < 0.1:
            size = rng.randint(1, max(1, sum(rows)))
        else:
            size = rng.randint(1, max(1, min(widest + 1, 8)))
        group = {"id": f"{rng.choice(NAMES)}-{i}", "size": size}
        roll = rng.random()
        if roll < 0.45:
            group["may_split"] = True
        elif roll < 0.6:
            group["may_split"] = False
        if rng.random() < 0.05:
            group["note"] = rng.choice(["aisle please", None, 3, ["x"]])
        groups.append(group)
    request = {"rows": rows, "groups": groups}
    if blocked or rng.random() < 0.4:
        request["blocked"] = blocked
    if rng.random() < 0.05:
        request["show"] = {"title": "matinee", "night": rng.randint(1, 9)}
    return request


def generated(seed, count):
    rng = random.Random(seed)
    return [generate(rng) for _ in range(count)]


# ---------------------------------------------------------------- running

def call_all(requests):
    """Run every request (a dict, or a str sent as raw text) in parallel; results in order."""
    def one(request):
        return call(raw=request) if isinstance(request, str) else call(request)

    with concurrent.futures.ThreadPoolExecutor(WORKERS) as pool:
        return list(pool.map(one, requests))


def raw_all(texts, timeout=10):
    """Send each text on stdin; results are (exit status, stdout exactly as written)."""
    import os
    import subprocess

    import _cmd

    if not os.access(_cmd.PATH, os.X_OK):
        sys.exit(f"the workspace has no executable named {_cmd.COMMAND}")

    def one(text):
        try:
            done = subprocess.run([_cmd.PATH], input=text, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return 124, ""
        return done.returncode, done.stdout

    with concurrent.futures.ThreadPoolExecutor(WORKERS) as pool:
        return list(pool.map(one, texts))


def brief(request, limit=160):
    text = json.dumps(request, ensure_ascii=False)
    return text if len(text) <= limit else text[: limit - 3] + "..."
