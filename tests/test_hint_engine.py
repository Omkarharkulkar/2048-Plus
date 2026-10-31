
import random
import unittest

from game.engine import Game2048
from game.hint_engine import HintEngine


class TestHintEngine(unittest.TestCase):

    def setUp(self):
        self.game = Game2048()
        self.game.board = [
            [2, 2, 0, 0],
            [4, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        self.game.score = 0
        self.game.won = False
        self.game.game_over = False
        self.hints = HintEngine()

    def test_suggests_a_legal_direction(self):
        suggestion = self.hints.suggest_move(self.game)

        self.assertIn(
            suggestion,
            HintEngine.DIRECTIONS,
        )

    def test_hint_does_not_change_board_or_score(self):
        original_board = [row[:] for row in self.game.board]
        original_score = self.game.score

        self.hints.suggest_move(self.game)

        self.assertEqual(self.game.board, original_board)
        self.assertEqual(self.game.score, original_score)

    def test_hint_does_not_change_undo_history(self):
        original_history = self.game.history.copy()

        self.hints.suggest_move(self.game)

        self.assertEqual(
            self.game.history,
            original_history,
        )

    def test_repeated_hints_are_consistent(self):
        first = self.hints.suggest_move(self.game)
        second = self.hints.suggest_move(self.game)

        self.assertEqual(first, second)

    def test_hint_does_not_change_random_state(self):
        random_state = random.getstate()

        self.hints.suggest_move(self.game)

        self.assertEqual(random.getstate(), random_state)

    def test_no_hint_when_game_is_over(self):
        self.game.game_over = True

        self.assertIsNone(
            self.hints.suggest_move(self.game)
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
