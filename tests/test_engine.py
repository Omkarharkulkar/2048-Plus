
import unittest

from game.engine import Game2048


class TestGameEngine(unittest.TestCase):

    def setUp(self):
        """Create a fresh game for every test."""
        self.game = Game2048()

        # Use a predictable board for testing.
        self.game.board = [
            [2, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        self.game.score = 0
        self.game.won = False
        self.game.game_over = False
        self.game.history.clear()

    def test_merge_line(self):
        result, points, merges = self.game.merge_line(
            [2, 2, 4, 4]
        )

        self.assertEqual(result, [4, 8, 0, 0])
        self.assertEqual(points, 12)
        self.assertEqual(merges, 2)

    def test_left_move_merges_tiles(self):
        changed = self.game.move("left")

        self.assertTrue(changed)
        self.assertEqual(self.game.board[0][:2], [4, 0])
        self.assertEqual(self.game.score, 4)

    def test_move_does_not_merge_a_tile_twice(self):
        result, points, merges = self.game.merge_line(
            [2, 2, 4, 0]
        )

        self.assertEqual(result, [4, 4, 0, 0])
        self.assertEqual(points, 4)
        self.assertEqual(merges, 1)

    def test_undo_restores_previous_board(self):
        original_board = [row[:] for row in self.game.board]
        original_score = self.game.score

        self.game.move("left")
        restored = self.game.undo()

        self.assertTrue(restored)
        self.assertEqual(self.game.board, original_board)
        self.assertEqual(self.game.score, original_score)

    
    def test_invalid_direction_does_not_change_board(self):
        original_board = [row[:] for row in self.game.board]

        with self.assertRaises(ValueError):
          self.game.move("diagonal")

        self.assertEqual(self.game.board, original_board)



if __name__ == "__main__":
    unittest.main(verbosity=2)
