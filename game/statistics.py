
import json
from pathlib import Path


class PlayerStatistics:
    """Track player progress across multiple games."""

    def __init__(self, save_path=None):
        if save_path is None:
            save_path = (
                Path(__file__).resolve().parent.parent
                / "storage"
                / "statistics.json"
            )

        self.save_path = Path(save_path)

        self.games_played = 0
        self.best_score = 0
        self.highest_tile = 0
        self.total_merges = 0
        self.unlocked_achievements = []

        self.load()

    def record_game_started(self):
        """Count a newly started game."""
        self.games_played += 1
        self.save()

    def record_move(self, score, board, merges=0):
        """Update records after a successful move."""
        self.best_score = max(self.best_score, score)
        self.total_merges += merges

        largest_tile = max(
            (value for row in board for value in row),
            default=0,
        )
        self.highest_tile = max(
            self.highest_tile,
            largest_tile,
        )

        self._check_achievements()
        self.save()

    def _check_achievements(self):
        """Unlock achievements based on the highest tile reached."""
        milestones = {
            128: "Getting Started",
            512: "Tile Collector",
            1024: "Puzzle Expert",
            2048: "2048 Master",
        }

        for tile, name in milestones.items():
            if self.highest_tile >= tile:
                if name not in self.unlocked_achievements:
                    self.unlocked_achievements.append(name)

    def save(self):
        """Persist statistics to a JSON file."""
        self.save_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = {
            "version": 1,
            "games_played": self.games_played,
            "best_score": self.best_score,
            "highest_tile": self.highest_tile,
            "total_merges": self.total_merges,
            "unlocked_achievements": self.unlocked_achievements,
        }

        with self.save_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def load(self):
        """Load saved statistics, or use defaults if unavailable."""
        if not self.save_path.exists():
            return

        try:
            with self.save_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            self.games_played = max(
                0, int(data.get("games_played", 0))
            )
            self.best_score = max(
                0, int(data.get("best_score", 0))
            )
            self.highest_tile = max(
                0, int(data.get("highest_tile", 0))
            )
            self.total_merges = max(
                0, int(data.get("total_merges", 0))
            )

            achievements = data.get(
                "unlocked_achievements", []
            )

            if isinstance(achievements, list):
                self.unlocked_achievements = [
                    name for name in achievements
                    if isinstance(name, str)
                ]

            self._check_achievements()

        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            # Keep default values if the statistics file is invalid.
            pass

    def get_summary(self):
        """Return statistics in a convenient dictionary."""
        return {
            "games_played": self.games_played,
            "best_score": self.best_score,
            "highest_tile": self.highest_tile,
            "total_merges": self.total_merges,
            "unlocked_achievements": list(
                self.unlocked_achievements
            ),
        }

