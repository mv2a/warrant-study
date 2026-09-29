"""Shared helpers for the hidden checks: a minute-by-minute model of the intent and request builders."""

from _cmd import call

DAY = 1440


def everyone(request):
    """A request without a quorum means everyone listed must be free: fill in quorum = number of people."""
    if "quorum" in request:
        return request
    return {**request, "quorum": len(request["busy"])}


def expected_slots(request):
    """Count the busy people at every minute, then read off the free runs inside the working hours (G1, G2, C1, C2, C3)."""
    request = everyone(request)
    day_start, day_end = request["workday"]
    busy_people = [0] * DAY
    for person in request["busy"]:
        minutes = set()
        for start, end in person:
            minutes.update(range(start, end))  # an interval does not include its end minute
        for minute in minutes:  # one person counts once, however many of their intervals cover a minute
            busy_people[minute] += 1
    allowed = len(request["busy"]) - request["quorum"]
    free = [busy_people[m] <= allowed for m in range(DAY)]
    slots, minute = [], day_start
    while minute < day_end:
        if not free[minute]:
            minute += 1
            continue
        end = minute
        while end < day_end and free[end]:
            end += 1
        if end - minute >= request["min_length"]:
            slots.append([minute, end])
        minute = end
    return slots


def slots_of(request):
    """Run the command. Returns (status, slots or None)."""
    status, body = call(everyone(request))
    if status == 0 and isinstance(body, dict) and "slots" in body:
        return status, body["slots"]
    return status, None


def compare(problems, label, request, expected=None):
    """Run one request and record a problem when the answer differs from the expected slots."""
    if expected is None:
        expected = expected_slots(request)
    status, slots = slots_of(request)
    if status != 0 or slots != expected:
        problems.append(f"{label}: expected {expected}, got {slots!r} (status {status})")
        return False
    return True


def layout(day_start, pieces, people=1):
    """Build a request from alternating ('free', n) and ('busy', n) pieces laid end to end from day_start.

    Busy pieces are handed out to the people in turn. Returns (workday, busy, free stretches)."""
    busy = [[] for _ in range(people)]
    free, clock, turn = [], day_start, 0
    for kind, length in pieces:
        if kind == "busy":
            busy[turn % people].append([clock, clock + length])
            turn += 1
        else:
            free.append([clock, clock + length])
        clock += length
    return [day_start, clock], busy, free


def random_request(rng, people=None, min_length=None, nested=False, touching=0.25, quorum="any"):
    """A random valid request. Meetings may overlap, touch and run past the working hours.

    quorum="any" picks everyone about a third of the time and otherwise any number from 1 to everyone."""
    day_start = rng.choice([0, 360, 480, 540, rng.randrange(0, 1200)])
    day_end = rng.choice([DAY, min(DAY, day_start + rng.randrange(60, 721)), rng.randrange(day_start + 1, DAY + 1)])
    count = people if people is not None else rng.randint(1, 6)
    busy = []
    for _ in range(count):
        meetings, clock = [], rng.randrange(max(0, day_start - 90), min(DAY - 1, day_end + 30))
        for _ in range(rng.randint(0, 6)):
            if not (meetings and rng.random() < touching):
                clock = rng.randrange(max(0, day_start - 90), min(DAY - 1, day_end + 30))
            length = rng.choice([5, 10, 15, 30, 45, 60, 90, rng.randint(1, 240)])
            end = min(DAY, clock + length)
            if clock < end:
                meetings.append([clock, end])
                if nested and end - clock >= 3 and rng.random() < 0.5:
                    inner = rng.randrange(clock + 1, end - 1)
                    meetings.append([inner, rng.randrange(inner + 1, end)])
            clock = end
        rng.shuffle(meetings)
        busy.append(meetings)
    if min_length is None:
        min_length = rng.choice([1, 5, 15, 25, 30, 45, 60, 90, rng.randint(1, 180)])
    if quorum == "any":
        quorum = count if rng.random() < 0.35 else rng.randint(1, count)
    elif quorum is None:
        quorum = count
    return {"workday": [day_start, day_end], "min_length": min_length, "quorum": quorum, "busy": busy}
