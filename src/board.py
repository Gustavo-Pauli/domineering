import tkinter as tk
from src.cell import Cell
from src.domineering_game import Game

class Board:
    def __init__(self, parent_interface, parent_frame, settings, click_callback=None, hover_callback=None, leave_callback=None):
        self.parent_interface = parent_interface
        self.parent_frame = parent_frame
        self.settings = settings
        self.click_callback = click_callback
        self.hover_callback = hover_callback
        self.leave_callback = leave_callback
        self.cell_size = settings.cell_size
        self.preview_cells = []  # Track cells currently being previewed
        self.cells = []
        
        # Use a game instance to manage logic
        self.game = Game(board_size=settings.board_size)
        
        self.create_board()
    
    def create_board(self):
        """Create or recreate the game board display"""
        # Clear existing board
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        board_size = self.settings.board_size
        self.cells = []
        
        # Create cells
        for row in range(board_size):
            row_cells = []
            for col in range(board_size):
                # Determine the cell's background color (checkerboard pattern)
                bg_color = "white" if (row + col) % 2 == 0 else "#f0f0f0"
                
                # Create a Cell object for this position
                cell = Cell(
                    self,  # Reference to this Board object
                    row, 
                    col, 
                    self.parent_frame, 
                    self.cell_size, 
                    bg_color
                )
                
                row_cells.append(cell)
            self.cells.append(row_cells)
        
        # Initialize all cells
        self.refresh_board()
    
    def refresh_board(self):
        """Refresh all cells based on game state."""
        board_size = self.game.board_size
        for row in range(board_size):
            for col in range(board_size):
                cell = self.cells[row][col]
                cell_state = self.game.get_cell_state(row, col)
                # Redraw the cell based on game logic
                if cell_state == self.game.VERTICAL:
                    cell.set_state(Cell.VERTICAL)
                elif cell_state == self.game.HORIZONTAL:
                    cell.set_state(Cell.HORIZONTAL)
                else:
                    cell.set_state(Cell.EMPTY)
    
    def place_vertical_domino(self, row, col):
        """Place a vertical domino, ignoring local logic and using the game."""
        self.game.current_orientation = self.game.VERTICAL
        success = self.game.place_domino(row, col)
        self.refresh_board()
        return success
    
    def place_horizontal_domino(self, row, col):
        """Place a horizontal domino, ignoring local logic and using the game."""
        self.game.current_orientation = self.game.HORIZONTAL
        success = self.game.place_domino(row, col)
        self.refresh_board()
        return success
    
    def is_valid_move(self, row, col, is_vertical=True):
        """Check validity via the game."""
        orientation = self.game.VERTICAL if is_vertical else self.game.HORIZONTAL
        return self.game.is_valid_move(row, col, orientation)
    
    def preview_move(self, row, col, is_vertical=True):
        """Show preview only if the game says the move is valid."""
        # Clear any existing preview first
        self.clear_preview()
        
        orientation = self.game.VERTICAL if is_vertical else self.game.HORIZONTAL
        if not self.game.is_valid_move(row, col, orientation):
            return
        
        # Store the cells being previewed
        self.preview_cells = []
        
        if is_vertical:
            # Vertical domino preview
            if row < self.settings.board_size - 1:
                self.cells[row][col].draw_preview(is_vertical=True)
                self.cells[row + 1][col].draw_preview(is_vertical=True)
                self.preview_cells = [(row, col), (row + 1, col)]
        else:
            # Horizontal domino preview
            if col < self.settings.board_size - 1:
                self.cells[row][col].draw_preview(is_vertical=False)
                self.cells[row][col + 1].draw_preview(is_vertical=False)
                self.preview_cells = [(row, col), (row, col + 1)]
    
    def clear_preview(self):
        """Remove any domino placement preview"""
        for row, col in self.preview_cells:
            if row < len(self.cells) and col < len(self.cells[row]):
                self.cells[row][col].clear_preview()
        
        # Clear the list of previewed cells
        self.preview_cells = []
    
    def reset(self):
        """Reset the entire board/game to empty."""
        self.game.clear_board()
        self.refresh_board()
