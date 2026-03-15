# MAGI System — Dev Notes

## Running

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -e ".[dev]"
magi                  # launch app
pytest                # run tests (39 tests)
```

## Architecture

Pure-Python data layer (`themes.py`, `proposals.py`, `voting.py`) has no Textual dependency — fully unit-tested. `MagiApp` wires self-contained widgets via Textual messages. Three async workers run deliberation timers independently.

## Key files

| File | What it does |
|------|-------------|
| `magi/app.py` | App layout, voting workflow, theme/language switching, key handling |
| `magi/llm.py` | Gemini streaming — per-subsystem personas, retry logic, language support |
| `magi/voting.py` | Vote state machine — `generate_votes()` returns 70% split / 30% unanimous |
| `magi/widgets/magi_panel.py` | Animated telemetry + streaming LLM trace — most complex widget |
| `magi/widgets/verdict.py` | Verdict banner — sticky post-vote, proposal display, flash/dim by outcome |
| `magi/themes.py` | Three `Theme` dataclasses; `get_next_theme()` cycles them |

## Textual 8.x gotchas

- `current_theme` is a built-in Textual property — our theme uses `_magi_theme` internally with a `current_theme` property override in `app.py`
- `Widget._render()` is an internal Textual method — don't name methods `_render()`; use `_refresh_content()` or similar
- `Static.content` (not `.renderable`) to read text set via `.update()`
- Add `if not self.is_attached: return` guard in `watch_*` methods before calling `query_one()`
- Rich markup: escape literal brackets with `[[` / `]]`

## Voting flow

```
IDLE → DELIBERATING → VERDICT → (sticky) → IDLE (on input refocus)
```

Each of 3 panels gets a random 2–6s deliberation delay (`VoteCast`) and a concurrent Gemini LLM call. Panel vote badge reveals as soon as **its own** LLM stream completes (outcome already known). Verdict banner fires when all 3 LLM streams done **and** all 3 `VoteCast` messages received. Verdict stays visible until the user refocuses the input.

## LLM traces

- Model: `gemini-3.1-flash-lite-preview` via SSE streaming
- One retry on timeout, then canned error message
- Per-subsystem system prompts (MELCHIOR = rational, BALTHASAR = protective, CASPAR = emotional)
- Language toggleable: ZH (default) / EN — applied per vote submission
- `GEMINI_API_KEY` loaded from `.env` via python-dotenv

## Visual design

- APPROVED outcomes: bold accent (brightest theme colour), pulsing while active
- REJECTED outcomes: dim (most muted theme colour), static
- All colours derived from `Theme` — safe across Amber / Blue / Red Alert
- Telemetry animates fast during DELIBERATING only; IDLE and post-vote are calm
- Theme changes re-render all live content (traces, verdict) immediately
