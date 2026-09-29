"""X6 (C1): items whose category is exactly "gift_card" earn nothing.

They are left out of eligible_cents and earn no base, tier or category points, even when
"gift_card" is listed as a bonus category; an order of only gift cards earns 0 in every
tier. Only the exact category "gift_card" is a gift card.
"""

from _cmd import finish
from _expect import expect, response

problems = []
count = 0
ZERO = response(0, 0, 0)


def item(category, price, quantity=1):
    return {"category": category, "price_cents": price, "quantity": quantity}


def check(label, tier, items, promoted, want):
    global count
    count += 1
    request = {"tier": tier, "items": items}
    if promoted is not None:
        request["bonus_categories"] = promoted
    expect(problems, label, request, want)


# Only gift cards: 0 in every tier, promoted or not, whatever the amount.
for tier in ("standard", "silver", "gold"):
    check(f"{tier}, one gift card", tier, [item("gift_card", 10000)], None, ZERO)
    check(f"{tier}, gift cards listed as promoted", tier, [item("gift_card", 2500, 4), item("gift_card", 99)], ["gift_card"], ZERO)
check("gold, huge gift card order with gift_card promoted", "gold", [item("gift_card", 50000, 200)], ["gift_card", "garden"], ZERO)
check("silver, cheap gift cards", "silver", [item("gift_card", 1), item("gift_card", 0, 3)], ["gift_card"], ZERO)

# Mixed orders: the gift cards contribute nothing anywhere.
# gold: eligible $10.00 -> base 10, tier 5.
check("gold, gift card beside groceries", "gold", [item("grocery", 1000), item("gift_card", 100000)], None, response(1000, 10, 5))
# silver: eligible $12.34 -> base 12, tier 15 -> 3, tools $12.34 -> 24.
check("silver, gift_card and tools promoted", "silver", [item("gift_card", 20000, 3), item("tools", 1234)], ["gift_card", "tools"], response(1234, 12, 27))
# standard: gift card cents must not complete a dollar.
check("standard, $0.60 + $0.60 gift card", "standard", [item("grocery", 60), item("gift_card", 60)], None, response(60, 0, 0))
check("standard, $0.99 + $0.01 gift card, both promoted", "standard", [item("grocery", 99), item("gift_card", 1)], ["grocery", "gift_card"], response(99, 0, 0))
# gold: gift cards first and last, promoted; eligible $30.00 -> base 30, tier 15, category $20.00 -> 40.
check("gold, gift cards around promoted items", "gold",
      [item("gift_card", 7500), item("seeds", 1000, 2), item("grocery", 1000), item("gift_card", 2500, 2)],
      ["seeds", "gift_card"], response(3000, 30, 55))
# The C2 cap cannot be reached through gift cards: 400 promoted gift-card dollars earn nothing.
check("standard, gift card spend cannot reach the cap", "standard", [item("gift_card", 40000), item("seeds", 500)], ["gift_card", "seeds"], response(500, 5, 10))

# Only the exact category "gift_card" is a gift card; look-alikes are ordinary items.
for look_alike in ("Gift_Card", "GIFT_CARD", "gift card", "giftcard", "gift_cards", " gift_card", "gift_card "):
    # standard: $25.00 -> base 25; promoted -> 50.
    check(f"{look_alike!r} is an ordinary category", "standard", [item(look_alike, 2500)], [look_alike], response(2500, 25, 50))

finish(problems, f"gift cards ok: {count} orders")
