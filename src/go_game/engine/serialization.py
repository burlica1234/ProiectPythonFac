from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional, Tuple

from go_game.engine.game_state import GameState, MoveRecord
from go_game.engine.types import Color, Point


def _point_to_obj(p: Optional[Point]) -> Optional[dict[str, int]]:
    if p is None:
        return None
    return {"row": p.row, "col": p.col}


def _obj_to_point(obj: Optional[dict[str, int]]) -> Optional[Point]:
    if obj is None:
        return None
    return Point(row=int(obj["row"]), col=int(obj["col"]))


def game_to_dict(
    state: GameState,
    *,
    ai_enabled: bool,
    ai_color: Color,
    board_size: int,
) -> dict[str, Any]:
    return {
        "version": 1,
        "board_size": board_size,
        "ai_enabled": ai_enabled,
        "ai_color": ai_color.value,
        "history": [
            {
                "color": m.color.value,
                "point": _point_to_obj(m.point),
                "captured": m.captured,
            }
            for m in state.history
        ],
    }


def dict_to_game(data: dict[str, Any]) -> Tuple[GameState, bool, Color, int]:
    size = int(data.get("board_size", 9))
    ai_enabled = bool(data.get("ai_enabled", True))
    ai_color = Color(data.get("ai_color", "W"))

    state = GameState.new(size=size)

    hist = data.get("history", [])
    for m in hist:
        color = Color(m["color"])
        point = _obj_to_point(m.get("point"))
        if state.next_player != color:
            state = state.pass_turn()

        if point is None:
            state = state.pass_turn()
        else:
            state = state.play(point)

    return state, ai_enabled, ai_color, size


def save_session(path: str | Path, state: GameState, *, ai_enabled: bool, ai_color: Color, board_size: int) -> None:
    """Save a game session to disk"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = game_to_dict(state, ai_enabled=ai_enabled, ai_color=ai_color, board_size=board_size)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_session(path: str | Path) -> Tuple[GameState, bool, Color, int]:
    """Load a game session from disk"""
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return dict_to_game(data)
