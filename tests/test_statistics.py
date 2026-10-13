
import json
import tempfile
import unittest
from pathlib import Path

from game.statistics import PlayerStatistics


class TestPlayerStatistics(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.stats_file = (
            Path(self.temp_dir.name) / "statistics.json"
        )
        self.stats = PlayerStatistics(
            save_path=self.stats_file
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initial_statistics(self):
        summary = self.stats.get_summary()

        self.assertEqual(summary["games_played"], 0)
        self.assertEqual(summary["best_score"], 0)
        self.assertEqual(summary["highest_tile"], 0)
        self.assertEqual(summary["total_merges"], 0)

    def test_record_game_started(self):
        self.stats.record_game_started()

        self.assertEqual(
            self.stats.get_summary()["games_played"],
            1,
        )

    def test_record_move_updates_statistics(self):
        board = [
            [4, 8, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]

        self.stats.record_move(
            score=20,
            board=board,
            merges=2,
        )

        summary = self.stats.get_summary()

        self.assertEqual(summary["best_score"], 20)
        self.assertEqual(summary["highest_tile"], 8)
        self.assertEqual(summary["total_merges"], 2)

    def test_statistics_persist_after_reload(self):
        self.stats.record_game_started()
        self.stats.record_move(
            score=64,
            board=[
                [32, 16, 8, 4],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            merges=3,
        )

        reloaded = PlayerStatistics(
            save_path=self.stats_file
        )
        summary = reloaded.get_summary()

        self.assertEqual(summary["games_played"], 1)
        self.assertEqual(summary["best_score"], 64)
        self.assertEqual(summary["highest_tile"], 32)
        self.assertEqual(summary["total_merges"], 3)

    def test_achievement_is_unlocked(self):
        self.stats.record_move(
            score=100,
            board=[
                [128, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            merges=1,
        )

        achievements = (
            self.stats.get_summary()["unlocked_achievements"]
        )

        self.assertIn("Getting Started", achievements)


if __name__ == "__main__":
    unittest.main(verbosity=2)

