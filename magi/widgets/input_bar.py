from __future__ import annotations
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input, Static
from textual.containers import Horizontal
from magi.proposals import ProposalCycler
from magi.themes import THEMES, Theme


class InputBar(Widget):
    DEFAULT_CSS = """
    InputBar {
        height: 3;
        border-top: solid $border;
        padding: 0 1;
    }
    InputBar Horizontal {
        height: 1fr;
        align: left middle;
    }
    InputBar Static#prompt {
        width: auto;
        padding-right: 1;
    }
    InputBar Input {
        width: 1fr;
        border: none;
        background: transparent;
        padding: 0;
    }
    InputBar Input:focus {
        border: none;
    }
    """

    theme: reactive[Theme] = reactive(THEMES[0])

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._cycler = ProposalCycler()

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Static("PROPOSAL ▸ ", id="prompt")
            yield Input(
                placeholder="TYPE A PROPOSAL OR PRESS TAB FOR PRELOADED...",
                id="proposal-input",
            )

    def on_mount(self) -> None:
        self._apply_theme_colors()

    def watch_theme(self, theme: Theme) -> None:
        self.styles.background = theme.background
        self._apply_theme_colors()

    def _apply_theme_colors(self) -> None:
        if not self.is_attached:
            return
        t = self.theme
        self.query_one("#prompt", Static).update(f"[bold {t.accent}]PROPOSAL ▸[/] ")

    def cycle_preload(self) -> None:
        """Fill input with next preloaded proposal (wrap-around)."""
        proposal = self._cycler.next()
        inp = self.query_one("#proposal-input", Input)
        inp.value = proposal
        inp.cursor_position = len(proposal)

    def get_value(self) -> str:
        return self.query_one("#proposal-input", Input).value.strip()

    def disable(self) -> None:
        self.query_one("#proposal-input", Input).disabled = True

    def reset(self) -> None:
        inp = self.query_one("#proposal-input", Input)
        inp.disabled = False
        inp.value = ""
