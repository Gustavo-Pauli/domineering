""" The Board class handles the VIEW of the game board """

import tkinter as tk
# from src.domineering_game import Game  # Commented out to allow testing with mock objects
from src.settings import *
from src.game import Game

class Board:
    def __init__(self, game_instance: Game, parent_frame: tk.Frame, click_callback=None, hover_callback=None, leave_callback=None):
        self.parent_frame = parent_frame
        self.game = game_instance
        self.click_callback = click_callback
        self.hover_callback = hover_callback
        self.leave_callback = leave_callback
        self.cell_size = CELL_SIZE

        self.canvas = tk.Canvas(
            parent_frame,
            width=self.game.board_size * self.cell_size,
            height=self.game.board_size * self.cell_size,
            bg="white"
        )
        self.canvas.pack()

        self._bind_events()
        self.refresh_board() # initial draw

    # START: Board utils

    def _canvas_coords_to_cell(self, x: int, y: int) -> tuple[int, int] | None:
        """Convert canvas x,y coords to (row,col)."""
        row = int(y // self.cell_size)
        col = int(x // self.cell_size)
        if 0 <= row < self.game.board_size and 0 <= col < self.game.board_size:
            return (row, col)
        else:
            return None
        
    # END: Board utils

    # START: Input handling
        
    def _bind_events(self):
        """Bind canvas events for clicks and mouse movement."""
        self.canvas.bind("<Button-1>", self._handle_click)
        self.canvas.bind("<Motion>", self._handle_motion)
        self.canvas.bind("<Leave>", self._handle_leave)

    def _handle_click(self, event: tk.Event) -> None:
        """ Calls the click callback for handling cell clicks. """
        coords = self._canvas_coords_to_cell(event.x, event.y)
        if coords is not None and self.click_callback:
            row, col = coords
            self.click_callback(row, col)

    def _handle_motion(self, event: tk.Event) -> None:
        """ Calls the hover callback for handling mouse movement over cells. """
        coords = self._canvas_coords_to_cell(event.x, event.y)
        if coords is not None and self.hover_callback:
            row, col = coords
            self.hover_callback(row, col)

    def _handle_leave(self, event: tk.Event) -> None:
        """ Calls the leave callback when mouse leaves the canvas area. """
        if self.leave_callback:
            self.leave_callback() # TODO: check if this is needed like this

    # END: Input handling

    # START: Drawing methods

    def refresh_board(self) -> None:
        """Redraws the entire board based on the current self.game state."""
        self.canvas.delete("all")
        self._draw_grid()
        self._draw_dominos()

    def _draw_grid(self) -> None:
        for row in range(self.game.board_size):
            for col in range(self.game.board_size):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                color = "white" if (row + col) % 2 == 0 else "#f0f0f0"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, width=1, outline=GRID_COLOR)

    def _draw_dominos(self) -> None:
        drawn_vertical = set()
        drawn_horizontal = set()

        for r in range(self.game.board_size):
            for c in range(self.game.board_size):
                state = self.game.get_cell_state(r, c)
                if state == VERTICAL and (r, c) not in drawn_vertical:
                    self._draw_single_domino(r, c, orientation=VERTICAL)
                    drawn_vertical.add((r, c))
                    drawn_vertical.add((r + 1, c))
                elif state == HORIZONTAL and (r, c) not in drawn_horizontal:
                    self._draw_single_domino(r, c, orientation=HORIZONTAL)
                    drawn_horizontal.add((r, c))
                    drawn_horizontal.add((r, c + 1))

    def preview_move(self, row: int, col: int, orientation: str) -> None:
        """Draws a semi-transparent preview of a move."""
        # self.clear_preview()  # TODO: removed for now, verify if needed
        if self.game.is_valid_move(row, col, orientation):
            self._draw_single_domino(row, col, orientation, preview=True)

    def clear_preview(self) -> None:
        """Clears any active preview shapes from the canvas."""
        self.canvas.delete("preview")

    def _draw_single_domino(self, row: int, col: int, orientation: str, preview: bool = False) -> None:
        color = VERTICAL_PLAYER_COLOR if orientation == VERTICAL else HORIZONTAL_PLAYER_COLOR
        x1, y1 = col * self.cell_size, row * self.cell_size

        if orientation == VERTICAL:
            x2, y2 = x1 + self.cell_size, y1 + (2 * self.cell_size)
        else:
            x2, y2 = x1 + (2 * self.cell_size), y1 + self.cell_size

        tags = "preview" if preview else "domino"
        stipple = "gray50" if preview else ""

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=2, stipple=stipple, tags=tags)

    # END: Drawing methods

    # ======== OLD =========

#     def _draw_single_domino(self, row: int, col: int, is_vertical: bool, preview: bool = False) -> None:
#         color = VERTICAL_PLAYER_COLOR if is_vertical else HORIZONTAL_PLAYER_COLOR
#         x1, y1 = col * self.cell_size, row * self.cell_size

#         if is_vertical:
#             x2, y2 = x1 + self.cell_size, y1 + (2 * self.cell_size)
#         else:
#             x2, y2 = x1 + (2 * self.cell_size), y1 + self.cell_size

#         tags = "preview" if preview else "domino"
#         stipple = "gray50" if preview else ""

#         self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=2, stipple=stipple, tags=tags)

#     def place_vertical_domino(self, row, col):
#         self.game.current_orientation = self.game.VERTICAL
#         self.game.place_domino(row, col)
#         self.refresh_board()

#     def place_horizontal_domino(self, row, col):
#         self.game.current_orientation = self.game.HORIZONTAL
#         self.game.place_domino(row, col)
#         self.refresh_board()

#     def is_valid_move(self, row, col, is_vertical=True):
#         orientation = self.game.VERTICAL if is_vertical else self.game.HORIZONTAL
#         return self.game.is_valid_move(row, col, orientation)

#     def clear_preview(self):
#         """Clear any preview rectangle."""
#         if self.preview_id:
#             self.canvas.delete("preview")
#             self.preview_id = None

#     def reset(self):
#         self.game.clear_board()
#         self.refresh_board()
