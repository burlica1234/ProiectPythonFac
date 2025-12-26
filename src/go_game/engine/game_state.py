from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .types import Color, Point
from .board import Board
from .rules import apply_move
from .errors import GoError


@dataclass(frozen=True, slots=True)
class GameState:
    board: Board
    next_player: Color
    captures_black: int
    captures_white: int
    ko_forbidden_signature: Optional[tuple] = None
    last_move: Optional[Point] = None  # NEW

    @staticmethod
    def new(size: int = 19, next_player: Color = Color.BLACK) -> "GameState":
        return GameState(
            board=Board.empty(size),
            next_player=next_player,
            captures_black=0,
            captures_white=0,
            ko_forbidden_signature=None,
            last_move=None,
        )

    def play(self, p: Point) -> "GameState":
        prev_signature = self.board.signature()

        res = apply_move(
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

        new_ko = prev_signature if res.captured == 1 else None

        return GameState(
            board=res.board,
            next_player=self.next_player.opponent,
            captures_black=cb,
            captures_white=cw,
            ko_forbidden_signature=new_ko,
            last_move=p,  # NEW
        )

    def legal_moves(self) -> list[Point]:
        """All legal moves for next_player in current position."""
        size = self.board.size
        moves: list[Point] = []
        for r in range(size):
            for c in range(size):
                p = Point(r, c)
                if self.board.get(p) is not None:
                    continue
                try:
                    _ = apply_move(
                        self.board, p, self.next_player,
                        ko_forbidden_signature=self.ko_forbidden_signature
                    )
                    moves.append(p)
                except GoError:
                    pass
        return moves
