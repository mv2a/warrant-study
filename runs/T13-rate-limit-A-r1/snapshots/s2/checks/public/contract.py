"""P1: `limit` follows the interface in C1."""

from _cmd import call, finish

problems = []
log = [("web", 0), ("web", 0), ("cron", 10), ("web", 20), ("cron", 2000)]
request = {"burst": 1, "rate": 1, "requests": [{"client": c, "at": t} for c, t in log]}
status, body = call(request)
if status != 0:
    problems.append(f"a valid log: exited with status {status}, expected 0")
elif not isinstance(body, dict) or set(body) != {"decisions", "clients"}:
    problems.append(f"a valid log: expected an object with exactly decisions and clients, got {body!r}")
else:
    decisions, clients = body["decisions"], body["clients"]
    if not isinstance(decisions, list) or len(decisions) != len(log) or not all(d in ("accept", "reject") for d in decisions):
        problems.append(f"decisions must list accept or reject for each of the {len(log)} requests, got {decisions!r}")
    elif not isinstance(clients, dict) or set(clients) != {"web", "cron"}:
        problems.append(f"clients must have one entry for web and one for cron, got {clients!r}")
    else:
        for name in ("web", "cron"):
            mine = [d for (c, _), d in zip(log, decisions) if c == name]
            want = {"accepted": mine.count("accept"), "rejected": mine.count("reject")}
            if clients[name] != want:
                problems.append(f"clients[{name!r}] should count its decisions as {want}, got {clients[name]!r}")

for name, raw in (("a burst of 0", '{"burst": 0, "rate": 1, "requests": []}'), ("text that isn't JSON", "hello")):
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{name} must be refused with status 2 and no output, got status {status} and {body!r}")

finish(problems, "contract ok: 3 requests")
