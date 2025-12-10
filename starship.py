from __future__ import annotations
from typing import TYPE_CHECKING
from entity import Entity
import math

if TYPE_CHECKING:
    from starbase import Starbase

class Starship(Entity):
    """
    A mobile combat unit that can move between sectors, dock with starbases,
    attack enemy ships, and be repaired at friendly starbases.
    """
    entity_type = "starship"
    MIN_DAMAGE = 5
    MIN_CREW = 1

    def __init__(self, sector: int, max_attack: int = 30, max_defense:int = 10, max_crew:int = 10, max_health:int = 100):
        self.validate_attributes([
            ("max_health", max_health, self.MIN_STAT),
            ("max_crew", max_crew, self.MIN_CREW)
        ])

        super().__init__(sector, max_health, max_defense)
        self.max_attack_strength = max_attack
        self.curr_crew = self.max_crew = max_crew
        self.docked_at = None
        self.actions_to_skip = 0
        
    def get_curr_attack_strength(self) -> int:
        """Calculate the starship's current attack strength.

        Returns:
            float: Current attack output based on remaining health.
        """
        return math.ceil(self.max_attack_strength * (self.curr_health / self.max_health))
    
    def get_curr_defense_strength(self) -> int:
        """Calculate the starship's current defence strength.

        Returns:
            float: Current defensive power based on remaining health and crew.
        """
        return math.floor(self.max_defense_strength * ((self.curr_health + self.curr_crew)/
                                            (self.max_health + self.max_crew)))
    
    def get_docked_at(self) -> Starbase:
        return self.docked_at
    
    def move(self, sector: int) -> None:
        """Move the starship to a new sector.

        The action is skipped if the ship is disabled or is being repaired.

        Args:
            sector (int): The sector number to move into.
        """
        if not self.can_perform_action():
            return
        
        if self.sector == sector:
            self.output(f"already in sector {sector}")
            return
        
        if self.docked_at:
            self.output("cannot move while docked")
            return
        
        self.sector = sector
        self.output(f"has moved to sector {sector}")

    def dock(self, starbase: Starbase) -> None:
        """Dock the ship at a friendly starbase in the same sector.

        The ship is invincible while docked at a starbase and can choose to repair itself.
        
        A ship cannot dock if it is already docked, the starbase is in 
        another sector, or if the starbase belongs to an enemy fleet.

        Args:
            starbase (Starbase): The starbase to dock at.
        """
        if not self.can_perform_action():
            return
        
        if self.docked_at:
            self.output(f"cannot dock - already docked at {self.docked_at.get_full_name()}")
            return
        
        if not self.same_fleet(starbase):
            self.output(f"cannot dock at {starbase.get_full_name()} - it belongs to an enemy fleet")
            return
        
        if not self.same_sector(starbase):
            self.output(f"cannot dock at {starbase.get_full_name()} - it is in sector {starbase.sector}, we are in sector {self.sector}")
            return

        if starbase.is_dead():
            self.output(f"cannot dock at {starbase.get_full_name()} - starbase has been destroyed")
            return

        self.docked_at = starbase
        starbase.dock(self)
        self.output(f"has docked at {starbase.get_full_name()}")

    def undock(self) -> None:
        """Undock the ship from it's current starbase if it is docked.
        """
        if self.can_perform_action() and self.docked_at:
            if not self.is_dead():
                self.output(f"has undocked from {self.docked_at.get_full_name()}")
            
            self.docked_at.undock(self)
            self.docked_at = None        

    def repair(self) -> None:
        """Fully restore the ship's health and crew while docked in a starbase.

        Repairs cause the ship to skip a number of subsequent actions depending
        on its damage level at the time of repair.
        """
        if not self.can_perform_action():
            return
        
        if not self.docked_at:
            self.output("cannot repair - not docked at a starbase")
            return

        self.output("is being repaired")
        health_percentage = self.curr_health / self.max_health
        actions_to_skip = 1

        if health_percentage < 0.25:
            actions_to_skip = 4
        elif health_percentage < 0.5:
            actions_to_skip = 3
        elif health_percentage < 0.75:
            actions_to_skip = 2

        self.actions_to_skip = actions_to_skip
        self.curr_health = self.max_health
        self.curr_crew = self.max_crew

    def attack(self, target: Entity) -> None:
        """Attack a target entity in the same sector.

        Damage is based on the minimum of:
        - Ship's current attack strength minus the target's current defence strength
        - 5

        Args:
            target (Entity): The target to attack.
        """
        if not self.can_perform_action(): 
            return

        if self.docked_at:
            self.output("cannot attack while docked")
            return

        if self.same_fleet(target):
            self.output(f"cannot attack teammate {target.get_full_name()} - no friendly fire")
            return

        if not self.same_sector(target):
            self.output(f"cannot attack {target.get_full_name()} - target is in sector {target.sector}, we are in sector {self.sector}")
            return

        if target.is_dead():
            self.output(f"cannot attack {target.get_full_name()} - target already destroyed")
            return

        self.output(f"attacked {target.get_full_name()}")
        damage = max(self.MIN_DAMAGE, self.get_curr_attack_strength() - target.get_curr_defense_strength())
        target.take_damage(damage)

    def take_damage(self, damage: int) -> None:
        """Handles taking damage from enemy ships.
        
        The number of crew members incapacitated is the maximum of:
        - Product of the current crew and the damage received over the ship's
        max health
        - 1

        If the ship isn't docked it can take damage.

        Args:
            damage (int): The amount of damage to be deducted from the ship's health
        """
        if not self.docked_at:
            incapacitated = math.ceil((damage / self.max_health) * self.curr_crew)
            self.curr_crew = max(self.MIN_CREW, self.curr_crew - incapacitated)
            super().take_damage(damage)
    
    def destroy(self) -> None:
        """Set a ship's health to zero to be instantly destroyed if it is docked
        at a starship that gets destroyed.
        """
        self.docked_at = None
        self.take_damage(self.curr_health)

    def can_perform_action(self) -> bool:
        """Check whether the ship can act this turn.

        If the ship is dead or waiting for a number of turns due to being repaired,
        it can't take any actions.

        Returns:
            bool: True if the ship is available, False if repairing or disabled.
        """
  
        if self.disabled:
            return False
        
        if self.actions_to_skip == 0:
            return True
        else:
            actions_to_skip = self.actions_to_skip
            self.output(f"is currently being repaired and will be ready in {actions_to_skip} {"actions" if actions_to_skip > 1 else "action"}")
            self.actions_to_skip -= 1
            return False


  