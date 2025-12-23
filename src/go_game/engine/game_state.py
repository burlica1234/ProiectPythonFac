from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Optional

from .types import Color, Point
from .board import Board
from .rules import apply_move, MoveResult


@dataclass(frozen=True, slots=True)
class GameState:
    board: Board
    next_player: Color
    captures_black: int
    captures_white: int

    # For simple ko: we keep the signature that is forbidden for the next move (if any).
    ko_forbidden_signature: Optional[tuple] = None

    @staticmethod
    def new(size: int = 19, next_player: Color = Color.BLACK) -> "GameState":
        return GameState(
            board=Board.empty(size),
            next_player=next_player,
            captures_black=0,
            captures_white=0,
            ko_forbidden_signature=None,
        )

    def play(self, p: Point) -> "GameState":
        """
        Play a move for next_player.
        Implements simple-ko update:
        - If exactly one stone was captured AND the move results in a position that would allow immediate recapture,
          we forbid recreating the board position *before* this move for the opponent.
        In practice for simple ko: if captured == 1, set ko_forbidden_signature = previous_board.signature(),
        else None.
        """
        prev_signature = self.board.signature()

        res: MoveResult = apply_move(
            self.board,
            p,
            self.next_player,
            ko_forbidden_signature=self.ko_forbidden_signature,
        )

        cb, cw = self.captures_black, self.captures_white
        if self.next_player is Color.BLACK:
            cb += res.captured
        else:
            cw += res.captured

        # Simple ko handling: only set forbidden signature on single-stone capture.
        new_ko = prev_signature if res.captured == 1 else None

        return GameState(
            board=res.board,
            next_player=self.next_player.opponent,
            captures_black=cb,
            captures_white=cw,
            ko_forbidden_signature=new_ko,
        )
