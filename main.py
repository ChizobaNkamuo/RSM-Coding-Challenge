from starship import Starship
from starbase import Starbase
from fleet import Fleet

player1 = Fleet("Player1") # Intialise player 1
player1.add_entity(Starbase(1))

player2 = Fleet("Player2") # Intialise player 2
player2.add_entity(Starbase(2))

for i in range(3): # Add 3 starships
    player1.add_entity(Starship(1))
    player2.add_entity(Starship(2))

player1.mobilise(2) # Move player 1's ships to sector 2

player2_ships_two = player2.get_available_ships()[:2]
player2_starbase = player2.get_starbases()[0]

for ship in player2_ships_two: # Dock player 2's ships at the starbase
    ship.dock(player2_starbase)

player1_ship = player1.get_available_ships()[0]
player2_ship = player2.get_available_ships()[0]
for i in range(2): # Attack player 2's ship twice
    player1_ship.attack(player2_ship)

player2_ship.dock(player2_starbase) # Dock and repair player 2's ship
player2_ship.repair()

while not player2_starbase.is_dead(): # Player 1's ships attack player 2's starbase until it is destroyed
    player1.attack(player2_starbase)
