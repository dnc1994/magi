import pytest
from textual.app import App, ComposeResult
from textual.widgets import Static
from magi.themes import THEMES
from magi.widgets.header import MagiHeader
from magi.widgets.activity_log import ActivityLog
from magi.widgets.sidebar import Sidebar
from magi.widgets.verdict import VerdictBanner
from magi.widgets.input_bar import InputBar
from magi.widgets.magi_panel import MagiPanel


class HeaderTestApp(App):
    def compose(self) -> ComposeResult:
        w = MagiHeader()
        w.theme = THEMES[0]
        yield w


class LogTestApp(App):
    def compose(self) -> ComposeResult:
        yield ActivityLog()


@pytest.mark.asyncio
async def test_header_mounts():
    async with HeaderTestApp().run_test() as pilot:
        assert pilot.app.query_one(MagiHeader) is not None


@pytest.mark.asyncio
async def test_activity_log_mounts():
    async with LogTestApp().run_test() as pilot:
        log = pilot.app.query_one(ActivityLog)
        assert log is not None


@pytest.mark.asyncio
async def test_activity_log_add_entry():
    async with LogTestApp().run_test() as pilot:
        log = pilot.app.query_one(ActivityLog)
        log.add_entry("MELCHIOR-1 → APPROVED")
        # RichLog line_count should increment
        assert log.line_count >= 1


class SidebarTestApp(App):
    def compose(self) -> ComposeResult:
        yield Sidebar()


class VerdictTestApp(App):
    def compose(self) -> ComposeResult:
        yield VerdictBanner()


@pytest.mark.asyncio
async def test_sidebar_mounts():
    async with SidebarTestApp().run_test() as pilot:
        assert pilot.app.query_one(Sidebar) is not None


@pytest.mark.asyncio
async def test_verdict_banner_mounts():
    async with VerdictTestApp().run_test() as pilot:
        assert pilot.app.query_one(VerdictBanner) is not None


@pytest.mark.asyncio
async def test_verdict_banner_shows_verdict():
    async with VerdictTestApp().run_test() as pilot:
        banner = pilot.app.query_one(VerdictBanner)
        banner.show_verdict("APPROVED (2–1)")
        content = str(pilot.app.query_one("#verdict-text", Static).content)
        assert "APPROVED" in content


class InputBarTestApp(App):
    def compose(self) -> ComposeResult:
        yield InputBar()


@pytest.mark.asyncio
async def test_input_bar_mounts():
    async with InputBarTestApp().run_test() as pilot:
        assert pilot.app.query_one(InputBar) is not None


@pytest.mark.asyncio
async def test_input_bar_cycle_preload():
    from magi.proposals import PROPOSALS
    async with InputBarTestApp().run_test() as pilot:
        bar = pilot.app.query_one(InputBar)
        bar.cycle_preload()
        from textual.widgets import Input
        inp = pilot.app.query_one(Input)
        assert inp.value == PROPOSALS[0]
        bar.cycle_preload()
        assert inp.value == PROPOSALS[1]


@pytest.mark.asyncio
async def test_input_bar_reset_clears():
    async with InputBarTestApp().run_test() as pilot:
        bar = pilot.app.query_one(InputBar)
        bar.cycle_preload()
        bar.reset()
        from textual.widgets import Input
        assert pilot.app.query_one(Input).value == ""


@pytest.mark.asyncio
async def test_input_bar_disable_prevents_submit():
    async with InputBarTestApp().run_test() as pilot:
        bar = pilot.app.query_one(InputBar)
        bar.disable()
        from textual.widgets import Input
        assert pilot.app.query_one(Input).disabled


class PanelTestApp(App):
    def compose(self) -> ComposeResult:
        yield MagiPanel("MELCHIOR", "1")


@pytest.mark.asyncio
async def test_magi_panel_mounts():
    async with PanelTestApp().run_test() as pilot:
        assert pilot.app.query_one(MagiPanel) is not None


@pytest.mark.asyncio
async def test_magi_panel_idle_badge():
    async with PanelTestApp().run_test() as pilot:
        panel = pilot.app.query_one(MagiPanel)
        badge = str(pilot.app.query_one("#badge", Static).content)
        assert "STANDBY" in badge


@pytest.mark.asyncio
async def test_magi_panel_voted_approved():
    async with PanelTestApp().run_test() as pilot:
        panel = pilot.app.query_one(MagiPanel)
        panel.set_state("VOTED", "APPROVED")
        badge = str(pilot.app.query_one("#badge", Static).content)
        assert "APPROVED" in badge


@pytest.mark.asyncio
async def test_magi_panel_voted_rejected():
    async with PanelTestApp().run_test() as pilot:
        panel = pilot.app.query_one(MagiPanel)
        panel.set_state("VOTED", "REJECTED")
        badge = str(pilot.app.query_one("#badge", Static).content)
        assert "REJECTED" in badge


from magi.app import MagiApp


@pytest.mark.asyncio
async def test_full_app_mounts():
    async with MagiApp().run_test(size=(140, 40)) as pilot:
        assert pilot.app.query_one(MagiHeader) is not None
        assert len(pilot.app.query(MagiPanel)) == 3
        assert pilot.app.query_one(VerdictBanner) is not None
        assert pilot.app.query_one(ActivityLog) is not None
        assert pilot.app.query_one(Sidebar) is not None
        assert pilot.app.query_one(InputBar) is not None


@pytest.mark.asyncio
async def test_theme_cycles():
    from magi.themes import THEMES
    async with MagiApp().run_test(size=(140, 40)) as pilot:
        assert pilot.app.current_theme is THEMES[0]  # Amber
        await pilot.press("t")
        assert pilot.app.current_theme is THEMES[1]  # Blue
        await pilot.press("t")
        assert pilot.app.current_theme is THEMES[2]  # Red Alert
        await pilot.press("t")
        assert pilot.app.current_theme is THEMES[0]  # Back to Amber
