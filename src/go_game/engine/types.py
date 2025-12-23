from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

class Color(str, Enum):
    BLACK = "B"
    WHITE = "W"

    @property
    def opponent(self) -> "Color":
        return Color.WHITE if self is Color.BLACK else Color.BLACK

@dataclass(frozen=True, slots=True)
class Point:
    row: int
    col: int

def iter_neighbors(p: Point, size: int) -> Iterable[Point]:
    r, c = p.row, p.col
    if r > 0: yield Point(r - 1, c)
    if r < size - 1: yield Point(r + 1, c)
    if c > 0: yield Point(r, c - 1)
    if c < size - 1: yield Point(r, c + 1)
