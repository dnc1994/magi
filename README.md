# MAGI System

A terminal GUI simulating the MAGI supercomputer voting system from Neon Genesis Evangelion.

MELCHIOR-1, BALTHASAR-2, and CASPAR-3 independently deliberate on proposals and cast votes. Watch the drama unfold.

## Setup

```bash
source .venv/bin/activate
magi
```

Requires a terminal at least **120×30**.

## Controls

| Key | Action |
|-----|--------|
| `Enter` | Submit proposal |
| `Tab` | Cycle preloaded Evangelion proposals |
| `T` | Cycle theme (Amber → Blue → Red Alert) |
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
