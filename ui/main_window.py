
import tkinter as tk
from tkinter import messagebox

from game.engine import Game2048

from storage.save_manager import save_game, load_game

from game.statistics import PlayerStatistics

from game.hint_engine import HintEngine

class GameWindow:
    """Tkinter interface for the 2048 game."""

    BACKGROUND = "#FAF8EF"
    BOARD_BACKGROUND = "#BBADA0"
    EMPTY_COLOR = "#CDC1B4"

    TILE_COLORS = {
        2: "#EEE4DA",
        4: "#EDE0C8",
        8: "#F2B179",
        16: "#F59563",
        32: "#F67C5F",
        64: "#F65E3B",
        128: "#EDCF72",
        256: "#EDCC61",
        512: "#EDC850",
        1024: "#EDC53F",
        2048: "#EDC22E",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("2048 Plus")
        self.root.configure(bg=self.BACKGROUND)
        self.root.resizable(False, False)

        self.game = Game2048()
        self.stats = PlayerStatistics()
        self._game_counted = False
        self.tile_labels = []
        self.previous_won = False
        self.previous_game_over = False

        self.build_interface()
        self.refresh_board()
        
        self.hint_engine = HintEngine()

        # Listen for arrow keys.
        self.root.bind("<Left>", lambda event: self.handle_move("left"))
        self.root.bind("<Right>", lambda event: self.handle_move("right"))
        self.root.bind("<Up>", lambda event: self.handle_move("up"))
        self.root.bind("<Down>", lambda event: self.handle_move("down"))

        # Also support WASD.
        self.root.bind("a", lambda event: self.handle_move("left"))
        self.root.bind("d", lambda event: self.handle_move("right"))
        self.root.bind("w", lambda event: self.handle_move("up"))
        self.root.bind("s", lambda event: self.handle_move("down"))

    def build_interface(self):
        """Create the window's widgets."""

        header = tk.Frame(self.root, bg=self.BACKGROUND)
        header.pack(fill="x", padx=18, pady=(18, 8))

        title = tk.Label(
            header,
            text="2048 PLUS",
            font=("Arial", 25, "bold"),
            bg=self.BACKGROUND,
            fg="#776E65",
        )
        title.pack(side="left")

        score_box = tk.Frame(
            header,
            bg=self.BOARD_BACKGROUND,
            padx=12,
            pady=6,
        )
        score_box.pack(side="right")

        tk.Label(
            score_box,
            text="SCORE",
            font=("Arial", 9, "bold"),
            bg=self.BOARD_BACKGROUND,
            fg="white",
        ).pack()

        self.score_label = tk.Label(
            score_box,
            text="0",
            font=("Arial", 17, "bold"),
            bg=self.BOARD_BACKGROUND,
            fg="white",
        )
        self.score_label.pack()

        self.status_label = tk.Label(
            self.root,
            text="Merge tiles and reach 2048!",
            font=("Arial", 10),
            bg=self.BACKGROUND,
            fg="#776E65",
        )
        self.status_label.pack(pady=(0, 10))

        board_frame = tk.Frame(
            self.root,
            bg=self.BOARD_BACKGROUND,
            padx=7,
            pady=7,
        )
        board_frame.pack(padx=18, pady=4)

        for row in range(4):
            label_row = []

            for col in range(4):
                label = tk.Label(
                    board_frame,
                    text="",
                    width=4,
                    height=2,
                    font=("Arial", 22, "bold"),
                    bg=self.EMPTY_COLOR,
                    fg="#776E65",
                    relief="flat",
                )
                label.grid(
                    row=row,
                    column=col,
                    padx=4,
                    pady=4,
                    sticky="nsew",
                )
                label_row.append(label)

            self.tile_labels.append(label_row)

        controls = tk.Frame(self.root, bg=self.BACKGROUND)
        controls.pack(fill="x", padx=18, pady=(12, 18))

        tk.Label(
            controls,
            text="Move with arrow keys or W A S D",
            font=("Arial", 9),
            bg=self.BACKGROUND,
            fg="#776E65",
        ).pack(side="left")

        
        tk.Button(
            controls,
            text="Undo",
            command=self.undo_move,
            font=("Arial", 10, "bold"),
            bg="#8F7A66",
            fg="white",
            relief="flat",
            padx=10,
            pady=7,
        ).pack(side="left", padx=(0, 5))

        tk.Button(
            controls,
            text="Save",
            command=self.save_current_game,
            font=("Arial", 10, "bold"),
            bg="#5B8E7D",
            fg="white",
            relief="flat",
            padx=10,
            pady=7,
        ).pack(side="left", padx=5)

        tk.Button(
            controls,
            text="Resume",
            command=self.resume_game,
            font=("Arial", 10, "bold"),
            bg="#5B8E7D",
            fg="white",
            relief="flat",
            padx=10,
            pady=7,
        ).pack(side="left", padx=5)

        tk.Button(
            controls,
            text="New Game",
            command=self.restart_game,
            font=("Arial", 10, "bold"),
            bg="#8F7A66",
            fg="white",
            relief="flat",
            padx=10,
            pady=7,
        ).pack(side="right")
        
        tk.Button(
            controls,
            text="Statistics",
            command=self.show_statistics,
            font=("Arial", 10, "bold"),
            bg="#5B8E7D",
            fg="white",
            relief="flat",
            padx=10,
            pady=7,
        ).pack(side="left", padx=5)
        
        tk.Button(
           controls,
           text="Hint",
           command=self.show_hint,
           font=("Arial", 10, "bold"),
           bg="#D9A441",
           fg="white",
           relief="flat",
           padx=10,
           pady=7,
        ).pack(side="left", padx=5)




    def refresh_board(self):
        """Update tile colors, values, score, and status."""

        for row in range(4):
            for col in range(4):
                value = self.game.board[row][col]
                label = self.tile_labels[row][col]

                if value == 0:
                    label.configure(
                        text="",
                        bg=self.EMPTY_COLOR,
                    )
                else:
                    color = self.TILE_COLORS.get(
                        value, "#3C3A32"
                    )

                    text_color = (
                        "#776E65" if value <= 4 else "#FFFFFF"
                    )

                    # Use a smaller font for large tile values.
                    font_size = 22 if value < 1024 else 16

                    label.configure(
                        text=str(value),
                        bg=color,
                        fg=text_color,
                        font=("Arial", font_size, "bold"),
                    )

        self.score_label.configure(text=str(self.game.score))

        if self.game.game_over:
            self.status_label.configure(
                text="Game over! Start a new game to play again."
            )
        elif self.game.won:
            self.status_label.configure(
                text="You reached 2048! Keep playing if you like."
            )
        else:
            self.status_label.configure(
                text="Merge tiles and reach 2048!"
            )

    def handle_move(self, direction):
        """Send a move to the engine and refresh the display."""

        if self.game.game_over:
            return

        changed = self.game.move(direction)

        if changed:
            if not self._game_counted:
                 self.stats.record_game_started()
                 self._game_counted = True
                 
            previous_achievements = set(
               self.stats.get_summary()["unlocked_achievements"]
            )

            self.stats.record_move(
               score=self.game.score,
               board=self.game.board,
               merges=self.game.last_move_merges,
            )

            current_achievements = set(
               self.stats.get_summary()["unlocked_achievements"]
            )

            newly_unlocked = current_achievements - previous_achievements

            self.refresh_board()

            for achievement in sorted(newly_unlocked):
                messagebox.showinfo(
                    "Achievement Unlocked!",
                    f"Congratulations!\n\nYou unlocked: {achievement}",
                )

            # Display each milestone only once.
            if self.game.won and not self.previous_won:
                self.previous_won = True
                messagebox.showinfo(
                    "Congratulations!",
                    "You reached 2048! You can keep playing.",
                )

            if (
                self.game.game_over
                and not self.previous_game_over
            ):
                self.previous_game_over = True
                messagebox.showinfo(
                    "Game Over",
                    f"No more moves are available.\n"
                    f"Final score: {self.game.score}",
                )

    def restart_game(self):
        """Reset the engine and the interface."""

        self.game.restart()
        self.previous_won = False
        self.previous_game_over = False
        self.refresh_board()
        
    
    def undo_move(self):
        """Undo the last valid move."""
        if self.game.undo():
            self.refresh_board()
            self.status_label.configure(text="Last move undone.")
        else:
            self.status_label.configure(text="No moves to undo.")

    def save_current_game(self):
        """Save the current game."""
        try:
            save_game(self.game)
            self.status_label.configure(text="Game saved successfully.")
        except OSError as error:
            messagebox.showerror(
                "Save Error",
                f"Could not save the game:\n{error}",
            )

    def resume_game(self):
        """Restore the previously saved game."""
        try:
            if load_game(self.game):
                self.previous_won = self.game.won
                self.previous_game_over = self.game.game_over
                self._game_counted = True
                self.refresh_board()
                self.status_label.configure(text="Saved game loaded.")
            else:
                messagebox.showinfo(
                    "Resume Game",
                    "No valid saved game was found.",
                )
        except OSError as error:
            messagebox.showerror(
                "Load Error",
                f"Could not load the saved game:\n{error}",
            )
            
    
    def show_statistics(self):
        """Display the player's persistent statistics."""
        summary = self.stats.get_summary()

        window = tk.Toplevel(self.root)
        window.title("Player Statistics")
        window.configure(bg=self.BACKGROUND)
        window.resizable(False, False)

        tk.Label(
            window,
            text="PLAYER STATISTICS",
            font=("Arial", 18, "bold"),
            bg=self.BACKGROUND,
            fg="#776E65",
        ).pack(padx=24, pady=(20, 12))

        stats_text = (
            f"Games played: {summary['games_played']}\n"
            f"Personal best: {summary['best_score']}\n"
            f"Highest tile: {summary['highest_tile']}\n"
            f"Total merges: {summary['total_merges']}\n"
            f"Achievements unlocked: "
            f"{len(summary['unlocked_achievements'])}"
            )

        tk.Label(
            window,
            text=stats_text,
            font=("Arial", 12),
            justify="left",
            bg=self.BACKGROUND,
            fg="#776E65",
        ).pack(padx=24, pady=8, anchor="w")

        tk.Label(
            window,
            text="ACHIEVEMENTS",
            font=("Arial", 13, "bold"),
            bg=self.BACKGROUND,
            fg="#776E65",
        ).pack(padx=24, pady=(12, 6), anchor="w")

        achievements = summary["unlocked_achievements"]

        if achievements:
            achievement_text = "\n".join(
                f"✓ {name}" for name in achievements
            )
        else:
            achievement_text = "No achievements unlocked yet."

        tk.Label(
            window,
            text=achievement_text,
            font=("Arial", 10),
            justify="left",
            bg=self.BACKGROUND,
            fg="#776E65",
        ).pack(padx=24, pady=(0, 20), anchor="w")
    
    def show_hint(self):
      """Show a recommended move without changing the game."""
      direction = self.hint_engine.suggest_move(self.game)

      if direction is None:
          messagebox.showinfo(
               "Hint",
               "No legal moves are available. Start a new game!",
          )
          return

      messagebox.showinfo(
        "Suggested Move",
        f"Try moving {direction}.\n\n"
        "This suggestion is based on the current board. "
        "It will not move any tiles automatically.",
    )
      
    def new_game(self):
        """Start and count a new game."""
        self.game.restart()

        self.stats.record_game_started()
        self._game_counted = True

        self.refresh_board()





def main():
    root = tk.Tk()
    GameWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()

