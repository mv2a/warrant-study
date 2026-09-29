"""H2: masses convert with the exact definitions in G2."""

from kind_check import check_kind

KNOWN = [
    ("1", "lb", "g", 5, "453.59237"),
    ("1", "oz", "g", 9, "28.349523125"),
    ("1", "st", "kg", 8, "6.35029318"),
    ("1", "st", "oz", 0, "224"),
    ("16", "oz", "lb", 0, "1"),
    ("1", "t", "lb", 3, "2204.623"),
    ("1", "kg", "mg", 0, "1000000"),
    ("1", "kg", "oz", 4, "35.2740"),
    ("3.5", "t", "kg", 1, "3500.0"),
]
check_kind("mass", 1502, KNOWN)
