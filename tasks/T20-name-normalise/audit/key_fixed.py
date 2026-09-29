"""X14 (G5): the duplicate key, written out by hand from the rule in G5: NFKD, lower-cased
character by character, only letters kept."""

from _audit import key_of, show
from _cmd import finish

CASES = [
    ("Sigr\xfan Gu\xf0laugsd\xf3ttir", "sigrungu\xf0laugsdottir"),    # \xf0 does not decompose
    ("\xf8yvind \xd8DEG\xc5RD", "\xf8yvind\xf8degard"),
    ("\u0141ucja Wa\u0142\u0119cka", "\u0142ucjawa\u0142ecka"),
    ("\xc6thelfl\xe6d", "\xe6thelfl\xe6d"),
    ("\xfe\xf3ra", "\xfeora"),
    ("GRO\u1e9e", "gro\xdf"),                                                # not "gross"
    ("stra\xdfe", "stra\xdfe"),
    ("\u0434\u043c\u0438\u0442\u0440\u0438\u0439 \u0428\u041e\u0421\u0422\u0410\u041a",
     "\u0434\u043c\u0438\u0442\u0440\u0438\u0438\u0448\u043e\u0441\u0442\u0430\u043a"),  # \u0439 loses its breve too
    ("\u0439\u043e\u043a\u043e", "\u0438\u043e\u043a\u043e"),                 # NFKD splits the breve off
    ("\u0391\u0398\u0397\u039d\u0391", "\u03b1\u03b8\u03b7\u03bd\u03b1"),
    ("\u0645\u062d\u0645\u062f", "\u0645\u062d\u0645\u062f"),
    ("\u4e2d\u6751 \u3055\u304f\u3089", "\u4e2d\u6751\u3055\u304f\u3089"),
    ("\uae40\ubbfc\uc218", "\u1100\u1175\u11b7\u1106\u1175\u11ab\u1109\u116e"),  # NFKD gives conjoining jamo
    ("\uff52\uff55\uff4e\uff41 \uff4c\uff49\uff4e\uff44", "runalind"),         # fullwidth letters
    ("ra\ufb01k", "rafik"),                                                      # compatibility ligatures
    ("schi\ufb00er", "schiffer"),
    ("runa\xb2 lind", "runalind"),
    ("runa lind 3rd", "runalindrd"),
    ("runa (rue) o'neil-smythe", "runarueoneilsmythe"),
    ("paula col\xb7lell", "paulacollell"),
    ("runa\u200blind", "runalind"),
    ("e\u0301lodie", "elodie"),
    ("\xc9LODIE", "elodie"),
    ("Nguy\u1ec5n", "nguyen"),
    ("\xc7elik \u015eahin", "celiksahin"),
    ("Dvo\u0159\xe1k", "dvorak"),
    ("Zo\xeb Salda\xf1a", "zoesaldana"),
    ("J.R.R. Ul-Haq", "jrrulhaq"),
]

problems = []
for name, expected in CASES:
    key, error = key_of(name)
    if error:
        problems.append(f"{show(name)}: expected key {show(expected)}, got {error}")
    elif key != expected:
        problems.append(f"{show(name)}: expected key {show(expected)}, got {show(key)}")

finish(problems, f"keys ok: {len(CASES)} names")
