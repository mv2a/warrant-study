"""X8 (G3): capitalisation of words, written out by hand from the rule in G3.

Names here have no honorifics, no particles and single spaces, so only G3 decides them."""

from _audit import display_of, show
from _cmd import finish

CASES = [
    ("bram-OSKAR lind", "Bram-Oskar Lind"),
    ("SEAN o'BRIEN", "Sean O'Brien"),
    ("sean o\u2019brien", "Sean O\u2019Brien"),           # the typographic apostrophe
    ("a.b.c. HUGHES", "A.B.C. Hughes"),
    ("MACLEOD", "Macleod"),
    ("mcintyre-o'HARA", "Mcintyre-O'Hara"),
    ("henry 4TH", "Henry 4th"),
    ("ODILE 21ST", "Odile 21st"),
    ("\xc9MILE ZOLAN", "\xc9mile Zolan"),
    ("\xc5SA \xd6BERG", "\xc5sa \xd6berg"),
    ("\xf8YVIND", "\xd8yvind"),
    ("\u0142UKASZ", "\u0141ukasz"),
    ("\u0434\u043c\u0438\u0442\u0440\u0438\u0439 \u0418\u0412\u0410\u041d\u041e\u0412",
     "\u0414\u043c\u0438\u0442\u0440\u0438\u0439 \u0418\u0432\u0430\u043d\u043e\u0432"),
    ("GRO\u1e9e", "Gro\xdf"),                            # capital sharp s lower-cases to sharp s
    ("stra\xdfe", "Stra\xdfe"),
    ("kofi (KOKO) varga", "Kofi (koko) Varga"),           # only - ' \u2019 . start a capital
    ("o\u2018neil", "O\u2018neil"),                        # a left quotation mark is not an apostrophe
    ("runa\u2013LENA", "Runa\u2013lena"),                  # an en dash is not a hyphen
    ("runa_LENA", "Runa_lena"),
    ("runa/LENA", "Runa/lena"),
    ("runa3LENA", "Runa3lena"),
    ("-runa", "-Runa"),
    ("'runa", "'Runa"),
    (".runa", ".Runa"),
    ("runa-", "Runa-"),
    ("o''neil", "O''Neil"),
    ("runa--lena", "Runa--Lena"),
    ("runa.-lena", "Runa.-Lena"),
    ("runa-3RD", "Runa-3rd"),
    ("1'a", "1'A"),
    ("st.JOHN", "St.John"),
    ("paula col\xb7LELL", "Paula Col\xb7lell"),        # a middle dot is not a full stop
    ("runa-\xe9lodie", "Runa-\xc9lodie"),
    ("d'\xc9LODIE", "D'\xc9lodie"),
    ("\u4e2d\u6751 \u3055\u304f\u3089", "\u4e2d\u6751 \u3055\u304f\u3089"),  # no case to change
    ("x y z", "X Y Z"),
    ("runa ' lind", "Runa ' Lind"),
    ("ELODIE-anne o'CONNOR-smythe", "Elodie-Anne O'Connor-Smythe"),
    ("\u0391\u0398\u0397\u039d\u0391", "\u0391\u03b8\u03b7\u03bd\u03b1"),
]

problems = []
for name, expected in CASES:
    display, error = display_of(name)
    if error:
        problems.append(f"{show(name)}: expected {show(expected)}, got {error}")
    elif display != expected:
        problems.append(f"{show(name)}: expected {show(expected)}, got {show(display)}")

finish(problems, f"capitalisation ok: {len(CASES)} names")
