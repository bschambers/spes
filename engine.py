# SPES: Starship Programming Edutainment System --- GAME ENGINE
#
# author: B. S. Chambers
# email: ben@bschambers.info
# website: https://github.com/bschambers/spes
#
# Copyright 2019-present B. S. Chambers - Distributed under GPL, version 3

import math
from random import randint

def pr(text):
    if False:
        print(text)

######################### UTILITY FUNCTIONS ##########################

def within_range(n, low, high):
    "Returns True if n is within range (inclusive)."
    return n >= low and n <= high

def rand_canvas_pos(gui):
    return [randint(0, gui.get_width()),
            randint(0, gui.get_height())]

########################### EDGE BEHAVIOUR ###########################

def do_nothing_on_edges(gui, actor):
    pass

def die_on_edges(gui, actor):
    """Die if actor.position is outside of bounds."""
    pr('die_on_edges')
    p = actor.position
    if p[0] < 0 or p[1] < 0 or p[0] > gui.get_width() or p[1] > gui.get_height():
        actor.is_live = False

def bounce_on_edges(gui, actor):
    """Bounce if any part of actor's bounding box is outside of bounds."""
    pr('bounce_on_edges')
    a = actor
    box = actor.bbox
    if not box:
        print("WARNING! engine.bounce_on_edges() - Actor {} has no bounding box".format(a.name))
    if box[0] < 0 and within_range(a.angle, 181, 359):
        diff = 270 - a.angle
        a.angle = 90 + diff
    elif box[1] < 0 and within_range(a.angle, 91, 269):
        diff = 180 - a.angle
        a.angle = 0 + diff
    elif box[2] > gui.get_width() and within_range(a.angle, 1, 179):
        diff = 90 - a.angle
        a.angle = 270 + diff
    elif box[3] > gui.get_height()\
         and (within_range(a.angle, 0, 89) or within_range(a.angle, 271, 359)):
        diff = 0 - a.angle
        a.angle = 180 + diff
    a.angle = a.angle % 360

############################ GAME ENGINE #############################

class Game():
    """The game engine."""

    num_drones = 1
    actors = []
    actors_to_add = []
    player = None
    gui = None

    # debugging
    show_bounding_boxes = False

    def __init__(self):
        self.player = Ship(self, 'magenta')
        self.player.name = 'player'
        self.player.position = [200, 200]
        self.add_actor(self.player)

    def setup(self, gui):
        self.gui = gui

    def add_actor(self, actor):
        self.actors_to_add.append(actor)

    def iterate_loop(self, gui):
        "The main game loop"
        self.action(gui)
        self.collisions()
        self.garbage_collection(gui)
        self.display(gui)

    def action(self, gui):
        # any actors to add
        while self.actors_to_add:
            pr("adding actor")
            self.actors.append(self.actors_to_add.pop())
        # add more drones if required
        while len(self.actors) - 1 < self.num_drones:
            pr("adding drone")
            drone = Ship(self, 'grey')
            drone.name = 'drone'
            drone.position = rand_canvas_pos(gui)
            drone.angle = randint(0, 360)
            drone.velocity = randint(1, 10)
            self.actors.append(drone)
        # each actor perform it's action
        for a in self.actors:
            a.act(gui)

    def collisions(self):
        for a in self.actors:
            for b in self.actors:
                if a != b:
                    self.collision_detection(a, b)

    def garbage_collection(self, gui):
        to_remove = []
        for a in self.actors:
            if not a.is_live:
                to_remove.append(a)
        for a in to_remove:
            self.actors.remove(a)
            a.dispose_gui(gui)

    def display(self, gui):
        for a in self.actors:
            a.update_gui_shape(gui)
        gui.set_info_text('score: {}\nshow boxes: {}'.format(self.player.score, self.show_bounding_boxes))

    def collision_detection(self, a, b):
        """Do collision detection for two Actors."""
        # compare bounding boxes
        ba = a.bbox
        bb = b.bbox
        # check that both boxes exist
        if ba and bb:
            # x bounds
            if ba[0] <= bb[2]:
                if bb[0] <= ba[2]:
                    # y bounds
                    if ba[1] <= bb[3]:
                        if bb[1] <= ba[3]:
                            # kill both actors
                            a.die()
                            b.die()

class Actor(object):
    """Abstract base class for actors."""

    game = None
    name = 'unnamed'
    is_live = True
    scheduled_jobs = []
    new_jobs = []
    edge_behaviour = do_nothing_on_edges
    score = 0
    # geometry
    position = [0, 0]
    bbox = [] # bounding box
    # gui objects
    gui_shape = None
    gui_bbox = None

    def __init__(self, game):
        self.game = game

    def act(self, gui):
        pr('Actor.act()')
        # add new jobs
        while self.new_jobs:
            self.scheduled_jobs.append(self.new_jobs.pop())
        # do scheduled jobs
        for job in self.scheduled_jobs:
            countdown = job[0]
            func = job[1]
            if countdown <= 0:
                func()
            job[0] -= 1
        # garbage collection
        rem = []
        for job in self.scheduled_jobs:
            if job[0] < 0:
                rem.append(job)
        for job in rem:
            pr("removing completed job from schedule")
            self.scheduled_jobs.remove(job)

    def schedule(self, num_steps, job):
        "Schedule a new job to be done after specified number of steps"
        self.new_jobs.append([num_steps, job])

    def die(self):
        self.is_live = False

    def dispose_gui(self, gui):
        if self.gui_shape:
            gui.get_canvas().delete(self.gui_shape)
        if self.gui_bbox:
            gui.get_canvas().delete(self.gui_bbox)

class PolygonActor(Actor):
    """An actor with polygonal shape."""

    rotation = 0
    angle = 0
    velocity = 0
    shape_archetype = None
    shape = []
    color = None

    def __init__(self, game, shape_coords, color):
        super().__init__(game)
        self.shape_archetype = shape_coords
        self.color = color
        self.edge_behaviour = bounce_on_edges

    def act(self, gui):
        pr('PolygonActor.act(): name={}'.format(self.name))
        super().act(gui)
        # move ship (updates shape, bounding box etc)
        self.move_by(self.angle, self.velocity)
        # screen edges
        self.edge_behaviour(gui, self)

    def _update_shape(self):
        """Build shape from the archetype, position and rotation. Also updates bounding box."""
        pr('PolygonActor.update_shape() --- pos={}'.format(self.position))

        # shape
        self.shape = []
        for i in range(0, len(self.shape_archetype), 2):
            x = self.shape_archetype[i]
            y = self.shape_archetype[i + 1]
            # vertex = rotate_vertex(x, y, 0, 0, self.rotation)
            # self.shape.append(vertex[0] + self.position[0])
            # self.shape.append(vertex[1] + self.position[1])
            self.shape.append(x + self.position[0])
            self.shape.append(y + self.position[1])

        # bounding box
        xmin = self.shape[0]
        xmax = xmin
        ymin = self.shape[1]
        ymax = ymin
        for i in range(0, len(self.shape), 2):
            x = self.shape[i]
            y = self.shape[i + 1]
            if x < xmin: xmin = x
            if x > xmax: xmax = x
            if y < ymin: ymin = y
            if y > ymax: ymax = y
        self.bbox = [xmin, ymin, xmax, ymax]
        pr("bbox = {}".format(self.bbox))

    def move_by(self, angle, dist):
        pr('PolygonActor.move_by: {} {}'.format(angle, dist))
        # print("move: ", self)
        x = math.sin(math.radians(angle)) * dist
        y = math.cos(math.radians(angle)) * dist
        self.position[0] += x
        self.position[1] += y
        self._update_shape()

    def rotate(self, angle):
        self.rotation = angle
        self._update_shape()

    def update_gui_shape(self, gui):
        """Update gui shape based on current actual shape..."""
        pr('PolygonActor.update_gui_shape()')
        # if gui_shape already exists, get rid of it
        if self.gui_shape:
            gui.canvas.delete(self.gui_shape)
        self.gui_shape = gui.canvas.create_polygon(self.shape, fill=self.color)
        if self.gui_bbox:
            gui.canvas.delete(self.gui_bbox)
        if self.game.show_bounding_boxes:
            self.gui_bbox = gui.canvas.create_rectangle(self.bbox, outline='yellow')

    def set_velocity(self, n):
        self.velocity = n

    def set_is_live(self, val):
        self.is_live = val

    def thrust(self, angle, velocity):
        self.angle = angle
        self.velocity = velocity

    def move(self, angle, distance):
        vel = 4
        steps = distance / vel
        self.angle = angle
        self.velocity = vel
        self.schedule(steps, lambda: self.set_velocity(0))

    # OVERRIDE
    def die(self):
        self.color = 'red'
        self.schedule(20, lambda: self.set_is_live(False))

class Ship(PolygonActor):
    """A PolygonActor who can shoot missiles and lasers."""

    def __init__(self, game, color):
        super().__init__(game, [10, -15, 0, 15, -10, -15], color)

    def missile(self, angle):
        print('missile: angle {}'.format(angle))
        x_origin = self.shape[2]
        y_origin = self.shape[3]
        m = Bullet(self.game, x_origin, y_origin, angle, self)
        self.game.add_actor(m)

    def laser(self, angle):
        print('laser: angle = {}'.format(angle))
        x_origin = self.shape[2]
        y_origin = self.shape[3]
        beam = LaserBeam(self.game, x_origin, y_origin, angle, self)
        self.game.add_actor(beam)

class LaserBeam(Actor):
    """A static line with limited lifespan which does damage to other actors."""

    line = []
    lifespan = 20

    def __init__(self, game, x_origin, y_origin, angle, parent):
        super().__init__(game)
        self.parent = parent
        self.angle = angle
        dist = 1000
        x2 = x_origin + (math.sin(math.radians(angle)) * dist)
        y2 = y_origin + (math.cos(math.radians(angle)) * dist)
        self.line = [x_origin, y_origin, x2, y2]

    def act(self, gui):
        # count down lifespan
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.is_live = False

    def update_gui_shape(self, gui):
        # make shape, if it doesn't already exist
        if not self.gui_shape:
            ln = self.line
            self.gui_shape = gui.get_canvas().create_line(ln[0], ln[1], ln[2], ln[3], fill="white")

class Bullet(PolygonActor):
    """Bullet starts a little in front of origin point, shoots forward rapidly, and
dies when it reaches the edge of the screen."""

    def __init__(self, game, x, y, angle, parent):
        super().__init__(game, [3,3, 3,-3, -3,-3, -3,3], "white")
        self.parent = parent
        self.angle = angle
        self.velocity = 10
        self.edge_behaviour = die_on_edges
        # position a little in front, so we don't collide with nose of ship
        dist = 30
        x2 = math.sin(math.radians(angle)) * dist
        y2 = math.cos(math.radians(angle)) * dist
        self.position = [x + x2, y + y2]
