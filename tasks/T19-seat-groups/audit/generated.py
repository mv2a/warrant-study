"""Generated requests with fixed seeds, judged per promise. Usage: generated.py MODE

G2, G3, G4: every group's answer is compared with the model's decision from the same free
            seats (the command's own earlier answers are replayed), and a difference is
            charged to the promise that governs the model's decision: sitting together (G2),
            splitting (G3) or refusing (G4). G3 also fails when a group without
            "may_split": true gets seats that are not together.
G1:         booking order, without the model: the answers for the first k groups are the
            same whether or not later groups are in the request, and removing a refused
            group changes nobody else's answer.
C2:         no overselling, without the model: every sold seat exists, is not blocked and is
            sold once, each seated group has exactly `size` seats, and `free` counts the
            seats neither blocked nor sold.
"""

import random
import sys

from _audit import answers, brief, call_all, generated, normal, parse, review, seats_of, show
from _cmd import finish

MODE = sys.argv[1]
SEEDS = {"G2": 60613, "G3": 71129, "G4": 83357, "G1": 94421, "C2": 50287}
COUNTS = {"G2": 150, "G3": 150, "G4": 150, "G1": 80, "C2": 150}
requests = generated(SEEDS[MODE], COUNTS[MODE])
problems = []


def judge_model():
    for request, (status, body) in zip(requests, call_all(requests)):
        for promise, message in review(request, status, body):
            if promise in (MODE, "*"):
                problems.append(f"{message} | request {brief(request)}")


def same_answers(request, got_small, got_full, ids, what):
    for gid in ids:
        a, b = got_small.get(gid, []), got_full.get(gid, [])
        if len(a) != 1 or len(b) != 1 or normal(a[0]) != normal(b[0]):
            sa = show(a[0]) if len(a) == 1 else f"{len(a)} answers"
            sb = show(b[0]) if len(b) == 1 else f"{len(b)} answers"
            problems.append(f"{gid}: {sa} {what}, but {sb} in the full request | {brief(request)}")
            return


def judge_order():
    rng = random.Random(SEEDS["G1"] + 1)
    cases = [r for r in requests if len(r["groups"]) >= 2]
    prefixes = []
    for request in cases:
        k = rng.randint(1, len(request["groups"]) - 1)
        prefixes.append({**request, "groups": request["groups"][:k]})
    results = call_all(cases + prefixes)
    full, short = results[: len(cases)], results[len(cases):]
    removals, bases = [], []
    for request, prefix, (status, body), (pstatus, pbody) in zip(cases, prefixes, full, short):
        got = answers(body) if status == 0 else None
        if got is None:
            problems.append(f"status {status}, unreadable or refused response for a valid request | {brief(request)}")
            continue
        pgot = answers(pbody) if pstatus == 0 else None
        if pgot is None:
            problems.append(f"status {pstatus} or unreadable response for a valid request | {brief(prefix)}")
            continue
        same_answers(request, pgot, got, [g["id"] for g in prefix["groups"]], f"with only the first {len(prefix['groups'])} groups")
        refused = [g for g in request["groups"] if [a[0] for a in got.get(g["id"], [])] == ["refused"]]
        if refused:
            drop = rng.choice(refused)
            removals.append({**request, "groups": [g for g in request["groups"] if g is not drop]})
            bases.append((request, got, drop["id"]))
    for (request, got, dropped), (status, body) in zip(bases, call_all(removals)):
        rgot = answers(body) if status == 0 else None
        if rgot is None:
            problems.append(f"status {status} or unreadable response without refused group {dropped} | {brief(request)}")
            continue
        others = [g["id"] for g in request["groups"] if g["id"] != dropped]
        same_answers(request, rgot, got, others, f"without the refused group {dropped}")


def judge_oversell():
    for request, (status, body) in zip(requests, call_all(requests)):
        got = answers(body) if status == 0 else None
        if got is None:
            problems.append(f"status {status} or unreadable response for a valid request | {brief(request)}")
            continue
        rows = request["rows"]
        exist = set(seats_of(rows))
        blocked = {parse(s) for s in request.get("blocked", [])}
        sizes = {g["id"]: g["size"] for g in request["groups"]}
        sold, bad, seen = set(), [], set()
        for entry in body["seated"]:
            gid, names = entry["id"], entry["seats"]
            if gid in seen:
                bad.append(f"{gid} is seated more than once")
            seen.add(gid)
            if gid not in sizes:
                bad.append(f"seats sold to unknown group {gid!r}")
            elif len(names) != sizes[gid]:
                bad.append(f"{gid} has size {sizes[gid]} but got {len(names)} seats")
            for seat_name in names:
                seat = parse(seat_name)
                if seat not in exist:
                    bad.append(f"{gid} got {seat_name!r}, which is not a seat of this theatre")
                elif seat in blocked:
                    bad.append(f"{gid} got blocked seat {seat_name}")
                elif seat in sold:
                    bad.append(f"{seat_name} sold twice")
                else:
                    sold.add(seat)
        free = len(exist) - len(blocked) - len(sold)
        if type(body.get("free")) is not int or body["free"] != free:
            bad.append(f"free is {body.get('free')!r}, but {free} seats are neither blocked nor sold")
        if bad:
            problems.append("; ".join(bad[:3]) + f" | {brief(request)}")


{"G2": judge_model, "G3": judge_model, "G4": judge_model, "G1": judge_order, "C2": judge_oversell}[MODE]()
finish(problems, f"generated {MODE} ok: {len(requests)} requests, seed {SEEDS[MODE]}")
