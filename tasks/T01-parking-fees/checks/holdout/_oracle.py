"""The tariff in intent.md, restated independently of any implementation for the hidden checks.

It walks the stay hour by hour and minute by minute instead of using closed-form arithmetic.
"""

WEEK = 10080
FIELDS = ("minutes", "time_cents", "overnight_cents", "lost_ticket_cents", "total_cents")


def stay_minutes(entry, exit_):
    return (exit_ - entry) % WEEK  # an earlier exit is next week; an equal one is zero minutes


def expected(entry, exit_, lost_ticket):
    minutes = stay_minutes(entry, exit_)
    time_cents = overnight_cents = 0
    if minutes > 15:
        per_period = {}
        start = 0  # each started hour begins at this many minutes after entry
        while start < minutes:
            period = start // 1440
            per_period[period] = per_period.get(period, 0) + 250
            start += 60
        time_cents = sum(min(cents, 1600) for cents in per_period.values())
        nights = sum(1 for t in range(entry, entry + minutes) if t % 1440 == 120)
        overnight_cents = 600 * nights
    lost_ticket_cents = 2500 if lost_ticket else 0
    return {
        "minutes": minutes,
        "time_cents": time_cents,
        "overnight_cents": overnight_cents,
        "lost_ticket_cents": lost_ticket_cents,
        "total_cents": time_cents + overnight_cents + lost_ticket_cents,
    }


def request(entry, exit_, lost_ticket=False):
    return {"entry": entry, "exit": exit_, "lost_ticket": lost_ticket}


def clock(minute):
    """Minute of the week as a readable label, for failure messages."""
    day = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")[minute // 1440 % 7]
    return f"{day} {minute % 1440 // 60:02d}:{minute % 60:02d} ({minute})"
