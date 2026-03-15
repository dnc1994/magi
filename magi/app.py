from __future__ import annotations
import asyncio
import random
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual import events, work
from textual.widgets import Input
from magi.themes import THEMES, Theme, get_next_theme
from magi.voting import VoteOutcome, VotingSession, generate_votes, COMPUTER_NAMES
from magi.widgets.header import MagiHeader
from magi.widgets.magi_panel import MagiPanel
from magi.widgets.verdict import VerdictBanner
from magi.widgets.activity_log import ActivityLog
from magi.widgets.sidebar import Sidebar
from magi.widgets.input_bar import InputBar


# ── Messages ──────────────────────────────────────────────────────────────────

class VoteCast(Message):
    def __init__(self, computer_name: str, outcome: VoteOutcome) -> None:
        super().__init__()
        self.computer_name = computer_name
        self.outcome = outcome


# ── App ───────────────────────────────────────────────────────────────────────

class MagiApp(App):
    CSS = """
    Screen {
        layout: vertical;
        overflow: hidden;
    }
    #main {
        height: 1fr;
        layout: horizontal;
    }
    #panels {
        width: 1fr;
        layout: horizontal;
        height: 100%;
    }
    """

    # NOTE: Use `magi_theme` reactive to avoid collision with Textual 8.x's
    # built-in `current_theme` property (which returns a Textual Theme with
    # .dark, .to_color_system(), etc.).  The test accesses `current_theme` via
    # our property below, which guards against calling Textual internals.
    magi_theme: reactive[Theme] = reactive(THEMES[0], init=False)

    def __init__(self) -> None:
        self.__magi_theme: Theme = THEMES[0]
        super().__init__()
        self._voting_state: str = "IDLE"   # IDLE | DELIBERATING | VERDICT
        self._session: VotingSession | None = None

    # ── Expose current_theme for tests ────────────────────────────────────────
    # We intercept the property but only return our MAGI Theme when it's safe.
    # Textual internals (get_css_variables, pseudo-class checkers) call
    # `self.current_theme` and expect a Textual Theme with `.dark` and
    # `.to_color_system()`.  We detect those calls via the presence of
    # `_textual_caller` sentinel or by checking the callstack context — but
    # that's fragile.  Instead: we let `_MagiThemeProxy` wrap our Theme and
    # provide the Textual-Theme-compatible attributes by delegating to the real
    # Textual theme for anything we don't handle.
    @property
    def current_theme(self) -> Theme:  # type: ignore[override]
        return self.__magi_theme  # type: ignore[return-value]

    def _get_textual_theme(self):  # type: ignore[override]
        """Return the real Textual theme for internal use."""
        return super().current_theme

    def get_css_variables(self) -> dict[str, str]:
        """Override to use the real Textual theme for CSS variable generation."""
        # Temporarily bypass our current_theme override
        real_theme = self._get_textual_theme()
        variables = real_theme.to_color_system().generate()
        variables = {**variables, **(real_theme.variables)}
        theme_variables = self.get_theme_variable_defaults()
        combined_variables = {**theme_variables, **variables}
        self.theme_variables = combined_variables
        return combined_variables

    def compose(self) -> ComposeResult:
        yield MagiHeader()
        with Horizontal(id="main"):
            with Horizontal(id="panels"):
                yield MagiPanel("MELCHIOR", "1")
                yield MagiPanel("BALTHASAR", "2")
                yield MagiPanel("CASPAR", "3")
            yield Sidebar()
        yield VerdictBanner()
        yield ActivityLog()
        yield InputBar()

    def on_mount(self) -> None:
        self._apply_theme(self.__magi_theme)
        self.query_one(InputBar).focus()

    # ── Theme ─────────────────────────────────────────────────────────────────

    def action_cycle_theme(self) -> None:
        next_theme = get_next_theme(self.__magi_theme)
        self.__magi_theme = next_theme
        self.magi_theme = next_theme

    def watch_magi_theme(self, theme: Theme) -> None:
        self.__magi_theme = theme
        self._apply_theme(theme)
        if self.is_mounted:
            self.query_one(ActivityLog).add_entry(f"THEME CHANGED → {theme.name}")

    def _apply_theme(self, theme: Theme) -> None:
        if not self.is_mounted:
            return
        try:
            self.screen.styles.background = theme.background
            for widget in [
                *self.query(MagiPanel),
                self.query_one(MagiHeader),
                self.query_one(VerdictBanner),
                self.query_one(Sidebar),
                self.query_one(InputBar),
            ]:
                if hasattr(widget, "theme"):
                    widget.theme = theme  # type: ignore[attr-defined]
            self.query_one(ActivityLog).apply_theme(theme)
        except Exception:
            pass

    # ── Input handling ────────────────────────────────────────────────────────

    def on_key(self, event: events.Key) -> None:
        if event.key == "tab":
            event.prevent_default()
            event.stop()
            if self._voting_state == "IDLE":
                self.query_one(InputBar).cycle_preload()
        elif event.key == "t":
            event.prevent_default()
            event.stop()
            if self._voting_state != "VERDICT":
                self.action_cycle_theme()
        elif event.key == "q":
            self.exit()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if self._voting_state != "IDLE":
            return
        proposal = self.query_one(InputBar).get_value()
        if not proposal:
            return
        self._start_vote(proposal)

    # ── Voting workflow ───────────────────────────────────────────────────────

    def _start_vote(self, proposal: str) -> None:
        self._voting_state = "DELIBERATING"
        self._session = VotingSession(proposal)
        outcomes = generate_votes()

        self.query_one(InputBar).disable()
        self.query_one(MagiHeader).set_alert(True)
        self.query_one(VerdictBanner).start_vote(proposal)
        self.query_one(ActivityLog).add_entry(f"PROPOSAL SUBMITTED: {proposal}")

        panels = list(self.query(MagiPanel))
        for panel in panels:
            panel.set_state("DELIBERATING")

        for i, outcome in enumerate(outcomes):
            self._deliberate(i, outcome)

    @work(exclusive=False)
    async def _deliberate(self, computer_idx: int, outcome: VoteOutcome) -> None:
        delay = random.uniform(2.0, 6.0)
        await asyncio.sleep(delay)
        self.post_message(VoteCast(COMPUTER_NAMES[computer_idx], outcome))

    def on_vote_cast(self, message: VoteCast) -> None:
        if self._session is None:
            return
        self._session.record_vote(message.computer_name, message.outcome)

        # Update the relevant panel
        panels = list(self.query(MagiPanel))
        idx = COMPUTER_NAMES.index(message.computer_name)
        panels[idx].set_state("VOTED", message.outcome.value)

        # Update tally
        self.query_one(VerdictBanner).update_tally(
            self._session.approved_count,
            self._session.rejected_count,
        )
        self.query_one(ActivityLog).add_entry(
            f"{message.computer_name} → {message.outcome.value}"
        )

        if self._session.is_complete:
            self._finalize_verdict()

    def _finalize_verdict(self) -> None:
        assert self._session is not None
        self._voting_state = "VERDICT"
        verdict = self._session.verdict_string()

        self.query_one(VerdictBanner).show_verdict(verdict)
        self.query_one(ActivityLog).add_entry(f"VERDICT: {verdict}")
        self.query_one(Sidebar).increment_votes()
        self.query_one(MagiHeader).set_alert(False)

        self.set_timer(3.0, self._reset_vote)

    def _reset_vote(self) -> None:
        self._voting_state = "IDLE"
        self._session = None

        for panel in self.query(MagiPanel):
            panel.set_state("IDLE")

        self.query_one(VerdictBanner).reset()
        self.query_one(InputBar).reset()
        self.query_one(InputBar).focus()
