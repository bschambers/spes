# SPES: Starship Programming Edutainment System --- BUILT-IN EDITOR FRONTEND
#
# author: B. S. Chambers
# email: ben@bschambers.info
# website: https://github.com/bschambers/spes
#
# Copyright 2019-present B. S. Chambers - Distributed under GPL, version 3

# SPES BUILT-IN EDITOR FRONTEND
#
# Game window has a built-in editor panel where commands can be typed and
# executed.
#
# Code in editor can also be saved and loaded from file.

# RUNNING THE GAME:
#
# NOTE: Requires Python 3!
#
# Just run the file spes_builtin.py:
#
#     $ python spes_builtin.py

from engine import Game

import tkinter as tk
import tkinter.filedialog as filedialog

class GameGUI(object):
    """Public interface:

    get_width()
    get_height()
    get_canvas()
    set_info_text(text)
    """

    game_running = True
    engine = None
    restart_with_game_engine = None

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("game")
        # canvas
        self.canvas = tk.Canvas(self.root, bg='blue', width=800, height=600)
        self.info = self.canvas.create_text(10, 20, anchor=tk.NW, text="info", fill="white")
        self.canvas.grid()
        # editor
        self.editor = tk.Text(self.root, height=10, bg='black', fg='cyan', insertbackground='white')
        self.editor.grid()
        self.editor.bind('<Control-l>', self.typed_exec_line)
        # controls
        self.control_panel = tk.Frame(self.root)
        self.restart_button = tk.Button(self.control_panel, text='RESTART', command=self.restart_game)
        self.restart_button.grid(row=0, column=0)
        self.save_button = tk.Button(self.control_panel, text="save", command=self.save_as)
        self.save_button.grid(row=0, column=1)
        self.load_button = tk.Button(self.control_panel, text='load', command=self.load_file)
        self.load_button.grid(row=0, column=2)
        self.exec_button = tk.Button(self.control_panel, text='exec', command=self.exec_text)
        self.exec_button.grid(row=0, column=3)
        self.exec_sel_button = tk.Button(self.control_panel, text='exec selected', command=self.exec_selected_text)
        self.exec_sel_button.grid(row=0, column=4)
        self.exec_line_button = tk.Button(self.control_panel, text='exec line (Ctrl-l)', command=self.exec_current_line)
        self.exec_line_button.grid(row=0, column=5)
        self.control_panel.grid()

    def setup_game_engine(self, engine):
        self.engine = engine
        self.engine.setup(self)

    def restart_game(self):
        game = Game()
        self.restart_with_game_engine = game

    def save_as(self):
        #global text
        text = self.editor.get("1.0", "end-1c")
        saveLocation = filedialog.asksaveasfilename()
        file1 = open(saveLocation, "w+")
        file1.write(text)
        file1.close()

    def load_file(self):
        #global text
        filename = filedialog.askopenfilename()
        print("load file: ", filename)
        with open(filename, "r") as f:
            self.editor.delete(1.0, tk.END)
            self.editor.insert(tk.END, f.read())

    def exec_text(self):
        # global text
        # global root
        # global canv
        global p
        text = self.editor.get("1.0", "end-1c")
        exec(text)

    def exec_selected_text(self):
        # global text
        # global root
        # global canv
        global p
        text = self.editor.get(tk.SEL_FIRST, tk.SEL_LAST)
        exec(text)

    def exec_current_line(self):
        # global text
        # global root
        # global canv
        global p
        text = self.editor.get("insert linestart", "insert lineend")
        exec(text)

    def typed_exec_line(self, event):
        self.exec_current_line()

    def game_loop(self):

        if self.restart_with_game_engine:
            global game
            global p
            game = self.restart_with_game_engine
            self.restart_with_game_engine = None
            self.canvas.delete(tk.ALL)
            self.setup_game_engine(game)
            p = game.player

        self.engine.iterate_loop(self)
        if self.game_running:
            self.root.after(50, self.game_loop)
        else:
            # stop thread and dispose of GUI
            print('Goodbye!\n')
            self.root.destroy()

    #### PUBLIC INTERFACE ####

    def get_width(self):
        return self.canvas.winfo_width()

    def get_height(self):
        return self.canvas.winfo_height()

    def get_canvas(self):
        return self.canvas

    def set_info_text(self, text):
        debug_text = 'num canvas items: {}\n'.format(len(self.canvas.find_all()))
        self.canvas.itemconfig(self.info, text=debug_text + text)

game = Game()
gui = GameGUI()
gui.setup_game_engine(game)
p = game.player
gui.root.after(500, gui.game_loop)
gui.root.mainloop()
