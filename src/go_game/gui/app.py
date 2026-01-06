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

        self.size = size
        self.state = GameState.new(size=size)
        self.cfg = RenderConfig()

        # Layout: controls (top), canvas (middle), status (bottom)
        self.controls = tk.Frame(root)
        self.controls.pack(fill="x", padx=8, pady=6)

        self.pass_btn = tk.Button(self.controls, text="Pass", command=self.on_pass)
        self.pass_btn.pack(side="left")

        self.new_btn = tk.Button(self.controls, text="New Game", command=self.on_new_game)
        self.new_btn.pack(side="left", padx=(8, 0))
        w = self.cfg.margin * 2 + self.cfg.cell * (size - 1)
        h = self.cfg.margin * 2 + self.cfg.cell * (size - 1)

        self.canvas = tk.Canvas(root, width=w, height=h, highlightthickness=0)
        self.canvas.pack()

        self.status = tk.Label(root, text="", anchor="w")
        self.status.pack(fill="x", padx=8, pady=6)

        self.canvas.bind("<Button-1>", self.on_click)

        self.redraw()

    # ---------- coordinate mapping ----------
    def p_to_xy(self, p: Point) -> tuple[int, int]:
        x = self.cfg.margin + p.col * self.cfg.cell
        y = self.cfg.margin + p.row * self.cfg.cell
        return x, y

    def xy_to_point(self, x: int, y: int) -> Point | None:
        size = self.state.board.size
        col = round((x - self.cfg.margin) / self.cfg.cell)
        row = round((y - self.cfg.margin) / self.cfg.cell)
        if 0 <= row < size and 0 <= col < size:
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
        self.update_controls()

    def draw_grid(self):
        size = self.state.board.size
        m, cell = self.cfg.margin, self.cfg.cell
        start = m
        end = m + cell * (size - 1)

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
        # Optional: hide hints when game over or during AI busy turn
        if self.state.is_over:
            return

        r = self.cfg.hint_radius
        fill = "black" if self.state.next_player is Color.BLACK else "white"
        outline = "gray25"

        for p in self.state.legal_moves():
            x, y = self.p_to_xy(p)
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline=outline)

    def draw_last_move_marker(self):
        if self.state.last_move is None or self.state.is_over:
            return
        x, y = self.p_to_xy(self.state.last_move)
        r = self.cfg.stone_radius + 6
        self.canvas.create_oval(x - r, y - r, x + r, y + r, outline="red", width=2)

    def update_status(self):
        if self.state.is_over:
            self.status.config(
                text=f"GAME OVER | Captures B:{self.state.captures_black} W:{self.state.captures_white}{ai_txt}"
            )
        else:
            self.status.config(
                text=f"Turn: {self.state.next_player.value} | "
                     f"Captures B:{self.state.captures_black} W:{self.state.captures_white} | "
                     f"Passes: {self.state.consecutive_passes}{ai_txt}"
            )

    # ---------- actions ----------
    def on_new_game(self):
        self.state = GameState.new(size=self.size)
        self.redraw()

    def on_pass(self):
        if self.state.is_over:
            return
        self.state = self.state.pass_turn()
        self.redraw()

    # ---------- events ----------
    def on_click(self, event):
        if self.state.is_over:
            return

        p = self.xy_to_point(event.x, event.y)
        if p is None:
            return

        try:
            self.state = self.state.play(p)
        except GoError as e:
            self.status.config(text=f"Illegal move: {e}")
            self.root.after(900, self.update_status)
            return

        self.redraw()


def run_gui(size: int = 9):
    root = tk.Tk()
    GoApp(root, size=size)
    root.mainloop()
