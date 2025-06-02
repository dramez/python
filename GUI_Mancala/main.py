import tkinter as tk
from tkinter import messagebox
import time # For potential animation delays

# --- Constants ---
PITS_PER_SIDE = 6
INITIAL_SEEDS_PER_PIT = 4
PLAYER_1 = 0
PLAYER_2 = 1
STORE_INDICES = {PLAYER_1: PITS_PER_SIDE, PLAYER_2: PITS_PER_SIDE} # Relative to player's pits

# --- Board Class ---
class Board:
    """
    Represents the Mancala board state.
    Player 1 pits: 0 to 5, Player 1 store: index 6 (conceptually)
    Player 2 pits: 0 to 5, Player 2 store: index 6 (conceptually)
    Internal representation:
    self.pits[PLAYER_1] = [seeds, seeds, ..., seeds] (PITS_PER_SIDE long)
    self.pits[PLAYER_2] = [seeds, seeds, ..., seeds] (PITS_PER_SIDE long)
    self.stores = [player1_store_seeds, player2_store_seeds]
    """
    def __init__(self, pits_per_side=PITS_PER_SIDE, initial_seeds=INITIAL_SEEDS_PER_PIT):
        self.pits_per_side = pits_per_side
        self.initial_seeds = initial_seeds
        self.pits = [[initial_seeds] * pits_per_side for _ in range(2)]
        self.stores = [0, 0]

    def get_seeds(self, player_id, pit_index):
        return self.pits[player_id][pit_index]

    def set_seeds(self, player_id, pit_index, count):
        self.pits[player_id][pit_index] = count

    def add_to_store(self, player_id, count):
        self.stores[player_id] += count

    def get_store_seeds(self, player_id):
        return self.stores[player_id]

    def is_pit_empty(self, player_id, pit_index):
        return self.pits[player_id][pit_index] == 0

    def get_opponent_pit_index(self, pit_index):
        # Opposite pit for capture
        return self.pits_per_side - 1 - pit_index

    def get_player_pits_sum(self, player_id):
        return sum(self.pits[player_id])

    def reset(self):
        self.pits = [[self.initial_seeds] * self.pits_per_side for _ in range(2)]
        self.stores = [0, 0]

# --- MancalaGame Class (Game Logic) ---
class MancalaGame:
    def __init__(self):
        self.board = Board()
        self.current_player = PLAYER_1
        self.game_over = False
        self.winner = None
        self.ai_opponent = True # Set to False for two human players

    def switch_player(self):
        self.current_player = 1 - self.current_player

    def is_valid_move(self, player_id, pit_index):
        if self.game_over:
            return False
        if player_id != self.current_player:
            return False # Not current player's turn
        if pit_index < 0 or pit_index >= self.board.pits_per_side:
            return False # Invalid pit index
        if self.board.get_seeds(player_id, pit_index) == 0:
            return False # Pit is empty
        return True

    def make_move(self, pit_index):
        if not self.is_valid_move(self.current_player, pit_index):
            return False # Invalid move

        player_id = self.current_player
        seeds_to_sow = self.board.get_seeds(player_id, pit_index)
        self.board.set_seeds(player_id, pit_index, 0)

        current_side = player_id
        current_pit_index = pit_index

        extra_turn = False

        for i in range(seeds_to_sow):
            current_pit_index += 1

            if current_side == player_id:
                if current_pit_index == self.board.pits_per_side: # Landed in own store
                    self.board.add_to_store(player_id, 1)
                    if i == seeds_to_sow - 1: # Last seed
                        extra_turn = True
                    current_pit_index = -1 # Reset for next potential pit on opponent's side
                    current_side = 1 - player_id # Switch to opponent's side for sowing
                else:
                    self.board.pits[current_side][current_pit_index] += 1
            else: # Sowing on opponent's side
                if current_pit_index == self.board.pits_per_side: # Skipped opponent's store
                    current_pit_index = 0 # Start from first pit on own side
                    current_side = player_id
                    self.board.pits[current_side][current_pit_index] += 1
                else:
                    self.board.pits[current_side][current_pit_index] += 1

            # Capture logic
            if i == seeds_to_sow - 1 and not extra_turn: # Last seed
                if current_side == player_id and self.board.get_seeds(player_id, current_pit_index) == 1:
                    # Landed in own empty pit (now has 1 seed)
                    opponent_pit_index = self.board.get_opponent_pit_index(current_pit_index)
                    opponent_seeds = self.board.get_seeds(1 - player_id, opponent_pit_index)
                    if opponent_seeds > 0:
                        # Capture own seed and opponent's seeds
                        self.board.add_to_store(player_id, 1 + opponent_seeds)
                        self.board.set_seeds(player_id, current_pit_index, 0)
                        self.board.set_seeds(1 - player_id, opponent_pit_index, 0)

        self.check_game_over()
        if self.game_over:
            self.collect_remaining_seeds()
            self.determine_winner()
            return True # Move made, game ended

        if not extra_turn:
            self.switch_player()

        return True # Move successfully made

    def check_game_over(self):
        if self.board.get_player_pits_sum(PLAYER_1) == 0 or \
           self.board.get_player_pits_sum(PLAYER_2) == 0:
            self.game_over = True

    def collect_remaining_seeds(self):
        for player_id in [PLAYER_1, PLAYER_2]:
            for pit_idx in range(self.board.pits_per_side):
                seeds = self.board.get_seeds(player_id, pit_idx)
                self.board.add_to_store(player_id, seeds)
                self.board.set_seeds(player_id, pit_idx, 0)

    def determine_winner(self):
        p1_score = self.board.get_store_seeds(PLAYER_1)
        p2_score = self.board.get_store_seeds(PLAYER_2)
        if p1_score > p2_score:
            self.winner = PLAYER_1
        elif p2_score > p1_score:
            self.winner = PLAYER_2
        else:
            self.winner = -1 # Draw

    def reset_game(self):
        self.board.reset()
        self.current_player = PLAYER_1
        self.game_over = False
        self.winner = None

    def simple_ai_move(self):
        if not self.ai_opponent or self.current_player != PLAYER_2 or self.game_over:
            return None # Not AI's turn or AI disabled or game over

        best_move = -1

        # 1. Try for an extra turn
        for pit_idx in range(self.board.pits_per_side):
            if self.board.get_seeds(PLAYER_2, pit_idx) == 0:
                continue
            seeds = self.board.get_seeds(PLAYER_2, pit_idx)
            if (seeds % (self.board.pits_per_side * 2 + 2)) == (self.board.pits_per_side - pit_idx):
                 # This is a simplified check, real check is more complex
                 # A more robust check would simulate the move
                if self.is_valid_move(PLAYER_2, pit_idx):
                    best_move = pit_idx
                    break

        # 2. Try for a capture (simplified: land in an empty own pit)
        if best_move == -1:
            for pit_idx in range(self.board.pits_per_side):
                if self.board.get_seeds(PLAYER_2, pit_idx) == 0:
                    continue
                seeds = self.board.get_seeds(PLAYER_2, pit_idx)
                # Simulate landing position (very simplified)
                # A full simulation is needed for accurate capture prediction
                # This is a placeholder for a more complex AI
                # For now, let's pick a valid move if no obvious extra turn
                if self.is_valid_move(PLAYER_2, pit_idx):
                    best_move = pit_idx # Take first valid move if no better option found yet
                    # A better AI would simulate the move and check for capture potential
                    # For simplicity, we are not fully simulating here.
                    # A true capture check:
                    # temp_board = copy.deepcopy(self.board)
                    # ... simulate move on temp_board ...
                    # if lands in empty own pit and opposite has seeds:
                    #    best_move = pit_idx; break
                    break # Take the first one for simplicity

        # 3. If no special move, pick a random valid move or first valid one
        if best_move == -1:
            for pit_idx in range(self.board.pits_per_side):
                if self.is_valid_move(PLAYER_2, pit_idx):
                    best_move = pit_idx
                    break

        if best_move != -1:
            return best_move
        else: # Should not happen if game is not over
            return None


# --- MancalaGUI Class ---
class MancalaGUI:
    def __init__(self, master):
        self.master = master
        self.game = MancalaGame()
        master.title("Mancala Game")
        master.configure(bg="#F0F0F0")

        self.pit_radius = 30
        self.store_width = 70
        self.store_height = self.pit_radius * 2 + 20
        self.pit_padding = 10
        self.board_width = (self.pit_radius * 2 + self.pit_padding) * PITS_PER_SIDE + self.store_width * 2 + self.pit_padding * 4
        self.board_height = self.pit_radius * 4 + self.pit_padding * 3 + self.store_height / 2 # Adjusted for labels

        self.canvas = tk.Canvas(master, width=self.board_width, height=self.board_height, bg="#E0E0E0", highlightthickness=0)
        self.canvas.pack(pady=20)

        self.status_label = tk.Label(master, text="Player 1's Turn", font=("Arial", 14), bg="#F0F0F0")
        self.status_label.pack(pady=5)

        self.score_label = tk.Label(master, text="P1: 0 - P2: 0", font=("Arial", 14), bg="#F0F0F0")
        self.score_label.pack(pady=5)

        reset_button = tk.Button(master, text="New Game / Reset", command=self.reset_game_gui, font=("Arial", 12), bg="#D0D0D0", activebackground="#C0C0C0")
        reset_button.pack(pady=10)

        self.pit_coords = {PLAYER_1: [], PLAYER_2: []}
        self.store_coords = {}

        self.draw_board_layout()
        self.update_display()

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        # For hover effects (basic example)
        self.canvas.bind("<Motion>", self.on_mouse_motion)
        self.current_hover_item = None


    def draw_board_layout(self):
        self.canvas.delete("all") # Clear previous drawings

        # Player 1 Store (Right)
        x0_s1 = self.board_width - self.store_width - self.pit_padding
        y0_s1 = (self.board_height - self.store_height) / 2
        x1_s1 = self.board_width - self.pit_padding
        y1_s1 = y0_s1 + self.store_height
        self.store_coords[PLAYER_1] = self.canvas.create_rectangle(x0_s1, y0_s1, x1_s1, y1_s1, fill="#ADD8E6", outline="black", width=2, tags="store_p1")
        self.canvas.create_text((x0_s1 + x1_s1) / 2, y0_s1 - 10, text="P1 Store", anchor="s")


        # Player 2 Store (Left)
        x0_s2 = self.pit_padding
        y0_s2 = (self.board_height - self.store_height) / 2
        x1_s2 = self.pit_padding + self.store_width
        y1_s2 = y0_s2 + self.store_height
        self.store_coords[PLAYER_2] = self.canvas.create_rectangle(x0_s2, y0_s2, x1_s2, y1_s2, fill="#FFB6C1", outline="black", width=2, tags="store_p2")
        self.canvas.create_text((x0_s2 + x1_s2) / 2, y0_s2 - 10, text="P2 Store", anchor="s")

        # Player 1 Pits (Bottom row, drawn right to left for indexing 0-5 from player's view)
        y_p1 = self.board_height - self.pit_padding - self.pit_radius * 1.5
        for i in range(PITS_PER_SIDE):
            x_center = self.board_width - self.store_width - self.pit_padding * 2 - self.pit_radius - i * (self.pit_radius * 2 + self.pit_padding)
            x0 = x_center - self.pit_radius
            y0 = y_p1 - self.pit_radius
            x1 = x_center + self.pit_radius
            y1 = y_p1 + self.pit_radius
            pit_id = self.canvas.create_oval(x0, y0, x1, y1, fill="#ADD8E6", outline="black", width=2, tags=f"pit_p1_{i}")
            self.pit_coords[PLAYER_1].append((pit_id, x_center, y_p1))
            self.canvas.create_text(x_center, y_p1 + self.pit_radius + 10, text=str(i), anchor="n")


        # Player 2 Pits (Top row, drawn left to right for indexing 0-5 from player's view)
        self.pit_coords[PLAYER_2] = [] # Ensure it's fresh
        y_p2 = self.pit_padding + self.pit_radius * 1.5
        for i in range(PITS_PER_SIDE):
            x_center = self.store_width + self.pit_padding * 2 + self.pit_radius + i * (self.pit_radius * 2 + self.pit_padding)
            x0 = x_center - self.pit_radius
            y0 = y_p2 - self.pit_radius
            x1 = x_center + self.pit_radius
            y1 = y_p2 + self.pit_radius
            pit_id = self.canvas.create_oval(x0, y0, x1, y1, fill="#FFB6C1", outline="black", width=2, tags=f"pit_p2_{i}")
            self.pit_coords[PLAYER_2].append((pit_id, x_center, y_p2))
            self.canvas.create_text(x_center, y_p2 - self.pit_radius - 10, text=str(i), anchor="s")

        self.update_seeds_display()

    def update_seeds_display(self):
        self.canvas.delete("seeds") # Clear only seed counts

        # Player 1 Pits
        for i in range(PITS_PER_SIDE):
            _, x_center, y_center = self.pit_coords[PLAYER_1][i]
            seeds = self.game.board.get_seeds(PLAYER_1, i)
            self.canvas.create_text(x_center, y_center, text=str(seeds), font=("Arial", 12, "bold"), tags="seeds")

        # Player 2 Pits
        for i in range(PITS_PER_SIDE):
            _, x_center, y_center = self.pit_coords[PLAYER_2][i]
            seeds = self.game.board.get_seeds(PLAYER_2, i)
            self.canvas.create_text(x_center, y_center, text=str(seeds), font=("Arial", 12, "bold"), tags="seeds")

        # Stores
        s1_seeds = self.game.board.get_store_seeds(PLAYER_1)
        s1_coords = self.canvas.coords(self.store_coords[PLAYER_1])
        self.canvas.create_text((s1_coords[0] + s1_coords[2]) / 2, (s1_coords[1] + s1_coords[3]) / 2,
                                text=str(s1_seeds), font=("Arial", 16, "bold"), tags="seeds")

        s2_seeds = self.game.board.get_store_seeds(PLAYER_2)
        s2_coords = self.canvas.coords(self.store_coords[PLAYER_2])
        self.canvas.create_text((s2_coords[0] + s2_coords[2]) / 2, (s2_coords[1] + s2_coords[3]) / 2,
                                text=str(s2_seeds), font=("Arial", 16, "bold"), tags="seeds")

    def update_display(self):
        self.update_seeds_display()

        p1_score = self.game.board.get_store_seeds(PLAYER_1)
        p2_score = self.game.board.get_store_seeds(PLAYER_2)
        self.score_label.config(text=f"P1 Store: {p1_score}  -  P2 Store: {p2_score}")

        if self.game.game_over:
            if self.game.winner == PLAYER_1:
                msg = "Player 1 Wins!"
            elif self.game.winner == PLAYER_2:
                msg = "Player 2 Wins!"
            else:
                msg = "It's a Draw!"
            self.status_label.config(text=msg)
            messagebox.showinfo("Game Over", msg)
        else:
            player_name = "Player 1" if self.game.current_player == PLAYER_1 else "Player 2"
            self.status_label.config(text=f"{player_name}'s Turn")

            # Highlight current player's pits (simple outline change)
            for i in range(PITS_PER_SIDE):
                pit_id_p1, _, _ = self.pit_coords[PLAYER_1][i]
                pit_id_p2, _, _ = self.pit_coords[PLAYER_2][i]
                self.canvas.itemconfig(pit_id_p1, outline="black", width=2)
                self.canvas.itemconfig(pit_id_p2, outline="black", width=2)

            if self.game.current_player == PLAYER_1:
                 for i in range(PITS_PER_SIDE):
                    if self.game.board.get_seeds(PLAYER_1, i) > 0:
                        self.canvas.itemconfig(self.pit_coords[PLAYER_1][i][0], outline="green", width=3)
            else: # Player 2
                 for i in range(PITS_PER_SIDE):
                    if self.game.board.get_seeds(PLAYER_2, i) > 0:
                        self.canvas.itemconfig(self.pit_coords[PLAYER_2][i][0], outline="green", width=3)


    def on_canvas_click(self, event):
        if self.game.game_over:
            return

        item = self.canvas.find_closest(event.x, event.y)
        if not item:
            return

        tags = self.canvas.gettags(item[0])

        clicked_player = -1
        clicked_pit_index = -1

        for tag in tags:
            if tag.startswith("pit_p1_"):
                clicked_player = PLAYER_1
                clicked_pit_index = int(tag.split("_")[-1])
                break
            elif tag.startswith("pit_p2_"):
                clicked_player = PLAYER_2
                clicked_pit_index = int(tag.split("_")[-1])
                break

        if clicked_player != -1 and clicked_player == self.game.current_player:
            if self.game.is_valid_move(clicked_player, clicked_pit_index):
                move_successful = self.game.make_move(clicked_pit_index)
                if move_successful:
                    # Basic "animation": just update display after a short delay
                    # For real animation, you'd move individual seed representations
                    self.master.after(100, self.update_display) # Short delay to simulate action

                    if self.game.ai_opponent and self.game.current_player == PLAYER_2 and not self.game.game_over:
                        self.master.after(500, self.trigger_ai_move) # AI moves after a delay
                else:
                    messagebox.showwarning("Invalid Move", "Cannot select an empty pit or opponent's pit.")
            else:
                 messagebox.showwarning("Invalid Move", "Cannot select an empty pit or opponent's pit.")
        elif clicked_player != -1 and clicked_player != self.game.current_player:
            messagebox.showinfo("Not Your Turn", "It's not your turn.")

        self.update_display() # Ensure display is current

    def on_mouse_motion(self, event):
        # Basic hover effect: change outline of clickable pits for current player
        if self.game.game_over:
            if self.current_hover_item:
                self.canvas.itemconfig(self.current_hover_item, outline="black") # Reset old hover
                self.current_hover_item = None
            return

        items = self.canvas.find_overlapping(event.x-1, event.y-1, event.x+1, event.y+1)
        new_hover_item = None

        if items:
            for item_id in items:
                tags = self.canvas.gettags(item_id)
                is_pit_tag = any(t.startswith(f"pit_p{self.game.current_player}_") for t in tags)
                if is_pit_tag:
                    # Check if pit is not empty
                    pit_index = int(tags[0].split("_")[-1]) # Assuming tag like "pit_p0_3" is first
                    if self.game.board.get_seeds(self.game.current_player, pit_index) > 0:
                        new_hover_item = item_id
                        break

        if self.current_hover_item != new_hover_item:
            if self.current_hover_item:
                # Reset outline of previously hovered item if it's not a generally highlighted active pit
                is_active_pit = False
                if self.game.current_player == PLAYER_1:
                    if self.game.board.get_seeds(PLAYER_1, int(self.canvas.gettags(self.current_hover_item)[0].split("_")[-1])) > 0:
                         is_active_pit = True
                else: # Player 2
                    if self.game.board.get_seeds(PLAYER_2, int(self.canvas.gettags(self.current_hover_item)[0].split("_")[-1])) > 0:
                         is_active_pit = True

                self.canvas.itemconfig(self.current_hover_item, outline="green" if is_active_pit else "black")


            if new_hover_item:
                self.canvas.itemconfig(new_hover_item, outline="blue") # Hover color

            self.current_hover_item = new_hover_item


    def trigger_ai_move(self):
        if self.game.ai_opponent and self.game.current_player == PLAYER_2 and not self.game.game_over:
            ai_pit_choice = self.game.simple_ai_move()
            if ai_pit_choice is not None:
                self.status_label.config(text="Player 2 (AI) is thinking...")
                self.master.update() # Force GUI update
                time.sleep(0.5) # Simulate thinking

                self.game.make_move(ai_pit_choice)
                self.master.after(100, self.update_display) # Update after AI move

                # If AI gets another turn
                if self.game.current_player == PLAYER_2 and not self.game.game_over:
                    self.master.after(500, self.trigger_ai_move)
            else:
                # This case should ideally not be reached if AI has valid moves
                print("AI could not find a move.")
            self.update_display()


    def reset_game_gui(self):
        self.game.reset_game()
        self.draw_board_layout() # Redraws layout and initial seeds
        self.update_display()
        messagebox.showinfo("Game Reset", "New game started. Player 1's turn.")


# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    gui = MancalaGUI(root)

    # Initial check for AI move if AI is Player 1 (not typical for this setup)
    # if gui.game.ai_opponent and gui.game.current_player == PLAYER_1:
    #    gui.trigger_ai_move()

    root.mainloop()