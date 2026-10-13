
import random
import copy


class Game2048:
    """Core rules and state for the 2048 puzzle game."""

    def __init__(self, size=4):
        self.size = size
        self.history = []
        self.restart()

    def restart(self):
        """Start a new game."""
        self.history.clear()
        self.board = [
            [0 for _ in range(self.size)]
            for _ in range(self.size)
        ]
        self.score = 0
        self.won = False
        self.game_over = False

        self.add_random_tile()
        self.add_random_tile()
        self.last_move_merges = 0

    def add_random_tile(self):
        """Place a 2 or 4 in a randomly selected empty cell."""
        empty_cells = [
            (row, col)
            for row in range(self.size)
            for col in range(self.size)
            if self.board[row][col] == 0
        ]

        if not empty_cells:
            return

        row, col = random.choice(empty_cells)
        self.board[row][col] = random.choices(
            [2, 4],
            weights=[90, 10]
        )[0]

    
    @staticmethod
    def merge_line(line):
        """Compress and merge one line toward the left."""
        non_zero = [value for value in line if value != 0]
        merged = []
        gained_score = 0
        merge_count = 0
        index = 0

        while index < len(non_zero):
            if (
                index + 1 < len(non_zero)
                and non_zero[index] == non_zero[index + 1]
            ):
                new_value = non_zero[index] * 2
                merged.append(new_value)
                gained_score += new_value
                merge_count += 1
                index += 2
            else:
                merged.append(non_zero[index])
                index += 1

        merged.extend([0] * (len(line) - len(merged)))
        return merged, gained_score, merge_count


    def move(self, direction, spawn=True):
        """Move tiles. Return True if the board changed."""
        if direction not in ("left", "right", "up", "down"):
            raise ValueError(
                "Direction must be left, right, up, or down."
            )

        if self.game_over:
            return False

        old_board = copy.deepcopy(self.board)
        old_score = self.score
        old_won = self.won
        old_game_over = self.game_over
        old_random_state = random.getstate()
        gained_score = 0
        merges_this_move = 0

        if direction in ("left", "right"):
            for row_index in range(self.size):
                line = self.board[row_index][:]

                if direction == "right":
                    line.reverse()

                new_line, points, merge_count = self.merge_line(line)
                merges_this_move += merge_count

                if direction == "right":
                    new_line.reverse()

                self.board[row_index] = new_line
                gained_score += points

        else:
            for col_index in range(self.size):
                line = [
                    self.board[row_index][col_index]
                    for row_index in range(self.size)
                ]

                if direction == "down":
                    line.reverse()

                new_line, points, merge_count = self.merge_line(line)
                merges_this_move += merge_count

                if direction == "down":
                    new_line.reverse()

                for row_index in range(self.size):
                    self.board[row_index][col_index] = (
                        new_line[row_index]
                    )

                gained_score += points

        changed = self.board != old_board
        
        if changed:
            self.history.append({
                "board": old_board,
                "score": old_score,
                "won": old_won,
                "game_over": old_game_over,
                "random_state": old_random_state,
            })
            
            self.score += gained_score
            
            if spawn:
                self.add_random_tile()
            
            self.check_win()
            self.check_game_over()
            self.last_move_merges = merges_this_move

        return changed

    def check_win(self):
        """Record whether the target tile has been reached."""
        self.won = any(
            value >= 2048
            for row in self.board
            for value in row
        )
        return self.won

    def check_game_over(self):
        """Check whether any legal move remains."""
        for row in self.board:
            if 0 in row:
                self.game_over = False
                return False

        for row in range(self.size):
            for col in range(self.size):
                value = self.board[row][col]

                if col + 1 < self.size:
                    if value == self.board[row][col + 1]:
                        self.game_over = False
                        return False

                if row + 1 < self.size:
                    if value == self.board[row + 1][col]:
                        self.game_over = False
                        return False

        self.game_over = True
        return True

    def get_state(self):
        """Return a copy of the current game state."""
        return {
            "board": copy.deepcopy(self.board),
            "score": self.score,
            "won": self.won,
            "game_over": self.game_over,
            }
    
    def save_snapshot(self):
        """Remember the current state before a valid move."""
        self.history.append({
            "board": copy.deepcopy(self.board),
            "score": self.score,
            "won": self.won,
            "game_over": self.game_over,
            "random_state": random.getstate(),
            })

    def undo(self):
        """Restore the state before the last valid move."""
        if not self.history:
            return False

        previous = self.history.pop()

        self.board = copy.deepcopy(previous["board"])
        self.score = previous["score"]
        self.won = previous["won"]
        self.game_over = previous["game_over"]
        random.setstate(previous["random_state"])

        return True

