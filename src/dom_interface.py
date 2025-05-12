import tkinter as tk
from tkinter import simpledialog, messagebox
from src.board import Board
from src.settings import *
from dog.dog_interface import DogPlayerInterface
from dog.dog_actor import DogActor

class DomInterface(DogPlayerInterface):
  """Main player interface class that coordinates between game logic and UI"""

  def __init__(self):
    self.main_window = tk.Tk()

    self.build_window()
    self.build_menu()

    # Board handles logic via its internal Game instance
    self.board = Board(
        parent_interface=self,
        parent_frame=self.board_frame, 
        click_callback=self._on_cell_click_internal,
        hover_callback=self._on_cell_hover_internal,
        leave_callback=self._on_cell_leave_internal
    )

    # DOG
    self.player_name = simpledialog.askstring(title="Nome do Jogador", prompt="Digite seu nome:")
    self.dog_server_interface = DogActor()
    message = self.dog_server_interface.initialize(self.player_name, self)
    messagebox.showinfo(message=message)
    print(message)
    print(f"Player name: {self.player_name}")

    self.main_window.mainloop() # iniciar o loop de eventos

    
  def build_window(self):
    """Build the main window and its components."""
    # window settings
    self.main_window.title("Domineering")
    self.main_window.iconbitmap("assets/icon.ico")
    self.main_window.geometry("680x860")
    self.main_window.resizable(False, False)
    self.main_window["bg"]=BG_COLOR
    
    # create the game frame board with a 8x8 grid
    self.board_frame = tk.Frame(
      self.main_window,
      width=560,
      height=560,
      bg="white",
      bd=2,
      relief="solid"
    )
    self.board_frame.place(relx=0.5, rely=0.09, anchor="n")

    # create the gui bottom frame
    self.gui_frame = tk.Frame(
      self.main_window,
      width=560,
      height=200,
      bg="#2f4255"
    )
    self.gui_frame.place(relx=0.5, rely=0.9, anchor="s")
    turn_label = tk.Label(self.gui_frame, text="Sua vez", font=("Arial", 20, "bold"), fg="white", bg="#2f4255")
    turn_label.pack(expand=True)

    # create the score frame
    score_frame = tk.Frame(self.gui_frame, bg="#2f4255")
    score_frame.pack(pady=20)

    player_header = tk.Label(score_frame, text="Você", font=("Arial", 16, "bold"), fg="white", bg="#2f4255")
    player_header.grid(row=0, column=0, padx=20)
    opponent_header = tk.Label(score_frame, text="Oponente", font=("Arial", 16, "bold"), fg="white", bg="#2f4255")
    opponent_header.grid(row=0, column=1, padx=20)

    self.player_moves_label = tk.Label(score_frame, text="0", font=("Arial", 16), fg="white", bg="#2f4255")
    self.player_moves_label.grid(row=1, column=0, padx=20, pady=5)
    self.opponent_moves_label = tk.Label(score_frame, text="0", font=("Arial", 16), fg="white", bg="#2f4255")
    self.opponent_moves_label.grid(row=1, column=1, padx=20, pady=5)
    
  def build_menu(self):
    """Create the menu bar with "Ações"."""
    menubar = tk.Menu(self.main_window)
    acoes_menu = tk.Menu(menubar, tearoff=0)
    acoes_menu.add_command(label="Iniciar partida", command=self.start_match)
    acoes_menu.add_command(label="Restaurar estado inicial", command=self.restore_initial_state)
    menubar.add_cascade(label="Ações", menu=acoes_menu)
    self.main_window.config(menu=menubar)
    
  def restore_initial_state(self):
    """Restore the initial state of the game."""
    print("Restaurando estado inicial...")
    # Add restoration logic here
    
  def _on_cell_click_internal(self, row, col):
    """Handle cell click and place using the orientation in Board.game if needed."""
    print(f"Cell clicked: {row}, {col}")
    self.board.clear_preview()
    # Domino placement now draws one piece automatically
    if self.board.game.current_orientation == self.board.game.VERTICAL:
        self.board.place_vertical_domino(row, col)
        self.board.game.toggle_orientation()
    else:
        self.board.place_horizontal_domino(row, col)
        self.board.game.toggle_orientation()
    
  def _on_cell_hover_internal(self, row, col):
    """Preview potential move based on current orientation in self.board.game."""
    # Board handles single-piece preview
    is_vertical = (self.board.game.current_orientation == self.board.game.VERTICAL)
    self.board.preview_move(row, col, is_vertical)
    
  def _on_cell_leave_internal(self, row, col):
    """Clear the move preview."""
    self.board.clear_preview()
    
  def update_board(self):
    """Tell the board to refresh its display"""
    if hasattr(self, 'board'):
        self.board.refresh_board()

  def start_match(self):
    """Start a new match"""
    print("Starting match...")
    start_status = self.dog_server_interface.start_match(2)
    message = start_status.get_message()
    messagebox.showinfo(message=message)
    self.start_game(start_status)

  def start_game(self, start_status):
    """Start a new game"""
    print("Starting game...")
    self.board.initialize()
    self.player_moves_label.config(text="0")
    self.opponent_moves_label.config(text="0")


  def receive_start(self, start_status):
    message = start_status.get_message()
    code = start_status.get_code()
    if code == 2:
        self.start_game(start_status)
        messagebox.showinfo(message=message)
    else:
        messagebox.showinfo(message=message)
        print(f"Start status: {code}")