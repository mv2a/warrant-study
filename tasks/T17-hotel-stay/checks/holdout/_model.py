"""An independent statement of intent.md as arithmetic, shared by the hidden checks."""

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def nights_of(check_in, nights):
    """The weekday each night begins on (G1)."""
    first = DAYS.index(check_in)
    return [DAYS[(first + k) % 7] for k in range(nights)]


def surcharge(rate):
    """25% of the rate, nearest cent, exact half up (C2). rate / 4 has fractions .0 .25 .5 .75."""
    whole, quarters = divmod(rate, 4)
    return whole + (1 if quarters >= 2 else 0)


def refused_by_min_stay(check_in, nights):
    """G4: a stay with a Saturday night must be at least 3 nights."""
    return "sat" in nights_of(check_in, nights) and nights < 3


def room(check_in, nights, rate):
    return sum(rate + (surcharge(rate) if day in ("fri", "sat") else 0) for day in nights_of(check_in, nights))


def percent(nights):
    """G2 tiers."""
    return 15 if nights >= 14 else 10 if nights >= 7 else 0


def tax(nights):
    """G3: 275 cents for each of the first 10 nights."""
    return 275 * min(nights, 10)


def quote(check_in, nights, rate):
    """The full expected response for a valid request, or None when it must be refused."""
    if refused_by_min_stay(check_in, nights):
        return None
    r = room(check_in, nights, rate)
    d = r * percent(nights) // 100
    t = tax(nights)
    return {"room_cents": r, "discount_cents": d, "tax_cents": t, "total_cents": r - d + t}


def valid_stays(max_nights=30):
    """Every (check_in, nights) pair the minimum-stay rule allows."""
    return [(day, n) for day in DAYS for n in range(1, max_nights + 1) if not refused_by_min_stay(day, n)]


def priced(status, body):
    return status == 0 and isinstance(body, dict)


def refused(status, body):
    """Refused, not priced: a nonzero exit and no amounts on standard output (C1 checks the exact form)."""
    return status != 0 and not (isinstance(body, dict) and "total_cents" in body)
