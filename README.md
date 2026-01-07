# Go Game – Python Project

## Description
This project implements a simplified version of the Go board game in Python.  
It includes a rule engine (stone placement, captures, suicide prevention, and a simple ko rule), a Tkinter-based GUI for interactive play, an optional random AI opponent, scoring with basic territory evaluation, and session persistence.

## Project Structure
- `src/go_game/engine/` – Core game logic (board model, rules, game state, AI, scoring, persistence)
  - `board.py` – Immutable board representation
  - `rules.py` – Move application, captures, legality checks, simple ko
  - `game_state.py` – Game flow, turns, passes, end conditions, history, scoring access
  - `scoring.py` – Territory evaluation and score breakdown
  - `serialization.py` – Save/load sessions (JSON)
  - `ai/` – AI opponent implementations
- `src/go_game/gui/` – Tkinter graphical interface
  - `app.py` – Board rendering, interaction, controls, integration with engine
- `src/go_game/sessions/` – Saved sessions (JSON)

## Implemented Features
- Variable-size Go board (9x9 / 13x13 / 19x19)
- Legal move enforcement (bounds, occupied points, suicide prevention)
- Captures and removal of captured groups
- Simple ko rule prevention
- Human vs Human play
- Optional AI opponent (random legal move selection with pass support)
- End-of-game detection (two consecutive passes)
- Scoring:
  - Captures tracking
  - Simple territory evaluation
  - Final score display and winner calculation
- Undo/Redo support
- Save/Load session support (JSON)

## Code Style and Documentation
The project follows Python PEP guidelines, including:
- **PEP 257** for docstring conventions (modules, classes, and public methods are documented with standard Python docstrings)

## How to Run
From the project root:

```bash
python -m go_game.main
