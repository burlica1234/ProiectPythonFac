from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox
from dataclasses import dataclass
from pathlib import Path

from go_game.engine.game_state import GameState
from go_game.engine.types import Point, Color
from go_game.engine.errors import GoError

from go_game.engine.ai import RandomAI
from go_game.engine.serialization import save_session, load_session


@dataclass
class RenderConfig:
    margin: int = 30
    cell: int = 40
    stone_radius: int = 16
    hint_radius: int = 5


class GoApp:
    def __init__(self, root: tk.Tk, size: int = 9):
        self.root = root
        self.root.title("Go - Phase 6")

        self.cfg = RenderConfig()
        self.ai = RandomAI()

        # Session path (autosave)
        self.session_dir = Path.cwd() / "sessions"
        self.autosave_path = self.session_dir / "last_session.json"

        # State + settings
        self.size = size
        self.state = GameState.new(size=self.size)

        self.ai_enabled = True
        self.ai_color = Color.WHITE
        self.ai_busy = False

        # Undo/Redo stacks
        self.undo_stack: list[GameState] = []
        self.redo_stack: list[GameState] = []

        # -------- Controls (top) --------
        self.controls = tk.Frame(root)
        self.controls.pack(fill="x", padx=8, pady=6)

        self.pass_btn = tk.Button(self.controls, text="Pass", command=self.on_pass)
        self.pass_btn.pack(side="left")

        self.undo_btn = tk.Button(self.controls, text="Undo", command=self.on_undo)
        self.undo_btn.pack(side="left", padx=(8, 0))

        self.redo_btn = tk.Button(self.controls, text="Redo", command=self.on_redo)
        self.redo_btn.pack(side="left", padx=(8, 0))

        self.new_btn = tk.Button(self.controls, text="New Game", command=self.on_new_game)
        self.new_btn.pack(side="left", padx=(8, 0))

        self.ai_btn = tk.Button(self.controls, text="AI: ON", command=self.toggle_ai)
        self.ai_btn.pack(side="left", padx=(8, 0))

        # Board size selection
        tk.Label(self.controls, text="Size:").pack(side="left", padx=(12, 4))
        self.size_var = tk.StringVar(value=str(self.size))
        self.size_menu = tk.OptionMenu(self.controls, self.size_var, "9", "13", "19")
        self.size_menu.pack(side="left")

        self.apply_size_btn = tk.Button(self.controls, text="Apply", command=self.apply_board_size)
        self.apply_size_btn.pack(side="left", padx=(6, 0))

        # Save/Load
        self.save_btn = tk.Button(self.controls, text="Save", command=self.on_save)
        self.save_btn.pack(side="left", padx=(12, 0))

        self.load_btn = tk.Button(self.controls, text="Load", command=self.on_load)
        self.load_btn.pack(side="left", padx=(6, 0))

        # -------- Canvas --------
        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.canvas.pack()

        self.status = tk.Label(root, text="", anchor="w")
        self.status.pack(fill="x", padx=8, pady=6)

        self.canvas.bind("<Button-1>", self.on_click)

        # First layout & render
        self._resize_canvas_for_board()
        self.redraw()

        # Try autosave load (optional): uncomment if you want auto-restore at startup.
        # self.try_autoload()

        self.maybe_ai_turn()

    # ---------- layout ----------
    def _resize_canvas_for_board(self):
        w = self.cfg.margin * 2 + self.cfg.cell * (self.size - 1)
        h = self.cfg.margin * 2 + self.cfg.cell * (self.size - 1)
        self.canvas.config(width=w, height=h)

    # ---------- coordinate mapping ----------
    def p_to_xy(self, p: Point) -> tuple[int, int]:
        x = self.cfg.margin + p.col * self.cfg.cell
        y = self.cfg.margin + p.row * self.cfg.cell
        return x, y

    def xy_to_point(self, x: int, y: int) -> Point | None:
        col = round((x - self.cfg.margin) / self.cfg.cell)
        row = round((y - self.cfg.margin) / self.cfg.cell)
        if 0 <= row < self.size and 0 <= col < self.size:
            ix, iy = self.p_to_xy(Point(row, col))
            if abs(ix - x) <= self.cfg.cell * 0.35 and abs(iy - y) <= self.cfg.cell * 0.35:
                return Point(row, col)
        return None

    # ---------- undo/redo helpers ----------
    def push_undo(self):
        self.undo_stack.append(self.state)
        self.redo_stack.clear()

    def autosave(self):
        try:
            save_session(
                self.autosave_path,
                self.state,
                ai_enabled=self.ai_enabled,
                ai_color=self.ai_color,
                board_size=self.size,
            )
        except Exception:
            # Autosave should never crash the app
            pass

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
        m, cell = self.cfg.margin, self.cfg.cell
        start = m
        end = m + cell * (self.size - 1)

        for i in range(self.size):
            x = m + i * cell
            y = m + i * cell
            self.canvas.create_line(start, y, end, y)
            self.canvas.create_line(x, start, x, end)

    def draw_stones(self):
        r = self.cfg.stone_radius
        for row in range(self.size):
            for col in range(self.size):
                p = Point(row, col)
                stone = self.state.board.get(p)
                if stone is None:
                    continue
                x, y = self.p_to_xy(p)
                fill = "black" if stone is Color.BLACK else "white"
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline="black", width=2)

    def draw_hints(self):
        if self.state.is_over:
            return
        r = self.cfg.hint_radius
        fill = "black" if self.state.next_player is Color.BLACK else "white"
        for p in self.state.legal_moves():
            x, y = self.p_to_xy(p)
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline="gray25")

    def draw_last_move_marker(self):
        if self.state.last_move is None or self.state.is_over:
            return
        x, y = self.p_to_xy(self.state.last_move)
        r = self.cfg.stone_radius + 6
        self.canvas.create_oval(x - r, y - r, x + r, y + r, outline="red", width=2)

    # ---------- status / controls ----------
    def update_status(self):
        ai_txt = f" | AI: {'ON' if self.ai_enabled else 'OFF'} ({self.ai_color.value})"

        if self.state.is_over:
            sb = self.state.score()
            if sb.score_black > sb.score_white:
                winner = "B"
            elif sb.score_white > sb.score_black:
                winner = "W"
            else:
                winner = "DRAW"

            self.status.config(
                text=(
                    f"GAME OVER | "
                    f"Territory B:{sb.territory_black} W:{sb.territory_white} | "
                    f"Captures B:{sb.captures_black} W:{sb.captures_white} | "
                    f"Score B:{sb.score_black} W:{sb.score_white} | "
                    f"Winner: {winner}"
                    f"{ai_txt}"
                )
            )
        else:
            self.status.config(
                text=f"Turn: {self.state.next_player.value} | "
                     f"Captures B:{self.state.captures_black} W:{self.state.captures_white} | "
                     f"Passes: {self.state.consecutive_passes}{ai_txt}"
            )

    def update_controls(self):
        # Disable during AI thinking
        busy = self.ai_busy

        self.pass_btn.config(state=("disabled" if self.state.is_over or busy else "normal"))
        self.new_btn.config(state=("disabled" if busy else "normal"))
        self.ai_btn.config(state=("disabled" if busy else "normal"))
        self.undo_btn.config(state=("normal" if (not busy and len(self.undo_stack) > 0) else "disabled"))
        self.redo_btn.config(state=("normal" if (not busy and len(self.redo_stack) > 0) else "disabled"))
        self.apply_size_btn.config(state=("disabled" if busy else "normal"))
        self.size_menu.config(state=("disabled" if busy else "normal"))
        self.save_btn.config(state=("disabled" if busy else "normal"))
        self.load_btn.config(state=("disabled" if busy else "normal"))

    # ---------- settings ----------
    def toggle_ai(self):
        self.ai_enabled = not self.ai_enabled
        self.ai_btn.config(text=f"AI: {'ON' if self.ai_enabled else 'OFF'}")
        self.redraw()
        self.maybe_ai_turn()
        self.autosave()

    def apply_board_size(self):
        if self.ai_busy:
            return
        try:
            new_size = int(self.size_var.get())
            if new_size not in (9, 13, 19):
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid size", "Choose 9, 13, or 19.")
            return

        if new_size == self.size:
            return

        # New game with selected size
        self.size = new_size
        self.state = GameState.new(size=self.size)
        self.undo_stack.clear()
        self.redo_stack.clear()

        self._resize_canvas_for_board()
        self.redraw()
        self.maybe_ai_turn()
        self.autosave()

    # ---------- main actions ----------
    def on_new_game(self):
        if self.ai_busy:
            return
        self.size = int(self.size_var.get())
        self.state = GameState.new(size=self.size)
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._resize_canvas_for_board()
        self.redraw()
        self.maybe_ai_turn()
        self.autosave()

    def on_pass(self):
        if self.state.is_over or self.ai_busy:
            return
        if self.ai_enabled and self.state.next_player is self.ai_color:
            return

        self.push_undo()
        self.state = self.state.pass_turn()
        self.redraw()
        self.autosave()
        self.maybe_ai_turn()

    def on_undo(self):
        if self.ai_busy or not self.undo_stack:
            return
        self.redo_stack.append(self.state)
        self.state = self.undo_stack.pop()
        self.redraw()
        self.autosave()

    def on_redo(self):
        if self.ai_busy or not self.redo_stack:
            return
        self.undo_stack.append(self.state)
        self.state = self.redo_stack.pop()
        self.redraw()
        self.autosave()
        self.maybe_ai_turn()

    # ---------- persistence ----------
    def on_save(self):
        if self.ai_busy:
            return
        path = filedialog.asksaveasfilename(
            title="Save session",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
        )
        if not path:
            return
        save_session(path, self.state, ai_enabled=self.ai_enabled, ai_color=self.ai_color, board_size=self.size)
        self.status.config(text="Saved session.")
        self.root.after(900, self.update_status)

    def on_load(self):
        if self.ai_busy:
            return
        path = filedialog.askopenfilename(
            title="Load session",
            filetypes=[("JSON files", "*.json")],
        )
        if not path:
            return

        state, ai_enabled, ai_color, size = load_session(path)
        self.state = state
        self.ai_enabled = ai_enabled
        self.ai_color = ai_color
        self.size = size
        self.size_var.set(str(size))

        self.undo_stack.clear()
        self.redo_stack.clear()

        self.ai_btn.config(text=f"AI: {'ON' if self.ai_enabled else 'OFF'}")
        self._resize_canvas_for_board()
        self.redraw()
        self.autosave()
        self.maybe_ai_turn()

    # ---------- AI ----------
    def maybe_ai_turn(self):
        if self.state.is_over:
            return
        if not self.ai_enabled:
            return
        if self.state.next_player is not self.ai_color:
            return
        if self.ai_busy:
            return

        self.ai_busy = True
        self.status.config(text="AI is thinking...")
        self.update_controls()
        self.root.after(150, self.do_ai_turn)

    def do_ai_turn(self):
        try:
            if self.state.is_over or not self.ai_enabled or self.state.next_player is not self.ai_color:
                return

            # AI action is a state transition => should be undoable
            self.push_undo()

            move = self.ai.pick_move(self.state)
            if move is None:
                self.state = self.state.pass_turn()
            else:
                self.state = self.state.play(move)

        finally:
            self.ai_busy = False
            self.redraw()
            self.autosave()
            self.maybe_ai_turn()

    # ---------- events ----------
    def on_click(self, event):
        if self.state.is_over or self.ai_busy:
            return
        if self.ai_enabled and self.state.next_player is self.ai_color:
            return

        p = self.xy_to_point(event.x, event.y)
        if p is None:
            return

        try:
            self.push_undo()
            self.state = self.state.play(p)
        except GoError as e:
            # remove the undo snapshot if move failed
            if self.undo_stack and self.undo_stack[-1] == self.state:
                self.undo_stack.pop()
            self.status.config(text=f"Illegal move: {e}")
            self.root.after(900, self.update_status)
            return

        self.redraw()
        self.autosave()
        self.maybe_ai_turn()


def run_gui(size: int = 9):
    root = tk.Tk()
    GoApp(root, size=size)
    root.mainloop()
