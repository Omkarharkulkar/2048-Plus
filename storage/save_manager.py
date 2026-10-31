
import json
from pathlib import Path


SAVE_FILE = Path(__file__).resolve().parent / "savegame.json"


def save_game(game):
    """Save the current game state as JSON."""
    data = {
        "version": 1,
        "size": game.size,
        "board": game.board,
        "score": game.score,
        "won": game.won,
        "game_over": game.game_over,
    }

    with SAVE_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_game(game):
    """Load a saved game. Return False if no valid save exists."""
    if not SAVE_FILE.exists():
        return False

    try:
        with SAVE_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        size = data["size"]
        board = data["board"]
        score = data["score"]

        if not isinstance(size, int) or size != game.size:
            return False

        if (
            not isinstance(board, list)
            or len(board) != size
            or any(
                not isinstance(row, list) or len(row) != size
                for row in board
            )
        ):
            return False

        # Validate tile values before accepting the save.
        for row in board:
            for value in row:
                if (
                    not isinstance(value, int)
                    or value < 0
                    or (value != 0 and value & (value - 1) != 0)
                ):
                    return False

        if not isinstance(score, int) or score < 0:
            return False

        won = data["won"]
        game_over = data["game_over"]

        if not isinstance(won, bool) or not isinstance(game_over, bool):
            return False

        # A full board may still have a legal merge.
        game.board = [row[:] for row in board]
        game.score = score
        game.won = won
        game.game_over = game.check_game_over()

        # Don't retain undo history from the previous session.
        game.history.clear()

        return True

    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return False
