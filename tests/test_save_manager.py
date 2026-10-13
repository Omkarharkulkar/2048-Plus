
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from game.engine import Game2048
from storage import save_manager


class TestSaveManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.save_path = Path(self.temp_dir.name) / "savegame.json"

        self.save_path_patcher = patch.object(
            save_manager,
            "SAVE_FILE",
            self.save_path,
        )
        self.save_path_patcher.start()

        self.game = Game2048()
        self.game.board = [
            [2, 4, 8, 16],
            [32, 64, 128, 256],
            [512, 1024, 0, 0],
            [0, 0, 0, 0],
        ]
        self.game.score = 1200
        self.game.won = False
        self.game.game_over = False

    def tearDown(self):
        self.save_path_patcher.stop()
        self.temp_dir.cleanup()

    def test_save_creates_file(self):
        save_manager.save_game(self.game)

        self.assertTrue(self.save_path.exists())

    def test_load_restores_board_and_score(self):
        save_manager.save_game(self.game)

        restored = Game2048()
        restored.board = [[0] * 4 for _ in range(4)]
        restored.score = 0

        result = save_manager.load_game(restored)

        self.assertTrue(result)
        self.assertEqual(restored.board, self.game.board)
        self.assertEqual(restored.score, 1200)

    def test_load_clears_undo_history(self):
        save_manager.save_game(self.game)

        restored = Game2048()
        restored.history.append({"test": "old history"})

        result = save_manager.load_game(restored)

        self.assertTrue(result)
        self.assertEqual(restored.history, [])

    def test_missing_save_returns_false(self):
        result = save_manager.load_game(self.game)

        self.assertFalse(result)

    def test_invalid_board_is_rejected(self):
        save_manager.save_game(self.game)

        with self.save_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        data["board"] = [[2, 4], [8, 16]]

        with self.save_path.open("w", encoding="utf-8") as file:
            json.dump(data, file)

        original_board = [row[:] for row in self.game.board]
        original_score = self.game.score

        result = save_manager.load_game(self.game)

        self.assertFalse(result)
        self.assertEqual(self.game.board, original_board)
        self.assertEqual(self.game.score, original_score)


if __name__ == "__main__":
    unittest.main(verbosity=2)

