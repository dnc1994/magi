from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    name: str
    primary: str    # main text color
    accent: str     # highlight / vote badge color
    background: str # terminal background
    border: str     # panel border color
    dim: str        # secondary / dim text
    scanlines: bool # amber-only decorative hint


THEMES: list[Theme] = [
    Theme(
        name="AMBER",
        primary="#c8740a",
        accent="#ffaa22",
        background="#0d0800",
        border="#b8640a",
        dim="#886004",
        scanlines=True,
    ),
    Theme(
        name="BLUE",
        primary="#4499cc",
        accent="#00aaff",
        background="#000810",
        border="#004488",
        dim="#2266aa",
        scanlines=False,
    ),
    Theme(
        name="RED ALERT",
        primary="#cc4444",
        accent="#ff4444",
        background="#0d0000",
        border="#440000",
        dim="#882222",
        scanlines=False,
    ),
]


def get_next_theme(current: Theme) -> Theme:
    idx = THEMES.index(current)
    return THEMES[(idx + 1) % len(THEMES)]
