"""The audit's own model of intent.md, written from the intent alone.

It works minute by minute, straight from G1, C1 and C2: a person is busy at minute m when
one of their own intervals [s, e] has s <= m < e (counted once, however many do), and
minute m of the working hours is free when at least quorum of the people are not busy at
it. A free stretch is a maximal run of free minutes (the definition above the goals), and
a slot is a free stretch that lasts at least min_length minutes (G2).
"""

DAY = 1440


def all_of(request):
    """Hand-made requests written without a quorum ask for everyone listed (quorum = number of people)."""
    if "quorum" in request:
        return request
    return dict(request, quorum=len(request["busy"]))


def free_stretches(workday, busy, quorum=None):
    """Every maximal run of minutes inside the working hours when at least quorum people are free."""
    if quorum is None:
        quorum = len(busy)
    start, end = workday
    free_people = [len(busy)] * DAY
    for person in busy:
        taken = set()
        for s, e in person:
            taken.update(range(s, e))
        for minute in taken:
            free_people[minute] -= 1
    blocked = [free_people[minute] < quorum for minute in range(DAY)]
    runs, run_start = [], None
    for minute in range(start, end):
        if blocked[minute]:
            if run_start is not None:
                runs.append([run_start, minute])
                run_start = None
        elif run_start is None:
            run_start = minute
    if run_start is not None:
        runs.append([run_start, end])
    return runs


def expected(request):
    """The slots the intent asks for, in time order."""
    need = request["min_length"]
    stretches = free_stretches(request["workday"], request["busy"], request["quorum"])
    return [r for r in stretches if r[1] - r[0] >= need]


def minutes(slots):
    """The set of minutes a list of [start, end] slots covers."""
    covered = set()
    for s, e in slots:
        covered.update(range(s, e))
    return covered


def slots_of(status, body):
    """The slots list from a successful answer, or None when the answer is unusable."""
    if status != 0 or not isinstance(body, dict):
        return None
    slots = body.get("slots")
    if not isinstance(slots, list):
        return None
    for slot in slots:
        if not (isinstance(slot, list) and len(slot) == 2 and all(isinstance(t, (int, float)) and not isinstance(t, bool) for t in slot)):
            return None
        if slot[0] != int(slot[0]) or slot[1] != int(slot[1]):
            return None
    return [[int(slot[0]), int(slot[1])] for slot in slots]


def describe(request, limit=160):
    text = str(request)
    return text if len(text) <= limit else text[: limit - 3] + "..."


# ---- generators (each caller passes its own seeded random.Random) ----

def random_workday(rng):
    roll = rng.random()
    if roll < 0.12:
        return [0, DAY]
    if roll < 0.2:
        start = rng.randrange(0, DAY - 1)
        return [start, rng.randint(start + 1, min(DAY, start + 3))]
    start = rng.randrange(0, DAY - 30)
    span = rng.choice([30, 90, 240, 480, 600, 900, DAY])
    return [start, rng.randint(start + 1, min(DAY, start + span))]


def random_interval(rng, low, high, longest):
    """A valid busy interval [s, e] with low <= s < e <= high."""
    s = rng.randrange(low, high)
    return [s, min(high, s + rng.randint(1, longest))]


def random_busy(rng, workday, people=None, per_person=None, grid=1, spill=120, longest=180):
    """Busy lists for a few people, mostly near the working hours, sometimes on a grid."""
    low = max(0, workday[0] - spill)
    high = min(DAY, workday[1] + spill)
    count = people if people is not None else rng.randint(1, 6)
    busy = []
    for _ in range(count):
        n = per_person if per_person is not None else rng.choice([0, 1, 2, 3, 4, 6, 9])
        person = []
        for _ in range(n):
            s, e = random_interval(rng, low, high, longest)
            if grid > 1:
                s = min(DAY - grid, s - s % grid)
                e = max(s + grid, min(DAY, e - e % grid))
            person.append([s, e])
        busy.append(person)
    return busy


def random_quorum(rng, busy):
    """Everyone about a quarter of the time, one person sometimes, otherwise anything in between."""
    roll = rng.random()
    if roll < 0.25:
        return len(busy)
    if roll < 0.35:
        return 1
    return rng.randint(1, len(busy))


def random_min_length(rng, workday, busy, quorum=None):
    stretches = free_stretches(workday, busy, quorum)
    roll = rng.random()
    if stretches and roll < 0.45:
        length = rng.choice(stretches)
        length = length[1] - length[0]
        return max(1, length + rng.choice([-1, 0, 0, 1]))
    if roll < 0.6:
        return 1
    if roll < 0.9:
        return rng.randint(1, 120)
    return rng.randint(1, workday[1] - workday[0] + 2)


def random_request(rng, **busy_options):
    workday = random_workday(rng)
    busy = random_busy(rng, workday, **busy_options)
    quorum = random_quorum(rng, busy)
    return {"workday": workday, "min_length": random_min_length(rng, workday, busy, quorum), "quorum": quorum, "busy": busy}
