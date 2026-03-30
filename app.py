"""SubCiph — Textual TUI app"""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Footer, Header, Static

from .model import CipherState
from .widgets.cipher_panel import CipherPanel
from .widgets.word_panel import WordPanel


class SubstitutionSolver(App):
    """Main application: wires key events to CipherState and refreshes widgets."""

    CSS = """
    Screen {
        layout: horizontal;
    }
    #status {
        dock: bottom;
        height: 3;
        padding: 0 2;
        background: $surface;
        border-top: solid $primary;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("left", "cursor_left", "←", show=False),
        Binding("right", "cursor_right", "→", show=False),
        Binding("up", "cursor_up", "↑", show=False),
        Binding("down", "cursor_down", "↓", show=False),
        Binding("home", "cursor_home", "Home", show=False),
        Binding("end", "cursor_end", "End", show=False),
        Binding("backspace", "undo", "Undo"),
    ]

    def __init__(
        self,
        cipher_text: str,
        wordlist: dict[int, list[str]] | None = None,
    ):
        super().__init__()
        self.state = CipherState(cipher_text)
        self.wordlist = wordlist or {}

    # ── Compose / Mount ──────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Horizontal():
            yield CipherPanel(self.state, id="cipher")
            yield WordPanel(id="words")
        yield Static("", id="status")

    def on_mount(self) -> None:
        wp = self.query_one(WordPanel)
        wp.set_cipher_words(self.state.cipher_words)
        wp.set_wordlist(self.wordlist)
        self._refresh_all()

    # ── Refresh helpers ──────────────────────────────────────────────

    def _refresh_all(self) -> None:
        self.query_one(CipherPanel).refresh()
        self._refresh_word_panel()
        self._refresh_status()

    def _refresh_word_panel(self) -> None:
        cp = self.query_one(CipherPanel)
        wp = self.query_one(WordPanel)
        wp.word = self.state.word_at(cp.cursor_pos)
        wp.pattern = self.state.pattern_at(cp.cursor_pos)
        wp.refresh()

    def _refresh_status(self) -> None:
        cp = self.query_one(CipherPanel)
        pos = cp.cursor_pos
        ch = self.state.current[pos] if 0 <= pos < len(self.state.current) else "?"
        orig = self.state.original[pos] if 0 <= pos < len(self.state.original) else "?"
        self.query_one("#status", Static).update(
            f" Pos: {pos}  |  Original: {orig}  →  Current: {ch}  |  "
            f"Locked: {len(self.state.locked)}/26  |  "
            f"Undo stack: {len(self.state.undo_stack)}  |  "
            f"[A-Z] swap  [Backspace] undo  [Q] quit"
        )

    # ── Cursor movement ──────────────────────────────────────────────

    def action_cursor_left(self) -> None:
        cp = self.query_one(CipherPanel)
        new = max(0, cp.cursor_pos - 1)
        cp.cursor_pos = cp.clamp_cursor(new, direction=-1)
        self._refresh_all()

    def action_cursor_right(self) -> None:
        cp = self.query_one(CipherPanel)
        new = min(len(self.state.current) - 1, cp.cursor_pos + 1)
        cp.cursor_pos = cp.clamp_cursor(new, direction=1)
        self._refresh_all()

    def action_cursor_up(self) -> None:
        cp = self.query_one(CipherPanel)
        lines_ranges, _ = cp._get_line_layout()
        cur = cp.cursor_pos
        for idx, (start, end) in enumerate(lines_ranges):
            if start <= cur <= end:
                col = cur - start
                if idx > 0:
                    prev_start, prev_end = lines_ranges[idx - 1]
                    cp.cursor_pos = cp.clamp_cursor(
                        min(prev_start + col, prev_end), direction=-1
                    )
                break
        self._refresh_all()

    def action_cursor_down(self) -> None:
        cp = self.query_one(CipherPanel)
        lines_ranges, _ = cp._get_line_layout()
        cur = cp.cursor_pos
        for idx, (start, end) in enumerate(lines_ranges):
            if start <= cur <= end:
                col = cur - start
                if idx < len(lines_ranges) - 1:
                    next_start, next_end = lines_ranges[idx + 1]
                    cp.cursor_pos = cp.clamp_cursor(
                        min(next_start + col, next_end), direction=1
                    )
                break
        self._refresh_all()

    def action_cursor_home(self) -> None:
        self.query_one(CipherPanel).cursor_pos = 0
        self._refresh_all()

    def action_cursor_end(self) -> None:
        self.query_one(CipherPanel).cursor_pos = len(self.state.current) - 1
        self._refresh_all()

    # ── Undo ─────────────────────────────────────────────────────────

    def action_undo(self) -> None:
        if not self.state.undo():
            self.bell()
            return
        wp = self.query_one(WordPanel)
        wp.set_cipher_words(self.state.cipher_words)
        self._refresh_all()

    # ── Key input (letter swaps) ─────────────────────────────────────

    def on_key(self, event) -> None:
        key = event.character
        if not (key and key.isalpha() and len(key) == 1):
            return

        event.prevent_default()
        event.stop()

        cp = self.query_one(CipherPanel)
        if self.state.swap(cp.cursor_pos, key):
            self.query_one(WordPanel).set_cipher_words(self.state.cipher_words)
            self._refresh_all()
