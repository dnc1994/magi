from __future__ import annotations
from datetime import datetime
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static
from magi.themes import THEMES, Theme


class MagiHeader(Widget):
    DEFAULT_CSS = """
    MagiHeader {
        height: 1;
        padding: 0 1;
    }
    MagiHeader Static {
        width: 1fr;
    }
    """

    theme: reactive[Theme] = reactive(THEMES[0])
    _alert: reactive[bool] = reactive(False)
    _clock: reactive[str] = reactive("")

    def compose(self) -> ComposeResult:
        yield Static(id="header-left")
        yield Static(id="header-right")

    def on_mount(self) -> None:
        self.set_interval(1.0, self._tick_clock)
        self._tick_clock()
        self._refresh_content()

    def _tick_clock(self) -> None:
        self._clock = datetime.now().strftime("%Y.%m.%d  %H:%M:%S")
        self._refresh_content()

    def set_alert(self, alert: bool) -> None:
        self._alert = alert
        self._refresh_content()

    def watch_theme(self, theme: Theme) -> None:
        self.styles.background = theme.background
        self._refresh_content()

    def _refresh_content(self) -> None:
        if not self.is_attached:
            return
        theme = self.theme
        status = f"[bold {theme.accent}]⚠ ALERT[/]" if self._alert else f"[{theme.dim}]NORMAL[/]"
        left = f"[bold {theme.accent}]◈ MAGI SYSTEM[/] [{theme.primary}]· NERV HQ · TOKYO-3[/]"
        right = f"[{theme.dim}]{self._clock}[/]  STATUS: {status}"
        self.query_one("#header-left", Static).update(left)
        self.query_one("#header-right", Static).update(right)
