"""CipherPanel — left panel showing the cipher text with cursor."""

from __future__ import annotations

from textual.reactive import reactive
from textual.widget import Widget
from rich.text import Text

from ..model import CipherState
from ..utils import wrap_text

WRAP_WIDTH = 70


class CipherPanel(Widget):
    """Displays the cipher text, cursor position, and locked-letter highlights."""

    DEFAULT_CSS = """
    CipherPanel {
        width: 3fr;
        height: 100%;
        padding: 1 2;
        border: solid $primary;
        overflow-y: auto;
    }
    """

    cursor_pos: reactive[int] = reactive(0)

    def __init__(self, state: CipherState, **kwargs):
        super().__init__(**kwargs)
        self.state = state

    # ── Rendering ────────────────────────────────────────────────────

    def render(self) -> Text:
        text = self.state.text
        lines = wrap_text(text, WRAP_WIDTH)

        result = Text()
        flat_idx = 0

        for line_no, line in enumerate(lines):
            for ch in line:
                if flat_idx == self.cursor_pos:
                    style = "black on cyan"
                elif ch.upper() in self.state.locked and ch != " ":
                    style = "bold white on rgb(60,60,60)"
                elif ch == " ":
                    style = "dim"
                else:
                    style = "bright_yellow"
                result.append("·" if ch == " " else ch.lower(), style=style)
                flat_idx += 1
            if line_no < len(lines) - 1:
                result.append("\n")
                flat_idx += 1  # consumed space from word-wrap

        return result

    # ── Line layout (for cursor navigation) ──────────────────────────

    def _get_line_layout(self) -> tuple[list[tuple[int, int]], set[int]]:
        """
        Returns
        -------
        lines_ranges : list of (start, end) flat indices per display line
        consumed     : set of flat positions that are wrap-consumed spaces
        """
        lines = wrap_text(self.state.text, WRAP_WIDTH)
        lines_ranges: list[tuple[int, int]] = []
        consumed: set[int] = set()
        flat_idx = 0
        for line_no, line in enumerate(lines):
            line_start = flat_idx
            flat_idx += len(line)
            lines_ranges.append((line_start, flat_idx - 1))
            if line_no < len(lines) - 1:
                consumed.add(flat_idx)
                flat_idx += 1
        return lines_ranges, consumed

    def clamp_cursor(self, pos: int, direction: int = 1) -> int:
        """Skip consumed (invisible) spaces when moving the cursor."""
        _, consumed = self._get_line_layout()
        max_pos = len(self.state.current) - 1
        while pos in consumed:
            pos += direction
        return max(0, min(max_pos, pos))
