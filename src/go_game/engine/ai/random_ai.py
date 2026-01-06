from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

from go_game.engine.game_state import GameState
from go_game.engine.types import Point


@dataclass(frozen=True, slots=True)
class RandomAI:
    """
    Picks a random legal move. If no legal moves, returns None (caller can Pass).
    """

    def pick_move(self, state: GameState) -> Optional[Point]:
        moves = state.legal_moves()
        if not moves:
            return None
        return random.choice(moves)
