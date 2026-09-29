"""The fine rules from intent.md, used by the hidden checks to work out expected answers."""

RATE = {"book": 25, "dvd": 100, "reference": 150}
GRACE = {"book": 3, "dvd": 3, "reference": 0}
ITEM_CAP = {"book": 800, "dvd": 2000, "reference": 1500}
ACCOUNT_CAP = 2500
TYPES = ("book", "dvd", "reference")


def days_late(due_day, returned_day):
    return max(0, returned_day - due_day)


def item_fine(kind, due_day, returned_day):
    charged = max(0, days_late(due_day, returned_day) - GRACE[kind])
    return min(charged * RATE[kind], ITEM_CAP[kind])


def item(ident, kind, due_day, late):
    """A request item that is `late` days late (negative means returned early)."""
    return {"id": ident, "type": kind, "due_day": due_day, "returned_day": due_day + late}


def fines_by_id(body):
    """The response's fine_cents per id, or None when the response has the wrong shape."""
    try:
        return {line["id"]: line["fine_cents"] for line in body["items"]}
    except (TypeError, KeyError):
        return None
