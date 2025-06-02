import tkinter as tk
from tkinter import messagebox
import threading
import time
import random

# --- Game Logic Classes ---

class Board:
    """Represents the state of the Mancala board."""
    def __init__(self, pits_per_side=6, seeds_per_pit=4):
        self.pits_per_side = pits_per_side
        self.seeds_per_pit = seeds_per_pit
        self.reset()

    def reset(self):
        self.pits = [
            [self.seeds_per_pit] * self.pits_per_side,  # Player 1 side (bottom)
            [self.seeds_per_pit] * self.pits_per_side   # Player 2 side (top)
        ]
        self.stores = [0, 0]  # [Player 1 store, Player 2 store]

    def is_side_empty(self, player):
        return all(seeds == 0 for seeds in self.pits[player])

    def total_seeds(self, player):
        return sum(self.pits[player]) + self.stores[player]

    def get_state(self):
        return [row[:] for row in self.pits], self.stores[:]

    def set_state(self, pits, stores):
        self.pits = [row[:] for row in pits]
        self.stores = stores[:]

class MancalaGame:
    """Handles the rules and logic of the game."""
    def __init__(self, ai_enabled=False):
        self.board = Board()
        self.current_player = 0  # 0: Player 1 (bottom), 1: Player 2 (top)
        self.game_over = False
        self.move_history = []
        self.ai_enabled = ai_enabled
        self.ai_player = 1  # AI is always Player 2 (top) for simplicity

    def reset(self):
        self.board.reset()
        self.current_player = 0
        self.game_over = False
        self.move_history = []

    def valid_moves(self, player):
        return [i for i, seeds in enumerate(self.board.pits[player]) if seeds > 0]

    def is_valid_move(self, pit_idx):
        return (not self.game_over and
                0 <= pit_idx < self.board.pits_per_side and
                self.board.pits[self.current_player][pit_idx] > 0)

    def make_move(self, pit_idx):
        """Returns (move_sequence, extra_turn, capture_info, game_over)"""
        if not self.is_valid_move(pit_idx):
            return None, False, None, self.game_over

        pits, stores = self.board.get_state()
        player = self.current_player
        seeds = pits[player][pit_idx]
        pits[player][pit_idx] = 0
        pos = pit_idx
        side = player
        move_sequence = []  # For animation: [(side, pos, is_store)]
        capture_info = None

        while seeds > 0:
            # Move to next pit or store
            pos += 1
            if pos == self.board.pits_per_side:
                if side == player:
                    # Place in own store
                    stores[player] += 1
                    move_sequence.append((side, 'store', True))
                    seeds -= 1
                    if seeds == 0:
                        # Last seed in own store: extra turn
                        extra_turn = True
                        break
                # Switch side
                side = 1 - side
                pos = 0
            if seeds > 0 and pos < self.board.pits_per_side:
                pits[side][pos] += 1
                move_sequence.append((side, pos, False))
                seeds -= 1

        # Check for capture
        extra_turn = False
        if move_sequence:
            last_side, last_pos, is_store = move_sequence[-1]
            if not is_store and last_side == player:
                if pits[player][last_pos] == 1 and self.board.pits[player][last_pos] == 0:
                    opp = 1 - player
                    opp_pit = self.board.pits_per_side - 1 - last_pos
                    captured = pits[opp][opp_pit]
                    if captured > 0:
                        pits[opp][opp_pit] = 0
                        pits[player][last_pos] = 0
                        stores[player] += captured + 1
                        capture_info = (last_side, last_pos, opp, opp_pit, captured)
        # Check for extra turn
        if move_sequence and move_sequence[-1][2] and move_sequence[-1][0] == player:
            extra_turn = True

        # Update board
        self.board.set_state(pits, stores)

        # Check for game end
        if self.board.is_side_empty(0) or self.board.is_side_empty(1):
            self.game_over = True
            # Sweep remaining seeds to stores
            for p in [0, 1]:
                stores[p] += sum(pits[p])
                pits[p] = [0] * self.board.pits_per_side
            self.board.set_state(pits, stores)

        # Record move
        self.move_history.append((player, pit_idx, self.board.get_state()))

        if not extra_turn and not self.game_over:
            self.current_player = 1 - self.current_player

        return move_sequence, extra_turn, capture_info, self.game_over

    def get_winner(self):
        if not self.game_over:
            return None
        s1, s2 = self.board.stores
        if s1 > s2:
            return 0
        elif s2 > s1:
            return 1
        else:
            return -1  # Draw

    def ai_move(self):
        """Simple AI: pick the move that gives extra turn or max seeds, else random."""
        moves = self.valid_moves(self.ai_player)
        best = []
        for pit in moves:
            # Simulate move
            test_game = MancalaGame()
            test_game.board.set_state(*self.board.get_state())
            test_game.current_player = self.ai_player
            seq, extra, _, _ = test_game.make_move(pit)
            if extra:
                best.append(pit)
        if best:
            return random.choice(best)
        # Otherwise, pick the move with most seeds
        if moves:
            max_seeds = max(self.board.pits[self.ai_player][i] for i in moves)
            best = [i for i in moves if self.board.pits[self.ai_player][i] == max_seeds]
            return random.choice(best)
        return None

# --- GUI Classes ---

class MancalaGUI:
    """Tkinter GUI for the Mancala game."""
    PIT_RADIUS = 38
    STORE_RADIUS = 60
    SEED_RADIUS = 7
    PIT_GAP = 30
    PIT_COLOR_1 = "#f7c873"
    PIT_COLOR_2 = "#7ec4cf"
    STORE_COLOR_1 = "#f7a440"
    STORE_COLOR_2 = "#3b8ea5"
    SEED_COLOR_1 = "#e85d04"
    SEED_COLOR_2 = "#4361ee"
    HIGHLIGHT_COLOR = "#ffd166"
    BG_COLOR = "#f6f6f6"
    BOARD_OUTLINE = "#444"
    PLAYER_ARROW = "#ff006e"
    HOVER_COLOR = "#ffe066"
    ANIMATION_DELAY = 0.08

    def __init__(self, root):
        self.root = root
        self.root.title("Mancala (Kalah) Game")
        self.game = MancalaGame(ai_enabled=True)
        self.animating = False
        self.hovered_pit = None
        self.selected_pit = None

        # Layout
        self.canvas = tk.Canvas(root, width=820, height=340, bg=self.BG_COLOR, highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
        self.status_label = tk.Label(root, text="", font=("Segoe UI", 14), bg=self.BG_COLOR)
        self.status_label.grid(row=1, column=0, sticky="w", padx=20)
        self.score_label = tk.Label(root, text="", font=("Segoe UI", 14), bg=self.BG_COLOR)
        self.score_label.grid(row=1, column=1)
        self.newgame_btn = tk.Button(root, text="⟳ New Game", font=("Segoe UI", 12, "bold"),
                                     command=self.reset_game, bg="#e0e0e0", relief="raised")
        self.newgame_btn.grid(row=1, column=2, sticky="e", padx=20)
        self.move_history_box = tk.Listbox(root, width=40, height=8, font=("Consolas", 10))
        self.move_history_box.grid(row=2, column=0, columnspan=3, pady=(5, 10))

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<Leave>", self.on_leave)

        self.draw_board()
        self.update_status()
        self.root.after(500, self.check_ai_move)

    def pit_coords(self, side, idx):
        """Returns (x, y) center of pit."""
        x0 = 120 + idx * (self.PIT_RADIUS * 2 + self.PIT_GAP)
        y0 = 220 if side == 0 else 120
        return x0, y0

    def store_coords(self, side):
        x0 = 60 if side == 1 else 760
        y0 = 170
        return x0, y0

    def draw_board(self):
        self.canvas.delete("all")
        # Draw stores
        for side in [0, 1]:
            x, y = self.store_coords(side)
            color = self.STORE_COLOR_1 if side == 0 else self.STORE_COLOR_2
            self.canvas.create_oval(x - self.STORE_RADIUS, y - self.STORE_RADIUS,
                                    x + self.STORE_RADIUS, y + self.STORE_RADIUS,
                                    fill=color, outline=self.BOARD_OUTLINE, width=3)
            # Store label
            self.canvas.create_text(x, y - self.STORE_RADIUS - 18, text=f"Store {side+1}",
                                   font=("Segoe UI", 12, "bold"), fill="#333")
        # Draw pits
        for side in [0, 1]:
            for idx in range(self.game.board.pits_per_side):
                x, y = self.pit_coords(side, idx)
                color = self.PIT_COLOR_1 if side == 0 else self.PIT_COLOR_2
                outline = self.HIGHLIGHT_COLOR if (self.hovered_pit == (side, idx) and
                                                   self.is_pit_clickable(side, idx)) else self.BOARD_OUTLINE
                self.canvas.create_oval(x - self.PIT_RADIUS, y - self.PIT_RADIUS,
                                        x + self.PIT_RADIUS, y + self.PIT_RADIUS,
                                        fill=color, outline=outline, width=3, tags=f"pit_{side}_{idx}")
                # Pit label
                pit_label = f"{idx+1}" if side == 0 else f"{self.game.board.pits_per_side-idx}"
                self.canvas.create_text(x, y + self.PIT_RADIUS + 16, text=pit_label,
                                       font=("Segoe UI", 10, "bold"), fill="#555")
        # Draw seeds
        self.draw_seeds()
        # Draw player indicator
        self.draw_player_indicator()
        # Draw pit labels (A-F, F-A)
        for idx in range(self.game.board.pits_per_side):
            x, y = self.pit_coords(0, idx)
            self.canvas.create_text(x, 320, text=chr(ord('A') + idx), font=("Segoe UI", 11, "bold"), fill="#888")
            x, y = self.pit_coords(1, idx)
            self.canvas.create_text(x, 30, text=chr(ord('A') + self.game.board.pits_per_side - 1 - idx),
                                   font=("Segoe UI", 11, "bold"), fill="#888")
        # Draw move history
        self.update_move_history()

    def draw_seeds(self):
        # Pits
        for side in [0, 1]:
            for idx in range(self.game.board.pits_per_side):
                x, y = self.pit_coords(side, idx)
                n = self.game.board.pits[side][idx]
                self.draw_seed_group(x, y, n, side)
                # Seed count
                self.canvas.create_text(x, y, text=str(n), font=("Segoe UI", 13, "bold"), fill="#222")
        # Stores
        for side in [0, 1]:
            x, y = self.store_coords(side)
            n = self.game.board.stores[side]
            self.draw_seed_group(x, y, n, side, is_store=True)
            self.canvas.create_text(x, y, text=str(n), font=("Segoe UI", 16, "bold"), fill="#111")

    def draw_seed_group(self, x, y, n, side, is_store=False):
        if n == 0:
            return
        color = self.SEED_COLOR_1 if side == 0 else self.SEED_COLOR_2
        # Arrange seeds in a circle or grid
        if is_store:
            cols = 6
            rows = (n + cols - 1) // cols
            for i in range(n):
                cx = x - 30 + (i % cols) * 12
                cy = y - 30 + (i // cols) * 12
                self.canvas.create_oval(cx - self.SEED_RADIUS, cy - self.SEED_RADIUS,
                                       cx + self.SEED_RADIUS, cy + self.SEED_RADIUS,
                                       fill=color, outline="#fff", width=1)
        else:
            angle_step = 360 / max(n, 1)
            r = 18 + min(n, 8)
            for i in range(n):
                angle = i * angle_step
                rad = angle * 3.14159 / 180
                cx = x + r * (0.7 * (i % 2)) * (1 if i % 4 < 2 else -1)
                cy = y + r * (0.7 * ((i // 2) % 2)) * (1 if i % 4 < 2 else -1)
                # For up to 8 seeds, arrange in a circle; for more, grid
                if n <= 8:
                    cx = x + r * (0.8 * (i % 2)) * (1 if i % 4 < 2 else -1)
                    cy = y + r * (0.8 * ((i // 2) % 2)) * (1 if i % 4 < 2 else -1)
                else:
                    cx = x - 16 + (i % 4) * 10
                    cy = y - 16 + (i // 4) * 10
                self.canvas.create_oval(cx - self.SEED_RADIUS, cy - self.SEED_RADIUS,
                                       cx + self.SEED_RADIUS, cy + self.SEED_RADIUS,
                                       fill=color, outline="#fff", width=1)

    def draw_player_indicator(self):
        # Arrow under current player
        side = self.game.current_player
        y = 320 if side == 0 else 20
        x = 410
        self.canvas.create_polygon(
            x - 30, y, x, y + (20 if side == 0 else -20), x + 30, y,
            fill=self.PLAYER_ARROW, outline=""
        )
        self.canvas.create_text(x, y + (32 if side == 0 else -32),
                               text=f"Player {side+1} {'(You)' if side==0 else '(AI)'}",
                               font=("Segoe UI", 13, "bold"), fill=self.PLAYER_ARROW)

    def is_pit_clickable(self, side, idx):
        return (not self.animating and
                not self.game.game_over and
                side == self.game.current_player and
                self.game.board.pits[side][idx] > 0 and
                (not self.game.ai_enabled or self.game.current_player == 0))

    def on_click(self, event):
        if self.animating or self.game.game_over:
            return
        # Find which pit was clicked
        for side in [0, 1]:
            for idx in range(self.game.board.pits_per_side):
                x, y = self.pit_coords(side, idx)
                if (x - self.PIT_RADIUS < event.x < x + self.PIT_RADIUS and
                    y - self.PIT_RADIUS < event.y < y + self.PIT_RADIUS):
                    if self.is_pit_clickable(side, idx):
                        self.selected_pit = (side, idx)
                        self.animate_move(idx)
                    else:
                        self.status_label.config(text="Invalid move! Choose a pit on your side with seeds.",
                                                fg="#d90429")
                    return

    def on_motion(self, event):
        if self.animating or self.game.game_over:
            return
        found = None
        for side in [0, 1]:
            for idx in range(self.game.board.pits_per_side):
                x, y = self.pit_coords(side, idx)
                if (x - self.PIT_RADIUS < event.x < x + self.PIT_RADIUS and
                    y - self.PIT_RADIUS < event.y < y + self.PIT_RADIUS):
                    if self.is_pit_clickable(side, idx):
                        found = (side, idx)
        if found != self.hovered_pit:
            self.hovered_pit = found
            self.draw_board()

    def on_leave(self, event):
        if self.hovered_pit is not None:
            self.hovered_pit = None
            self.draw_board()

    def animate_move(self, pit_idx):
        """Animate the move, then update the board."""
        self.animating = True
        move_seq, extra_turn, capture_info, game_over = self.game.make_move(pit_idx)
        if move_seq is None:
            self.animating = False
            return
        # Animate seeds
        def do_animation():
            # Remove all seeds from selected pit
            side, idx = self.game.current_player, pit_idx
            n = self.game.board.pits[side][idx]
            # Animate each seed
            for i, (s, p, is_store) in enumerate(move_seq):
                self.draw_board()
                # Highlight pit or store
                if is_store:
                    x, y = self.store_coords(s)
                else:
                    x, y = self.pit_coords(s, p)
                self.canvas.create_oval(x - self.PIT_RADIUS, y - self.PIT_RADIUS,
                                       x + self.PIT_RADIUS, y + self.PIT_RADIUS,
                                       outline=self.HOVER_COLOR, width=5)
                self.root.update()
                time.sleep(self.ANIMATION_DELAY)
            # Animate capture
            if capture_info:
                s, p, opp, opp_pit, captured = capture_info
                self.draw_board()
                x, y = self.pit_coords(opp, opp_pit)
                self.canvas.create_oval(x - self.PIT_RADIUS, y - self.PIT_RADIUS,
                                       x + self.PIT_RADIUS, y + self.PIT_RADIUS,
                                       outline="#ff595e", width=5)
                self.root.update()
                time.sleep(0.3)
            self.draw_board()
            self.update_status()
            self.animating = False
            self.check_ai_move()
        threading.Thread(target=do_animation).start()

    def update_status(self):
        if self.game.game_over:
            winner = self.game.get_winner()
            if winner == -1:
                msg = "Game Over! It's a draw."
            else:
                msg = f"Game Over! Player {winner+1} wins!"
            self.status_label.config(text=msg, fg="#222")
        else:
            side = self.game.current_player
            msg = f"Player {side+1}'s turn. Click a pit to move."
            if self.game.ai_enabled and side == self.game.ai_player:
                msg = "AI is thinking..."
            self.status_label.config(text=msg, fg="#222")
        s1, s2 = self.game.board.stores
        self.score_label.config(text=f"Score: Player 1 = {s1}   Player 2 = {s2}")

    def update_move_history(self):
        self.move_history_box.delete(0, tk.END)
        for i, (player, pit, (pits, stores)) in enumerate(self.game.move_history):
            move = f"P{player+1} {chr(ord('A')+pit)}"
            s1, s2 = stores
            self.move_history_box.insert(tk.END, f"{i+1:2d}. {move:7s} | P1: {s1:2d}  P2: {s2:2d}")

    def reset_game(self):
        if self.animating:
            return
        self.game.reset()
        self.draw_board()
        self.update_status()

    def check_ai_move(self):
        if (self.game.ai_enabled and
            not self.game.game_over and
            self.game.current_player == self.game.ai_player and
            not self.animating):
            self.root.after(500, self.do_ai_move)

    def do_ai_move(self):
        pit = self.game.ai_move()
        if pit is not None:
            self.animate_move(pit)
        else:
            self.update_status()

# --- Main ---

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="#f6f6f6")
    app = MancalaGUI(root)
    root.mainloop()