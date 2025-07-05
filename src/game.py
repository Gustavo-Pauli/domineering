from src.settings import *

##### match_status dictionary #####
# 1 - no match (initial state)
# 2 - finished match (game with winner)
# 3 - your turn, match in progress
# 4 - not your turn, match in progress - waiting move from opponent
# 5 - match abandoned by opponent

class Game:
    """
    === MODEL ===
    Core Domineering game logic.
    Manages the board state, player turns, scores, and all game rules.
    It is the single source of truth for the game state.
    """

    def __init__(self):
        self._board_state: list[list[str | None]] = []  # [[None for _ in range(board_size)] for _ in range(board_size)]
        self.local_player_orientation: str | None = None
        self.current_player_orientation: str = VERTICAL
        self.winner = None
        self.domino_counts: dict[str, int] = {}
        self.match_status: int = 1  # see comments above for dictionary

        self.restore_initial_state()

    # START: Assessors

    def get_match_status(self) -> int:
        """Returns the current match status."""
        return self.match_status
    
    # END: Assessors
    
    def restore_initial_state(self) -> None:
        """Reset the game to the initial states."""
        self._board_state = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.local_player_orientation = None
        self.current_player_orientation = VERTICAL
        self.winner = None
        self.domino_counts = {VERTICAL: 0, HORIZONTAL: 0}
        self.match_status = 1

    def is_my_turn(self) -> bool:
        """Check if it's the current player's turn based on their orientation."""
        return self.local_player_orientation == self.current_player_orientation

    def switch_player(self) -> None:
        """Toggle the current player and check for a game-over condition."""
        self.current_player_orientation = HORIZONTAL if self.current_player_orientation == VERTICAL else VERTICAL
        if self.is_game_over():
            # The player who was supposed to move but couldn't has lost.
            # So the other player (the one who just moved) is the winner.
            self.winner = HORIZONTAL if self.current_player_orientation == VERTICAL else VERTICAL

    def is_game_over(self) -> bool:
        """
        Checks if the current player has any valid moves left.
        If not, the game is over.
        """
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.is_valid_move(r, c, self.current_player_orientation):
                    return False  # Found at least one valid move
        return True  # No valid moves found for the current player

    def get_cell_state(self, row: int, col: int) -> str | None:
        """Return the state of a cell."""
        return self._board_state[row][col]
    
    def place_domino(self, row: int, col: int, orientation: str) -> bool:
        """
        Attempt to place a domino with the specified orientation.
        Returns True if successful, False if invalid move.
        """
        if not self.is_valid_move(row, col, orientation):
            return False

        if orientation == VERTICAL:
            self._board_state[row][col] = VERTICAL
            self._board_state[row + 1][col] = VERTICAL
        else:
            self._board_state[row][col] = HORIZONTAL
            self._board_state[row][col + 1] = HORIZONTAL

        # Update domino counts
        self.domino_counts[orientation] += 1
        return True

    def is_valid_move(self, row: int, col: int, orientation: str) -> bool:
        """Check if the domino with specified orientation can be placed at (row, col)."""
        if row < 0 or col < 0 or row >= BOARD_SIZE or col >= BOARD_SIZE:
            return False

        if orientation == VERTICAL:
            if row >= BOARD_SIZE - 1:
                return False
            return (self._board_state[row][col] == EMPTY and
                    self._board_state[row + 1][col] == EMPTY)
        else:  # HORIZONTAL
            if col >= BOARD_SIZE - 1:
                return False
            return (self._board_state[row][col] == EMPTY and
                    self._board_state[row][col + 1] == EMPTY)

#     def toggle_orientation(self):
#         """Switch between vertical/horizontal placement."""
#         if self.current_orientation == self.VERTICAL:
#             self.current_orientation = self.HORIZONTAL
#         else:
#             self.current_orientation = self.VERTICAL

#     def get_cell_state(self, row, col):
#         """Return the state of a cell."""
#         return self._board_state[row][col]

#     def place_domino(self, row, col):
#         """
#         Attempt to place a domino with the current orientation.
#         Returns True if successful, False if invalid move.
#         """
#         if not self.is_valid_move(row, col, self.current_orientation):
#             return False

#         if self.current_orientation == self.VERTICAL:
#             self._board_state[row][col] = self.VERTICAL
#             self._board_state[row + 1][col] = self.VERTICAL
#         else:
#             self._board_state[row][col] = self.HORIZONTAL
#             self._board_state[row][col + 1] = self.HORIZONTAL

#         return True

#     def is_valid_move(self, row, col, orientation):
#         """Check if the current orientation domino can be placed at (row, col)."""
#         if row < 0 or col < 0 or row >= BOARD_SIZE or col >= BOARD_SIZE:
#             return False

#         if orientation == self.VERTICAL:
#             if row >= BOARD_SIZE - 1:
#                 return False
#             return (self._board_state[row][col] is None and
#                     self._board_state[row + 1][col] is None)
#         else:
#             if col >= BOARD_SIZE - 1:
#                 return False
#             return (self._board_state[row][col] is None and
#                     self._board_state[row][col + 1] is None)

#     def clear_board(self):
#         """Reset the board to empty."""
#         for r in range(BOARD_SIZE):
#             for c in range(BOARD_SIZE):
#                 self._board_state[r][c] = None

#     # Additional logic for checking game over, counting moves, etc. could go here.
