
from copy import copy

from game.engine import Game2048


class HintEngine:
    """Evaluate possible moves without changing the real game."""

    DIRECTIONS = ("Left", "Right", "Up", "Down")

    @staticmethod
    def count_empty_cells(board):
        return sum(
            cell == 0
            for row in board
            for cell in row
        )

    @staticmethod
    def largest_tile(board):
        return max(max(row) for row in board)

    @staticmethod
    def smoothness(board):
        penalty = 0

        for row in board:
            for first, second in zip(row, row[1:]):
                if first and second:
                    penalty += abs(
                        first.bit_length() - second.bit_length()
                    )

        for column in zip(*board):
            for first, second in zip(column, column[1:]):
                if first and second:
                    penalty += abs(
                        first.bit_length() - second.bit_length()
                    )

        return -penalty

    def evaluate(self, board, score):
        empty_cells = self.count_empty_cells(board)
        largest = self.largest_tile(board)

        return (
            empty_cells * 100
            + largest.bit_length() * 10
            + self.smoothness(board) * 3
            + score * 0.1
        )

    def suggest_move(self, game):
        if game.game_over:
            return None

        best_direction = None
        best_value = float("-inf")

        for direction in self.DIRECTIONS:
            candidate = copy(game)
            candidate.board = [row[:] for row in game.board]
            candidate.history = []

            changed = candidate.move(
                direction.lower(),
                spawn=False,
            )

            if not changed:
                continue

            value = self.evaluate(
                candidate.board,
                candidate.score,
            )

            if value > best_value:
                best_value = value
                best_direction = direction

        return best_direction
