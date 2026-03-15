from __future__ import annotations
from datetime import datetime
from textual.widgets import RichLog
from magi.themes import THEMES, Theme


class ActivityLog(RichLog):
    DEFAULT_CSS = """
    ActivityLog {
        height: 5;
        border-top: solid $border;
        padding: 0 1;
    }
    """

    theme = THEMES[0]

    @property
    def line_count(self) -> int:
        return len(self.lines)

    def add_entry(self, message: str) -> None:
        t = self.theme
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.write(f"[{t.dim}][{timestamp}][/] [{t.primary}]{message}[/]")

    def apply_theme(self, theme: "Theme") -> None:
        self.theme = theme
        self.styles.background = theme.background
