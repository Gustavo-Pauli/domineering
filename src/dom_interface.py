import tkinter as tk
from tkinter import simpledialog, messagebox
from src.board import Board
from src.settings import *
from src.game import Game
from dog.dog_interface import DogPlayerInterface
from dog.dog_actor import DogActor
from typing import Dict, Callable
import queue
from functools import partial
import copy



class DomInterface(DogPlayerInterface):
    """Main player interface class that coordinates between game logic and UI"""

    def __init__(self):
        # -- MODEL --
        self.game = Game()

        # -- Window --
        self.main_window = tk.Tk()
        self.main_window.title("Domineering")
        self.main_window.iconbitmap("assets/icon.ico")
        self.main_window.geometry("680x860")
        self.main_window.resizable(False, False)
        self.main_window["bg"]=BG_COLOR

        # -- VIEW --
        self.turn_label: tk.Label
        self.player_moves_label: tk.Label
        self.opponent_moves_label: tk.Label
        self.board_frame: tk.Frame
        self.build_ui_components()
        self.build_menu()
        self.board = Board(
            game_instance=self.game,
            parent_frame=self.board_frame,
            click_callback=self._on_cell_click,
            hover_callback=self._on_cell_hover,
            leave_callback=self._on_cell_leave
        )

        self.main_window.mainloop()

    # def _on_cell_hover(self, row: int, col: int):
    #   if self.is_my_turn and self.my_player_orientation:
    #       self.board.preview_move(row, col, self.my_player_orientation)

    # ========= OLD =========

    #     # DOG
    #     self.player_name = simpledialog.askstring(title="Nome do Jogador", prompt="Digite seu nome:")
    #     self.dog_server_interface = DogActor()
    #     message = self.dog_server_interface.initialize(self.player_name, self)
    #     messagebox.showinfo(message=message)
    #     print(message)
    #     print(f"Player name: {self.player_name}")

    #     self.main_window.mainloop() # iniciar o loop de eventos

    # START: UI

    def build_ui_components(self):
        """Build the main window and its components."""
        self.board_frame = tk.Frame(self.main_window, width=560, height=560, bg="white", bd=2, relief="solid")
        self.board_frame.place(relx=0.5, rely=0.09, anchor="n")
        gui_frame = tk.Frame(self.main_window, width=560, height=200, bg=BG_COLOR)
        gui_frame.place(relx=0.5, rely=0.9, anchor="s")
        self.turn_label = tk.Label(gui_frame, text="Waiting for match...", font=("Arial", 20, "bold"), fg="white", bg=BG_COLOR)
        self.turn_label.pack(expand=True)
        score_frame = tk.Frame(gui_frame, bg=BG_COLOR)
        score_frame.pack(pady=20)
        tk.Label(score_frame, text="You", font=("Arial", 16, "bold"), fg="white", bg=BG_COLOR).grid(row=0, column=0, padx=20)
        tk.Label(score_frame, text="Opponent", font=("Arial", 16, "bold"), fg="white", bg=BG_COLOR).grid(row=0, column=1, padx=20)
        self.player_moves_label = tk.Label(score_frame, text="0", font=("Arial", 16), fg="white", bg=BG_COLOR)
        self.player_moves_label.grid(row=1, column=0, padx=20, pady=5)
        self.opponent_moves_label = tk.Label(score_frame, text="0", font=("Arial", 16), fg="white", bg=BG_COLOR)
        self.opponent_moves_label.grid(row=1, column=1, padx=20, pady=5)

    def build_menu(self):
        menubar = tk.Menu(self.main_window)
        actions_menu = tk.Menu(menubar, tearoff=0)
        actions_menu.add_command(label="Start Match", command=self.start_match)
        menubar.add_cascade(label="Actions", menu=actions_menu)
        self.main_window.config(menu=menubar)

    # called by the actions menu
    def start_match(self):
        print("Starting match...")

    # start_status = self.dog_server_interface.start_match(2)
    # message = start_status.get_message()
    # messagebox.showinfo(message=message)
    # self.start_game(start_status)

    # match_status = self.board.get_match_status()


    # match_status = self.board.get_match_status()
    # if match_status == 1:
    #     answer = messagebox.askyesno("START", "Deseja iniciar uma nova partida?")
    #     if answer:
    #         start_status = self.dog_server_interface.start_match(2)
    #         code = start_status.get_code()
    #         message = start_status.get_message()
    #         if code == "0" or code == "1":
    #             messagebox.showinfo(message=message)
    #         else:  #    (code=='2')
    #             players = start_status.get_players()
    #             local_player_id = start_status.get_local_id()
    #             self.board.start_match(players, local_player_id)
    #             game_state = self.board.get_status()
    #             self.update_gui(game_state)
    #             messagebox.showinfo(message=start_status.get_message())


    # END: UI

    # START: Input Handlers

    def _on_cell_click(self, row: int, col: int):
        if not self.is_my_turn or self.game.winner or self.my_player_orientation is None: return
        orientation = self.my_player_orientation
        if self.game.is_valid_move(row, col, orientation):
            # --- THIS IS THE CRITICAL CHANGE ---
            # Do not apply the move locally. Only send it to the server.
            # The server will broadcast it back, and we will process it then.

            # Create the move dictionary for the server.
            move_dict = {'row': row, 'col': col, 'orientation': orientation}

            # Add the required `match_status` key for the DOG framework.
            # To do this, we "look ahead" to see if this move ends the game.
            temp_game = copy.deepcopy(self.game)
            temp_game.place_domino(row, col, orientation)
            if temp_game.is_game_over(): # Check if the *next* player has any moves
                move_dict["match_status"] = "finished"
            else:
                move_dict["match_status"] = "next"

            self.dog_server_interface.send_move(move_dict)

            # After sending, disable the turn locally to prevent sending multiple moves.
            self.is_my_turn = False
            self.turn_label.config(text="Opponent's Turn")

    def _on_cell_hover(self, row: int, col: int):

        if self.game.my_turn():
            self.board.preview_move(row, col, self.game.local_player_orientation)

    def _on_cell_leave(self):
        self.board.clear_preview()

    # END: Input Handlers

#   def restore_initial_state(self):
#     """Restore the initial state of the game."""
#     print("Restaurando estado inicial...")
#     # Add restoration logic here

#   def _on_cell_click_internal(self, row, col):
#     """Handle cell click and place using the orientation in Board.game if needed."""
#     print(f"Cell clicked: {row}, {col}")
#     self.board.clear_preview()
#     # Domino placement now draws one piece automatically
#     if self.board.game.current_orientation == self.board.game.VERTICAL:
#         self.board.place_vertical_domino(row, col)
#         self.board.game.toggle_orientation()
#     else:
#         self.board.place_horizontal_domino(row, col)
#         self.board.game.toggle_orientation()

#   def _on_cell_hover_internal(self, row, col):
#     """Preview potential move based on current orientation in self.board.game."""
#     # Board handles single-piece preview
#     is_vertical = (self.board.game.current_orientation == self.board.game.VERTICAL)
#     self.board.preview_move(row, col, is_vertical)

#   def _on_cell_leave_internal(self, row, col):
#     """Clear the move preview."""
#     self.board.clear_preview()

#   def refresh_ui(self):
#     """Refresh all views"""
#     self.board.refresh_board()
#     self.player_moves_label.config(text=str(self.board.game.get_player_moves()))
#     self.opponent_moves_label.config(text=str(self.board.game.get_opponent_moves()))

#   def start_match(self):
#     """Start a new match"""
#     print("Starting match...")
#     start_status = self.dog_server_interface.start_match(2)
#     message = start_status.get_message()
#     messagebox.showinfo(message=message)
#     self.start_game(start_status)

#   def start_game(self, start_status):
#     """Start a new game"""
#     print("Starting game...")
#     self.board.initialize()
#     self.player_moves_label.config(text="0")
#     self.opponent_moves_label.config(text="0")

#   # DOG
#   def receive_start(self, start_status):
#     message = start_status.get_message()
#     code = start_status.get_code()
#     if code == 2:
#         self.start_game(start_status)
#         messagebox.showinfo(message=message)
#     else:
#         messagebox.showinfo(message=message)
#         print(f"Start status: {code}")

#   # DOG
#   def receive_move(self, a_move):
#     print(f"Received move: {a_move}")
#     self.board.update_board(a_move)
#     self.opponent_moves_label.config(text=str(int(self.opponent_moves_label.cget("text")) + 1))
#     self.update_board()

#   # DOG
#   def receive_withdrawal_notification(self):
#     print("Received withdrawal notification")
#     self.board.handle_opponent_withdrawal()
