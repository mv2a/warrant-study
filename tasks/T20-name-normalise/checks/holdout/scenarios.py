"""H9 (S1-S4): the intent's scenarios, exactly, plus the S4 duplicate pair sharing a key."""

from _cmd import call, finish

SCENARIOS = [
    ("S1", "  prof. DR.  anna-maria   o'neil ", {"display": "Anna-Maria O'Neil", "key": "annamariaoneil"}),
    ("S2", "LUDWIG VAN BEETHOVEN", {"display": "Ludwig van Beethoven", "key": "ludwigvanbeethoven"}),
    ("S3", "van der berg", {"display": "Van der Berg", "key": "vanderberg"}),
    ("S4", "Mr José García", {"display": "José García", "key": "josegarcia"}),
    ("S4", "jose  GARCIA", {"display": "Jose Garcia", "key": "josegarcia"}),
]
problems = []
keys = {}
for scenario, name, expected in SCENARIOS:
    status, body = call({"name": name})
    if status != 0 or body != expected:
        problems.append(f"{scenario} {name!r}: expected {expected}, got {body!r} (status {status})")
    if isinstance(body, dict):
        keys.setdefault(scenario, set()).add(body.get("key"))
if len(keys.get("S4", ())) != 1:
    problems.append(f"S4: the two sign-ups should share one key, got {keys.get('S4')}")

finish(problems, "scenarios ok: S1, S2, S3, S4")
