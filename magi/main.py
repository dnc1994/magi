from __future__ import annotations
import shutil
import sys


MIN_COLS = 120
MIN_ROWS = 30


def main() -> None:
    cols, rows = shutil.get_terminal_size()
    if cols < MIN_COLS or rows < MIN_ROWS:
        print(
            f"ERROR: Terminal too small ({cols}×{rows}).\n"
            f"Minimum required: {MIN_COLS}×{MIN_ROWS}.\n"
            f"Please resize your terminal and try again.",
            file=sys.stderr,
        )
        sys.exit(1)

    from magi.app import MagiApp
    MagiApp().run()


if __name__ == "__main__":
    main()
