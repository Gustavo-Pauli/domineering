import tkinter as tk

class Cell:
    """
    Represents a single cell in the Domineering game board data structure,
    without its own Canvas.
    """
    EMPTY = "empty"
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.state = self.EMPTY

    def set_state(self, state):
        """Set the cell's state."""
        self.state = state

    def is_empty(self):
        return self.state == self.EMPTY
