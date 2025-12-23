import pytest
from go_game.engine.game_state import GameState
from go_game.engine.types import Point
from go_game.engine.errors import OccupiedPoint, SuicideMove

def test_occupied():
    gs = GameState.new(5)
    gs = gs.play(Point(0, 0))
    with pytest.raises(OccupiedPoint):
        gs.play(Point(0, 0))

def test_simple_capture():
    gs = GameState.new(5)
    gs = gs.play(Point(1, 0))
    gs = gs.play(Point(1, 1))
    gs = gs.play(Point(0, 1))
    gs = gs.play(Point(4, 4))
    gs = gs.play(Point(1, 2))
    gs = gs.play(Point(4, 3))
    gs = gs.play(Point(2, 1))
    assert gs.captures_black == 1

def test_suicide_not_allowed():
    gs = GameState.new(5)
    gs = gs.play(Point(0, 1))  # B
    gs = gs.play(Point(4, 4))  # W
    gs = gs.play(Point(1, 0))  # B
    gs = gs.play(Point(4, 3))  # W
    gs = gs.play(Point(1, 2))  # B
    gs = gs.play(Point(3, 3))  # W
    gs = gs.play(Point(2, 1))  # B
    with pytest.raises(SuicideMove):
        gs.play(Point(1, 1))

def test_ko_violation_smoke():
    pass
