"""Command-line entry point for the heartbeatudon text adventure."""
from __future__ import annotations

from heartbeatudon_game import AdventureGame


def main() -> None:
    """Run the interactive adventure game loop."""

    game = AdventureGame()
    print("Welcome to the Heartbeat Udon Adventure!\n")
    print(game.describe_current_room())

    try:
        while not game.game_over:
            action = input("\nWhat will you do? ")
            response = game.handle_action(action)
            print(f"\n{response}")
        if game.won:
            print("\nCongratulations! You completed the adventure.")
        else:
            print("\nThe adventure ends here. Thanks for playing!")
    except (EOFError, KeyboardInterrupt):
        print("\n\nYou step away from the adventure for now. Farewell!")


if __name__ == "__main__":
    main()
