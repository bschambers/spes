# SPES: Starship Programming Edutainment System --- EXAMPLE EDITOR HISTORY FILE

p.move(100, 50)
p.move(45, 30)

p.laser(61)
p.missile(50)

user.spread_fire(p, 11, 45, 5)

user.right(p)

p.respawn()

print(p.position)
print(p.angle)

for deg in range(0, 360, 15): p.missile(deg)

gui.game_running = False

