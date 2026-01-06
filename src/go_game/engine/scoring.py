from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .board import Board
from .types import Color, Point, iter_neighbors


@dataclass(frozen=True, slots=True)
class TerritoryResult:
    territory_black: int
    territory_white: int
    neutral: int


@dataclass(frozen=True, slots=True)
class ScoreBreakdown:
    captures_black: int
    captures_white: int
    territory_black: int
    territory_white: int

    @property
    def score_black(self) -> int:
        # Simple Japanese-style: territory + captures
        return self.territory_black + self.captures_black

    @property
    def score_white(self) -> int:
        return self.territory_white + self.captures_white


def _region_owner(board: Board, region: set[Point]) -> Optional[Color]:
    """
    Determine owner of an empty region:
    - If all bordering stones are BLACK => BLACK owns region
    - If all bordering stones are WHITE => WHITE owns region
    - Mixed / none => neutral
    """
    bordering: set[Color] = set()

    for p in region:
        for nb in iter_neighbors(p, board.size):
            s = board.get(nb)
            if s is not None:
                bordering.add(s)

    if bordering == {Color.BLACK}:
        return Color.BLACK
    if bordering == {Color.WHITE}:
        return Color.WHITE
    return None


def evaluate_territory(board: Board) -> TerritoryResult:
    """
    Flood-fill empty regions and assign them to BLACK/WHITE if surrounded by one color.
    No dead-stone marking (naive territory).
    """
    size = board.size
    visited: set[Point] = set()

    tb = tw = neutral = 0

    for r in range(size):
        for c in range(size):
            p = Point(r, c)
            if p in visited:
                continue
            if board.get(p) is not None:
                continue

            # BFS/DFS empty region
            stack = [p]
            region: set[Point] = set()

            while stack:
                cur = stack.pop()
                if cur in visited:
                    continue
                if board.get(cur) is not None:
                    continue
                visited.add(cur)
                region.add(cur)
                for nb in iter_neighbors(cur, size):
                    if nb not in visited and board.get(nb) is None:
                        stack.append(nb)

            owner = _region_owner(board, region)
            if owner is Color.BLACK:
                tb += len(region)
            elif owner is Color.WHITE:
                tw += len(region)
            else:
                neutral += len(region)

    return TerritoryResult(territory_black=tb, territory_white=tw, neutral=neutral)
