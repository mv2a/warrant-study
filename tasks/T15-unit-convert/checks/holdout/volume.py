"""H3: volumes convert with the exact US definitions in G3."""

from kind_check import check_kind

KNOWN = [
    ("1", "gal", "ml", 6, "3785.411784"),
    ("1", "gal", "floz", 0, "128"),
    ("1", "floz", "ml", 10, "29.5735295625"),
    ("1", "qt", "l", 9, "0.946352946"),
    ("2", "pt", "qt", 0, "1"),
    ("1", "m3", "gal", 4, "264.1721"),
    ("1", "l", "floz", 6, "33.814023"),
    ("1", "l", "pt", 5, "2.11338"),
    ("0.25", "m3", "l", 0, "250"),
]
check_kind("volume", 1503, KNOWN)
