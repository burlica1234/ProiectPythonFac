from __future__ import annotations
import tkinter as tk
from dataclasses import dataclass

from go_game.engine.game_state import GameState
from go_game.engine.types import Point, Color
from go_game.engine.errors import GoError


@dataclass
class RenderConfig:
    margin: int = 30
    cell: int = 40
    stone_radius: int = 16
    hint_radius: int = 5


class GoApp:
    def __init__(self, root: tk.Tk, size: int = 9):
        self.root = root
        self.root.title("Go - Phase 2")

        self.state = GameState.new(size=size)
        self.cfg = RenderConfig()

        w = self.cfg.margin * 2 + self.cfg.cell * (size - 1)
        h = self.cfg.margin * 2 + self.cfg.cell * (size - 1)

        self.canvas = tk.Canvas(root, width=w, height=h, highlightthickness=0)
        self.canvas.pack()

        self.status = tk.Label(root, text="", anchor="w")
        self.status.pack(fill="x")

        self.canvas.bind("<Button-1>", self.on_click)

        self.redraw()

    # ---------- coordinate mapping ----------
    def p_to_xy(self, p: Point) -> tuple[int, int]:
        x = self.cfg.margin + p.col * self.cfg.cell
        y = self.cfg.margin + p.row * self.cfg.cell
        return x, y

    def xy_to_point(self, x: int, y: int) -> Point | None:
        # Find nearest intersection
        size = self.state.board.size
        col = round((x - self.cfg.margin) / self.cfg.cell)
        row = round((y - self.cfg.margin) / self.cfg.cell)
        if 0 <= row < size and 0 <= col < size:
            # Ensure click is reasonably close to intersection
            ix, iy = self.p_to_xy(Point(row, col))
            if abs(ix - x) <= self.cfg.cell * 0.35 and abs(iy - y) <= self.cfg.cell * 0.35:
                return Point(row, col)
        return None

    # ---------- drawing ----------
    def redraw(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_hints()
        self.draw_stones()
        self.draw_last_move_marker()
        self.update_status()

    def draw_grid(self):
        size = self.state.board.size
        m, cell = self.cfg.margin, self.cfg.cell
        start = m
        end = m + cell * (size - 1)

        # lines
        for i in range(size):
            x = m + i * cell
            y = m + i * cell
            self.canvas.create_line(start, y, end, y)
            self.canvas.create_line(x, start, x, end)

    def draw_stones(self):
        size = self.state.board.size
        r = self.cfg.stone_radius

        for row in range(size):
            for col in range(size):
                p = Point(row, col)
                stone = self.state.board.get(p)
                if stone is None:
                    continue
                x, y = self.p_to_xy(p)
                fill = "black" if stone is Color.BLACK else "white"
                outline = "black"
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline=outline, width=2)

    def draw_hints(self):
        # highlight valid placements as small dots
        r = self.cfg.hint_radius
        for p in self.state.legal_moves():
            x, y = self.p_to_xy(p)
            # dot color based on next player (subtle)
            fill = "black" if self.state.next_player is Color.BLACK else "white"
            outline = "gray25"
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline=outline)

    def draw_last_move_marker(self):
        if self.state.last_move is None:
            return
        x, y = self.p_to_xy(self.state.last_move)
        r = self.cfg.stone_radius + 6
        self.canvas.create_oval(x - r, y - r, x + r, y + r, outline="red", width=2)

    def update_status(self):
        self.status.config(
            text=f"Turn: {self.state.next_player.value} | "
                 f"Captures B:{self.state.captures_black} W:{self.state.captures_white}"
        )

    # ---------- events ----------
    def on_click(self, event):
        p = self.xy_to_point(event.x, event.y)
        if p is None:
            return
        try:
            self.state = self.state.play(p)
        except GoError as e:
            # optional: show error briefly
            self.status.config(text=f"Illegal move: {e}")
            self.root.after(900, self.update_status)
            return

        self.redraw()


def run_gui(size: int = 9):
    root = tk.Tk()
    GoApp(root, size=size)
    root.mainloop()
