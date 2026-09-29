"""X7 (C2): tier bonus plus category bonus is capped at 500 per order; base points never are.

Boundaries on each side of 500 for the category bonus alone, the tier bonus alone and the
two together, plus orders whose base points are far above 500.
"""

from _cmd import finish
from _expect import expect, response

problems = []
count = 0


def item(category, price, quantity=1):
    return {"category": category, "price_cents": price, "quantity": quantity}


def check(label, tier, items, promoted, want):
    global count
    count += 1
    request = {"tier": tier, "items": items}
    if promoted is not None:
        request["bonus_categories"] = promoted
    expect(problems, label, request, want)


# Category bonus alone (standard members have no tier bonus).
check("category 498", "standard", [item("patio", 24999)], ["patio"], response(24999, 249, 498))
check("category exactly 500", "standard", [item("patio", 25000)], ["patio"], response(25000, 250, 500))
check("category 500 from $250.99", "standard", [item("patio", 25099)], ["patio"], response(25099, 250, 500))
check("category 502 capped", "standard", [item("patio", 25100)], ["patio"], response(25100, 251, 500))
check("category 1998 capped", "standard", [item("patio", 99999)], ["patio"], response(99999, 999, 500))
check("category 20000 capped", "standard", [item("patio", 250000, 4)], ["patio"], response(1000000, 10000, 500))

# Tier bonus alone (nothing promoted).
check("gold tier 499", "gold", [item("sheds", 99899)], None, response(99899, 998, 499))
check("gold tier exactly 500", "gold", [item("sheds", 100000)], None, response(100000, 1000, 500))
check("gold tier 500 from base 1001", "gold", [item("sheds", 100150)], None, response(100150, 1001, 500))
check("gold tier 501 capped", "gold", [item("sheds", 100200)], None, response(100200, 1002, 500))
check("gold tier 550 capped", "gold", [item("sheds", 110000)], None, response(110000, 1100, 500))
check("silver tier 499", "silver", [item("sheds", 199999)], None, response(199999, 1999, 499))
check("silver tier exactly 500", "silver", [item("sheds", 200000)], None, response(200000, 2000, 500))
check("silver tier 500 from base 2003", "silver", [item("sheds", 200350)], None, response(200350, 2003, 500))
check("silver tier 501 capped", "silver", [item("sheds", 200400)], None, response(200400, 2004, 500))
check("silver tier 750 capped", "silver", [item("sheds", 300000)], None, response(300000, 3000, 500))

# Tier and category together.
# silver: base 400 -> tier 100; category $200.00 -> 400; exactly 500.
check("silver 100 + 400 = 500", "silver", [item("patio", 20000), item("sheds", 20000)], ["patio"], response(40000, 400, 500))
# silver: base 404 -> tier 101; category 400; 501 capped.
check("silver 101 + 400 capped", "silver", [item("patio", 20000), item("sheds", 20400)], ["patio"], response(40400, 404, 500))
# gold: base 300 -> tier 150; category $175.00 -> 350; exactly 500.
check("gold 150 + 350 = 500", "gold", [item("patio", 17500), item("sheds", 12500)], ["patio"], response(30000, 300, 500))
# gold: base 301 -> tier 150; category $175.50 -> 350; 500.
check("gold 150 + 350 from base 301", "gold", [item("patio", 17550), item("sheds", 12550)], ["patio"], response(30100, 301, 500))
# gold: base 302 -> tier 151; category 350; 501 capped.
check("gold 151 + 350 capped", "gold", [item("patio", 17500), item("sheds", 12700)], ["patio"], response(30200, 302, 500))
# gold: base 600 -> tier 300; category 1200; capped.
check("gold 300 + 1200 capped", "gold", [item("patio", 60000)], ["patio"], response(60000, 600, 500))
# silver: base 200 -> tier 50; category 300 from $150; 350, not capped.
check("silver 50 + 300 not capped", "silver", [item("patio", 15000), item("sheds", 5000)], ["patio"], response(20000, 200, 350))
# silver: tier alone under the cap, category alone under the cap, the sum over it.
# base 360 -> tier 90; category $210.00 -> 420; 510 capped.
check("silver 90 + 420 capped", "silver", [item("patio", 21000), item("sheds", 15000)], ["patio"], response(36000, 360, 500))

# Base points are never capped.
check("standard, base 123456", "standard", [item("sheds", 12345600)], None, response(12345600, 123456, 0))
check("gold, base 10,000,000", "gold", [item("sheds", 1000000, 1000)], None, response(1000000000, 10000000, 500))
check("silver, base 5000 all promoted", "silver", [item("patio", 500000)], ["patio"], response(500000, 5000, 500))
check("standard, $999.99 promoted", "standard", [item("patio", 99999), item("gift_card", 99999)], ["patio", "gift_card"], response(99999, 999, 500))

finish(problems, f"cap ok: {count} orders")
