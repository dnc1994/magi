from __future__ import annotations
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static
from magi.themes import THEMES, Theme

_VERDICT_PULSE = 0.5
_BAR = "═" * 44


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

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._verdict_timer = None
        self._pulse_on: bool = True
        self._verdict_text: str = ""
        self._proposal: str = ""
        self._is_unanimous: bool = False
        self._is_approved: bool = True

    def compose(self) -> ComposeResult:
        yield Static(id="verdict-text")

    def on_mount(self) -> None:
        self.reset()

    def reset(self) -> None:
        if self._verdict_timer:
            self._verdict_timer.stop()
            self._verdict_timer = None
        self.styles.height = 3
        t = self.theme
        self.query_one("#verdict-text", Static).update(
            f"[{t.dim}]◈ MAGI VOTING SYSTEM READY — SUBMIT A PROPOSAL TO BEGIN ◈[/]"
        )

    def start_vote(self, proposal: str) -> None:
        self._proposal = proposal
        t = self.theme
        self.query_one("#verdict-text", Static).update(
            f"[{t.primary}]PROPOSAL:[/] [{t.accent}]{proposal}[/] "
            f"[{t.dim}]— AWAITING VOTES...[/]"
        )

    def update_tally(self, approved: int, rejected: int) -> None:
        t = self.theme
        pending = 3 - approved - rejected
        self.query_one("#verdict-text", Static).update(
            f"[bold {t.accent}]✓ {approved} APPROVE[/]  [{t.dim}]·[/]  "
            f"[{t.dim}]✗ {rejected} REJECT[/]  [{t.dim}]·[/]  "
            f"[{t.dim}]⟳ {pending} PENDING[/]"
        )

    def freeze(self) -> None:
        """Stop pulsing but keep verdict text and expanded height."""
        if self._verdict_timer:
            self._verdict_timer.stop()
            self._verdict_timer = None
        self._pulse_on = True
        self._render_verdict()

    def show_verdict(self, verdict: str) -> None:
        self._verdict_text = verdict
        self._is_unanimous = "UNANIMOUS" in verdict
        self._is_approved = "APPROV" in verdict
        self._pulse_on = True
        self.styles.height = 6
        self._render_verdict()
        self._verdict_timer = self.set_interval(_VERDICT_PULSE, self._tick_verdict)

    def _tick_verdict(self) -> None:
        self._pulse_on = not self._pulse_on
        self._render_verdict()

    def _render_verdict(self) -> None:
        t = self.theme
        prefix = "⚡⚡⚡" if self._is_unanimous else "◈◈◈"
        bar = f"[{t.dim}]{_BAR}[/]"
        proposal_line = f"[{t.dim}]PROPOSAL:[/] [{t.primary}]{self._proposal}[/]"
        if self._is_approved:
            # Flashy: pulse bold accent ↔ primary
            mid = (
                f"[bold {t.accent}]  {prefix}  {self._verdict_text}  {prefix}  [/]"
                if self._pulse_on else
                f"[{t.primary}]  {prefix}  {self._verdict_text}  {prefix}  [/]"
            )
        else:
            # Rejected: pulse primary ↔ dim
            mid = (
                f"[{t.primary}]  {prefix}  {self._verdict_text}  {prefix}  [/]"
                if self._pulse_on else
                f"[{t.dim}]  {prefix}  {self._verdict_text}  {prefix}  [/]"
            )
        self.query_one("#verdict-text", Static).update(f"{proposal_line}\n{bar}\n{mid}\n{bar}")

    def watch_theme(self, theme: Theme) -> None:
        if not self.is_attached:
            return
        self.styles.background = theme.background
        if self._verdict_text:
            self._render_verdict()
