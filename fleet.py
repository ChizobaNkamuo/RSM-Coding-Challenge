from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from starship import Starship
    from starbase import Starbase
    from entity import Entity

class Fleet():
    """Represents a player's fleet, containing all their starships and 
    starbases, and coordinating fleet-wide actions such as mobilising or 
    attacking a target.
    """
    def __init__(self, name: str):
        self.name = name
        self.starships = []
        self.starbases = []

    def get_entity_list(self, entity: Entity) -> list[Entity]:
        entity_list = self.starships if entity.get_entity_type() == "starship" else self.starbases
        return entity_list

    def add_entity(self, entity: Entity) -> None:
        """Add a starship or starbase to the fleet.

        Args:
            entity (Entity): The entity to add.

        Notes:
            If the entity already belongs to another fleet, it is removed from
            that fleet before being reassigned.
        """
        curr_fleet = entity.get_fleet()
        if curr_fleet:
            curr_fleet.remove_entity(entity)

        entity_list = self.get_entity_list(entity)
        entity_list.append(entity)
        entity.set_fleet(self, len(entity_list))

    def remove_entity(self, entity: Entity) -> None:
        """Remove an entity from the fleet.

        Args:
            entity (Entity): The entity to remove.
        """
        entity_list = self.get_entity_list(entity)
        for i, curr_entity in enumerate(entity_list):
            if curr_entity == entity:
                entity_list.pop(i)
                break
    
    def mobilise(self, sector: int) -> None:
        """Move all mobile ships in the fleet to a specified sector.

        Docked ships do not move.

        Args:
            sector (int): The target sector for mobilisation. 
        """
        print(f"{self.name} mobilised their starships to sector {sector}")
        for ship in self.starships:
            ship.move(sector)

    def get_available_ships(self) -> list[Starship]:
        """Retrieve all ships in the fleet that are not docked.

        Returns:
            list[Starship]: A list of all undocked starships.
        """
        return [ship for ship in self.starships if not ship.get_docked_at()]
    
    def get_starbases(self) -> list[Starbase]:
        """Get all starbases controlled by the fleet.

        Returns:
            list[Starbase]: The fleet's starbases.
        """
        return self.starbases
    
    def get_name(self) -> str:
        return self.name
        
    def attack(self, target: Entity) -> None:
        """Order all eligible ships to attack a given target.

        Only ships in the same sector and not docked will attack.

        Args:
            target (Entity): The enemy entity to attack.
        """   
        print(f"{self.name}'s starships have been mobilised to attack {target.get_fleet().get_name()}'s {target.get_entity_type()}")
        for ship in self.starships:
            if target.is_dead():
                break
            ship.attack(target)