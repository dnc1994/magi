from __future__ import annotations
import random
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static
from magi.themes import THEMES, Theme

# Telemetry update interval in seconds: slow in IDLE, fast in DELIBERATING
_SLOW_TICK = 2.5
_FAST_TICK = 0.4
_PULSE_TICK = 0.55


class MagiPanel(Widget):
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
    MagiPanel #telemetry {
        height: 1fr;
    }
    MagiPanel #badge {
        height: 3;
        content-align: center middle;
        border: solid $border;
    }
    """

    theme: reactive[Theme] = reactive(THEMES[0])
    _cpu: reactive[float] = reactive(99.8)
    _mem: reactive[float] = reactive(847.3)
    _temp: reactive[float] = reactive(38.2)
    _sig: reactive[float] = reactive(0.000)
    _panel_state: reactive[str] = reactive("IDLE")  # IDLE | DELIBERATING | VOTED
    _vote_outcome: reactive[str | None] = reactive(None)
    _pulse: reactive[bool] = reactive(True)

    def __init__(self, name: str, num: str, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._name = name
        self._num = num
        self._telem_timer = None

    def compose(self) -> ComposeResult:
        yield Static(id="title")
        yield Static(id="telemetry")
        yield Static(id="badge")

    def on_mount(self) -> None:
        self._telem_timer = self.set_interval(_SLOW_TICK, self._tick_telemetry)
        self.set_interval(_PULSE_TICK, self._tick_pulse)
        self._refresh_title()
        self._refresh_telemetry()
        self._refresh_badge()

    # ── Public API ──────────────────────────────────────────────────────────

    def set_state(self, state: str, outcome: str | None = None) -> None:
        """Transition panel to IDLE / DELIBERATING / VOTED."""
        self._panel_state = state
        self._vote_outcome = outcome
        if state == "DELIBERATING":
            if self._telem_timer:
                self._telem_timer.stop()
            self._telem_timer = self.set_interval(_FAST_TICK, self._tick_telemetry)
        elif state in ("IDLE", "VOTED"):
            if self._telem_timer:
                self._telem_timer.stop()
            self._telem_timer = self.set_interval(_SLOW_TICK, self._tick_telemetry)
        self._refresh_badge()

    def watch_theme(self, theme: Theme) -> None:
        if not self.is_attached:
            return
        self.styles.background = theme.background
        self._refresh_title()
        self._refresh_telemetry()
        self._refresh_badge()

    # ── Timers ───────────────────────────────────────────────────────────────

    def _tick_telemetry(self) -> None:
        self._cpu = round(random.uniform(99.1, 99.9), 1)
        self._mem = round(random.uniform(840.0, 855.0), 1)
        self._temp = round(random.uniform(36.0, 41.0), 1)
        self._sig = round(random.uniform(0.000, 0.005), 3)
        self._refresh_telemetry()

    def _tick_pulse(self) -> None:
        if self._panel_state == "DELIBERATING":
            self._pulse = not self._pulse
            self._refresh_badge()

    # ── Rendering ────────────────────────────────────────────────────────────

    def _refresh_title(self) -> None:
        t = self.theme
        self.query_one("#title", Static).update(
            f"[bold {t.accent}]◈ {self._name}·{self._num}[/]\n"
            f"[{t.dim}]{'─' * 18}[/]"
        )

    def _refresh_telemetry(self) -> None:
        t = self.theme
        rows = [
            ("CPU", f"{self._cpu:>5.1f}%"),
            ("MEM", f"{self._mem:>5.1f}TB"),
            ("TEMP", f"{self._temp:>4.1f}°C"),
            ("NET", "SECURE"),
            ("SIG", f"{self._sig:>5.3f}"),
        ]
        lines = [f"[{t.dim}]{k:<4}[/] [{t.primary}]{v}[/]" for k, v in rows]
        self.query_one("#telemetry", Static).update("\n".join(lines))

    def _refresh_badge(self) -> None:
        if not self.is_attached:
            return
        t = self.theme
        state = self._panel_state
        if state == "IDLE":
            text = f"[{t.dim}][ STANDBY ][/]"
        elif state == "DELIBERATING":
            if self._pulse:
                text = f"[bold {t.accent}][ ANALYZING... ][/]"
            else:
                text = f"[{t.dim}][              ][/]"
        else:  # VOTED
            if self._vote_outcome == "APPROVED":
                text = f"[bold {t.accent}][ ✓  APPROVED  ][/]"
            else:
                text = f"[bold {t.primary}][ ✗  REJECTED  ][/]"
        self.query_one("#badge", Static).update(text)
