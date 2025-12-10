from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fleet import Fleet

class Entity():
    """
    Base class for all game entities (starships and starbases).

    Handles shared attributes such as health, fleet ownership, sector location,
    and behaviours like taking damage or checking destroyed state.
    """
    MIN_HEALTH = 1
    MIN_STAT = 0

    def validate_attributes(self, attributes: list[tuple[str, int, int]]) -> None:
        """Validate that all attributes meet their minimum thresholds.

        Args:
            attributes: List of (name, value, min_threshold) tuples
            
        Raises:
            ValueError: If any attribute is below its minimum threshold
        """
        for name, value, min_threshold in attributes:
            if value < min_threshold:
                raise ValueError(f"{name} must be at least {min_threshold}, got {value}")

    def __init__(self, sector: int, max_health: int, max_defense: int):
        self.validate_attributes([
            ("max_health", max_health, self.MIN_HEALTH),
            ("max_defense_strength", max_defense, self.MIN_STAT)
        ])

        self.sector = sector
        self.curr_health = self.max_health = max_health
        self.max_defense_strength = max_defense
        self.disabled = False
        self.sector = 1
        self.fleet = None
        self.fleet_id = 0


    def same_fleet(self, other: Entity) -> bool:
        """Check if another entity belongs to the same fleet.

        Args:
            other (Entity): The entity to compare against.

        Returns:
            bool: True if both entities belong to the same fleet.
        """
        return self.fleet == other.fleet
    
    def same_sector(self, other: Entity) -> bool:
        """Check if another entity is located in the same sector.

        Args:
            other (Entity): The entity to compare sectors with.

        Returns:
            bool: True if both entities are in the same sector.
        """
        return self.sector == other.sector

    def take_damage(self, damage: int) -> None:
        """Apply damage to the entity, updating its health and disabled state.

        Args:
            damage (float): The amount of damage attempted to be applied.
                The value is automatically capped so that health does not 
                go below zero.
        """
        damage = min(damage, self.curr_health)
        self.curr_health -= damage
        message = f"took {damage} damage and now has {self.curr_health} hp remaining"

        if self.curr_health <= 0:
            fleet = self.fleet
            self.disabled = True
            message = "has been destroyed"

            if fleet:
                fleet.remove_entity(self)
            
        self.output(message)
    
    def is_dead(self) -> bool:
        """Check whether the entity has been destroyed.

        Returns:
            bool: True if the entity is disabled and out of play.
        """
        return self.disabled

    def set_fleet(self, fleet: Fleet, fleet_id: int) -> None:
        """Assign the entity to a fleet.

        Args:
            fleet (Fleet): The fleet this entity belongs to.
            fleet_id (int): An identifier unique within the fleet for display.
        """
        self.fleet = fleet
        self.fleet_id = fleet_id

    def get_fleet(self) -> Fleet:
        return self.fleet
    
    def get_fleet_id(self) -> int:
        return self.fleet_id

    def get_entity_type(self) -> str:
        return self.entity_type
    
    def get_full_name(self) -> str:
        """Get a formatted entity name including fleet, type, and ID.

        Returns:
            str: Human-readable name such as 'Player1's starship #2'.
        """
        fleet = self.fleet
        if fleet:
            return f"{fleet.name}'s {self.entity_type} #{self.fleet_id}"
        else:
            return f"a neutral {self.entity_type}"
    
    def output(self, message: str) -> None:
        """Print a formatted message including the entity’s full name.

        Args:
            message (str): The text to display after the entity's name.
        """
        print(self.get_full_name() + " " + message)