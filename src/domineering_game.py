
class Game:
    """
    Core Domineering game logic without direct UI references.
    Manages a board_size x board_size grid storing 'vertical',
    'horizontal', or None for each cell.
    """

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"

    def __init__(self, board_size=8):
        self.board_size = board_size
        # 2D array storing None, 'vertical', or 'horizontal'
        self._board_state = [[None for _ in range(board_size)] for _ in range(board_size)]
        self.current_orientation = self.VERTICAL  # Example default

    def toggle_orientation(self):
        """Switch between vertical/horizontal placement."""
        if self.current_orientation == self.VERTICAL:
            self.current_orientation = self.HORIZONTAL
        else:
            self.current_orientation = self.VERTICAL

    def get_cell_state(self, row, col):
        """Return the state of a cell."""
        return self._board_state[row][col]

    def place_domino(self, row, col):
        """
        Attempt to place a domino with the current orientation.
        Returns True if successful, False if invalid move.
        """
        if not self.is_valid_move(row, col, self.current_orientation):
            return False

        if self.current_orientation == self.VERTICAL:
            self._board_state[row][col] = self.VERTICAL
            self._board_state[row + 1][col] = self.VERTICAL
        else:
            self._board_state[row][col] = self.HORIZONTAL
            self._board_state[row][col + 1] = self.HORIZONTAL

        return True

    def is_valid_move(self, row, col, orientation):
        """Check if the current orientation domino can be placed at (row, col)."""
        if row < 0 or col < 0 or row >= self.board_size or col >= self.board_size:
            return False

        if orientation == self.VERTICAL:
            if row >= self.board_size - 1:
                return False
            return (self._board_state[row][col] is None and
                    self._board_state[row + 1][col] is None)
        else:
            if col >= self.board_size - 1:
                return False
            return (self._board_state[row][col] is None and
                    self._board_state[row][col + 1] is None)

    def clear_board(self):
        """Reset the board to empty."""
        for r in range(self.board_size):
            for c in range(self.board_size):
                self._board_state[r][c] = None

    # Additional logic for checking game over, counting moves, etc. could go here.
