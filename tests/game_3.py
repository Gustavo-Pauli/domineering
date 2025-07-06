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
        self._board_state: list[list[str | None]] = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.local_player_orientation: str | None = None
        self.current_player_orientation: str = VERTICAL
        self.winner = None
        self.domino_counts: dict[str, int] = {VERTICAL: 0, HORIZONTAL: 0}
        self.match_status: int = 1  # see comments above for dictionary

    # START: Assessors

    def get_match_status(self) -> int:
        """Returns the current match status."""
        return self.match_status
    
    def get_local_player_orientation(self) -> str | None:
        """Returns the orientation of the local player."""
        return self.local_player_orientation
    
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
        # A sub-atividade "Efetuar colocação de peça" é chamada aqui.
        # A validação acontece primeiro.
        if not self.is_valid_move(row, col, orientation):
            return False

        #* Ação (após `Retornar jogada válida`): Colocar peça
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
        """
        Check if the domino with specified orientation can be placed at (row, col).
        """
        # Implicitamente verifica se a jogada está dentro do tabuleiro
        if row < 0 or col < 0 or row >= BOARD_SIZE or col >= BOARD_SIZE:
            return False

        #* Verificar se casa clicada está desocupada
        if self._board_state[row][col] != EMPTY:
            return False

        #* Verificar tipo de peça
        if orientation == VERTICAL:
            #* Avaliar se a posição abaixo existe no tabuleiro
            if row >= BOARD_SIZE - 1:
                return False
            #* Avaliar se posição abaixo está ocupada
            is_valid = self._board_state[row + 1][col] == EMPTY
            return is_valid
        else:  # HORIZONTAL
            #* Avaliar se a posição a direita existe no tabuleiro
            if col >= BOARD_SIZE - 1:
                return False
            #* Avaliar se posição a direita está ocupada
            is_valid = self._board_state[row][col + 1] == EMPTY
            return is_valid