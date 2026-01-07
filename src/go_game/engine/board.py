from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Iterable

from .types import Color, Point, iter_neighbors

Stone = Optional[Color]


@dataclass(frozen=True, slots=True)
class Board:
    """
    Represents an immutable Go board.

    The board stores stones on a square grid and provides utility
    methods for reading positions and producing a board signature.
    """
    size: int
    grid: tuple[tuple[Stone, ...], ...]

    @staticmethod
    def empty(size: int) -> "Board":
        """
        Create an empty Go board of the given size.
        Args:
            size: Board dimension.
        Returns:
            A new Board instance with no stones placed.
        Raises:
            ValueError: If the board size is less than 2.
        """
        if size < 2:
            raise ValueError("Board size must be >= 2")
        row = tuple([None] * size)
        return Board(size=size, grid=tuple([row for _ in range(size)]))

    def get(self, p: Point) -> Stone:
        """
        Retrieve the stone at the given board point.
        Args:
            p: Board point.
        Returns:
            The stone color at the point, or None if the point is empty.
        """
        return self.grid[p.row][p.col]

    def place(self, p: Point, color: Color) -> "Board":
        """
        Place a stone on the board.
        Args:
            p: Board point.
            color: Stone color.
        Returns:
            A new Board instance with the stone placed.
        """
        new_rows = [list(r) for r in self.grid]
        new_rows[p.row][p.col] = color
        return Board(self.size, tuple(tuple(r) for r in new_rows))

    def remove_many(self, points: Iterable[Point]) -> "Board":
        """
        Remove multiple stones from the board.
        Args:
            points: Iterable of board points to clear.
        Returns:
            A new Board instance with the specified points emptied.
        """
        new_rows = [list(r) for r in self.grid]
        for p in points:
            new_rows[p.row][p.col] = None
        return Board(self.size, tuple(tuple(r) for r in new_rows))

    def iter_neighbors(self, p: Point):
        """
        Iterate over valid neighboring points of a given point.
        Args:
            p: Board point.
        Returns:
            An iterable of neighboring board points.
        """
        return iter_neighbors(p, self.size)

    def signature(self) -> tuple:
        """
        Return a hashable board signature.
        This signature is used for ko comparison.
        """
        return self.grid
