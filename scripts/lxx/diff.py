"""Word-level diff between the Masoretic text and Tov's Hebrew retroversion."""

from __future__ import annotations

import difflib


def word_diff(masoretic: str, retroverted: str) -> str:
    """Render a word diff: [-MT only-] and {+retroversion only+}.

    The two texts are the same verse in the same language, so a word-level
    diff is meaningful. A replacement appears as [-old-]{+new+}; unchanged
    words stay plain.
    """
    old = masoretic.split()
    new = retroverted.split()
    if not old and not new:
        return ""
    if not old:
        return "{+" + " ".join(new) + "+}"
    if not new:
        return "[-" + " ".join(old) + "-]"

    parts: list[str] = []
    matcher = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            parts.extend(old[i1:i2])
        elif tag == "delete":
            parts.append("[-" + " ".join(old[i1:i2]) + "-]")
        elif tag == "insert":
            parts.append("{+" + " ".join(new[j1:j2]) + "+}")
        else:
            parts.append("[-" + " ".join(old[i1:i2]) + "-]{+" + " ".join(new[j1:j2]) + "+}")
    return " ".join(parts)
