# MAGI System — Dev Notes

## Running

```bash
source .venv/bin/activate
magi                  # launch app
pytest                # run tests (39 tests)
```

## Architecture

Pure-Python data layer (`themes.py`, `proposals.py`, `voting.py`) has no Textual dependency — fully unit-tested. `MagiApp` wires self-contained widgets via Textual messages. Three async workers run deliberation timers independently.

## Key files

| File | What it does |
|------|-------------|
| `magi/app.py` | App layout, voting workflow, theme switching, key handling |
| `magi/voting.py` | Vote state machine — `generate_votes()` returns 70% split / 30% unanimous |
| `magi/widgets/magi_panel.py` | Animated telemetry panel — most complex widget |
| `magi/themes.py` | Three `Theme` dataclasses; `get_next_theme()` cycles them |

## Textual 8.x gotchas

- `current_theme` is a built-in Textual property — our theme uses `_magi_theme` internally with a `current_theme` property override in `app.py`
- `Widget._render()` is an internal Textual method — don't name methods `_render()`; use `_refresh_content()` or similar
- `Static.content` (not `.renderable`) to read text set via `.update()`
- Add `if not self.is_attached: return` guard in `watch_*` methods before calling `query_one()`

## Voting flow

```
IDLE → DELIBERATING → VERDICT → IDLE
```

Each of 3 computers gets a random 2–6s delay then posts a `VoteCast` message. App routes it to the relevant `MagiPanel` and updates the `VerdictBanner` tally. After all 3 vote, verdict shows for 3 seconds then resets.
