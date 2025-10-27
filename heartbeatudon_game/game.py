"""Core game logic for the heartbeatudon text adventure."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Set, Tuple


@dataclass(frozen=True)
class Room:
    """Represents a location in the adventure map."""

    description: str
    exits: Dict[str, str]
    hint: Optional[str] = None


@dataclass
class AdventureGame:
    """A light-weight text adventure that can be played in the terminal."""

    rooms: Dict[str, Room] = field(default_factory=dict)
    room_items: Dict[str, Set[str]] = field(default_factory=dict)
    item_requirements: Dict[Tuple[str, str], Optional[str]] = field(default_factory=dict)
    locked_exits: Dict[Tuple[str, str], Optional[str]] = field(default_factory=dict)

    current_room: str = "camp"
    inventory: Set[str] = field(default_factory=set)
    game_over: bool = False
    won: bool = False

    def __post_init__(self) -> None:
        if not self.rooms:
            self.rooms = self._build_default_map()
        if not self.room_items:
            self.room_items = self._build_default_items()
        if not self.item_requirements:
            self.item_requirements = self._build_item_requirements()
        if not self.locked_exits:
            self.locked_exits = self._build_locked_exits()
        self.reset()

    # -- map builders -----------------------------------------------------
    def _build_default_map(self) -> Dict[str, Room]:
        return {
            "camp": Room(
                description=(
                    "You wake beside a quiet campfire. Pines sway overhead and a narrow "
                    "trail leads north into the forest."
                ),
                exits={"north": "forest"},
                hint="Try taking anything that looks useful before you leave.",
            ),
            "forest": Room(
                description=(
                    "Dense trees surround you. Paths twist north toward a dark cavern and "
                    "east toward a narrow ravine. The way back south leads to the safety "
                    "of your camp."
                ),
                exits={"south": "camp", "north": "cavern", "east": "ravine"},
                hint="Exploration rewards the prepared adventurer.",
            ),
            "cavern": Room(
                description=(
                    "A cavern yawns before you. The air is cool and the shadows are deep. "
                    "Without a light it will be hard to find anything of value here."
                ),
                exits={"south": "forest"},
                hint="A torch would help reveal what's hidden in the dark.",
            ),
            "ravine": Room(
                description=(
                    "A chasm splits the ground. A weathered watchtower rises beyond it, "
                    "its door inviting yet unreachable without aid."
                ),
                exits={"west": "forest", "east": "tower"},
                hint="Something flexible might help you cross safely.",
            ),
            "tower": Room(
                description=(
                    "Inside the tower dust motes float through the air. A stone chest rests "
                    "against the far wall, waiting to be searched."
                ),
                exits={"west": "ravine"},
                hint="Search carefully; this is what you came for.",
            ),
        }

    def _build_default_items(self) -> Dict[str, Set[str]]:
        return {
            "camp": {"torch"},
            "cavern": {"rope"},
            "tower": {"relic"},
        }

    def _build_item_requirements(self) -> Dict[Tuple[str, str], Optional[str]]:
        return {
            ("cavern", "rope"): "torch",
            ("tower", "relic"): "torch",
        }

    def _build_locked_exits(self) -> Dict[Tuple[str, str], Optional[str]]:
        return {
            ("ravine", "east"): "rope",
        }

    # -- core API ---------------------------------------------------------
    def reset(self) -> None:
        """Reset the game state for a new play-through."""

        self.current_room = "camp"
        self.inventory = set()
        self.game_over = False
        self.won = False

    def describe_current_room(self) -> str:
        """Return a description of the current location and any loose items."""

        room = self.rooms[self.current_room]
        description = room.description
        items = self.room_items.get(self.current_room, set())
        visible_items = [item for item in items if item not in self.inventory]
        if visible_items:
            item_list = ", ".join(sorted(visible_items))
            description += f"\nYou notice {item_list} here."
        if room.hint:
            description += f"\n(Hint: {room.hint})"
        return description

    def available_actions(self) -> Set[str]:
        """Return the set of actions that the player can attempt."""

        actions = {"look", "help", "inventory"}
        room = self.rooms[self.current_room]
        actions.update(room.exits.keys())
        items = self.room_items.get(self.current_room, set())
        for item in items:
            if item not in self.inventory:
                actions.add(f"take {item}")
        if self.current_room == "tower" and "relic" in self.inventory:
            actions.add("leave")
        return actions

    def handle_action(self, action: str) -> str:
        """Process a player's input and return the resulting narration."""

        if self.game_over:
            return "The adventure has ended. Reset the game to play again."

        normalized = action.strip().lower()
        if not normalized:
            return "You need to choose an action."

        if normalized == "help":
            return (
                "Type the direction you wish to travel (north/south/east/west). "
                "Try 'take <item>' to pick something up, 'inventory' to review what "
                "you're carrying, and 'look' to re-read the room description."
            )
        if normalized == "inventory":
            if not self.inventory:
                return "Your pack is empty."
            item_list = ", ".join(sorted(self.inventory))
            return f"You are carrying: {item_list}."
        if normalized == "look":
            return self.describe_current_room()

        if normalized.startswith("take "):
            return self._handle_take(normalized.replace("take ", "", 1).strip())

        if normalized == "leave" and self.current_room == "tower" and "relic" in self.inventory:
            self.game_over = True
            self.won = True
            return (
                "You leave the tower and return to the forest. With the relic secured, "
                "your adventure concludes in triumph!"
            )

        return self._handle_movement(normalized)

    # -- helpers ----------------------------------------------------------
    def _handle_take(self, item: str) -> str:
        """Handle taking an item from the current room."""

        if not item:
            return "Take what?"
        room_items = self.room_items.get(self.current_room, set())
        if item not in room_items:
            return "There is nothing like that to take."
        requirement = self.item_requirements.get((self.current_room, item))
        if requirement and requirement not in self.inventory:
            return f"You fumble around but realize you need a {requirement} first."
        if item in self.inventory:
            return "You already picked that up."
        self.inventory.add(item)
        if self.current_room == "tower" and item == "relic":
            self.game_over = True
            self.won = True
            return (
                "You lift the ancient relic from the chest. A warm glow surrounds you—"
                "you've completed your quest!"
            )
        return f"You add the {item} to your pack."

    def _handle_movement(self, direction: str) -> str:
        """Handle the player attempting to move to a different room."""

        room = self.rooms[self.current_room]
        if direction not in room.exits:
            return "You can't go that way."

        requirement = self.locked_exits.get((self.current_room, direction))
        if requirement and requirement not in self.inventory:
            return f"You need a {requirement} before you can go that way."

        self.current_room = room.exits[direction]
        next_room = self.rooms[self.current_room]
        narration = f"You travel {direction} and arrive in a new area."
        narration += f"\n{next_room.description}"
        items = self.room_items.get(self.current_room, set())
        visible_items = [item for item in items if item not in self.inventory]
        if visible_items:
            item_list = ", ".join(sorted(visible_items))
            narration += f"\nYou spot {item_list} nearby."
        return narration


__all__ = ["AdventureGame", "Room"]
