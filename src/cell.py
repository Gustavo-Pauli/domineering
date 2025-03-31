import tkinter as tk

class Cell:
    """
    Represents a single cell on the Domineering game board
    """
    EMPTY = "empty"
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    
    def __init__(self, board, row, col, parent_frame, size, bg_color):
        self.board = board
        self.row = row
        self.col = col
        self.size = size
        self.state = self.EMPTY
        
        # Create the canvas for this cell
        self.canvas = tk.Canvas(
            parent_frame,
            width=size,
            height=size,
            bg=bg_color,
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        self.canvas.grid(row=row, column=col)
        
        # Bind events (using lambdas to pass the cell's position)
        self.canvas.bind("<Button-1>", lambda event: self._on_click())
        self.canvas.bind("<Enter>", lambda event: self._on_hover())
        self.canvas.bind("<Leave>", lambda event: self._on_leave())
    
    def _on_click(self):
        """Handle click on this cell"""
        if self.board.click_callback:
            self.board.click_callback(self.row, self.col)
    
    def _on_hover(self):
        """Handle mouse hover on this cell"""
        if self.board.hover_callback:
            self.board.hover_callback(self.row, self.col)
    
    def _on_leave(self):
        """Handle mouse leave from this cell"""
        if self.board.leave_callback:
            self.board.leave_callback(self.row, self.col)
    
    def set_state(self, state):
        """Set the cell's state and update its appearance"""
        self.state = state
        self.redraw()
        
    def is_empty(self):
        """Check if the cell is empty"""
        return self.state == self.EMPTY
    
    def clear(self):
        """Clear all contents of the cell"""
        self.canvas.delete("all")
        
    def redraw(self):
        """Redraw the cell based on its current state"""
        self.clear()
        
        if self.state == self.VERTICAL:
            self._draw_domino_part(self.board.settings.vertical_player_color)
        elif self.state == self.HORIZONTAL:
            self._draw_domino_part(self.board.settings.horizontal_player_color)
    
    def draw_preview(self, is_vertical):
        """Draw a preview of a domino part in this cell"""
        color = self.board.settings.vertical_player_color if is_vertical else self.board.settings.horizontal_player_color
        
        padding = 5
        # Draw with transparency effect for preview
        self.canvas.create_rectangle(
            padding, padding, 
            self.size - padding, 
            self.size - padding,
            fill=color, outline="black", width=2,
            stipple="gray50",  # Creates a transparent effect
            tags="preview"
        )
    
    def clear_preview(self):
        """Clear any preview from this cell"""
        self.canvas.delete("preview")
    
    def _draw_domino_part(self, color):
        """Draw part of a domino in this cell"""
        padding = 5
        self.canvas.create_rectangle(
            padding, padding, 
            self.size - padding, 
            self.size - padding,
            fill=color, outline="black", width=2
        )
    
    def highlight(self, color):
        """Highlight the cell with a colored border"""
        padding = 2
        self.canvas.create_rectangle(
            padding, padding, 
            self.size - padding, 
            self.size - padding,
            outline=color, width=2,
            tags="highlight"
        )
    
    def clear_highlight(self):
        """Remove any highlighting from the cell"""
        self.canvas.delete("highlight")
