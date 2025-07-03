"""
Simple visual test for Board view component.
This file creates a mock Game class and provides interactive testing for the Board.
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.board import Board
from src.settings import *

class MockGame:
    """Mock Game class for testing Board view independently"""
    
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    
    def __init__(self, board_size=8):
        self.board_size = board_size
        self._board_state = [[None for _ in range(board_size)] for _ in range(board_size)]
        self.current_orientation = self.VERTICAL
        
    def get_cell_state(self, row, col):
        """Return the state of a cell."""
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            return self._board_state[row][col]
        return None
        
    def is_valid_move(self, row, col, orientation):
        """Check if a domino can be placed at (row, col) with given orientation."""
        if row < 0 or col < 0 or row >= self.board_size or col >= self.board_size:
            return False
            
        if orientation == self.VERTICAL:
            if row >= self.board_size - 1:
                return False
            return (self._board_state[row][col] is None and
                    self._board_state[row + 1][col] is None)
        else:  # HORIZONTAL
            if col >= self.board_size - 1:
                return False
            return (self._board_state[row][col] is None and
                    self._board_state[row][col + 1] is None)
    
    def place_domino(self, row, col, orientation):
        """Place a domino at (row, col) with given orientation."""
        if not self.is_valid_move(row, col, orientation):
            return False
            
        if orientation == self.VERTICAL:
            self._board_state[row][col] = self.VERTICAL
            self._board_state[row + 1][col] = self.VERTICAL
        else:  # HORIZONTAL
            self._board_state[row][col] = self.HORIZONTAL
            self._board_state[row][col + 1] = self.HORIZONTAL
            
        return True
    
    def clear_board(self):
        """Reset the board to empty."""
        for r in range(self.board_size):
            for c in range(self.board_size):
                self._board_state[r][c] = None

class BoardTester:
    """Visual testing interface for Board component"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_game_and_board()
        self.setup_controls()
        self.test_results = []
        
    def setup_window(self):
        """Setup the main testing window"""
        self.root.title("Board View Tester")
        self.root.geometry("900x700")
        self.root.configure(bg=BG_COLOR)
        
        # Title
        title_label = tk.Label(
            self.root, 
            text="Board View Testing Interface", 
            font=("Arial", 16, "bold"),
            fg="white", 
            bg=BG_COLOR
        )
        title_label.pack(pady=10)
        
    def setup_game_and_board(self):
        """Setup the mock game and board"""
        self.mock_game = MockGame(8)
        self.current_orientation = self.mock_game.VERTICAL
        
        # Create frame for the board
        self.board_frame = tk.Frame(
            self.root,
            width=560,
            height=560,
            bg="white",
            bd=2,
            relief="solid"
        )
        self.board_frame.pack(pady=20)
        
        # Create the board with callbacks
        self.board = Board(
            game_instance=self.mock_game,
            parent_frame=self.board_frame,
            click_callback=self._on_cell_click,
            hover_callback=self._on_cell_hover,
            leave_callback=self._on_cell_leave
        )
        
    def setup_controls(self):
        """Setup control buttons and info display"""
        controls_frame = tk.Frame(self.root, bg=BG_COLOR)
        controls_frame.pack(pady=20)
        
        # Orientation display
        self.orientation_label = tk.Label(
            controls_frame,
            text=f"Current: {self.current_orientation.upper()}",
            font=("Arial", 12, "bold"),
            fg="white",
            bg=BG_COLOR
        )
        self.orientation_label.grid(row=0, column=0, columnspan=2, pady=5)
        
        # Control buttons
        tk.Button(
            controls_frame,
            text="Toggle Orientation",
            command=self.toggle_orientation,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        ).grid(row=1, column=0, padx=5, pady=5)
        
        tk.Button(
            controls_frame,
            text="Clear Board",
            command=self.clear_board,
            bg="#f44336",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        ).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(
            controls_frame,
            text="Run Auto Tests",
            command=self.run_auto_tests,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        ).grid(row=2, column=0, padx=5, pady=5)
        
        tk.Button(
            controls_frame,
            text="Fill Random",
            command=self.fill_random,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        ).grid(row=2, column=1, padx=5, pady=5)
        
        # Status display
        self.status_label = tk.Label(
            controls_frame,
            text="Click on cells to place dominos. Hover to preview.",
            font=("Arial", 10),
            fg="white",
            bg=BG_COLOR,
            wraplength=400
        )
        self.status_label.grid(row=3, column=0, columnspan=2, pady=10)
        
    def _on_cell_click(self, row, col):
        """Handle cell click for placing dominos"""
        if self.mock_game.place_domino(row, col, self.current_orientation):
            self.board.refresh_board()
            self.status_label.config(text=f"Placed {self.current_orientation} domino at ({row}, {col})")
            self.toggle_orientation()  # Auto-switch orientation
        else:
            self.status_label.config(text=f"Invalid move at ({row}, {col})")
            
    def _on_cell_hover(self, row, col):
        """Handle cell hover for preview"""
        self.board.clear_preview()
        self.board.preview_move(row, col, self.current_orientation)
        
    def _on_cell_leave(self):
        """Handle mouse leaving board"""
        self.board.clear_preview()
        
    def toggle_orientation(self):
        """Switch between vertical and horizontal orientation"""
        if self.current_orientation == self.mock_game.VERTICAL:
            self.current_orientation = self.mock_game.HORIZONTAL
        else:
            self.current_orientation = self.mock_game.VERTICAL
        self.orientation_label.config(text=f"Current: {self.current_orientation.upper()}")
        
    def clear_board(self):
        """Clear the entire board"""
        self.mock_game.clear_board()
        self.board.refresh_board()
        self.status_label.config(text="Board cleared")
        
    def fill_random(self):
        """Fill board with some random dominos for testing"""
        import random
        self.clear_board()
        
        placements = 0
        attempts = 0
        max_attempts = 50
        
        while placements < 10 and attempts < max_attempts:
            row = random.randint(0, 7)
            col = random.randint(0, 7)
            orientation = random.choice([self.mock_game.VERTICAL, self.mock_game.HORIZONTAL])
            
            if self.mock_game.place_domino(row, col, orientation):
                placements += 1
            attempts += 1
            
        self.board.refresh_board()
        self.status_label.config(text=f"Randomly placed {placements} dominos")
        
    def run_auto_tests(self):
        """Run automated tests for board functionality"""
        self.test_results = []
        
        # Test 1: Clear board
        self.clear_board()
        all_empty = all(
            self.mock_game.get_cell_state(r, c) is None 
            for r in range(8) for c in range(8)
        )
        self.test_results.append(("Board Clear", all_empty))
        
        # Test 2: Place vertical domino
        success = self.mock_game.place_domino(0, 0, self.mock_game.VERTICAL)
        self.test_results.append(("Vertical Placement", success))
        
        # Test 3: Place horizontal domino
        success = self.mock_game.place_domino(2, 0, self.mock_game.HORIZONTAL)
        self.test_results.append(("Horizontal Placement", success))
        
        # Test 4: Invalid placement (overlapping)
        success = self.mock_game.place_domino(0, 0, self.mock_game.HORIZONTAL)
        self.test_results.append(("Invalid Placement Prevention", not success))
        
        # Test 5: Edge boundary
        success = self.mock_game.place_domino(7, 7, self.mock_game.VERTICAL)
        self.test_results.append(("Edge Boundary Check", not success))
        
        # Test 6: Refresh board after changes
        initial_state = self.mock_game.get_cell_state(0, 0)
        self.board.refresh_board()
        final_state = self.mock_game.get_cell_state(0, 0)
        self.test_results.append(("Board Refresh", initial_state == final_state))
        
        # Show results
        self.show_test_results()
        
    def show_test_results(self):
        """Display test results in a popup"""
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        
        results_text = f"Test Results: {passed}/{total} passed\n\n"
        for test_name, result in self.test_results:
            status = "✓ PASS" if result else "✗ FAIL"
            results_text += f"{test_name}: {status}\n"
            
        messagebox.showinfo("Test Results", results_text)
        self.status_label.config(text=f"Auto tests completed: {passed}/{total} passed")
        
    def run(self):
        """Start the testing interface"""
        self.root.mainloop()

if __name__ == "__main__":
    print("Starting Board View Tester...")
    tester = BoardTester()
    tester.run()
