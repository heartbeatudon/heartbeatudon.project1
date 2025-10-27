"""Unit tests for the heartbeatudon text adventure game."""
from heartbeatudon_game import AdventureGame


def test_requires_torch_to_take_rope() -> None:
    game = AdventureGame()
    game.handle_action("north")  # forest
    game.handle_action("north")  # cavern
    message = game.handle_action("take rope")
    assert "need a torch" in message.lower()


def test_player_can_win_the_game() -> None:
    game = AdventureGame()
    game.handle_action("take torch")
    game.handle_action("north")  # forest
    game.handle_action("north")  # cavern
    game.handle_action("take rope")
    game.handle_action("south")  # forest
    game.handle_action("east")  # ravine
    message = game.handle_action("east")  # tower
    assert "arrive" in message.lower()
    victory_message = game.handle_action("take relic")
    assert game.game_over is True
    assert game.won is True
    assert "relic" in victory_message.lower()
