# MAGI System Terminal GUI — Design Spec

**Date:** 2026-03-14
**Status:** Approved

---

## Overview

A full-screen terminal GUI built in Python using Textual that simulates the MAGI supercomputer voting system from Neon Genesis Evangelion. The user submits proposals (custom or preloaded) and watches MELCHIOR-1, BALTHASAR-2, and CASPAR-3 independently deliberate and cast votes, with dramatic animated results.

---

## Tech Stack

- **Language:** Python 3.11+
- **TUI Framework:** Textual
- **No external data sources** — all telemetry is simulated

---

## Project Structure

```
magi/
  main.py            # Entry point, CLI arg parsing
  app.py             # Textual App class, theme switching, global keybindings
  widgets/
    header.py        # Top status bar: system name, live clock, alert level
    magi_panel.py    # Reusable panel widget (instantiated 3x)
    verdict.py       # Central verdict banner
    activity_log.py  # Scrolling timestamped event log
    sidebar.py       # System stats, theme name, keybinding reference
    input_bar.py     # Proposal text input + Tab-to-cycle preloaded proposals
  themes.py          # Theme definitions: Amber, Blue, Red Alert
  voting.py          # Vote state machine + per-computer deliberation logic
  proposals.py       # ~15 preloaded Evangelion-themed proposals
```

Each widget is self-contained and communicates via Textual messages. `voting.py` owns all state and posts messages that widgets react to independently — no direct widget-to-widget coupling.

---

## Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ HEADER: ◈ MAGI SYSTEM · NERV HQ · TOKYO-3 · 2015.09.13 14:32  │
├───────────────────────────────────────────┬─────────────────────┤
│  MELCHIOR·1  │  BALTHASAR·2  │  CASPAR·3  │  SYSTEM            │
│              │               │            │  uptime / votes     │
│  stats       │  stats        │  stats     │  today / theme      │
│  data stream │  data stream  │  data stream│                    │
│              │               │            │  KEYBINDINGS        │
│  [APPROVED]  │  [ANALYZING…] │  [REJECTED]│  T: theme           │
│              │               │            │  Enter: submit      │
│              │               │            │  Tab: preloads      │
│              │               │            │  Q: quit            │
├───────────────────────────────────────────┴─────────────────────┤
│ ⚡ VERDICT: 1 APPROVE · 1 REJECT · 1 PENDING — AWAITING...     │
├─────────────────────────────────────────────────────────────────┤
│ ACTIVITY LOG (scrolling)                                        │
│ [14:32:01] MELCHIOR-1 → APPROVED                               │
│ [14:32:04] CASPAR-3 → REJECTED                                 │
├─────────────────────────────────────────────────────────────────┤
│ PROPOSAL ▸ █                                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Themes

Three named color themes, cycled at runtime with `T`:

| Theme | Primary | Accent | Background | Character |
|---|---|---|---|---|
| **Amber** | `#c8740a` | `#ffaa22` | `#0d0800` | Classic CRT phosphor, scanlines |
| **Blue** | `#4499cc` | `#00aaff` | `#000810` | Cold tactical display |
| **Red Alert** | `#cc4444` | `#ff4444` | `#0d0000` | Danger/crisis state |

All three themes share the same layout and widget structure — only colors change. Scanline overlay is Amber-only.

---

## Voting State Machine

```
IDLE → SUBMITTED → DELIBERATING → VOTED → VERDICT → IDLE
```

### States

**IDLE**
- Input bar is active and accepts text
- `Tab` cycles through preloaded proposals
- All MAGI panels show steady telemetry streams

**SUBMITTED**
- User presses `Enter` with a non-empty proposal
- Proposal text locks (input bar disabled)
- All 3 panels immediately switch to `ANALYZING…` badge (pulsing)
- Transitions to DELIBERATING

**DELIBERATING**
- Each computer runs an independent async timer (randomized 2–6 seconds)
- During deliberation: data stream lines scroll faster, vote badge pulses
- Each computer resolves independently — they do not wait for each other
- Vote outcome is weighted random: ~70% chance of a split (2–1) vote, ~30% chance of unanimous — to create drama
- When a computer finishes → transitions that computer to VOTED

**VOTED**
- Computer's badge snaps to `APPROVED` or `REJECTED` in theme accent color
- Activity log appends: `[HH:MM:SS] MELCHIOR-1 → APPROVED`
- Verdict banner updates live tally: `1 APPROVE · 1 REJECT · 1 PENDING`
- Once all 3 computers have voted → transitions to VERDICT

**VERDICT**
- Verdict banner shows final result: `APPROVED (2–1)`, `REJECTED (2–1)`, or `UNANIMOUS APPROVAL / REJECTION`
- Banner is highlighted (bold, full-width)
- Stays for 3 seconds, then full reset to IDLE. All keypresses except `Q` are ignored during this 3-second window.
- Activity log appends the final verdict line

---

## Widgets

### Header (`header.py`)
- Static content: `◈ MAGI SYSTEM · NERV HQ · TOKYO-3`
- Live clock (updates every second via Textual timer)
- Alert level indicator (NORMAL / ALERT — changes to ALERT during active vote)

### MagiPanel (`magi_panel.py`)
- Reusable; instantiated as MELCHIOR-1, BALTHASAR-2, CASPAR-3
- Shows: computer name, simulated telemetry (CPU %, memory, temperature, network status, signal integrity)
- Telemetry values update on a slow timer (every 2–3s) in IDLE; faster during DELIBERATING
- Vote badge at bottom: `STANDBY` → `ANALYZING…` (pulsing) → `APPROVED` / `REJECTED`

### Verdict (`verdict.py`)
- Single-line banner spanning main content width
- Shows live tally during DELIBERATING, final result during VERDICT
- Uses bold styling + accent color during VERDICT state

### ActivityLog (`activity_log.py`)
- Scrollable, fixed height (~4 lines visible)
- Appends timestamped events: vote casts, verdicts, theme changes
- Auto-scrolls to bottom on new entry

### Sidebar (`sidebar.py`)
- Fixed width (~20 chars)
- Sections: SYSTEM (uptime since session start, total votes cast this session), THEME (current theme name), CONTROLS (keybinding reference)
- Updates uptime every second, vote counts after each verdict

### InputBar (`input_bar.py`)
- Text input field with `PROPOSAL ▸` prefix
- `Tab` cycles preloaded proposals in a wrap-around loop (fills input field, user can edit before submitting)
- `Enter` submits; silently ignored if input is empty; disabled during active vote
- Clears on reset to IDLE

---

## Preloaded Proposals (`proposals.py`)

~15 Evangelion-themed proposals, examples:

- `INITIATE EVA UNIT-01 LAUNCH SEQUENCE`
- `AUTHORIZE THIRD IMPACT PROTOCOL`
- `DEPLOY N2 MINE — SECTOR 7`
- `OVERRIDE DUMMY SYSTEM — UNIT 03`
- `ACTIVATE ABSOLUTE TERROR FIELD`
- `INITIATE SELF-DESTRUCT SEQUENCE — NERV HQ`
- `AUTHORIZE INSTRUMENTALITY PROJECT`
- `ENGAGE ANGEL CONTAINMENT PROTOCOL`
- `REVOKE COMMANDER IKARI CLEARANCE LEVEL 4`
- `RELEASE EVANGELION UNIT-00 FROM LOCKDOWN`

---

## Keybindings

| Key | Action |
|---|---|
| `Enter` | Submit proposal (when IDLE) |
| `Tab` | Cycle preloaded proposals into input |
| `T` | Cycle theme (Amber → Blue → Red Alert → Amber) |
| `Q` / `Ctrl+C` | Quit |

---

## Terminal Requirements

Minimum terminal size: **120 columns × 30 rows**. The app does not gracefully degrade below this — it will display a warning and exit if the terminal is too small.

## Out of Scope

- Persistence (no saving vote history between sessions)
- Network features
- Sound
- Mouse interaction (keyboard-only)
- Multiple simultaneous votes
