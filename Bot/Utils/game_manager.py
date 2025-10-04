active_games = []  # key: uuid or game_number, value: GameView or KnuckleboneGame

def is_active(identifier: str) -> bool:
    """Check if a game is already active."""
    return identifier in active_games

def add_game(identifier: str):
    """Register a new active game."""
    active_games.append(identifier)

def remove_game(identifier: str):
    """Remove a finished game."""
    active_games.remove(identifier)
