"""An independent model of intent.md for the hidden checks.

It walks the week minute by minute instead of reasoning in blocks, and prices the result
with exact fractions, so it shares no arithmetic shortcuts with any implementation.
"""

from fractions import Fraction

FIELDS = ("regular_minutes", "overtime_minutes", "double_minutes",
          "regular_cents", "overtime_cents", "double_cents", "total_cents")
MINUTE_FIELDS = FIELDS[:3]
CENT_FIELDS = FIELDS[3:]


def split(minutes):
    """(regular, overtime, double) minutes for a week of 7 day lengths."""
    seventh = all(worked > 0 for worked in minutes)
    counts = {"regular": 0, "overtime": 0, "double": 0}
    week_regular = 0
    for day, worked in enumerate(minutes, start=1):
        for nth in range(1, worked + 1):
            if seventh and day == 7:
                kind = "overtime" if nth <= 480 else "double"
            elif nth <= 480:
                kind = "regular"
            elif nth <= 660:
                kind = "overtime"
            else:
                kind = "double"
            if kind == "regular":
                if week_regular == 2400:
                    kind = "overtime"
                else:
                    week_regular += 1
            counts[kind] += 1
    return counts["regular"], counts["overtime"], counts["double"]


def half_up(amount):
    return (amount + Fraction(1, 2)).__floor__()


def expected(minutes, rate):
    regular, overtime, double = split(minutes)
    regular_cents = half_up(Fraction(rate) * regular / 60)
    overtime_cents = half_up(Fraction(3, 2) * rate * overtime / 60)
    double_cents = half_up(Fraction(2) * rate * double / 60)
    values = (regular, overtime, double, regular_cents, overtime_cents, double_cents,
              regular_cents + overtime_cents + double_cents)
    return dict(zip(FIELDS, values))


def pick(body, fields):
    """The given fields of a response as a tuple, or None when the response is not an object."""
    return tuple(body.get(field) for field in fields) if isinstance(body, dict) else None
