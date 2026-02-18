from __future__ import annotations
from typing import TYPE_CHECKING
from entity import Entity
import math

if TYPE_CHECKING:
    from starship import Starship

class Starbase(Entity):
    """A stationary defensive structure that cannot move or attack but can 
    dock and repair friendly starships.
    """
    entity_type = "starbase"

    def __init__(self, sector: int, max_defense: int = 20, max_health: int = 500) -> None:
        super().__init__(sector, max_health, max_defense)
        self.docked_ships = []
        self.docked_at = None

    def get_curr_defense_strength(self) -> int:
        """Calculate the starbase's current defence strength.

        The defence strength is based on:
        - The product of the starbase's own defence value and fraction of health remaining
        - The product of the combined defence contributions of all docked starships scaled 
        and the number of docked ships over the starbase's max defense

        Returns:
            float: The computed defence strength of the starbase.
        """
        total_docked_defense = 0
        for ship in self.docked_ships:
            if not ship.is_being_repaired():
                total_docked_defense += ship.get_curr_defense_strength()

        return math.floor(self.max_defense_strength * (self.curr_health / self.max_health) +
                (total_docked_defense) * (len(self.docked_ships) / self.max_defense_strength))
    
    def dock(self, starship: Starship) -> None:
        """Dock a friendly starship at the starbase.

        A ship may only dock if:
        - It belongs to the same fleet
        - It is in the same sector as the starbase
        - The starbase is not disabled
        - It is currently not docked at another starbase

        Args:
            starship (Starship): The ship attempting to dock.
        """

        if not self.is_dead() and self.same_fleet(starship) and self.same_sector(starship) and not starship.is_dead() and not starship.get_docked_at():
            self.docked_ships.append(starship)

    def undock(self, starship: Starship) -> None:
        """Remove a docked starship from the starbase.

        If the starship is not currently docked no action is taken.

        Args:
            starship (Starship): The ship to undock.
        """

        for i, ship in enumerate(self.docked_ships):
            if ship == starship:
                self.docked_ships.pop(i)
                break

    def take_damage(self, damage: int) -> None:
        """Apply damage to the starbase and handle destruction logic.

        If the starbase is destroyed, all docked ships are automatically
        destroyed as well.

        Args:
            damage (float): The damage dealt to the starbase.
        """
        super().take_damage(damage)

        if self.is_dead():
            for ship in self.docked_ships:
                ship.destroy()
            self.docked_ships.clear()

    def attack(self, target: Entity) -> None:
        """Attack a target entity in the same sector.

        Damage is based on the maximum of:
        - Total current attack strength of ships docked minus the target's current defence strength
        - 5

        No damage can be dealt if there are no ships docked

        Args:
            target (Entity): The target to attack.
        """
        total_docked_attack = 0
        for ship in self.docked_ships:
            if not ship.is_being_repaired():
                total_docked_attack += ship.get_curr_attack_strength()
        
        super().attack(target, total_docked_attack)

    def tow(self, sector: int) -> None:
        """Get towed to a new sector by three friendly ships
        Tows any docked ships to the new sector as well

        Args:
            sector (int): Sector to be towed to.
        """    
        self.sector = sector

        for ship in self.docked_ships:
            ship.tow(sector)