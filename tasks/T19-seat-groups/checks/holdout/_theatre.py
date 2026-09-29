"""Shared helpers for the hidden checks: seat names, generated requests and replaying a response."""

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def name(row, number):
    return f"{LETTERS[row]}{number}"


def all_seats(rows):
    """Every seat name of the theatre, in seating order."""
    return [name(r, n) for r, count in enumerate(rows) for n in range(1, count + 1)]


def split_name(seat):
    """(row index, seat number) for a well-formed seat name, else None."""
    if not isinstance(seat, str) or len(seat) < 2 or seat[0] not in LETTERS:
        return None
    # str.isdigit() alone accepts non-ASCII digits such as '١' or '¹', so require ASCII too.
    if not (seat[1:].isascii() and seat[1:].isdigit()):
        return None
    if seat[1] == "0":
        return None
    return LETTERS.index(seat[0]), int(seat[1:])


def together_block(rows, free, size):
    """The block G2 asks for: frontmost row, lowest-numbered run of `size` free seats. None if none."""
    for r, count in enumerate(rows):
        for start in range(1, count - size + 2):
            block = [name(r, n) for n in range(start, start + size)]
            if all(seat in free for seat in block):
                return block
    return None


def first_free(rows, free, size):
    """The first `size` free seats in seating order (G3)."""
    return [seat for seat in all_seats(rows) if seat in free][:size]


def random_request(rng, max_rows=5, max_seats=12, max_groups=10, split_rate=0.3, blocked_rate=0.15, max_size=7):
    rows = [rng.randint(1, max_seats) for _ in range(rng.randint(1, max_rows))]
    blocked = [seat for seat in all_seats(rows) if rng.random() < blocked_rate]
    rng.shuffle(blocked)
    groups = []
    for i in range(rng.randint(1, max_groups)):
        group = {"id": f"g{i + 1}", "size": rng.randint(1, max_size)}
        if rng.random() < split_rate:
            group["may_split"] = True
        elif rng.random() < 0.2:
            group["may_split"] = False
        groups.append(group)
    request = {"rows": rows, "groups": groups}
    if blocked or rng.random() < 0.5:
        request["blocked"] = blocked
    return request


def replay(request, body):
    """Walk the groups in booking order, rebuilding the free seats from the response itself.

    Yields (group, free seats before this group, outcome) where outcome is
    ("seated", seats), ("refused", reason) or ("missing", None).
    """
    seated = {e.get("id"): e.get("seats") for e in body.get("seated", []) if isinstance(e, dict)}
    refused = {e.get("id"): e.get("reason") for e in body.get("refused", []) if isinstance(e, dict)}
    free = set(all_seats(request["rows"])) - set(request.get("blocked", []))
    for group in request["groups"]:
        before = set(free)
        if group["id"] in seated and isinstance(seated[group["id"]], list):
            seats = seated[group["id"]]
            free -= set(seats)
            yield group, before, ("seated", seats)
        elif group["id"] in refused:
            yield group, before, ("refused", refused[group["id"]])
        else:
            yield group, before, ("missing", None)


def response_ok(status, body):
    """A short reason the response cannot be replayed, or None."""
    if status != 0:
        return f"exit status {status}, expected 0"
    if not isinstance(body, dict) or not isinstance(body.get("seated"), list) or not isinstance(body.get("refused"), list):
        return f"unreadable response {body!r}"
    return None
