class Settings:
    def __init__(self):
        # Board configuration
        self.board_size = 8  # Default 8x8 grid
        self.cell_size = 64  # Size of each cell in pixels
        
        # Visual settings
        self.grid_color = "#cccccc"
        self.vertical_player_color = "blue"
        self.horizontal_player_color = "red"
        self.highlight_color = "#ffff99"  # Highlight for valid moves
        self.bg_color = "#2f4255"  # Background color
