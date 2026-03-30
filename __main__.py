"""
SubCiph — Textual TUI

Controls:
  Arrow keys / Home / End  — move cursor
  A-Z                      — swap the cipher letter under the cursor with the typed letter
  Backspace                — undo last swap
  q / Ctrl+C               — quit

Usage:
  python -m subciph [ciphertext_file] (-w wordlist)
"""

from __future__ import annotations

import argparse
import sys

from .utils import DEFAULT_TEXT, find_default_wordlist, load_wordlist
from .app import SubstitutionSolver


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SubCiph — Textual TUI",
    )
    parser.add_argument(
        "ciphertext",
        nargs="?",
        help="Path to ciphertext file (uses built-in demo text if omitted)",
    )
    parser.add_argument(
        "-w",
        "--wordlist",
        help="Path to wordlist file, one word per line "
        "(defaults to /usr/share/dict/words if available)",
    )
    args = parser.parse_args()

    # Load ciphertext
    if args.ciphertext:
        with open(args.ciphertext) as f:
            text = f.read().strip()
    else:
        text = DEFAULT_TEXT

    # Load wordlist
    wl_path = args.wordlist or find_default_wordlist()
    wordlist: dict[int, list[str]] = {}
    if wl_path:
        try:
            wordlist = load_wordlist(wl_path)
            total = sum(len(v) for v in wordlist.values())
            print(f"Loaded {total} words from {wl_path}")
        except FileNotFoundError:
            print(f"Warning: wordlist not found at {wl_path}", file=sys.stderr)
    else:
        print(
            "No wordlist found. Use -w/--wordlist to specify one.",
            file=sys.stderr,
        )

    app = SubstitutionSolver(text, wordlist=wordlist)
    app.run()
    print(app.state.get_summary())


if __name__ == "__main__":
    main()
