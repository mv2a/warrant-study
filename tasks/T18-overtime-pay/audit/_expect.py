"""Expected answers for the audit checks, worked out from intent.md alone.

The split is done the slow, literal way: every worked minute of every day is put in a
category by its position in the day (G1, G3), and only then is the weekly cap applied to
the regular total (G2). Money uses exact fractions and rounds halves up (C1).
"""

from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction

MINUTE_FIELDS = ("regular_minutes", "overtime_minutes", "double_minutes")
CENT_FIELDS = ("regular_cents", "overtime_cents", "double_cents")
FIELDS = MINUTE_FIELDS + CENT_FIELDS + ("total_cents",)

WEEK_REGULAR_CAP = 2400
MULTIPLIER = {"regular": Fraction(1), "overtime": Fraction(3, 2), "double": Fraction(2)}


def seventh_consecutive(minutes):
    """G3: day 7 is a seventh consecutive day only when all seven days have work."""
    return all(day > 0 for day in minutes)


def category_of(minute_of_day, seventh):
    """The category of the n-th minute (counting from 1) worked on one day."""
    if seventh:
        return "overtime" if minute_of_day <= 480 else "double"
    if minute_of_day <= 480:
        return "regular"
    if minute_of_day <= 660:
        return "overtime"
    return "double"


def split(minutes):
    """(regular, overtime, double) minutes for a valid week."""
    seventh = seventh_consecutive(minutes)
    counts = {"regular": 0, "overtime": 0, "double": 0}
    for day, worked in enumerate(minutes, start=1):
        for n in range(1, worked + 1):
            counts[category_of(n, seventh and day == 7)] += 1
    if counts["regular"] > WEEK_REGULAR_CAP:
        counts["overtime"] += counts["regular"] - WEEK_REGULAR_CAP
        counts["regular"] = WEEK_REGULAR_CAP
    return counts["regular"], counts["overtime"], counts["double"]


def price(rate_cents, category, minutes):
    """rate x multiplier x minutes / 60, to the nearest cent, exact halves up."""
    exact = Fraction(rate_cents) * MULTIPLIER[category] * minutes / 60
    cents = exact.numerator // exact.denominator
    if exact - cents >= Fraction(1, 2):
        cents += 1
    return cents


def prices(rate_cents, regular, overtime, double):
    """The four money fields for the given category totals."""
    amounts = (price(rate_cents, "regular", regular),
               price(rate_cents, "overtime", overtime),
               price(rate_cents, "double", double))
    return amounts + (sum(amounts),)


def expected(request):
    """The full response the intent requires for a valid request."""
    minutes = split(request["minutes"])
    return dict(zip(FIELDS, minutes + prices(request["rate_cents"], *minutes)))


def minutes_of(body):
    """The three minute fields of a response, or None when it is not a proper response."""
    if not isinstance(body, dict):
        return None
    got = tuple(body.get(field) for field in MINUTE_FIELDS)
    if not all(type(value) is int for value in got):
        return None
    return got


def call_all(call, items, raw=False, workers=4):
    """Run the command once per request (or raw text), a few at a time, in order."""
    def one(item):
        return call(raw=item) if raw else call(item)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(one, items))


def compare_minutes(call, weeks, rate_of, problems):
    """Run each week and compare only the minute split with the expected one."""
    requests = [{"minutes": week, "rate_cents": rate_of(index)} for index, week in enumerate(weeks)]
    for request, (status, body) in zip(requests, call_all(call, requests)):
        week, rate = request["minutes"], request["rate_cents"]
        want = split(week)
        got = minutes_of(body)
        if status != 0 or got != want:
            problems.append(f"{week} at {rate}: expected regular, overtime, double minutes "
                            f"{want}, got {got if got is not None else body!r} (status {status})")
