# SPES: Starship Programming Edutainment System --- COMMAND LINE FRONTEND
#
# author: B. S. Chambers
# email: ben@bschambers.info
# website: https://github.com/bschambers/spes
#
# Copyright 2019-present B. S. Chambers - Distributed under GPL, version 3

# SPES COMMAND LINE FRONTEND
#
# The game is started and commands are input with the standard command-line
# python interpreter.
#
# Tkinter is run on a separate thread, so that the command line remains
# responsive.
#
# All Tkinter GUI code is isolated inside the GameGUI run method.

# RUNNING THE GAME:
#
# NOTE: Requires Python 3!
#
# 1: Navigate to the game directory:
#
#     $ cd path/to/spes_dir
#
# 2: Load the command line frontend and enter the interactive Python interpreter:
#
#     $ python -i spes_cmd.py
#
# 3: Start the game GUI running:
#
#     >>> gui.start()

from engine import Game
import user

import tkinter as tk
import threading
from time import time
from random import randint
import importlib

class GameGUI(threading.Thread):
    """Makes a tkinter GUI on a thread of it's own.

    Public interface:

    get_width()
    get_height()
    get_canvas()
    set_info_text(text)
    """

    game_running = True
    restart_with_game_engine = None
    iteration_time = time()
    fps = 0

    def __init__(self, engine):
        threading.Thread.__init__(self)
        self.engine = engine

    def run(self):
        # on thread starting
        self.root = tk.Tk()
        self.root.title("game")
        self.canvas = tk.Canvas(self.root, bg='blue', width=800, height=800)
        self.canvas.pack()
        self.info = self.canvas.create_text(10, 20, anchor=tk.NW, text="info", fill="white")
        self.engine.setup(self)
        # start the GUI and game-loop
        self.root.after(500, self.game_loop)
        self.root.mainloop()

    def game_loop(self):

        if self.restart_with_game_engine:
            self.canvas.delete(tk.ALL)
            self.engine = self.restart_with_game_engine
            self.restart_with_game_engine = None
            self.engine.setup(self)

        self.engine.iterate_loop(self)
        if self.game_running:
            self.root.after(50, self.game_loop)
            # calculate fps
            last_time = self.iteration_time
            self.iteration_time = time()
            elapsed = self.iteration_time - last_time
            self.fps = 1.0 / elapsed
        else:
            # stop thread and dispose of GUI
            print('Goodbye!\n')
            self.root.destroy()

    def new_game(self, engine):
        self.new_game_engine = engine

    def exit(self):
        self.game_running = False

    #### PUBLIC INTERFACE ####

    def get_width(self):
        return self.canvas.winfo_width()

    def get_height(self):
        return self.canvas.winfo_height()

    def get_canvas(self):
        return self.canvas

    def set_info_text(self, text):
        fps_str = 'fps: {:.2f}\n'.format(self.fps)
        debug_str = 'num canvas items: {}\n'.format(len(self.canvas.find_all()))
        self.canvas.itemconfig(self.info, text=fps_str + debug_str + text)

###################### TOP LEVEL USER INTERFACE ######################

game = Game()
gui = GameGUI(game)
p = game.player

def update():
    print('updating from user file...')
    importlib.reload(user)

print('game initialised... to start, type: gui.start()')
