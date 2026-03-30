"""
CipherState — pure data model for the substitution cipher.

Holds the cipher text, current decryption state, locked letters,
and undo history.  All mutation logic lives here so it can be
tested without spinning up a TUI.
"""

from __future__ import annotations

from .utils import wrap_text


class CipherState:
    def __init__(self, cipher_text: str):
        self.original = cipher_text.upper().replace("\n", "")
        self.current: list[str] = list(self.original)
        self.locked: set[str] = set()
        # Each entry: (char_a, char_b, was_a_locked, was_b_locked)
        self.undo_stack: list[tuple[str, str, bool, bool]] = []

    # ── Queries ──────────────────────────────────────────────────────

    @property
    def text(self) -> str:
        return "".join(self.current)

    @property
    def cipher_words(self) -> list[str]:
        return self.text.split(" ")

    def word_at(self, pos: int) -> str:
        """Return the word surrounding *pos*, or '' if on a space."""
        text = self.text
        if pos < 0 or pos >= len(text) or text[pos] == " ":
            return ""
        start = pos
        while start > 0 and text[start - 1] != " ":
            start -= 1
        end = pos
        while end < len(text) and text[end] != " ":
            end += 1
        return text[start:end]

    def pattern_at(self, pos: int) -> str:
        """
        Pattern for the word at *pos*: locked chars kept lowercase,
        unlocked replaced with '_'.
        """
        text = self.text
        if pos < 0 or pos >= len(text) or text[pos] == " ":
            return ""
        start = pos
        while start > 0 and text[start - 1] != " ":
            start -= 1
        end = pos
        while end < len(text) and text[end] != " ":
            end += 1
        return "".join(
            ch.lower() if ch.upper() in self.locked else "_"
            for ch in text[start:end]
        )

    # ── Mutations ────────────────────────────────────────────────────

    def swap(self, pos: int, to_ch: str) -> bool:
        """
        Swap the cipher letter at *pos* with *to_ch* (uppercase).
        Returns True if a change was made.
        """
        if pos < 0 or pos >= len(self.current):
            return False

        from_ch = self.current[pos]
        to_ch = to_ch.upper()

        if from_ch == " ":
            return False

        # Same letter → just lock it
        if from_ch == to_ch:
            if to_ch in self.locked:
                return False
            self.locked.add(to_ch)
            self.undo_stack.append((from_ch, to_ch, False, False))
            return True

        was_from_locked = from_ch in self.locked
        was_to_locked = to_ch in self.locked

        # Global swap: every from_ch ↔ to_ch
        for i in range(len(self.current)):
            if self.current[i] == from_ch:
                self.current[i] = to_ch
            elif self.current[i] == to_ch:
                self.current[i] = from_ch

        self.locked.add(to_ch)
        self.undo_stack.append((from_ch, to_ch, was_from_locked, was_to_locked))
        return True

    def undo(self) -> bool:
        """Undo the last swap.  Returns True if there was something to undo."""
        if not self.undo_stack:
            return False

        char_a, char_b, was_a_locked, was_b_locked = self.undo_stack.pop()

        for i in range(len(self.current)):
            if self.current[i] == char_a:
                self.current[i] = char_b
            elif self.current[i] == char_b:
                self.current[i] = char_a

        if was_a_locked:
            self.locked.add(char_a)
        else:
            self.locked.discard(char_a)
        if was_b_locked:
            self.locked.add(char_b)
        else:
            self.locked.discard(char_b)

        return True

    # ── Summary ──────────────────────────────────────────────────────

    def get_summary(self) -> str:
        """Final-state summary: substitution key + deciphered text."""
        lines: list[str] = []

        key_map: dict[str, str] = {}
        for orig_ch, cur_ch in zip(self.original, self.current):
            if orig_ch != " " and cur_ch != " " and orig_ch not in key_map:
                key_map[orig_ch] = cur_ch

        lines.append("")
        lines.append("=" * 60)
        lines.append("SUBSTITUTION KEY")
        lines.append("=" * 60)
        lines.append("")
        lines.append("  Cipher → Plain  Status")
        lines.append("  " + "-" * 30)
        for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            mapped = key_map.get(ch, "?")
            status = "✓ locked" if mapped in self.locked else "  (guess)"
            changed = " *" if ch != mapped else "  "
            lines.append(f"  {ch}  →  {mapped.lower()}  {changed} {status}")

        key_str = "".join(
            key_map.get(ch, "?") for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        )
        lines.append("")
        lines.append(f"  Key: {key_str}")
        lines.append(f"  Locked: {len(self.locked)}/26")

        lines.append("")
        lines.append("=" * 60)
        lines.append("DECIPHERED TEXT")
        lines.append("=" * 60)
        lines.append("")
        for line in wrap_text(self.text.lower(), 70):
            lines.append(line)
        lines.append("")

        return "\n".join(lines)
