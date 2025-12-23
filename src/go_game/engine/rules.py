from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Set, Iterable

from .types import Color, Point
from .board import Board
from .errors import OutOfBounds, OccupiedPoint, SuicideMove, KoViolation


@dataclass(frozen=True, slots=True)
class MoveResult:
    board: Board
    captured: int
    captured_points: tuple[Point, ...]


def _check_bounds(board: Board, p: Point) -> None:
    if not (0 <= p.row < board.size and 0 <= p.col < board.size):
        raise OutOfBounds(f"Point out of bounds: {p}")


def _group_and_liberties(board: Board, start: Point) -> tuple[Set[Point], Set[Point]]:
    """
    Returns (group_points, liberties_points) for the chain at start.
    Assumes there is a stone at start.
    """
    color = board.get(start)
    assert color is not None

    group: Set[Point] = set()
    liberties: Set[Point] = set()
    stack = [start]

    while stack:
        p = stack.pop()
        if p in group:
            continue
        group.add(p)
        for nb in board.iter_neighbors(p):
            s = board.get(nb)
            if s is None:
                liberties.add(nb)
            elif s == color and nb not in group:
                stack.append(nb)

    return group, liberties


def _capturable_enemy_groups(board: Board, placed_at: Point, color: Color) -> Set[Point]:
    """
    After placing `color` at `placed_at`, find all enemy stones that have no liberties.
    Returns all points to remove.
    """
    to_capture: Set[Point] = set()
    for nb in board.iter_neighbors(placed_at):
        if board.get(nb) == color.opponent:
            grp, libs = _group_and_liberties(board, nb)
            if len(libs) == 0:
                to_capture |= grp
    return to_capture


def apply_move(
    board: Board,
    p: Point,
    color: Color,
    *,
    ko_forbidden_signature: Optional[tuple] = None,
) -> MoveResult:
    """
    Applies a move with legality checks:
    - bounds
    - occupied
    - captures
    - suicide prevention (unless capture grants liberties)
    - simple ko: forbid resulting board signature matching ko_forbidden_signature

    ko_forbidden_signature should be the *board signature* that is illegal to recreate
    (typically the position from 2 plies earlier in simple ko situations).
    """
    _check_bounds(board, p)
    if board.get(p) is not None:
        raise OccupiedPoint(f"Point already occupied: {p}")

    # Place stone
    b1 = board.place(p, color)

    # Capture any adjacent enemy groups with 0 liberties
    captured_points = _capturable_enemy_groups(b1, p, color)
    b2 = b1.remove_many(captured_points) if captured_points else b1

    # Suicide check: the placed stone's group must have liberties after captures
    grp, libs = _group_and_liberties(b2, p)
    if len(libs) == 0:
        raise SuicideMove(f"Suicide move at {p} for {color}")

    # Ko check (simple ko)
    if ko_forbidden_signature is not None and b2.signature() == ko_forbidden_signature:
        raise KoViolation("Ko rule violation: recreates forbidden position")

    return MoveResult(
        board=b2,
        captured=len(captured_points),
        captured_points=tuple(sorted(captured_points, key=lambda x: (x.row, x.col))),
    )
