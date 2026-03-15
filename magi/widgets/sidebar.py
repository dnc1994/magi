from __future__ import annotations
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static
from magi.themes import THEMES, Theme


class Sidebar(Widget):
    DEFAULT_CSS = """
    Sidebar {
        width: 22;
        border-left: solid $border;
        padding: 0 1;
    }
    """

    theme: reactive[Theme] = reactive(THEMES[0])
    _uptime: reactive[int] = reactive(0)
    _votes_cast: reactive[int] = reactive(0)

    def compose(self) -> ComposeResult:
        yield Static(id="sidebar-content")

    def on_mount(self) -> None:
        self.set_interval(1.0, self._tick)
        self._refresh_content()

    def _tick(self) -> None:
        self._uptime += 1
        self._refresh_content()

    def increment_votes(self) -> None:
        self._votes_cast += 1
        self._refresh_content()

    def watch_theme(self, theme: Theme) -> None:
        if not self.is_attached:
            return
        self.styles.background = theme.background
        self._refresh_content()

    def _refresh_content(self) -> None:
        if not self.is_attached:
            return
        t = self.theme
        h = self._uptime // 3600
        m = (self._uptime % 3600) // 60
        s = self._uptime % 60
        lines = [
            f"[bold {t.accent}]SYSTEM[/]",
            f"[{t.dim}]──────────────────[/]",
            f"[{t.dim}]UPTIME [/][{t.primary}]{h:02d}:{m:02d}:{s:02d}[/]",
            f"[{t.dim}]VOTES  [/][{t.primary}]{self._votes_cast:>4d}[/]",
            "",
            f"[bold {t.accent}]THEME[/]",
            f"[{t.dim}]──────────────────[/]",
            f"[{t.primary}]{t.name}[/]",
            "",
            f"[bold {t.accent}]CONTROLS[/]",
            f"[{t.dim}]──────────────────[/]",
            f"[{t.dim}][T][/]   [{t.primary}]CYCLE THEME[/]",
            f"[{t.dim}][↵][/]   [{t.primary}]SUBMIT[/]",
            f"[{t.dim}][TAB][/] [{t.primary}]PRELOAD[/]",
            f"[{t.dim}][Q][/]   [{t.primary}]QUIT[/]",
        ]
        self.query_one("#sidebar-content", Static).update("\n".join(lines))
