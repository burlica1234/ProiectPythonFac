from go_game.engine.game_state import GameState
from go_game.engine.types import Point

def main():
    gs = GameState.new(size=5)

    gs = gs.play(Point(1, 0))  # B
    gs = gs.play(Point(1, 1))  # W (stone we capture)

    gs = gs.play(Point(0, 1))  # B
    gs = gs.play(Point(4, 4))  # W (random move)

    gs = gs.play(Point(1, 2))  # B
    gs = gs.play(Point(4, 3))  # W ( random move)

    gs = gs.play(Point(2, 1))  # B -> captures (1,1)

    print("Black captures:", gs.captures_black)
    print("White captures:", gs.captures_white)

if __name__ == "__main__":
    main()
