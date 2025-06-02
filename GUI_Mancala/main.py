#This file is wrong or not
import tkinter as tk
from tkinter import messagebox
import math

class MancalaGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mancala Game")
        self.root.geometry("800x400")
        self.root.configure(bg='#8B4513')
        self.root.resizable(False, False)
        
        # Game state
        self.board = [4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4, 0]
        # Indices: 0-5 (Player 1), 6 (Player 1 store), 7-12 (Player 2), 13 (Player 2 store)
        self.current_player = 1
        self.game_over = False
        
        self.setup_ui()
        self.update_display()
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="MANCALA", font=('Arial', 24, 'bold'), 
                              bg='#8B4513', fg='white')
        title_label.pack(pady=10)
        
        # Game board frame
        self.board_frame = tk.Frame(self.root, bg='#8B4513')
        self.board_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Create board layout
        self.create_board()
        
        # Status and controls
        self.status_frame = tk.Frame(self.root, bg='#8B4513')
        self.status_frame.pack(pady=10)
        
        self.status_label = tk.Label(self.status_frame, text="Player 1's Turn", 
                                   font=('Arial', 16, 'bold'), bg='#8B4513', fg='white')
        self.status_label.pack()
        
        # Control buttons
        control_frame = tk.Frame(self.root, bg='#8B4513')
        control_frame.pack(pady=5)
        
        new_game_btn = tk.Button(control_frame, text="New Game", font=('Arial', 12),
                               command=self.new_game, bg='#DEB887', fg='black',
                               relief='raised', bd=3)
        new_game_btn.pack(side='left', padx=10)
        
        quit_btn = tk.Button(control_frame, text="Quit", font=('Arial', 12),
                           command=self.root.quit, bg='#CD853F', fg='black',
                           relief='raised', bd=3)
        quit_btn.pack(side='left', padx=10)
        
    def create_board(self):
        # Clear existing widgets
        for widget in self.board_frame.winfo_children():
            widget.destroy()
            
        # Configure grid
        self.board_frame.grid_columnconfigure(1, weight=1)
        self.board_frame.grid_rowconfigure(1, weight=1)
        
        # Player 2 label (top)
        player2_label = tk.Label(self.board_frame, text="Player 2", font=('Arial', 14, 'bold'),
                               bg='#8B4513', fg='lightblue')
        player2_label.grid(row=0, column=1, pady=5)
        
        # Player 2 store (left side)
        self.create_store(13, 0, 1, 'lightblue')
        
        # Main playing area
        play_frame = tk.Frame(self.board_frame, bg='#654321', relief='sunken', bd=3)
        play_frame.grid(row=1, column=1, sticky='nsew', padx=10, pady=5)
        
        # Player 2 pits (top row, reversed order for display)
        for i in range(6):
            pit_index = 12 - i  # Reverse order: 12, 11, 10, 9, 8, 7
            self.create_pit(pit_index, 0, i, play_frame, 'lightblue')
            
        # Player 1 pits (bottom row)
        for i in range(6):
            pit_index = i  # Normal order: 0, 1, 2, 3, 4, 5
            self.create_pit(pit_index, 1, i, play_frame, 'lightgreen')
            
        # Player 1 store (right side)
        self.create_store(6, 2, 1, 'lightgreen')
        
        # Player 1 label (bottom)
        player1_label = tk.Label(self.board_frame, text="Player 1", font=('Arial', 14, 'bold'),
                               bg='#8B4513', fg='lightgreen')
        player1_label.grid(row=2, column=1, pady=5)
        
    def create_pit(self, pit_index, row, col, parent, color):
        pit_frame = tk.Frame(parent, bg='#8B4513', relief='raised', bd=2)
        pit_frame.grid(row=row, column=col, padx=2, pady=2, sticky='nsew')
        parent.grid_columnconfigure(col, weight=1)
        parent.grid_rowconfigure(row, weight=1)
        
        # Make pit clickable only for current player's pits
        if ((pit_index <= 5 and self.current_player == 1) or 
            (7 <= pit_index <= 12 and self.current_player == 2)):
            pit_frame.configure(cursor='hand2')
            pit_frame.bind('<Button-1>', lambda e, idx=pit_index: self.make_move(idx))
        
        # Pit button
        pit_btn = tk.Button(pit_frame, text=str(self.board[pit_index]), 
                          font=('Arial', 16, 'bold'), bg=color, fg='black',
                          relief='raised', bd=3, width=6, height=3,
                          command=lambda idx=pit_index: self.make_move(idx))
        
        # Only enable button for current player's pits
        if ((pit_index <= 5 and self.current_player == 1) or 
            (7 <= pit_index <= 12 and self.current_player == 2)) and not self.game_over:
            pit_btn.configure(state='normal')
        else:
            pit_btn.configure(state='disabled')
            
        pit_btn.pack(expand=True, fill='both', padx=2, pady=2)
        
    def create_store(self, store_index, row, col, color):
        store_frame = tk.Frame(self.board_frame, bg='#8B4513', relief='raised', bd=3)
        store_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ns')
        
        store_label = tk.Label(store_frame, text=str(self.board[store_index]),
                             font=('Arial', 20, 'bold'), bg=color, fg='black',
                             relief='sunken', bd=3, width=4, height=8)
        store_label.pack(expand=True, fill='both', padx=3, pady=3)
        
    def make_move(self, pit_index):
        if self.game_over:
            return
            
        # Check if it's a valid move
        if ((pit_index <= 5 and self.current_player != 1) or 
            (7 <= pit_index <= 12 and self.current_player != 2) or
            self.board[pit_index] == 0):
            return
            
        # Pick up stones
        stones = self.board[pit_index]
        self.board[pit_index] = 0
        
        # Distribute stones
        current_pos = pit_index
        while stones > 0:
            current_pos = (current_pos + 1) % 14
            
            # Skip opponent's store
            if ((current_pos == 13 and self.current_player == 1) or 
                (current_pos == 6 and self.current_player == 2)):
                continue
                
            self.board[current_pos] += 1
            stones -= 1
            
        # Check for capture
        if (stones == 0 and self.board[current_pos] == 1 and 
            ((self.current_player == 1 and 0 <= current_pos <= 5) or
             (self.current_player == 2 and 7 <= current_pos <= 12))):
            
            # Calculate opposite pit
            opposite = 12 - current_pos
            if self.board[opposite] > 0:
                # Capture stones
                if self.current_player == 1:
                    self.board[6] += self.board[current_pos] + self.board[opposite]
                else:
                    self.board[13] += self.board[current_pos] + self.board[opposite]
                    
                self.board[current_pos] = 0
                self.board[opposite] = 0
        
        # Check if player gets another turn (landed in own store)
        extra_turn = ((current_pos == 6 and self.current_player == 1) or 
                     (current_pos == 13 and self.current_player == 2))
        
        if not extra_turn:
            self.current_player = 2 if self.current_player == 1 else 1
            
        # Check for game end
        self.check_game_end()
        
        # Update display
        self.update_display()
        
    def check_game_end(self):
        # Check if either side is empty
        player1_empty = all(self.board[i] == 0 for i in range(6))
        player2_empty = all(self.board[i] == 0 for i in range(7, 13))
        
        if player1_empty or player2_empty:
            # Move remaining stones to respective stores
            self.board[6] += sum(self.board[0:6])
            self.board[13] += sum(self.board[7:13])
            
            # Clear the pits
            for i in range(6):
                self.board[i] = 0
            for i in range(7, 13):
                self.board[i] = 0
                
            self.game_over = True
            
            # Determine winner
            if self.board[6] > self.board[13]:
                winner = "Player 1 Wins!"
            elif self.board[13] > self.board[6]:
                winner = "Player 2 Wins!"
            else:
                winner = "It's a Tie!"
                
            self.status_label.configure(text=f"Game Over! {winner}")
            messagebox.showinfo("Game Over", f"{winner}\nPlayer 1: {self.board[6]} stones\nPlayer 2: {self.board[13]} stones")
            
    def update_display(self):
        if not self.game_over:
            self.status_label.configure(text=f"Player {self.current_player}'s Turn")
        self.create_board()
        
    def new_game(self):
        self.board = [4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4, 0]
        self.current_player = 1
        self.game_over = False
        self.update_display()
        
    def run(self):
        self.root.mainloop()

# Create and save the game file
game_code = '''import tkinter as tk
from tkinter import messagebox
import math

class MancalaGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mancala Game")
        self.root.geometry("800x400")
        self.root.configure(bg='#8B4513')
        self.root.resizable(False, False)
        
        # Game state
        self.board = [4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4, 0]
        # Indices: 0-5 (Player 1), 6 (Player 1 store), 7-12 (Player 2), 13 (Player 2 store)
        self.current_player = 1
        self.game_over = False
        
        self.setup_ui()
        self.update_display()
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="MANCALA", font=('Arial', 24, 'bold'), 
                              bg='#8B4513', fg='white')
        title_label.pack(pady=10)
        
        # Game board frame
        self.board_frame = tk.Frame(self.root, bg='#8B4513')
        self.board_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Create board layout
        self.create_board()
        
        # Status and controls
        self.status_frame = tk.Frame(self.root, bg='#8B4513')
        self.status_frame.pack(pady=10)
        
        self.status_label = tk.Label(self.status_frame, text="Player 1's Turn", 
                                   font=('Arial', 16, 'bold'), bg='#8B4513', fg='white')
        self.status_label.pack()
        
        # Control buttons
        control_frame = tk.Frame(self.root, bg='#8B4513')
        control_frame.pack(pady=5)
        
        new_game_btn = tk.Button(control_frame, text="New Game", font=('Arial', 12),
                               command=self.new_game, bg='#DEB887', fg='black',
                               relief='raised', bd=3)
        new_game_btn.pack(side='left', padx=10)
        
        quit_btn = tk.Button(control_frame, text="Quit", font=('Arial', 12),
                           command=self.root.quit, bg='#CD853F', fg='black',
                           relief='raised', bd=3)
        quit_btn.pack(side='left', padx=10)
        
    def create_board(self):
        # Clear existing widgets
        for widget in self.board_frame.winfo_children():
            widget.destroy()
            
        # Configure grid
        self.board_frame.grid_columnconfigure(1, weight=1)
        self.board_frame.grid_rowconfigure(1, weight=1)
        
        # Player 2 label (top)
        player2_label = tk.Label(self.board_frame, text="Player 2", font=('Arial', 14, 'bold'),
                               bg='#8B4513', fg='lightblue')
        player2_label.grid(row=0, column=1, pady=5)
        
        # Player 2 store (left side)
        self.create_store(13, 0, 1, 'lightblue')
        
        # Main playing area
        play_frame = tk.Frame(self.board_frame, bg='#654321', relief='sunken', bd=3)
        play_frame.grid(row=1, column=1, sticky='nsew', padx=10, pady=5)
        
        # Player 2 pits (top row, reversed order for display)
        for i in range(6):
            pit_index = 12 - i  # Reverse order: 12, 11, 10, 9, 8, 7
            self.create_pit(pit_index, 0, i, play_frame, 'lightblue')
            
        # Player 1 pits (bottom row)
        for i in range(6):
            pit_index = i  # Normal order: 0, 1, 2, 3, 4, 5
            self.create_pit(pit_index, 1, i, play_frame, 'lightgreen')
            
        # Player 1 store (right side)
        self.create_store(6, 2, 1, 'lightgreen')
        
        # Player 1 label (bottom)
        player1_label = tk.Label(self.board_frame, text="Player 1", font=('Arial', 14, 'bold'),
                               bg='#8B4513', fg='lightgreen')
        player1_label.grid(row=2, column=1, pady=5)
        
    def create_pit(self, pit_index, row, col, parent, color):
        pit_frame = tk.Frame(parent, bg='#8B4513', relief='raised', bd=2)
        pit_frame.grid(row=row, column=col, padx=2, pady=2, sticky='nsew')
        parent.grid_columnconfigure(col, weight=1)
        parent.grid_rowconfigure(row, weight=1)
        
        # Make pit clickable only for current player's pits
        if ((pit_index <= 5 and self.current_player == 1) or 
            (7 <= pit_index <= 12 and self.current_player == 2)):
            pit_frame.configure(cursor='hand2')
            pit_frame.bind('<Button-1>', lambda e, idx=pit_index: self.make_move(idx))
        
        # Pit button
        pit_btn = tk.Button(pit_frame, text=str(self.board[pit_index]), 
                          font=('Arial', 16, 'bold'), bg=color, fg='black',
                          relief='raised', bd=3, width=6, height=3,
                          command=lambda idx=pit_index: self.make_move(idx))
        
        # Only enable button for current player's pits
        if ((pit_index <= 5 and self.current_player == 1) or 
            (7 <= pit_index <= 12 and self.current_player == 2)) and not self.game_over:
            pit_btn.configure(state='normal')
        else:
            pit_btn.configure(state='disabled')
            
        pit_btn.pack(expand=True, fill='both', padx=2, pady=2)
        
    def create_store(self, store_index, row, col, color):
        store_frame = tk.Frame(self.board_frame, bg='#8B4513', relief='raised', bd=3)
        store_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ns')
        
        store_label = tk.Label(store_frame, text=str(self.board[store_index]),
                             font=('Arial', 20, 'bold'), bg=color, fg='black',
                             relief='sunken', bd=3, width=4, height=8)
        store_label.pack(expand=True, fill='both', padx=3, pady=3)
        
    def make_move(self, pit_index):
        if self.game_over:
            return
            
        # Check if it's a valid move
        if ((pit_index <= 5 and self.current_player != 1) or 
            (7 <= pit_index <= 12 and self.current_player != 2) or
            self.board[pit_index] == 0):
            return
            
        # Pick up stones
        stones = self.board[pit_index]
        self.board[pit_index] = 0
        
        # Distribute stones
        current_pos = pit_index
        while stones > 0:
            current_pos = (current_pos + 1) % 14
            
            # Skip opponent's store
            if ((current_pos == 13 and self.current_player == 1) or 
                (current_pos == 6 and self.current_player == 2)):
                continue
                
            self.board[current_pos] += 1
            stones -= 1
            
        # Check for capture
        if (stones == 0 and self.board[current_pos] == 1 and 
            ((self.current_player == 1 and 0 <= current_pos <= 5) or
             (self.current_player == 2 and 7 <= current_pos <= 12))):
            
            # Calculate opposite pit
            opposite = 12 - current_pos
            if self.board[opposite] > 0:
                # Capture stones
                if self.current_player == 1:
                    self.board[6] += self.board[current_pos] + self.board[opposite]
                else:
                    self.board[13] += self.board[current_pos] + self.board[opposite]
                    
                self.board[current_pos] = 0
                self.board[opposite] = 0
        
        # Check if player gets another turn (landed in own store)
        extra_turn = ((current_pos == 6 and self.current_player == 1) or 
                     (current_pos == 13 and self.current_player == 2))
        
        if not extra_turn:
            self.current_player = 2 if self.current_player == 1 else 1
            
        # Check for game end
        self.check_game_end()
        
        # Update display
        self.update_display()
        
    def check_game_end(self):
        # Check if either side is empty
        player1_empty = all(self.board[i] == 0 for i in range(6))
        player2_empty = all(self.board[i] == 0 for i in range(7, 13))
        
        if player1_empty or player2_empty:
            # Move remaining stones to respective stores
            self.board[6] += sum(self.board[0:6])
            self.board[13] += sum(self.board[7:13])
            
            # Clear the pits
            for i in range(6):
                self.board[i] = 0
            for i in range(7, 13):
                self.board[i] = 0
                
            self.game_over = True
            
            # Determine winner
            if self.board[6] > self.board[13]:
                winner = "Player 1 Wins!"
            elif self.board[13] > self.board[6]:
                winner = "Player 2 Wins!"
            else:
                winner = "It's a Tie!"
                
            self.status_label.configure(text=f"Game Over! {winner}")
            messagebox.showinfo("Game Over", f"{winner}\\nPlayer 1: {self.board[6]} stones\\nPlayer 2: {self.board[13]} stones")
            
    def update_display(self):
        if not self.game_over:
            self.status_label.configure(text=f"Player {self.current_player}'s Turn")
        self.create_board()
        
    def new_game(self):
        self.board = [4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4, 0]
        self.current_player = 1
        self.game_over = False
        self.update_display()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = MancalaGame()
    game.run()
'''

# Save to file
with open('mancala_game.py', 'w') as f:
    f.write(game_code)

print("Mancala game created successfully!")
print("File saved as: mancala_game.py")
print("\nTo run the game, execute: python mancala_game.py")

# Also run the game to demonstrate
print("\nStarting the game...")
game = MancalaGame()
game.run()