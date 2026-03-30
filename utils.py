"""
Utility functions and constants for the cipher solver.
Pure functions with no TUI dependency.
"""

from __future__ import annotations

import os


def load_wordlist(path: str) -> dict[int, list[str]]:
    """
    Load a wordlist file (one word per line) and group by length.
    Words are stored lowercase, deduplicated, in order of first appearance.
    """
    by_length: dict[int, list[str]] = {}
    with open(path) as f:
        for raw in f:
            w = raw.strip().lower()
            if not w or not w.isalpha():
                continue
            by_length.setdefault(len(w), []).append(w)

    # Deduplicate while preserving order
    for k in by_length:
        seen: set[str] = set()
        deduped: list[str] = []
        for w in by_length[k]:
            if w not in seen:
                seen.add(w)
                deduped.append(w)
        by_length[k] = deduped

    return by_length


def wrap_text(text: str, width: int) -> list[str]:
    """Word-wrap *text* to *width* columns."""
    lines: list[str] = []
    current_line = ""
    for word in text.split(" "):
        if not current_line:
            current_line = word
        elif len(current_line) + 1 + len(word) <= width:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def find_default_wordlist() -> str | None:
    """Return the first system wordlist path that exists, or None."""
    candidates = [
        "/usr/share/dict/words",
        "/usr/share/dict/american-english",
        "/usr/share/dict/british-english",
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


DEFAULT_TEXT = (
    "T AUDIOF STRLIOE IH T STALESTAIRTC SNMEC NG T FEOEDTC "
    "RNSYUAIOF STRLIOEIA IH T ALENDEAIRTC MEBIRE ALTA "
    "STOIYUCTAEH HWSPNCH RNOATIOEM NO T HADIYNG ATYE AUDIOF "
    "STRLIOEH TDE ONA IOAEOMEM TH T YDTRAIRTC RNSYUAIOF "
    "AERLONCNFWPUA DTALED TH T FEOEDTC SNMEC NG T RNSYUAIOF "
    "STRLIOETOWALIOF GDNS TO TMBTOREMHUYEDRNSYUAED AN T "
    "STALESTAIRITO VIAL T YEORIC TOM YTYED IA IH PECIEBEM "
    "ALTAIG T YDNPCES RTO PE HNCBEM PW TO TCFNDIALS ALEDE "
    "E IHAH T AUDIOF STRLIOEALTA HNCBEH ALE YDNPCES IOMEEM "
    "ALIH IH ALE HATAESEOA NG ALE RLUDRLAUDIOFALEHIH "
    "GUDALEDSNDE IA IH KONVO ALTA EBEDWALIOF ALTA RTO PE "
    "RNSYUAEMNO NALED SNMECH NG RNSYUATAINO KONVO AN UH "
    "ANMTW HURL TH T DTS STRLIOERNOVTWH FTSE NG CIGE "
    "RECCUCTD TUANSTAT CTSPMT RTCRUCUH ND TOWYDNFDTSSIOF "
    "CTOFUTFE RTO PE RNSYUAEM NO T AUDIOF STRLIOE HIOERAUDIOF "
    "STRLIOEH TDE ETHW AN TOTCWQE STALESTAIRTCCW TOM "
    "TDEPECIEBEM AN PE TH YNVEDGUC TH TOW NALED SNMEC NG "
    "RNSYUATAINOALE AUDIOF STRLIOE IH ALE SNHA RNSSNOCW UHEM "
    "SNMEC IO RNSYCE IAW ALENDWSTOW AWYEH NG AUDIOF STRLIOEH "
    "TDE UHEM AN MEGIOE RNSYCE IAW RCTHHEHHURL TH MEAEDSIOIHAIR "
    "AUDIOF STRLIOEH YDNPTPICIHAIR AUDIOF STRLIOEHONOMEAEDSIOIHAIR "
    "AUDIOF STRLIOEH XUTOAUS AUDIOF STRLIOEH HWSSEADIR"
    "AUDIOF STRLIOEH TOM TCAEDOTAIOF AUD"
)
