"""WordPanel — right panel showing cipher-word frequencies and dictionary matches."""

from __future__ import annotations

from collections import Counter

from textual.reactive import reactive
from textual.widget import Widget
from rich.text import Text


class WordPanel(Widget):
    """Shows common cipher words and English dictionary matches for the cursor word."""

    DEFAULT_CSS = """
    WordPanel {
        width: 1fr;
        height: 100%;
        padding: 1 2;
        border: solid $accent;
        overflow-y: auto;
    }
    """

    word: reactive[str] = reactive("")
    pattern: reactive[str] = reactive("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cipher_words: list[str] = []
        self._wordlist: dict[int, list[str]] = {}

    def set_cipher_words(self, words: list[str]) -> None:
        self._cipher_words = words

    def set_wordlist(self, wordlist: dict[int, list[str]]) -> None:
        self._wordlist = wordlist

    # ── Rendering ────────────────────────────────────────────────────

    @staticmethod
    def _matches_pattern(word: str, pat: str) -> bool:
        if len(word) != len(pat):
            return False
        return all(pch == "_" or wch == pch for wch, pch in zip(word, pat))

    def render(self) -> Text:
        result = Text()
        result.append("Word Helper\n", style="bold underline")
        result.append("Selected: ", style="dim")
        result.append(f"{self.word.lower()}\n", style="bold cyan")
        result.append(f"Pattern:  {self.pattern}\n", style="dim")
        result.append(f"Length:   {len(self.word)}\n\n", style="dim")

        wlen = len(self.word)
        if wlen == 0:
            result.append("(move cursor to a word)", style="dim italic")
            return result

        self._render_cipher_words(result, wlen)
        self._render_english_words(result, wlen)

        return result

    def _render_cipher_words(self, result: Text, wlen: int) -> None:
        same_len = [w for w in self._cipher_words if len(w) == wlen]
        counts = Counter(same_len).most_common(15)
        if not counts:
            return

        result.append(f"Cipher words (len {wlen}):\n", style="bold")
        selected = self.word.upper()

        for w, c in counts:
            if w == selected:
                result.append(f"▸ {w.lower()} ", style="bold cyan")
            else:
                result.append(f"  {w.lower()} ", style="bright_yellow")
            result.append(f"×{c}\n", style="dim")

    def _render_english_words(self, result: Text, wlen: int) -> None:
        candidates = self._wordlist.get(wlen, [])
        pat = self.pattern

        if pat and any(ch != "_" for ch in pat):
            matching = [w for w in candidates if self._matches_pattern(w, pat)]
            result.append(f"\nMatching \"{pat}\":\n", style="bold")
            if matching:
                for w in matching[:20]:
                    result.append(f"  {w}\n", style="bright_green")
                if len(matching) > 20:
                    result.append(
                        f"  ... +{len(matching) - 20} more\n", style="dim"
                    )
            else:
                result.append("  (no matches)\n", style="dim italic")
        else:
            result.append(f"\nEnglish (len {wlen}):\n", style="bold")
            if candidates:
                for w in candidates[:15]:
                    result.append(f"  {w}\n", style="bright_green")
                if len(candidates) > 15:
                    result.append(
                        f"  ... +{len(candidates) - 15} more\n", style="dim"
                    )
            else:
                result.append("  (no words loaded)\n", style="dim italic")
