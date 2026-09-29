"""G1: groups are handled one at a time in booking order, each from the seats left by the
groups before it; a refused group takes no seats; later groups never change an earlier
group's answer.

The hand-worked cases are compared on outcomes only (seated with how many seats, or
refused), so that a fault in where a group sits inside a row (G2) or in the reason given
(G4) is not charged to G1; which seats each group gets is checked here only against the command itself:
every proper prefix of a request must give the same answers to the groups it keeps."""

from _audit import answers, brief, call_all, compare, expected, normal, show
from _cases import group as g, refused, response, row, seated
from _cmd import finish

CASES = [
    (
        "one row: the early small group is seated, the later full-row group is not",
        {"rows": [4], "groups": [g("Solo", 1), g("Full", 4)]},
        response(seated("Solo", "A1"), refused("Full", "not_enough_seats")),
    ),
    (
        "two rows: the early single goes first, the second trio finds no room",
        {"rows": [3, 3], "groups": [g("One", 1), g("Three", 3), g("Other", 3, True)]},
        response(seated("One", "A1"), seated("Three", *row("B", 1, 3)), refused("Other", "not_enough_seats")),
    ),
    (
        "a small early group before a large later one",
        {"rows": [4, 4], "groups": [g("Small", 1), g("Big", 4)]},
        response(seated("Small", "A1"), seated("Big", *row("B", 1, 4))),
    ),
    (
        "the order of the list, not the size of the group",
        {"rows": [4, 4], "groups": [g("Duo", 2), g("Quad", 4), g("Pair", 2)]},
        response(seated("Duo", "A1", "A2"), seated("Quad", *row("B", 1, 4)), seated("Pair", "A3", "A4")),
    ),
    (
        "a refused large group leaves its seats for a later smaller one",
        {"rows": [3], "groups": [g("Crowd", 4, True), g("Trio", 3)]},
        response(refused("Crowd", "not_enough_seats"), seated("Trio", "A1", "A2", "A3")),
    ),
    (
        "a group refused as not together takes nothing",
        {"rows": [2, 2], "groups": [g("Four", 3), g("PairA", 2), g("PairB", 2)]},
        response(refused("Four", "not_together"), seated("PairA", "A1", "A2"), seated("PairB", "B1", "B2")),
    ),
    (
        "first come, first seated",
        {"rows": [3, 3], "groups": [g("First", 3), g("Second", 3), g("Third", 1)]},
        response(seated("First", *row("A", 1, 3)), seated("Second", *row("B", 1, 3)), refused("Third", "not_enough_seats")),
    ),
    (
        "an early split group is served before a later group that could sit together",
        {"rows": [2, 2], "blocked": ["A1"], "groups": [g("Mix", 3, True), g("Pair", 2)]},
        response(seated("Mix", "A2", "B1", "B2"), refused("Pair", "not_enough_seats")),
    ),
    (
        "refusals in the middle of the list",
        {"rows": [5, 5], "blocked": ["A3"], "groups": [g("Ash", 2), g("Bo", 3), g("Cy", 5), g("Di", 1), g("Ed", 3)]},
        response(
            seated("Ash", "A1", "A2"), seated("Bo", "B1", "B2", "B3"), refused("Cy", "not_enough_seats"),
            seated("Di", "A4"), refused("Ed", "not_together"),
        ),
    ),
]


def outcome(answer):
    """Seated with how many seats, or refused (the reason belongs to G4)."""
    kind, value = answer
    return (kind, len(value) if kind == "seated" and isinstance(value, list) else None)


def describe(o):
    return f"{o[1]} seats" if o[0] == "seated" else "refused"


problems = []
full = dict(zip((c[0] for c in CASES), call_all([c[1] for c in CASES])))
for label, request, want in CASES:
    mismatch = compare(request, expected(request), want)  # hand-worked answers agree with the model
    if mismatch:
        raise SystemExit(f"audit error in case {label!r}: {mismatch[0]}")
    status, body = full[label]
    got = answers(body) if status == 0 else None
    if got is None:
        problems.append(f"{label}: status {status} or unreadable response | {brief(request)}")
        continue
    exp = answers(want)
    for group in request["groups"]:
        (w,) = exp[group["id"]]
        have = got.get(group["id"], [])
        if len(have) != 1 or outcome(have[0]) != outcome(w):
            shown = describe(outcome(have[0])) if len(have) == 1 else f"{len(have)} answers"
            problems.append(f"{label}: {group['id']} should get {describe(outcome(w))}, got {shown}")
            break

# Every proper prefix of each request must give the same answers to the groups it keeps.
prefixes = []
for label, request, _ in CASES:
    for k in range(1, len(request["groups"])):
        prefixes.append((label, request, {**request, "groups": request["groups"][:k]}))
for (label, request, prefix), (status, body) in zip(prefixes, call_all([p[2] for p in prefixes])):
    fstatus, fbody = full[label]
    got, whole = answers(body) if status == 0 else None, answers(fbody) if fstatus == 0 else None
    if got is None or whole is None:
        problems.append(f"{label}: status {status}/{fstatus} or unreadable response | {brief(prefix)}")
        continue
    for group in prefix["groups"]:
        a, b = got.get(group["id"], []), whole.get(group["id"], [])
        if len(a) != 1 or len(b) != 1 or normal(a[0]) != normal(b[0]):
            problems.append(
                f"{label}: {group['id']} gets {show(a[0]) if len(a) == 1 else a} with the first "
                f"{len(prefix['groups'])} groups but {show(b[0]) if len(b) == 1 else b} with all of them"
            )
            break

finish(problems, f"booking order ok: {len(CASES)} requests and {len(prefixes)} prefixes")
