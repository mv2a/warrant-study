"""An independent model of intent.md (G1-G5, C2, C3) and a seeded request generator for the audit checks."""

from _audit import e

TYPES = ("string", "integer", "number", "boolean")


def fits(value, kind):
    """G2: does a present, non-null value hold the field's type?"""
    if kind == "string":
        return type(value) is str
    if kind == "boolean":
        return type(value) is bool
    if kind == "number":
        return type(value) in (int, float)
    if kind == "integer":
        return type(value) is int or (type(value) is float and value.is_integer())
    raise ValueError(kind)


def expected_errors(schema, rows):
    """The errors intent.md asks for, in the order C3 asks for."""
    errors = []
    seen = {rule["name"]: [] for rule in schema if rule.get("unique")}
    for index, row in enumerate(rows):
        for rule in schema:
            name, kind = rule["name"], rule["type"]
            value = row.get(name)
            if value is None:  # left out or null (G1)
                if rule.get("required"):
                    errors.append(e(index, name, "missing"))
                continue
            if not fits(value, kind):
                errors.append(e(index, name, "type"))
                continue
            code = None
            if ("min" in rule and value < rule["min"]) or ("max" in rule and value > rule["max"]):
                code = "range"
            elif "allowed" in rule and not any(value == entry for entry in rule["allowed"]):
                code = "allowed"
            elif name in seen and any(value == earlier for earlier in seen[name]):
                code = "duplicate"
            if name in seen:
                seen[name].append(value)
            if code:
                errors.append(e(index, name, code))
    return errors


# Pools with deliberate near-collisions: case, spaces, accents, 2 and 2.0, 0 and -0.0.
POOLS = {
    "string": ["a", "A", "a ", " a", "b", "", "ab", "\u00e9", "e\u0301", "0", "true"],
    "integer": [-2, -1, 0, 1, 2, 3, 7, 1.0, 2.0, -0.0, 3.0, 40, 10**12],
    "number": [-2, -0.5, 0, 0.25, 1, 1.0, 1.5, 2, 2.0, -0.0, 3.75, 7, 1e3],
    "boolean": [True, False],
}
FOREIGN = [True, False, 0, 1, 1.0, 2.5, -3, "1", "true", "", "x", [], [1], {}, {"k": 1}]
NAMES = ["k", "Kappa", "kappa", "size", "gr\u00f6\u00dfe", "two words", "n_2", "row", "code", "\u5e74"]
BOUNDS = {"integer": [-1, 0, 0.5, 1, 1.5, 2, 3, 7, 40], "number": [-1, -0.5, 0, 0.25, 1, 1.5, 2, 3.75]}


def gen_rule(rng, name):
    kind = rng.choice(TYPES)
    rule = {"name": name, "type": kind}
    if rng.random() < 0.55:
        rule["required"] = rng.random() < 0.7
    if rng.random() < 0.45:
        rule["unique"] = rng.random() < 0.85
    if kind in BOUNDS:
        low = rng.choice(BOUNDS[kind]) if rng.random() < 0.45 else None
        high = rng.choice(BOUNDS[kind]) if rng.random() < 0.45 else None
        if low is not None and high is not None and low > high:
            low, high = high, low
        if low is not None:
            rule["min"] = low
        if high is not None:
            rule["max"] = high
    if rng.random() < 0.35:
        pool = POOLS[kind]
        rule["allowed"] = rng.sample(pool, rng.randint(1, min(4, len(pool))))
    keys = list(rule)
    rng.shuffle(keys)
    return {k: rule[k] for k in keys}


def gen_schema(rng, width=None):
    width = width or rng.randint(1, 6)
    return [gen_rule(rng, name) for name in rng.sample(NAMES, width)]


def gen_value(rng, rule):
    roll = rng.random()
    if roll < 0.12:
        return "LEAVE_OUT"
    if roll < 0.2:
        return None
    if roll < 0.75:
        return rng.choice(POOLS[rule["type"]])
    return rng.choice(FOREIGN)


def gen_rows(rng, schema, count=None):
    count = rng.randint(0, 25) if count is None else count
    rows = []
    for _ in range(count):
        row = {}
        for rule in schema:
            value = gen_value(rng, rule)
            if value != "LEAVE_OUT":
                row[rule["name"]] = value
        if rng.random() < 0.3:
            row[rng.choice(["extra", "note", "K", "Size"])] = rng.choice(FOREIGN + [None])
        keys = list(row)
        rng.shuffle(keys)
        rows.append({k: row[k] for k in keys})
    return rows
