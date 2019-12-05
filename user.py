# SPES: Starship Programming Edutainment System --- USER FILE
#
# Use this file to write your own code...

def spread_fire(angle, spread, num):
    global p
    start = angle - (spread / 2)
    end = angle + (spread / 2)
    step = spread / num
    for deg in range(start, end, step):
        p.missile(deg)
