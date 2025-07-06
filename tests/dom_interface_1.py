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
    """
    CONTROLLER
    This class serves as the main player interface, coordinating between Game MODEL, Board VIEW, and Tkinter VIEW.
    """

    ## Activity Diagram: Iniciar Programa ##
    def __init__(self):
        # -- MODEL --
        #* Instanciar Game
        self.game = Game()

        # -- Window --
        #* Instanciar elementos da GUI
        self.main_window = tk.Tk()
        self.main_window.title("Domineering")
        self.main_window.iconbitmap("assets/icon.ico")
        self.main_window.geometry("640x864")
        self.main_window.resizable(False, False)
        self.main_window["bg"]=BG_COLOR

        # -- VIEW --
        self.turn_label: tk.Label
        self.player_moves_label: tk.Label
        self.opponent_moves_label: tk.Label
        self.build_ui_components()
        self.build_menu()
        #* Instanciar Tabuleiro
        self.board = Board(
            game_instance=self.game,
            window=self.main_window,
            click_callback=self._on_cell_click,
            hover_callback=self._on_cell_hover,
            leave_callback=self._on_cell_leave
        )
        #* Atualizar interface
        self.refresh_ui()

        # DOG
        #* Solicitar nome do jogador
        self.player_name = simpledialog.askstring(title="Nome do Jogador", prompt="Digite seu nome:")
        #* Inicializar DogActor
        self.dog_server_interface = DogActor()
        #* Retornar resultado do pedido de conexão
        message = self.dog_server_interface.initialize(self.player_name, self)
        messagebox.showinfo(message=message)
        print("Nome:", self.player_name)

        self.main_window.mainloop()


    # def _on_cell_hover(self, row: int, col: int):
    #   if self.is_my_turn and self.my_player_orientation:
    #       self.board.preview_move(row, col, self.my_player_orientation)

    # START: UI

    def build_ui_components(self):
        """Build the main window and its components."""
        print("Building UI components...")
        gui_frame = tk.Frame(self.main_window, width=560, height=200, bg=BG_COLOR)
        gui_frame.place(relx=0.5, rely=1, y=-32, anchor="s")
        self.turn_label = tk.Label(gui_frame, text="", font=("Arial", 20, "bold"), fg="white", bg=BG_COLOR) # The text will be updated on refresh, based on the game state
        self.turn_label.pack(expand=True)
        score_frame = tk.Frame(gui_frame, bg=BG_COLOR)
        score_frame.pack(pady=32)
        tk.Label(score_frame, text="Você", font=("Arial", 16, "bold"), fg="white", bg=BG_COLOR).grid(row=0, column=0, padx=32)
        tk.Label(score_frame, text="Oponente", font=("Arial", 16, "bold"), fg="white", bg=BG_COLOR).grid(row=0, column=1, padx=32)
        self.player_moves_label = tk.Label(score_frame, text="0", font=("Arial", 16), fg="white", bg=BG_COLOR)
        self.player_moves_label.grid(row=1, column=0, padx=20, pady=5)
        self.opponent_moves_label = tk.Label(score_frame, text="0", font=("Arial", 16), fg="white", bg=BG_COLOR)
        self.opponent_moves_label.grid(row=1, column=1, padx=20, pady=5)

    def build_menu(self):
        print("Building menu...")
        menubar = tk.Menu(self.main_window)
        actions_menu = tk.Menu(menubar, tearoff=0)
        actions_menu.add_command(label="Iniciar Partida", command=self.start_match)
        menubar.add_cascade(label="Ações", menu=actions_menu)
        self.main_window.config(menu=menubar)

    def refresh_ui(self):
        """Refresh views and update labels based on the game state."""
        print("Refreshing UI...")
        self.board.refresh_board()
        self.board.clear_preview()
        
        # Update turn label based on match_status
        if self.game.match_status == 1:  # no match (initial state)
            self.turn_label.config(text="Esperando iniciar partida...")
        elif self.game.match_status == 2:  # finished match (game with winner)
            self.turn_label.config(text=f"Ganhador: {self.game.winner.capitalize()}!")
        elif self.game.match_status == 3:  # your turn, match in progress
            self.turn_label.config(text="Sua Vez")
        elif self.game.match_status == 4:  # not your turn, match in progress
            self.turn_label.config(text="Vez do Oponente")
        elif self.game.match_status == 5:  # match abandoned by opponent
            self.turn_label.config(text="Oponente abandonou a partida")

        # Update move counts
        if self.game.local_player_orientation:
            opponent_orientation = HORIZONTAL if self.game.local_player_orientation == VERTICAL else VERTICAL
            self.player_moves_label.config(text=str(self.game.domino_counts[self.game.local_player_orientation]))
            self.opponent_moves_label.config(text=str(self.game.domino_counts[opponent_orientation]))

    # called by the actions menu
    def start_match(self):
        print("Starting match...")
        #* Verificar status da partida
        match_status = self.game.get_match_status()
        if match_status == 1:
            #* Perguntar se o usuário quer começar uma nova partida
            answer = messagebox.askyesno("START", "Deseja iniciar uma nova partida?")
            if answer:
                #* Requisição para iniciar a partida
                start_status = self.dog_server_interface.start_match(2)
                code = start_status.get_code()
                message = start_status.get_message()
                #* Avaliar resposta
                if code == "0" or code == "1":
                    #* Notificar problema
                    messagebox.showinfo(message=message)
                else:  # code=='2'
                    self._setup_match(start_status)

    # END: UI

    # START: DOG Interface

    def receive_start(self, start_status):
        """
        Handles the start of a match, received from the DOG server.
        """
        #* Restaurar estado inicial
        self.game.restore_initial_state()
        self._setup_match(start_status)

    def _setup_match(self, start_status):
        """
        Sets up a match with the given start status.
        Common functionality between start_match and receive_start.
        """
        #* Atribuir vertical e horizontal para os jogadores (jogador com as peças verticais sempre inicia)
        player1, _ = start_status.get_players() # [name, id, number] (number 1=vertical, 2=horizontal)
        if player1[2] == "1":
            #* Instanciar status da partida para aguardar jogada local
            self.game.local_player_orientation = VERTICAL
            self.game.match_status = 3
        else:
            #* Instanciar status da partida para aguardar jogada remota
            self.game.local_player_orientation = HORIZONTAL
            self.game.match_status = 4
        #* Atualizar interface
        self.refresh_ui()
        #* Notificar sucesso
        messagebox.showinfo(message=start_status.get_message())

    # END: DOG Interface   

    # START: Input Handlers

    def _on_cell_click(self, row: int, col: int):
        #* Início (Diagrama 1: Posicionar peça)
        
        #* Ação: Verificar status da partida
        match_status = self.game.get_match_status()

        #* Decisão: A partida está em andamento?
        if match_status not in [3, 4]:
            #* Se [NOT partida]
            #* Ação: Notificar que não há partida em andamento
            messagebox.showwarning("Partida não iniciada", "Não há nenhuma partida em andamento. Inicie uma no menu 'Ações'.")
            #* Fim.
            return

        #* Se [partida]
        #* Ação: Verificar turno
        #* Decisão: É o turno do jogador local?
        if not self.game.is_my_turn():
            #* Se [else] (não é o turno local)
            #* Fim.
            return
        
        #* Se [turno_local]
        #* Ação: Efetuar colocação de peça (Sub-atividade do Diagrama 3)
        #    A validação e colocação são tratadas pelo método `place_domino` do Game.
        orientation = self.game.get_local_player_orientation()
        is_valid_placement = self.game.place_domino(row, col, orientation)

        #* Decisão: A colocação da peça foi válida?
        if not is_valid_placement:
            #* Se [NOT casas_validas]
            #* Ação: Notificar jogada inválida
            messagebox.showerror("Jogada Inválida", "Você não pode posicionar uma peça neste local.")
            #* Fim.
            return

        #* Se [casas_validas]
        #* Ação: Atualizar interface (desenha a peça que acabamos de colocar)
        self.refresh_ui()

        #* Ação: Verificar encerramento de partida (Sub-atividade do Diagrama 5)
        #    A lógica é encapsulada em `switch_player`, que define um vencedor se o próximo jogador não tiver movimentos.
        self.game.switch_player()

        move_dict = {'row': row, 'col': col, 'orientation': orientation}

        #* Decisão: A partida terminou?
        if self.game.winner:
            #* Se [encerrada]
            self.game.match_status = 2  # Estado de partida finalizada
            #* Ação: Enviar jogada e notificar jogador vencedor
            move_dict["match_status"] = "finished"
            self.dog_server_interface.send_move(move_dict)
            self.refresh_ui() # Atualiza a UI para mostrar a mensagem de vencedor
            messagebox.showinfo("Fim de Jogo", f"O jogador com as peças '{self.game.winner.capitalize()}' venceu!")
            #* Fim.
        else:
            #* Se [NOT encerrada]
            self.game.match_status = 4  # Estado de "aguardando jogada do oponente"
            #* Ação: Enviar jogada e trocar turno
            move_dict["match_status"] = "next"
            self.dog_server_interface.send_move(move_dict)
            self.refresh_ui() # Atualiza a UI para "Vez do Oponente"
            #* Fim.

    def _on_cell_hover(self, row: int, col: int):
        #* Verificar status da partida
        if self.game.get_match_status() == 3:
            #* Verificar turno
            if self.game.is_my_turn():
                #* Verificar se casa cujo mouse está em cima está ocupada
                if self.game.get_cell_state(row, col) is EMPTY:
                    #* Verificar tipo de peça
                    orientation = self.game.get_local_player_orientation()
                    if orientation == HORIZONTAL:
                        #* Avaliar se a posição a direita existe no tabuleiro
                        #* & Avaliar se posição a direita está ocupada
                        if col < BOARD_SIZE - 1 and self.game.get_cell_state(row, col + 1) is EMPTY:
                            #* Ocultar preview de peça
                            self.board.clear_preview()
                            #* Exibir preview da peça
                            self.board.preview_move(row, col, orientation)
                    else:  # VERTICAL
                        #* Avaliar se a posição abaixo existe no tabuleiro
                        #* & Avaliar se posição abaixo está ocupada
                        if row < BOARD_SIZE - 1 and self.game.get_cell_state(row + 1, col) is EMPTY:
                            #* Ocultar preview de peça
                            self.board.clear_preview()
                            #* Exibir preview da peça
                            self.board.preview_move(row, col, orientation)

    def _on_cell_leave(self):
        """Clear the preview when the mouse leaves the board."""
        self.board.clear_preview()

    # END: Input Handlers