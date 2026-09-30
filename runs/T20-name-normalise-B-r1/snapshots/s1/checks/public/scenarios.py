"""P2: the example requests written in the intent's scenarios."""

from _cmd import call, finish

SCENARIOS = [
    ("S1", "  prof. DR.  anna-maria   o'neil ", "Anna-Maria O'Neil", "annamariaoneil"),
    ("S2", "LUDWIG VAN BEETHOVEN", "Ludwig van Beethoven", "ludwigvanbeethoven"),
    ("S3", "van der berg", "Van der Berg", "vanderberg"),
    ("S4", "Mr José García", "José García", "josegarcia"),
    ("S4", "jose  GARCIA", "Jose Garcia", "josegarcia"),
]
problems = []
for scenario, name, display, key in SCENARIOS:
    status, body = call({"name": name})
    expected = {"display": display, "key": key}
    if status != 0 or body != expected:
        problems.append(f"{scenario} {name!r}: expected {expected}, got {body!r} (status {status})")

finish(problems, "scenarios ok: S1, S2, S3, S4")
