import pytest
from textual.app import App, ComposeResult
from magi.themes import THEMES
from magi.widgets.header import MagiHeader
from magi.widgets.activity_log import ActivityLog


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
