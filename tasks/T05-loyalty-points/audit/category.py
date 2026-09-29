"""X5 (G3): 2 bonus points per whole dollar of promoted spend, floored once before doubling.

Promoted spend is summed over every eligible item whose category is listed, across all
listed categories, matched exactly including case and spaces; listing a category twice
does not count its items twice. Standard members get no tier bonus, so the bonus here is
the category bonus alone; totals stay under the C2 cap.
"""

from _cmd import finish
from _expect import expect, response

problems = []
count = 0


def item(category, price, quantity=1):
    return {"category": category, "price_cents": price, "quantity": quantity}


def check(label, items, promoted, want, tier="standard"):
    global count
    count += 1
    request = {"tier": tier, "items": items}
    if promoted is not None:
        request["bonus_categories"] = promoted
    expect(problems, label, request, want)


# Floor once, then double.
check("$10.99 promoted earns 20, not 21", [item("hedging", 1099)], ["hedging"], response(1099, 10, 20))
check("$1.50 promoted earns 2, not 3", [item("hedging", 150)], ["hedging"], response(150, 1, 2))
check("$0.99 promoted earns 0", [item("hedging", 99)], ["hedging"], response(99, 0, 0))
check("$1.00 promoted earns 2", [item("hedging", 100)], ["hedging"], response(100, 1, 2))
check("$1.99 promoted earns 2", [item("hedging", 199)], ["hedging"], response(199, 1, 2))
check("$2.00 promoted earns 4", [item("hedging", 200)], ["hedging"], response(200, 2, 4))
check("$0.49 x 3 promoted earns 2", [item("hedging", 49, 3)], ["hedging"], response(147, 1, 2))
check("$2.50 x 4 promoted earns 20", [item("hedging", 250, 4)], ["hedging"], response(1000, 10, 20))
check("$10.99 x 3 promoted earns 64", [item("hedging", 1099, 3)], ["hedging"], response(3297, 32, 64))

# Summed across items before the floor, not item by item.
check("two promoted items at $0.60", [item("hedging", 60), item("hedging", 60)], ["hedging"], response(120, 1, 2))
check("three promoted items at $0.40", [item("hedging", 40), item("hedging", 40), item("hedging", 40)], ["hedging"], response(120, 1, 2))
check("promoted $19.99 + $0.01", [item("hedging", 1999), item("hedging", 1)], ["hedging"], response(2000, 20, 40))

# Summed across all listed categories, not category by category.
check("$0.50 in each of two promoted categories", [item("lawn", 50), item("fencing", 50)], ["lawn", "fencing"], response(100, 1, 2))
check("$3.70 + $4.40 across two promoted categories", [item("lawn", 370), item("fencing", 440)], ["fencing", "lawn"], response(810, 8, 16))
check("three promoted categories", [item("lawn", 333), item("fencing", 333), item("ponds", 334)], ["ponds", "lawn", "fencing"], response(1000, 10, 20))

# Only listed categories count; others still earn base points.
check("one promoted, one not", [item("lawn", 1000), item("grocery", 1000)], ["lawn"], response(2000, 20, 20))
check("promoted $5.50, not promoted $5.50", [item("lawn", 550), item("grocery", 550)], ["lawn"], response(1100, 11, 10))
check("listed category not in the order", [item("grocery", 2500)], ["lawn"], response(2500, 25, 0))
check("bonus_categories left out", [item("lawn", 2500)], None, response(2500, 25, 0))
check("bonus_categories empty", [item("lawn", 2500)], [], response(2500, 25, 0))
check("empty string listed", [item("lawn", 2500)], [""], response(2500, 25, 0))

# Exact match, including case and spaces.
check("item Lawn, listed lawn", [item("Lawn", 2500)], ["lawn"], response(2500, 25, 0))
check("item lawn, listed LAWN", [item("lawn", 2500)], ["LAWN"], response(2500, 25, 0))
check("item lawn, listed ' lawn'", [item("lawn", 2500)], [" lawn"], response(2500, 25, 0))
check("item 'lawn ', listed lawn", [item("lawn ", 2500)], ["lawn"], response(2500, 25, 0))
check("item lawn-care, listed lawn", [item("lawn-care", 2500)], ["lawn"], response(2500, 25, 0))
check("item lawn, listed lawn-care", [item("lawn", 2500)], ["lawn-care"], response(2500, 25, 0))
check("mixed case, only exact one counts", [item("Lawn", 1000), item("lawn", 700)], ["lawn"], response(1700, 17, 14))
check("both spellings listed", [item("Lawn", 1000), item("lawn", 700)], ["lawn", "Lawn"], response(1700, 17, 34))
check("non-ASCII exact match", [item("pépinière", 1234)], ["pépinière"], response(1234, 12, 24))

# An item counts once even when its category is listed more than once.
check("listed twice", [item("lawn", 1000)], ["lawn", "lawn"], response(1000, 10, 20))
check("listed three times among others", [item("lawn", 1000), item("ponds", 500)], ["lawn", "ponds", "lawn", "lawn"], response(1500, 15, 30))
check("listed twice, two $0.60 items", [item("lawn", 60), item("lawn", 60)], ["lawn", "lawn"], response(120, 1, 2))

# Gift cards are not eligible, so they are not promoted spend either (see also C1).
check("gift_card listed with a promoted category", [item("gift_card", 5000), item("lawn", 1000)], ["gift_card", "lawn"], response(1000, 10, 20))

# The category bonus is added to the tier bonus.
check("silver, tier bonus plus category bonus", [item("lawn", 2099), item("grocery", 1500)], ["lawn"], response(3599, 35, 48), tier="silver")  # 43.75 -> 8; 20 -> 40
check("gold, tier bonus plus category bonus", [item("lawn", 750, 2), item("grocery", 1)], ["lawn"], response(1501, 15, 37), tier="gold")  # 22.5 -> 7; 15 -> 30

finish(problems, f"category bonus ok: {count} orders")
