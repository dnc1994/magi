# MAGI System

A terminal GUI simulating the MAGI supercomputer voting system from Neon Genesis Evangelion.

MELCHIOR-1, BALTHASAR-2, and CASPAR-3 independently deliberate on proposals and cast votes. Watch the drama unfold.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -e ".[dev]"
cp .env.example .env   # then add your GEMINI_API_KEY
magi
```

Requires a terminal at least **120×30**.

### LLM deliberation traces

Each subsystem streams a live thinking trace via Gemini during deliberation, conditioned on its predetermined vote. Each subsystem has a distinct persona:

- **MELCHIOR-1** — pure rationality, analytical, zero emotion
- **BALTHASAR-2** — the mother, instincts of protection and survival
- **CASPAR-3** — the self, emotional, ambivalent, self-centred

To enable, add your API key to `.env`:

```
GEMINI_API_KEY=your_api_key_here
```

Get a key at https://aistudio.google.com/apikey. Without it the app runs normally — traces are simply blank.

## Controls

| Key | Action |
|-----|--------|
| `Enter` | Focus input / submit proposal |
| `Esc` | Unfocus input |
| `Tab` | Cycle preloaded Evangelion proposals |
| `T` | Cycle theme (Amber → Blue → Red Alert) |
| `L` | Toggle language (ZH / EN) for thinking traces |
| `Q` | Quit |

## Themes

- **Amber** — classic CRT phosphor glow
- **Blue** — cold tactical display
- **Red Alert** — danger mode

## Development

```bash
pip install -e ".[dev]"
pytest
```
