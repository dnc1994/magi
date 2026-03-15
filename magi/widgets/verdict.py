from __future__ import annotations
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static
from magi.themes import THEMES, Theme


class VerdictBanner(Widget):
    DEFAULT_CSS = """
    VerdictBanner {
        height: 3;
        border-top: solid $border;
        border-bottom: solid $border;
        padding: 0 1;
        content-align: center middle;
    }
    """

    theme: reactive[Theme] = reactive(THEMES[0])

    def compose(self) -> ComposeResult:
        yield Static(id="verdict-text")

    def on_mount(self) -> None:
        self.reset()

    def reset(self) -> None:
        t = self.theme
        self.query_one("#verdict-text", Static).update(
            f"[{t.dim}]◈ MAGI VOTING SYSTEM READY — SUBMIT A PROPOSAL TO BEGIN ◈[/]"
        )

    def start_vote(self, proposal: str) -> None:
        t = self.theme
        self.query_one("#verdict-text", Static).update(
            f"[{t.primary}]PROPOSAL:[/] [{t.accent}]{proposal}[/] "
            f"[{t.dim}]— AWAITING VOTES...[/]"
        )

    def update_tally(self, approved: int, rejected: int) -> None:
        t = self.theme
        pending = 3 - approved - rejected
        self.query_one("#verdict-text", Static).update(
            f"[{t.accent}]✓ {approved} APPROVE[/]  [{t.dim}]·[/]  "
            f"[bold red]✗ {rejected} REJECT[/]  [{t.dim}]·[/]  "
            f"[{t.dim}]⟳ {pending} PENDING[/]"
        )

    def show_verdict(self, verdict: str) -> None:
        t = self.theme
        prefix = "⚡" if "UNANIMOUS" in verdict else "◈"
        self.query_one("#verdict-text", Static).update(
            f"[bold {t.accent}]{prefix} VERDICT: {verdict} {prefix}[/]"
        )

    def watch_theme(self, theme: Theme) -> None:
        if not self.is_attached:
            return
        self.styles.background = theme.background
        self.reset()
