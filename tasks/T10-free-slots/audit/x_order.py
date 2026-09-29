"""X9 (C2): each person is busy for the time their own intervals cover together, however listed.

Hand-made requests with unsorted, overlapping, nested and repeated intervals are compared,
sorted, with answers worked out by hand, including requests where a quorum below the whole
group makes it matter that one person's overlapping intervals count as one busy person
while the same meeting for two people counts as two. Then each generated request is
rewritten several ways that keep every person's covered time the same (shuffled intervals,
shuffled people, repeats, nested and overlapping pieces added to the same person), and
every rewrite must get the same answer as the original, which must match the audit's own
model.
"""

import json
import random

from _cmd import call, finish
from _model import all_of, describe, expected, random_busy, random_quorum, random_workday, slots_of

W = [540, 1020]
HAND = [
    # Out of order within one person.
    ({"workday": W, "min_length": 30, "busy": [[[900, 960], [600, 660], [750, 780]]]},
     [[540, 600], [660, 750], [780, 900], [960, 1020]]),
    # Nested: the inner meeting ends earlier and comes after the outer one.
    ({"workday": W, "min_length": 1, "busy": [[[600, 800], [650, 700]]]}, [[540, 600], [800, 1020]]),
    ({"workday": W, "min_length": 1, "busy": [[[650, 700], [600, 800]]]}, [[540, 600], [800, 1020]]),
    ({"workday": W, "min_length": 1, "busy": [[[600, 800]], [[650, 700]]]}, [[540, 600], [800, 1020]]),
    ({"workday": W, "min_length": 1, "busy": [[[600, 800], [610, 620], [700, 790], [799, 800]]]}, [[540, 600], [800, 1020]]),
    # Nested, then a later meeting that starts inside the outer one and ends after it.
    ({"workday": W, "min_length": 1, "busy": [[[600, 800], [650, 700], [790, 850]]]}, [[540, 600], [850, 1020]]),
    # Repeated meetings, within and across people.
    ({"workday": W, "min_length": 1, "busy": [[[700, 760], [700, 760], [700, 760]]]}, [[540, 700], [760, 1020]]),
    ({"workday": W, "min_length": 1, "busy": [[[700, 760]], [[700, 760]], [[700, 760]]]}, [[540, 700], [760, 1020]]),
    # A chain of overlaps, listed backwards.
    ({"workday": W, "min_length": 1, "busy": [[[740, 800], [690, 750], [640, 700], [600, 650]]]}, [[540, 600], [800, 1020]]),
    # Same start, different ends.
    ({"workday": W, "min_length": 1, "busy": [[[600, 700], [600, 640]], [[600, 660]]]}, [[540, 600], [700, 1020]]),
    # Same end, different starts.
    ({"workday": W, "min_length": 1, "busy": [[[650, 700]], [[600, 700], [680, 700]]]}, [[540, 600], [700, 1020]]),
    # A quorum below the whole group: one person's overlapping, nested or repeated intervals
    # make one busy person, never several.
    ({"workday": W, "min_length": 1, "quorum": 1, "busy": [[[600, 720], [660, 780]], []]}, [[540, 1020]]),
    ({"workday": W, "min_length": 1, "quorum": 2, "busy": [[[700, 760], [700, 760], [700, 760]], [], []]}, [[540, 1020]]),
    ({"workday": W, "min_length": 1, "quorum": 3, "busy": [[[600, 900], [620, 640], [700, 800], [750, 760]], [[750, 800]], [], []]},
     [[540, 750], [800, 1020]]),
    ({"workday": W, "min_length": 1, "quorum": 2, "busy": [[[640, 700], [600, 650], [690, 750]], [[800, 820]], [[745, 810]]]},
     [[540, 745], [750, 800], [810, 1020]]),
    # ...while the same meeting in two people's lists makes two busy people.
    ({"workday": W, "min_length": 1, "quorum": 2, "busy": [[[700, 760]], [[700, 760]], []]}, [[540, 700], [760, 1020]]),
    ({"workday": W, "min_length": 1, "quorum": 1, "busy": [[[700, 760]], [[730, 790]]]}, [[540, 730], [760, 1020]]),
]
HAND = [(all_of(request), want) for request, want in HAND]

problems = []
calls = 0


def ask(request):
    global calls
    calls += 1
    status, body = call(request)
    return status, body, slots_of(status, body)


for request, want in HAND:
    status, body, got = ask(request)
    if got is None:
        problems.append(f"{describe(request)}: no usable answer (status {status}, {str(body)[:60]})")
    elif sorted(got) != want:
        problems.append(f"{describe(request)}: expected {want}, got {got[:5]}")


def rewrites(rng, busy):
    """Ways to list the same busy time of every person differently."""
    flat = [(who, list(i)) for who, person in enumerate(busy) for i in person]
    out = []
    # Every person's intervals shuffled, and the people shuffled.
    people = [rng.sample(person, len(person)) for person in busy]
    rng.shuffle(people)
    out.append(("shuffled", people))
    # Everything reversed.
    out.append(("reversed", [list(reversed(p)) for p in reversed(busy)]))
    if flat:
        # Repeats and nested pieces of a person's intervals, added anywhere in that person's list.
        extra = [list(p) for p in busy]
        for who, (s, e) in rng.sample(flat, min(len(flat), 4)):
            a = rng.randrange(s, e)
            piece = [a, rng.randint(a + 1, e)]
            for item in ([s, e], piece):
                extra[who].insert(rng.randrange(len(extra[who]) + 1), item)
        out.append(("repeats and nested pieces", extra))
        # Each interval replaced by two overlapping pieces that cover it together.
        split = []
        for person in busy:
            mine = []
            for s, e in person:
                if e - s >= 3:
                    cut = rng.randint(s + 1, e - 2)
                    mine += [[cut, e], [s, cut + 1]]
                else:
                    mine.append([s, e])
            split.append(mine)
        out.append(("overlapping pieces", split))
    return out


rng = random.Random(3_14159)
for _ in range(28):
    workday = random_workday(rng)
    busy = random_busy(rng, workday, people=rng.randint(1, 5), spill=40, longest=120)
    request = {"workday": workday, "min_length": rng.choice([1, 5, 20, 45]), "quorum": random_quorum(rng, busy), "busy": busy}
    status, body, base = ask(request)
    want = expected(request)
    if base is None or sorted(base) != want:
        problems.append(f"{describe(request)}: expected {want[:4]}, got {str(body)[:80]}")
        continue
    for how, other in rewrites(rng, busy):
        variant = dict(request, busy=other)
        status, body, got = ask(variant)
        if got != base:
            problems.append(f"{how}: {describe(variant, 120)} got {str(body)[:60]}, the original listing got {json.dumps(base)[:60]}")

finish(problems, f"listing-order ok: {calls} requests")
