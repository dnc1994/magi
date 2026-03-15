from __future__ import annotations
import random
from textual import work
from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static
from magi.themes import THEMES, Theme

# ── Timing constants ──────────────────────────────────────────────────────────
_IDLE_TELEM   = 1.5
_DELIB_TELEM  = 0.07

_IDLE_PULSE   = 1.2
_DELIB_PULSE  = 0.10

# ── Badge frame sequences ─────────────────────────────────────────────────────
_DELIB_FRAMES = [
    "[ ANALYZING...  ]",
    "[  PROCESSING   ]",
    "[ NEURAL SYNC   ]",
    "[  CALCULATING  ]",
    "[▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓]",
    "[   CRITICAL!   ]",
    "[  OVERLOADING  ]",
    "[████████████   ]",
    "[               ]",
    "[  CROSS-CHECK  ]",
    "[  VALIDATING   ]",
    "[███████████████]",
    "[               ]",
    "[  SYNC ACTIVE  ]",
]

# ── Cycling STATUS / NET values ───────────────────────────────────────────────
_STATUS_DELIB = [
    "WARNING", "CRITICAL", "OVERLOAD", "SYNC LOST",
    "MAXLOAD", "ALERT", "RECOVERING", "NOMINAL",
    "CRITICAL", "WARNING", "OVERLOAD", "ALERT",
]
_NET_DELIB = [
    "SECURE", "ENCRYPTING", "████████", "SCRAMBLED",
    "LOCKED", "ENCRYPTING", "████████", "SECURE",
]


class MagiPanel(Widget):

    class LlmComplete(Message):
        def __init__(self, computer_name: str, outcome: str | None) -> None:
            super().__init__()
            self.computer_name = computer_name
            self.outcome = outcome

    DEFAULT_CSS = """
    MagiPanel {
        width: 1fr;
        height: 100%;
        border-right: solid $border;
        padding: 0 1;
    }
    MagiPanel #title {
        height: 2;
    }
    MagiPanel #stats {
        height: 6;
    }
    MagiPanel #divider {
        height: 3;
        padding: 1 0;
    }
    MagiPanel #trace {
        height: 1fr;
    }
    MagiPanel #badge {
        height: 3;
        content-align: center middle;
        border: solid $border;
    }
    """

    theme: reactive[Theme] = reactive(THEMES[0])
    _panel_state: reactive[str] = reactive("IDLE")
    _vote_outcome: reactive[str | None] = reactive(None)

    def __init__(self, name: str, num: str, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._name = name
        self._num = num
        self._telem_timer = None
        self._pulse_timer = None
        # telemetry values
        self._cpu: float = 99.8
        self._mem: float = 847.3
        self._temp: float = 38.2
        self._sig: float = 0.000
        # animation state
        self._badge_frame: int = 0
        self._status_frame: int = 0
        self._net_frame: int = 0
        self._pulse_on: bool = True
        # LLM trace
        self._trace_buf: str = ""

    def compose(self) -> ComposeResult:
        yield Static(id="title")
        yield Static(id="stats")
        yield Static(id="divider")
        yield Static(id="trace")
        yield Static(id="badge")

    def on_mount(self) -> None:
        self._telem_timer = self.set_interval(_IDLE_TELEM, self._tick_telemetry)
        self._pulse_timer = self.set_interval(_IDLE_PULSE, self._tick_pulse)
        self._refresh_title()
        self._refresh_stats()
        self._refresh_divider()
        self._refresh_badge()

    # ── Public API ────────────────────────────────────────────────────────────

    def set_state(
        self,
        state: str,
        outcome: str | None = None,
        proposal: str | None = None,
        language: str = "EN",
    ) -> None:
        self._panel_state = state
        self._vote_outcome = outcome
        self._badge_frame = 0
        self._status_frame = 0
        self._net_frame = 0

        if self._telem_timer:
            self._telem_timer.stop()
        if self._pulse_timer:
            self._pulse_timer.stop()

        if state == "DELIBERATING":
            self._trace_buf = ""
            self.query_one("#trace", Static).update("")
            self._telem_timer = self.set_interval(_DELIB_TELEM, self._tick_telemetry)
            self._pulse_timer = self.set_interval(_DELIB_PULSE, self._tick_pulse)
            if outcome and proposal:
                self._generate_trace(proposal, outcome, language)
        elif state == "VOTED":
            # keep trace visible — generation continues until complete
            self._telem_timer = self.set_interval(_IDLE_TELEM, self._tick_telemetry)
            self._pulse_timer = self.set_interval(_IDLE_PULSE, self._tick_pulse)
        else:  # IDLE — new vote cycle starting, clear trace
            self._trace_buf = ""
            self.query_one("#trace", Static).update("")
            self._telem_timer = self.set_interval(_IDLE_TELEM, self._tick_telemetry)
            self._pulse_timer = self.set_interval(_IDLE_PULSE, self._tick_pulse)

        self._refresh_badge()

    def freeze_badge(self) -> None:
        """Stop badge pulsing: APPROVED holds bright, REJECTED holds dim."""
        if self._pulse_timer:
            self._pulse_timer.stop()
            self._pulse_timer = None
        # _pulse_on=True → bold accent for APPROVED; REJECTED ignores it (always dim)
        self._pulse_on = True
        self._refresh_badge()

    def watch_theme(self, theme: Theme) -> None:
        if not self.is_attached:
            return
        self.styles.background = theme.background
        self._refresh_title()
        self._refresh_stats()
        self._refresh_divider()
        self._refresh_trace()
        self._refresh_badge()

    # ── LLM trace worker ──────────────────────────────────────────────────────

    @work(exclusive=True)
    async def _generate_trace(self, proposal: str, outcome: str, language: str = "EN") -> None:
        from magi.llm import stream_deliberation
        async for chunk in stream_deliberation(self._name, proposal, outcome, language):
            if self._panel_state == "IDLE":
                break
            self._trace_buf += chunk
            self._refresh_trace()
        self.post_message(MagiPanel.LlmComplete(f"{self._name}-{self._num}", self._vote_outcome))

    # ── Timers ────────────────────────────────────────────────────────────────

    def _tick_telemetry(self) -> None:
        state = self._panel_state
        if state == "DELIBERATING":
            self._cpu  = round(random.uniform(42.0, 100.0), 1)
            self._mem  = round(random.uniform(490.0, 990.0), 1)
            self._temp = round(random.uniform(34.0, 97.0), 1)
            self._sig  = round(random.uniform(0.0, 0.999), 3)
            self._status_frame = (self._status_frame + 1) % len(_STATUS_DELIB)
            self._net_frame    = (self._net_frame + 1) % len(_NET_DELIB)
        else:  # IDLE or VOTED
            self._cpu  = round(random.uniform(98.5, 99.9), 1)
            self._mem  = round(random.uniform(840.0, 855.0), 1)
            self._temp = round(random.uniform(36.0, 41.0), 1)
            self._sig  = round(random.uniform(0.000, 0.005), 3)
        self._refresh_stats()

    def _tick_pulse(self) -> None:
        self._pulse_on = not self._pulse_on
        if self._panel_state == "DELIBERATING":
            self._badge_frame = (self._badge_frame + 1) % len(_DELIB_FRAMES)
        self._refresh_badge()

    # ── Rendering ─────────────────────────────────────────────────────────────

    def _refresh_trace(self) -> None:
        if not self._trace_buf:
            return
        t = self.theme
        lines = self._trace_buf.splitlines()
        visible = "\n".join(lines[-8:])
        self.query_one("#trace", Static).update(f"[{t.dim}]{visible}[/]")

    def _refresh_divider(self) -> None:
        t = self.theme
        self.query_one("#divider", Static).update(f"[{t.dim}]{'·' * 18}[/]")

    def _refresh_title(self) -> None:
        t = self.theme
        self.query_one("#title", Static).update(
            f"[bold {t.accent}]◈ {self._name}·{self._num}[/]\n"
            f"[{t.dim}]{'─' * 18}[/]"
        )

    def _refresh_stats(self) -> None:
        t = self.theme
        state = self._panel_state

        temp_color = t.accent if (state == "DELIBERATING" and self._temp > 80) else t.primary
        cpu_color  = t.accent if (state == "DELIBERATING" and self._cpu < 60)  else t.primary

        status = _STATUS_DELIB[self._status_frame] if state == "DELIBERATING" else "NOMINAL"
        net    = _NET_DELIB[self._net_frame]        if state == "DELIBERATING" else "SECURE"

        lines = [
            f"[{t.dim}]CPU [/][{cpu_color}]{self._cpu:>5.1f}%[/]",
            f"[{t.dim}]MEM [/][{t.primary}]{self._mem:>5.1f}TB[/]",
            f"[{t.dim}]TEMP[/] [{temp_color}]{self._temp:>4.1f}°C[/]",
            f"[{t.dim}]NET [/][{t.primary}]{net}[/]",
            f"[{t.dim}]SIG [/][{t.primary}]{self._sig:>5.3f}[/]",
            f"[{t.dim}]STAT[/] [{t.primary}]{status}[/]",
        ]
        self.query_one("#stats", Static).update("\n".join(lines))

    def _refresh_badge(self) -> None:
        if not self.is_attached:
            return
        t = self.theme
        state = self._panel_state

        if state == "IDLE":
            text = f"[{t.dim}][ STANDBY ][/]" if self._pulse_on else f"[{t.dim}][  ·····  ][/]"
        elif state == "DELIBERATING":
            frame = _DELIB_FRAMES[self._badge_frame]
            text = f"[bold {t.accent}]{frame}[/]" if self._pulse_on else f"[{t.dim}]{frame}[/]"
        else:  # VOTED
            if self._vote_outcome == "APPROVED":
                # Flashy: pulse bold accent ↔ primary
                text = (
                    f"[bold {t.accent}][ ✓  APPROVED  ][/]"
                    if self._pulse_on else f"[{t.primary}][ ✓  APPROVED  ][/]"
                )
            else:
                # Dimmed: always gray, no flash
                text = f"[{t.dim}][ ✗  REJECTED  ][/]"

        self.query_one("#badge", Static).update(text)
