import tkinter as tk
from src.cell import Cell
from src.domineering_game import Game
from src.settings import *

class Board:
    def __init__(self, parent_interface, parent_frame, click_callback=None, hover_callback=None, leave_callback=None):
        self.parent_interface = parent_interface
        self.parent_frame = parent_frame
        self.click_callback = click_callback
        self.hover_callback = hover_callback
        self.leave_callback = leave_callback
        self.cell_size = CELL_SIZE
        self.game = Game(board_size=BOARD_SIZE)

        # Instead of multiple canvases, use one canvas for the whole board
        self.canvas = tk.Canvas(
            parent_frame,
            width=self.game.board_size * self.cell_size,
            height=self.game.board_size * self.cell_size,
            bg="white"
        )
        self.canvas.pack()

        # Store Cell objects in a 2D list
        self.cells = [
            [Cell(row, col) for col in range(self.game.board_size)]
            for row in range(self.game.board_size)
        ]

        # Track preview rectangle ID (if any)
        self.preview_id = None

        self._bind_events()
        self.refresh_board()

    def _bind_events(self):
        """Bind canvas events for clicks and mouse movement."""
        self.canvas.bind("<Button-1>", self._handle_click)
        self.canvas.bind("<Motion>", self._handle_motion)
        self.canvas.bind("<Leave>", self._handle_leave)

    def _canvas_coords_to_cell(self, x, y):
        """Convert canvas x,y coords to (row,col)."""
        row = int(y // self.cell_size)
        col = int(x // self.cell_size)
        return (row, col)

    def _handle_click(self, event):
        row, col = self._canvas_coords_to_cell(event.x, event.y)
        if self.click_callback:
            self.click_callback(row, col)

    def _handle_motion(self, event):
        row, col = self._canvas_coords_to_cell(event.x, event.y)
        if 0 <= row < self.game.board_size and 0 <= col < self.game.board_size:
            if self.hover_callback:
                self.hover_callback(row, col)

    def _handle_leave(self, _event):
        if self.leave_callback:
            # We pass -1, -1 or similar so the callback knows we're off the board
            self.leave_callback(-1, -1)

    def refresh_board(self):
        """Redraw the entire board with background squares and dominos."""
        self.canvas.delete("all")
        board_size = self.game.board_size

        # Draw checkerboard squares
        for row in range(board_size):
            for col in range(board_size):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                color = "white" if (row + col) % 2 == 0 else "#f0f0f0"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, width=1, outline=GRID_COLOR)

        # Draw placed dominos as single rectangles
        for row in range(board_size):
            for col in range(board_size):
                cell_state = self.game.get_cell_state(row, col)
                if cell_state == self.game.VERTICAL:
                    # Draw only if it's the top part of vertical domino
                    # to avoid drawing twice
                    if row + 1 < board_size and self.game.get_cell_state(row + 1, col) == self.game.VERTICAL:
                        self._draw_domino(row, col, vertical=True)
                elif cell_state == self.game.HORIZONTAL:
                    # Draw only if it's the left part of horizontal domino
                    if col + 1 < board_size and self.game.get_cell_state(row, col + 1) == self.game.HORIZONTAL:
                        self._draw_domino(row, col, vertical=False)

    def _draw_domino(self, row, col, vertical=True, preview=False):
        """Draw a single rectangle spanning two cells."""
        color = VERTICAL_PLAYER_COLOR if vertical else HORIZONTAL_PLAYER_COLOR
        x1 = col * self.cell_size
        y1 = row * self.cell_size

        if vertical:
            x2 = x1 + self.cell_size
            y2 = y1 + (2 * self.cell_size)  # covers two squares vertically
        else:
            x2 = x1 + (2 * self.cell_size)  # covers two squares horizontally
            y2 = y1 + self.cell_size

        tag = "preview" if preview else "domino"
        stipple_val = "gray50" if preview else ""

        self.canvas.create_rectangle(x1, y1, x2, y2,
                                     fill=color, outline="black",
                                     width=2, stipple=stipple_val,
                                     tags=tag)

    def place_vertical_domino(self, row, col):
        self.game.current_orientation = self.game.VERTICAL
        self.game.place_domino(row, col)
        self.refresh_board()

    def place_horizontal_domino(self, row, col):
        self.game.current_orientation = self.game.HORIZONTAL
        self.game.place_domino(row, col)
        self.refresh_board()

    def is_valid_move(self, row, col, is_vertical=True):
        orientation = self.game.VERTICAL if is_vertical else self.game.HORIZONTAL
        return self.game.is_valid_move(row, col, orientation)

    def preview_move(self, row, col, is_vertical=True):
        """Draw a single preview rectangle if valid."""
        self.clear_preview()
        orientation = self.game.VERTICAL if is_vertical else self.game.HORIZONTAL
        if not self.game.is_valid_move(row, col, orientation):
            return
        self._draw_domino(row, col, vertical=is_vertical, preview=True)
        # We won't track a full ID list, just clear all "preview" on next call
        self.preview_id = True

    def clear_preview(self):
        """Clear any preview rectangle."""
        if self.preview_id:
            self.canvas.delete("preview")
            self.preview_id = None

    def reset(self):
        self.game.clear_board()
        self.refresh_board()
