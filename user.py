# SPES: Starship Programming Edutainment System --- USER FILE
#
# Use this file to write your own code...

def spread_fire(p, angle, spread, num):
    start = int(angle - (spread / 2))
    end = int(angle + (spread / 2))
    step = int(spread / num)
    for deg in range(start, end, step):
        p.missile(int(deg))

def up(p):
    p.move(180, 100)

def down(p):
    p.move(0, 100)

def left(p):
    p.move(270, 100)

def right(p):
    p.move(90, 100)

# def spread_laser(p):
#     for deg in range(45, 135, 20):
#         p.laser(deg)
