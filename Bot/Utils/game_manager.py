import main, inspect

active_games = []

def is_active(identifier: str) -> bool:
    """Check if a game is already active."""
    return identifier in active_games

def add_game(identifier: str):
    """Register a new active game."""
    # Get the current frame
    current_frame = inspect.currentframe()
    # Get the outer frame (the caller's frame)
    caller_frame = current_frame.f_back
    # Get the code object of the caller's frame
    caller_code = caller_frame.f_code
    # Get the name of the caller's method
    caller_name = caller_code.co_name
    active_games.append(identifier)
    main.logger.info(f"Adding game {identifier} to active games list.\n Active games: {active_games}\n From: {caller_name}")

def remove_game(identifier: str):
    """Remove a finished game."""
    try:
        active_games.remove(identifier)
        main.logger.info(f"Removing game {identifier} to active games list.\n Active games: {active_games}")
    except Exception as exception:
        # Get the current frame
        current_frame = inspect.currentframe()
        # Get the outer frame (the caller's frame)
        caller_frame = current_frame.f_back
        # Get the code object of the caller's frame
        caller_code = caller_frame.f_code
        # Get the name of the caller's method
        caller_name = caller_code.co_name
        main.logger.error(f"Failed to remove game {identifier} from active games list. \nError: {exception}\n Active games: {active_games}\n From: {caller_name}")
        pass
