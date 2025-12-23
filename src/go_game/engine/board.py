from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Iterable

from .types import Color, Point, iter_neighbors

Stone = Optional[Color]

@dataclass(frozen=True, slots=True)
class Board:
    """
    Immutable board. Internally stored as tuple-of-tuples for safe hashing/comparison.
    """
    size: int
    grid: tuple[tuple[Stone, ...], ...]

    @staticmethod
    def empty(size: int) -> "Board":
        if size < 2:
            raise ValueError("Board size must be >= 2")
        row = tuple([None] * size)
        return Board(size=size, grid=tuple([row for _ in range(size)]))

    def get(self, p: Point) -> Stone:
        return self.grid[p.row][p.col]

    def place(self, p: Point, color: Color) -> "Board":
        # Caller should validate bounds/occupied; we keep this minimal & fast.
        new_rows = [list(r) for r in self.grid]
        new_rows[p.row][p.col] = color
        return Board(self.size, tuple(tuple(r) for r in new_rows))

    def remove_many(self, points: Iterable[Point]) -> "Board":
        new_rows = [list(r) for r in self.grid]
        for p in points:
            new_rows[p.row][p.col] = None
        return Board(self.size, tuple(tuple(r) for r in new_rows))

    def iter_neighbors(self, p: Point):
        return iter_neighbors(p, self.size)

    def signature(self) -> tuple:
        """
        A hashable signature for ko comparison.
        Using the grid itself is enough because it's immutable and comparable.
        """
        return self.grid
