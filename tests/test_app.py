import pytest
from textual.app import App, ComposeResult
from textual.widgets import Static
from magi.themes import THEMES
from magi.widgets.header import MagiHeader
from magi.widgets.activity_log import ActivityLog
from magi.widgets.sidebar import Sidebar
from magi.widgets.verdict import VerdictBanner


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
