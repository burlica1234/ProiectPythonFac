from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .types import Color, Point
from .board import Board
from .rules import apply_move
from .errors import GoError
from .scoring import evaluate_territory, ScoreBreakdown


@dataclass(frozen=True, slots=True)
class MoveRecord:
    color: Color
    point: Optional[Point]          # None = PASS
    captured: int


@dataclass(frozen=True, slots=True)
class GameState:
    board: Board
    next_player: Color
    captures_black: int
    captures_white: int
    ko_forbidden_signature: Optional[tuple] = None
    last_move: Optional[Point] = None

    consecutive_passes: int = 0
    is_over: bool = False

    history: tuple[MoveRecord, ...] = ()

    @staticmethod
    def new(size: int = 19, next_player: Color = Color.BLACK) -> "GameState":
        return GameState(
            board=Board.empty(size),
            next_player=next_player,
            captures_black=0,
            captures_white=0,
            ko_forbidden_signature=None,
            last_move=None,
            consecutive_passes=0,
            is_over=False,
            history=(),
        )

    def play(self, p: Point) -> "GameState":
        if self.is_over:
            return self

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

        new_hist = self.history + (MoveRecord(self.next_player, p, res.captured),)

        return GameState(
            board=res.board,
            next_player=self.next_player.opponent,
            captures_black=cb,
            captures_white=cw,
            ko_forbidden_signature=new_ko,
            last_move=p,
            consecutive_passes=0,
            is_over=False,
            history=new_hist,
        )

    def pass_turn(self) -> "GameState":
        """Player passes. Two consecutive passes end the game."""
        if self.is_over:
            return self

        new_passes = self.consecutive_passes + 1
        over = new_passes >= 2

        new_hist = self.history + (MoveRecord(self.next_player, None, 0),)

        return GameState(
            board=self.board,
            next_player=self.next_player.opponent,
            captures_black=self.captures_black,
            captures_white=self.captures_white,
            ko_forbidden_signature=None,
            last_move=None,
            consecutive_passes=new_passes,
            is_over=over,
            history=new_hist,
        )

    def legal_moves(self) -> list[Point]:
        if self.is_over:
            return []
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

    # -------- Phase 5: scoring & stats --------
    def score(self) -> ScoreBreakdown:
        """
        Territory + captures (simple Japanese scoring).
        Assumes board is in a reasonable end state (after 2 passes).
        """
        terr = evaluate_territory(self.board)
        return ScoreBreakdown(
            captures_black=self.captures_black,
            captures_white=self.captures_white,
            territory_black=terr.territory_black,
            territory_white=terr.territory_white,
        )

    def stats(self) -> dict[str, int]:
        """Simple session statistics."""
        moves = len(self.history)
        passes = sum(1 for m in self.history if m.point is None)
        return {
            "moves_total": moves,
            "passes_total": passes,
            "captures_black": self.captures_black,
            "captures_white": self.captures_white,
        }
