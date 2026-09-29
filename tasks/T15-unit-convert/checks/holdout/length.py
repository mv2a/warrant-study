"""H1: lengths convert with the exact definitions in G1."""

from kind_check import check_kind

KNOWN = [
    ("1", "in", "mm", 1, "25.4"),
    ("1", "ft", "cm", 2, "30.48"),
    ("1", "yd", "in", 0, "36"),
    ("1", "mi", "yd", 0, "1760"),
    ("3", "mi", "ft", 0, "15840"),
    ("1", "mi", "km", 6, "1.609344"),
    ("1", "km", "mi", 9, "0.621371192"),
    ("100", "in", "m", 2, "2.54"),
    ("2.5", "km", "cm", 0, "250000"),
    ("1", "m", "ft", 6, "3.280840"),
]
check_kind("length", 1501, KNOWN)
