import tkinter as tk
from tkinter import messagebox
import time
import threading

class Board:
    """Represents the Mancala game board state"""
    
    def __init__(self):
        # Initialize board: [P1 pits (0-5), P1 store (6), P2 pits (7-12), P2 store (13)]
        self.pits = [4] * 6 + [0] + [4] * 6 + [0]
        self.current_player = 1  # Player 1 starts
        
    def get_player_pits(self, player):
        """Get pit indices for a player"""
        if player == 1:
            return list(range(0, 6))
        else:
            return list(range(7, 13))
    
    def get_player_store(self, player):
        """Get store index for a player"""
        return 6 if player == 1 else 13
    
    def get_opposite_pit(self, pit):
        """Get the opposite pit index"""
        return 12 - pit
    
    def is_valid_move(self, pit, player):
        """Check if a move is valid"""
        player_pits = self.get_player_pits(player)
        return pit in player_pits and self.pits[pit] > 0
    
    def is_game_over(self):
        """Check if the game is over"""
        p1_empty = all(self.pits[i] == 0 for i in range(0, 6))
        p2_empty = all(self.pits[i] == 0 for i in range(7, 13))
        return p1_empty or p2_empty
    
    def get_winner(self):
        """Get the winner of the game"""
        if self.pits[6] > self.pits[13]:
            return 1
        elif self.pits[13] > self.pits[6]:
            return 2
        else:
            return 0  # Tie

class MancalaGame:
    """Handles game logic and rules"""
    
    def __init__(self):
        self.board = Board()
        self.move_history = []
    
    def make_move(self, pit):
        """Execute a move and return animation steps"""
        if not self.board.is_valid_move(pit, self.board.current_player):
            return None
        
        # Record move
        self.move_history.append((self.board.current_player, pit, self.board.pits[:]))
        
        # Get seeds from selected pit
        seeds = self.board.pits[pit]
        self.board.pits[pit] = 0
        
        # Sow seeds
        current_pit = pit
        animation_steps = []
        
        for _ in range(seeds):
            current_pit = (current_pit + 1) % 14
            
            # Skip opponent's store
            if (self.board.current_player == 1 and current_pit == 13) or \
               (self.board.current_player == 2 and current_pit == 6):
                current_pit = (current_pit + 1) % 14
            
            self.board.pits[current_pit] += 1
            animation_steps.append(current_pit)
        
        # Check for capture
        last_pit = current_pit
        player_pits = self.board.get_player_pits(self.board.current_player)
        
        if (last_pit in player_pits and 
            self.board.pits[last_pit] == 1 and 
            self.board.pits[self.board.get_opposite_pit(last_pit)] > 0):
            
            # Capture seeds
            captured = self.board.pits[self.board.get_opposite_pit(last_pit)]
            self.board.pits[self.board.get_opposite_pit(last_pit)] = 0
            self.board.pits[last_pit] = 0
            
            store = self.board.get_player_store(self.board.current_player)
            self.board.pits[store] += captured + 1
        
        # Check for extra turn
        extra_turn = last_pit == self.board.get_player_store(self.board.current_player)
        
        # Switch players if no extra turn
        if not extra_turn:
            self.board.current_player = 3 - self.board.current_player
        
        # Check if game is over
        if self.board.is_game_over():
            self._collect_remaining_seeds()
        
        return animation_steps, extra_turn
    
    def _collect_remaining_seeds(self):
        """Collect remaining seeds when game ends"""
        # Collect Player 1's remaining seeds
        p1_remaining = sum(self.board.pits[0:6])
        for i in range(0, 6):
            self.board.pits[i] = 0
        self.board.pits[6] += p1_remaining
        
        # Collect Player 2's remaining seeds
        p2_remaining = sum(self.board.pits[7:13])
        for i in range(7, 13):
            self.board.pits[i] = 0
        self.board.pits[13] += p2_remaining
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.board = Board()
        self.move_history = []

class MancalaGUI:
    """GUI interface for the Mancala game"""
    
    def __init__(self):
        self.game = MancalaGame()
        self.root = tk.Tk()
        self.root.title("Mancala Game")
        self.root.geometry("800x400")
        self.root.configure(bg='#2E8B57')
        self.root.resizable(False, False)
        
        # Colors
        self.colors = {
            'bg': '#2E8B57',
            'pit': '#8B4513',
            'pit_hover': '#A0522D',
            'store': '#654321',
            'seed': '#FFD700',
            'p1_color': '#FF6B6B',
            'p2_color': '#4ECDC4',
            'text': '#FFFFFF'
        }
        
        # Animation variables
        self.animating = False
        self.pit_buttons = []
        self.pit_labels = []
        self.store_labels = []
        
        self.setup_gui()
        self.update_display()
    
    def setup_gui(self):
        """Setup the GUI components"""
        # Title
        title_label = tk.Label(self.root, text="MANCALA", 
                              font=('Arial', 24, 'bold'), 
                              fg=self.colors['text'], 
                              bg=self.colors['bg'])
        title_label.pack(pady=10)
        
        # Game frame
        game_frame = tk.Frame(self.root, bg=self.colors['bg'])
        game_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Player 2 pits (top row)
        p2_frame = tk.Frame(game_frame, bg=self.colors['bg'])
        p2_frame.pack(fill='x', pady=5)
        
        tk.Label(p2_frame, text="Player 2", font=('Arial', 14, 'bold'), 
                fg=self.colors['p2_color'], bg=self.colors['bg']).pack()
        
        p2_pits_frame = tk.Frame(p2_frame, bg=self.colors['bg'])
        p2_pits_frame.pack()
        
        # Player 2 store (left)
        self.store_labels.append(tk.Label(p2_pits_frame, text="0", 
                                         font=('Arial', 16, 'bold'),
                                         fg=self.colors['text'],
                                         bg=self.colors['store'],
                                         width=4, height=3,
                                         relief='raised', bd=3))
        self.store_labels[0].pack(side='left', padx=10)
        
        # Player 2 pits (reversed order for visual layout)
        for i in range(12, 6, -1):
            btn = tk.Button(p2_pits_frame, text="4", 
                           font=('Arial', 12, 'bold'),
                           fg=self.colors['text'],
                           bg=self.colors['pit'],
                           activebackground=self.colors['pit_hover'],
                           width=6, height=2,
                           relief='raised', bd=3,
                           command=lambda pit=i: self.make_move(pit))
            btn.pack(side='left', padx=5)
            self.pit_buttons.append((i, btn))
        
        # Middle separator
        separator = tk.Frame(game_frame, height=20, bg=self.colors['bg'])
        separator.pack(fill='x')
        
        # Player 1 pits (bottom row)
        p1_frame = tk.Frame(game_frame, bg=self.colors['bg'])
        p1_frame.pack(fill='x', pady=5)
        
        p1_pits_frame = tk.Frame(p1_frame, bg=self.colors['bg'])
        p1_pits_frame.pack()
        
        # Player 1 pits
        for i in range(0, 6):
            btn = tk.Button(p1_pits_frame, text="4", 
                           font=('Arial', 12, 'bold'),
                           fg=self.colors['text'],
                           bg=self.colors['pit'],
                           activebackground=self.colors['pit_hover'],
                           width=6, height=2,
                           relief='raised', bd=3,
                           command=lambda pit=i: self.make_move(pit))
            btn.pack(side='left', padx=5)
            self.pit_buttons.append((i, btn))
        
        # Player 1 store (right)
        self.store_labels.append(tk.Label(p1_pits_frame, text="0", 
                                         font=('Arial', 16, 'bold'),
                                         fg=self.colors['text'],
                                         bg=self.colors['store'],
                                         width=4, height=3,
                                         relief='raised', bd=3))
        self.store_labels[1].pack(side='right', padx=10)
        
        tk.Label(p1_frame, text="Player 1", font=('Arial', 14, 'bold'), 
                fg=self.colors['p1_color'], bg=self.colors['bg']).pack()
        
        # Status frame
        status_frame = tk.Frame(self.root, bg=self.colors['bg'])
        status_frame.pack(fill='x', pady=10)
        
        self.status_label = tk.Label(status_frame, text="Player 1's Turn", 
                                    font=('Arial', 14, 'bold'),
                                    fg=self.colors['text'], 
                                    bg=self.colors['bg'])
        self.status_label.pack()
        
        # Control buttons
        control_frame = tk.Frame(self.root, bg=self.colors['bg'])
        control_frame.pack(pady=10)
        
        new_game_btn = tk.Button(control_frame, text="🔄 New Game", 
                                font=('Arial', 12, 'bold'),
                                fg=self.colors['text'],
                                bg='#FF4444',
                                activebackground='#FF6666',
                                relief='raised', bd=3,
                                command=self.new_game)
        new_game_btn.pack(side='left', padx=10)
        
        quit_btn = tk.Button(control_frame, text="❌ Quit", 
                            font=('Arial', 12, 'bold'),
                            fg=self.colors['text'],
                            bg='#666666',
                            activebackground='#888888',
                            relief='raised', bd=3,
                            command=self.root.quit)
        quit_btn.pack(side='left', padx=10)
    
    def update_display(self):
        """Update the display with current game state"""
        # Update pit buttons
        for pit_index, button in self.pit_buttons:
            seeds = self.game.board.pits[pit_index]
            button.config(text=str(seeds))
            
            # Enable/disable buttons based on current player and valid moves
            if (self.animating or 
                not self.game.board.is_valid_move(pit_index, self.game.board.current_player)):
                button.config(state='disabled')
            else:
                button.config(state='normal')
        
        # Update stores
        self.store_labels[0].config(text=str(self.game.board.pits[13]))  # Player 2 store
        self.store_labels[1].config(text=str(self.game.board.pits[6]))   # Player 1 store
        
        # Update status
        if self.game.board.is_game_over():
            winner = self.game.board.get_winner()
            if winner == 0:
                self.status_label.config(text="Game Over - It's a Tie!", 
                                       fg='#FFFF00')
            else:
                color = self.colors['p1_color'] if winner == 1 else self.colors['p2_color']
                self.status_label.config(text=f"Game Over - Player {winner} Wins!", 
                                       fg=color)
        else:
            current_player = self.game.board.current_player
            color = self.colors['p1_color'] if current_player == 1 else self.colors['p2_color']
            self.status_label.config(text=f"Player {current_player}'s Turn", 
                                   fg=color)
    
    def make_move(self, pit):
        """Handle a move with animation"""
        if self.animating:
            return
        
        result = self.game.make_move(pit)
        if result is None:
            return
        
        animation_steps, extra_turn = result
        
        # Start animation
        self.animating = True
        self.animate_move(animation_steps, extra_turn)
    
    def animate_move(self, steps, extra_turn):
        """Animate the seed movement"""
        def animate_step(step_index):
            if step_index < len(steps):
                # Highlight current pit
                pit = steps[step_index]
                
                # Find the button/label for this pit
                if pit == 6:  # Player 1 store
                    self.store_labels[1].config(bg='#FFD700')
                elif pit == 13:  # Player 2 store
                    self.store_labels[0].config(bg='#FFD700')
                else:  # Regular pit
                    for pit_index, button in self.pit_buttons:
                        if pit_index == pit:
                            button.config(bg='#FFD700')
                            break
                
                # Schedule next step
                self.root.after(300, lambda: self.reset_highlight_and_continue(pit, step_index, steps, extra_turn))
            else:
                # Animation complete
                self.animating = False
                self.update_display()
                
                # Show extra turn message
                if extra_turn and not self.game.board.is_game_over():
                    self.status_label.config(text=f"Player {self.game.board.current_player} gets an extra turn!", 
                                           fg='#FFFF00')
                    self.root.after(1500, self.update_display)
        
        animate_step(0)
    
    def reset_highlight_and_continue(self, pit, step_index, steps, extra_turn):
        """Reset highlighting and continue animation"""
        # Reset highlight
        if pit == 6:  # Player 1 store
            self.store_labels[1].config(bg=self.colors['store'])
        elif pit == 13:  # Player 2 store
            self.store_labels[0].config(bg=self.colors['store'])
        else:  # Regular pit
            for pit_index, button in self.pit_buttons:
                if pit_index == pit:
                    button.config(bg=self.colors['pit'])
                    break
        
        # Update display for this step
        self.update_display()
        
        # Continue animation
        self.root.after(200, lambda: self.animate_move(steps[step_index + 1:], extra_turn))
    
    def new_game(self):
        """Start a new game"""
        self.game.reset_game()
        self.animating = False
        self.update_display()
        
        # Reset all button colors
        for _, button in self.pit_buttons:
            button.config(bg=self.colors['pit'])
        for store_label in self.store_labels:
            store_label.config(bg=self.colors['store'])
    
    def run(self):
        """Start the game"""
        self.root.mainloop()

# Main execution
if __name__ == "__main__":
    game = MancalaGUI()
    game.run()
