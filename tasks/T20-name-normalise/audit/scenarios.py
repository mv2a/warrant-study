"""X17-X20 (S1-S4): the requests written in the intent's scenarios, sent as the JSON text
the intent shows, must give exactly the output the intent shows. Usage: scenarios.py S1"""

import sys

from _cmd import call, finish

SCENARIOS = {
    "S1": [('{"name": "  prof. DR.  anna-maria   o\'neil "}', {"display": "Anna-Maria O'Neil", "key": "annamariaoneil"})],
    "S2": [('{"name": "LUDWIG VAN BEETHOVEN"}', {"display": "Ludwig van Beethoven", "key": "ludwigvanbeethoven"})],
    "S3": [('{"name": "van der berg"}', {"display": "Van der Berg", "key": "vanderberg"})],
    "S4": [('{"name":"Mr Jos\\u00e9 Garc\\u00eda"}', {"display": "Jos\xe9 Garc\xeda", "key": "josegarcia"}),
           ('{"name":"jose  GARCIA"}', {"display": "Jose Garcia", "key": "josegarcia"})],
}

scenario = sys.argv[1]
problems = []
bodies = []
for raw, expected in SCENARIOS[scenario]:
    status, body = call(raw=raw)
    bodies.append(body)
    if status != 0 or body != expected:
        problems.append(f"{scenario} {raw}: expected {expected!r} with status 0, got {body!r} (status {status})"[:200])
if scenario == "S4" and not problems and bodies[0]["key"] != bodies[1]["key"]:
    problems.append("S4: the two sign-ups should get the same key")

finish(problems, f"{scenario} ok")
