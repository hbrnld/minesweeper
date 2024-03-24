import tkinter as tk
from tkinter import messagebox                                              # Importing necessary packages
from datetime import datetime                                               # Tkinter, datetime, messagebox and random
import random


class Menu():                                                               # MENU CLASS: Creates an instance of the menu window
    def __init__(self):                                                     # INIT: Creates the menu root, and initializes mainloop
        self.menu = tk.Tk()
        self.menu.title("Menu")
        self.bgcolor = "#b3b3b3"
        self.create_menu()
        self.menu.mainloop()

    def create_menu(self):                                                  # CREATE_MENU: Defines all the widgets and places them om grid
        menuframe = tk.Frame(self.menu, bg=self.bgcolor)
        menuframe.grid()
        difficulty = tk.IntVar()
        difficulty.set(12)

        menuwidgets = {                                                     # dictionary that contains all the menu-widgets
            "title": tk.Label(menuframe, text="MINESWEEPER", font=("Helvetica", 36, "bold"), pady=10, padx=20),
            "label": tk.Label(menuframe, text="Choose a difficulty", font=("Helvetica", 16, "bold")),
            "easy": tk.Radiobutton(menuframe, text="Easy", variable=difficulty, value=12),
            "medium": tk.Radiobutton(menuframe, text="Medium", variable=difficulty, value=16),
            "hard": tk.Radiobutton(menuframe, text="Hard", variable=difficulty, value=26),
            "spacer1": tk.Frame(menuframe, height=10),
            "highscores_button": tk.Button(menuframe, text="HIGHSCORES", width=12, height=2, command=lambda: self.show_highscores()),
            "spacer2": tk.Frame(menuframe, height=10),
            "start_button": tk.Button(menuframe, text="START GAME", width=12, height=2, command=lambda: self.start_game(difficulty.get())),
            "spacer3": tk.Frame(menuframe, height=10),
            "quit_button": tk.Button(menuframe, text="QUIT", width=12, height=2, command=lambda: self.menu.destroy()),
            "spacer4": tk.Frame(menuframe, height=20)
        }
        for i, (key, widget) in enumerate(menuwidgets.items()):             # for-loop that places all menu-widgets
            widget.config(bg=self.bgcolor)
            widget.grid(row=i, column=0)

    def start_game(self, difficulty):                                       # START_GAME: method that is called when "Start Game" is pressed
        self.menu.destroy()
        Game(difficulty)

    def show_highscores(self):                                              # SHOW_HIGHSCORES: method that is called when "Highscores" is pressed
        self.menu.destroy()
        highscores = tk.Tk()                                                # creates new window for highscores
        highscores.config(bg=self.bgcolor)
        highscores.title("Highscores")

        highscorewidgets = {                                                # dictionary that contains all highscore-widgets
            "title": tk.Label(highscores, text="HIGHSCORES", font=("Helvetica", 36, "bold"), pady=10, padx=20),
            "scoreframe": tk.Frame(highscores),
            "spacer5": tk.Frame(highscores, height=20),
            "back_button": tk.Button(highscores, text="BACK", width=12, height=2, command=lambda: [highscores.destroy(), Menu()]),
            "spacer6": tk.Frame(highscores, height=20)
        }

        scores = []
        with open("highscores.txt", "r") as file:                           # reads the highscores from file
            for line in file.readlines():
                for word in line.split():
                    scores.append(word)
        times = scores[0::3]                                                # creates list of times
        names = scores[1::3]                                                # creates list of names
        difficulties = scores[2::3]                                         # creates list of difficulties
        sorted_scores = sorted(zip(times, names, difficulties))             # zips together lists and sorts by time
        try:
            for i in range(10):                                             # for-loop that adds top 10 scores to scoreframe
                item = sorted_scores[i]
                score = tk.Label(highscorewidgets["scoreframe"], text=f"{i+1}. {item[0]}  {item[1]}  ({item[2]})", bg=self.bgcolor)
                score.grid(row=i, column=0)
        except IndexError:                                                  # prohibits indexerror when number of lines in file is less than 10
            pass

        for i, (key, widget) in enumerate(highscorewidgets.items()):        # for-loop that places all highscore-widgets
            widget.config(bg=self.bgcolor)
            widget.grid(row=i, column=0)


class Game():                                                               # GAME CLASS: Creates an instance of the game
    def __init__(self, difficulty):                                         # INIT: declare main variables, difficulty parameter from menu choice
        self.root = tk.Tk()
        self.root.title("Minesweeper")

        self.rows = difficulty                                              # number of rows
        self.cols = difficulty                                              # number of columns
        self.difficulty = difficulty
        self.bgcolor = "#b3b3b3"

        self.images = {                                                     # dictionary of images, backgrounds of the cells
            "numbers": [tk.PhotoImage(master=self.root, file=f"images/{i}.png") for i in range(1, 9)],   # list comprehension
            "start": tk.PhotoImage(master=self.root, file="images/start.png"),
            "empty": tk.PhotoImage(master=self.root, file="images/empty.png"),
            "mine": tk.PhotoImage(master=self.root, file="images/mine.png"),
            "redmine": tk.PhotoImage(master=self.root, file="images/redmine.png"),
            "flag": tk.PhotoImage(master=self.root, file="images/flag.png"),
            "failflag": tk.PhotoImage(master=self.root, file="images/failflag.png")
        }

        self.frame = tk.Frame(self.root)                                    # create frame that contains the game grid
        self.frame.pack()

        self.setup_grid()                                                   # call setup_grid method
        self.update_timer()                                                 # call update_timer method
        self.root.mainloop()                                                # mainloop of the game instance

    def setup_grid(self):                                                   # SETUP_GRID: sets up the whole grid
        self.cells = dict({})                                               # main dictionary that contains all dictionaries of individual cells
        self.timelabel = tk.Label(self.frame, text="0:00:00")               # create time label
        self.timelabel.grid(row=0, column=0, columnspan=self.cols)
        self.starttime = datetime.now()                                     # initialize start time for the timer
        self.game_end = False                                               # used to control methods that are stopped when the game ends

        for i in range(0, self.rows):                                       # iterate through all rows
            self.cells[i] = {}                                              # create new dictionary for every new row
            for j in range(0, self.cols):                                   # iterate through all colummns
                mineHere = False                                            # ground state is no mine
                if random.randint(0, 100) < 10:                             # randomizes if the cell is a mine
                    mineHere = True

                cell = {                                                    # individual dictionary for every cell
                    "coordinates": {                                        # assign coordinates
                        "x": i,
                        "y": j
                    },                                                      # button widget connected to the cell
                    "button": tk.Button(self.frame, image=self.images["start"], bd=0),
                    "mineHere": mineHere,                                   # if the cell is a mine, boolean
                    "adjacentMines": 0,                                     # number of adjacent mines
                    "status": "unclicked"                                   # 3 states: unclicked, clicked, or flagged
                }

                cell["button"].grid(row=i + 1, column=j)                    # places cell in grid
                cell["button"].bind("<Button-1>", self.button_left_click(i, j))     # binds left click function
                cell["button"].bind("<Button-2>", self.button_right_click(i, j))    # binds right click function

                self.cells[i][j] = cell                                     # adds the cell dictionary in the main dictionary at [i][j]

        for i in range(0, self.rows):                                       # iterate through the whole grid
            for j in range(0, self.cols):
                mine_count = 0
                for cell in self.find_adjacent(i, j):                       # checks all adjacent cells if they contain a mine
                    if cell["mineHere"]:
                        mine_count += 1                                     # adds to mine_count if adjacent mine is found
                self.cells[i][j]["adjacentMines"] = mine_count              # updates "adjacentMines" for each cell

    def find_adjacent(self, x, y):                                          # FIND_ADJACENT: takes coordinates of cell and returs list of
        adjacent = []                                                       # all the 8 adjacent cells
        xlist = [x - 1, x, x + 1, x - 1, x + 1, x - 1, x, x + 1]            # list of x-coordinates
        ylist = [y - 1, y - 1, y - 1, y, y, y + 1, y + 1, y + 1, y + 1]     # list of y-coordinates

        for i in range(0, len(xlist)):                                      # top-left, top, top-right, left, right, down-left, down, down-right
            try:
                adjacent.append(self.cells[xlist[i]][ylist[i]])             # using SAME index in both lists
            except KeyError:                                                # handles if a cell is non-existent, i.e outside the grid
                pass
        return adjacent

    def clear_area(self, empty_cell):                                       # CLEAR_AREA: takes a cell and opens connected empty cells
        if isinstance(empty_cell, dict):                                    # if the cell is a dictionary, put it in a list (first iteration)
            empty_cell = [empty_cell]
        newCell = False

        for cell in empty_cell:                                             # iterate through the list of found empty_cells
            for cell in self.find_adjacent(cell["coordinates"]["x"], cell["coordinates"]["y"]):  # checks all adjacent cells
                if cell["adjacentMines"] == 0 and cell not in empty_cell:   # if also empty, add to list empty_cell
                    newCell = True                                          # a new cell was added, recursion is not done
                    empty_cell.append(cell)
                    if cell["status"] != "flagged":                         # if it's not a flag
                        cell["button"].config(image=self.images["empty"])   # open the cell
                        cell["status"] = "clicked"                          # make it unclickable
                elif cell["adjacentMines"] != 0:                            # change background to correct number
                    if cell["status"] != "flagged":
                        cell["button"].config(image=self.images["numbers"][cell["adjacentMines"] - 1])
                        cell["status"] = "clicked"

        if newCell:                                                         # recursively run until no new cell was added
            self.clear_area(empty_cell)

    def button_left_click(self, x, y):                                      # workaround to pass parameters to function in button
        return lambda Button: self.left_click(self.cells[x][y])

    def left_click(self, cell):                                             # LEFT_CLICK: called when cell is left clicked
        if cell["status"] == "unclicked":
            if cell["mineHere"]:                                            # if it's mine
                self.game_over(cell)
            elif cell["adjacentMines"] != 0:                                # if it's number
                cell["button"].config(image=self.images["numbers"][cell["adjacentMines"] - 1])
                cell["status"] = "clicked"
            elif cell["adjacentMines"] == 0 and not cell["mineHere"]:       # if it's empty
                cell["button"].config(image=self.images["empty"])
                cell["status"] = "clicked"
                self.clear_area(cell)
        if not self.game_end:
            self.check_win()                                                # checks if game is won after every left click

    def button_right_click(self, x, y):                                     # workaround to pass parameters to function in button
        return lambda Button: self.right_click(self.cells[x][y])

    def right_click(self, cell):                                            # RIGHT_CLICK: called when cell is right clicked
        if cell["status"] == "unclicked":                                   # if it's unclicked
            cell["button"].config(image=self.images["flag"])                # place flag
            cell["status"] = "flagged"
        elif cell["status"] == "flagged":                                   # if it's a flag
            cell["button"].config(image=self.images["start"])               # unflag
            cell["status"] = "unclicked"
        if not self.game_end:
            self.check_win()

    def game_over(self, cell):                                              # GAME_OVER: called when a mine is clicked
        for i in range(0, self.rows):                                       # iterate through grid
            for j in range(0, self.cols):
                if self.cells[i][j]["mineHere"]:                            # show all the mines
                    self.cells[i][j]["button"].config(image=self.images["mine"])
                elif not self.cells[i][j]["mineHere"] and self.cells[i][j]["status"] == "flagged":  # incorrectly placed flag
                    self.cells[i][j]["button"].config(image=self.images["failflag"])
                self.cells[i][j]["status"] = "clicked"
        cell["button"].config(image=self.images["redmine"])                 # placed redmine at clicked cell
        self.root.update()

        if messagebox.askyesno(title="Minesweeper", message="You lost, play again?"):  # yes/no window if wanna play again
            self.setup_grid()
        else:
            self.game_end = True
            self.root.destroy()
            # Menu()

    def check_win(self):                                                    # CHECK_WIN: checks if the game is won
        unopened_nonbomb = 0                                                # win by opening all non-bombs
        unflagged_bomb = 0                                                  # win by flagging all bombs
        for i in range(0, self.rows):
            for j in range(0, self.cols):
                cell = self.cells[i][j]
                if cell["status"] == "unclicked" and not cell["mineHere"]:  # if it's unclicked non-mine
                    unopened_nonbomb += 1
                elif cell["status"] == "flagged" and not cell["mineHere"]:  # if it's incorrect flag
                    unopened_nonbomb += 1
                    unflagged_bomb += 1
                elif cell["status"] == "unclicked" and cell["mineHere"]:    # if it's unflagged mine
                    unflagged_bomb += 1

        if unopened_nonbomb == 0 or unflagged_bomb == 0:                    # game is won
            for i in range(0, self.rows):
                for j in range(0, self.cols):
                    cell = self.cells[i][j]
                    if cell["mineHere"] and cell["status"] != "flagged":    # show unflagged mines
                        cell["button"].config(image=self.images["mine"])
                    if cell["status"] == "unclicked":                       # show unopened cells
                        if cell["adjacentMines"] != 0:
                            cell["button"].config(image=self.images["numbers"][cell["adjacentMines"] - 1])
                        else:
                            cell["button"].config(image=self.images["empty"])
                    cell["status"] == "clicked"                             # make all cells unlickable
            self.win_popup()                                                # calls win game method

    def win_popup(self):                                                    # WIN_POPUP: creates popup when game is won
        time = self.timestring
        self.game_end = True
        self.popup = tk.Tk()
        self.popup.title("Congratulations")
        self.popup.config(bg=self.bgcolor)
        popupwidgets = {                                               # dictionary that contains all the popup-widgets
            "title1": tk.Label(self.popup, text="YOU WON!", font=("Helvetica", 36, "bold"), pady=10, padx=20),
            "namelabel": tk.Label(self.popup, text="Enter your name:", font=("Helvetica", 16)),
            "inputbox": tk.Entry(self.popup),
            "spacer7": tk.Frame(self.popup, height=10),
            "enter_button": tk.Button(self.popup, text="ENTER", width=12, height=2,
                                      command=lambda: self.write_to_file(popupwidgets["inputbox"].get(), time)),
            "spacer8": tk.Frame(self.popup, height=10)
        }
        for i, (key, widget) in enumerate(popupwidgets.items()):       # places all the popup-widgets
            widget.config(bg=self.bgcolor)
            widget.grid(row=i, column=0)
        popupwidgets["inputbox"].config(bg="#ffffff")
        self.popup.mainloop()

    def write_to_file(self, name, time):                                    # WRITE_TO_FILE: writes time, name and difficulty to highscore-file
        self.popup.destroy()
        self.root.destroy()
        if name == "":                                                      # if no name is typed, placeholder is used
            name = "unknown"
        if self.difficulty == 12:                                           # translates difficulty to writable string
            diff = "Easy"
        elif self.difficulty == 16:
            diff = "Medium"
        elif self.difficulty == 26:
            diff = "Hard"
        with open("highscores.txt", "a") as file:                           # appends (writes) to file
            file.write(f"\n{time} {name.split()[0]} {diff}")                # writes to file
        Menu()                                                              # reopens menu

    def update_timer(self):                                                 # UPDATE_TIMER: updates the timer every second
        if not self.game_end:
            timechange = datetime.now() - self.starttime                    # calculate time that has passed since game started
            self.timestring = str(timechange).split(".")[0]
            self.timelabel.config(text=self.timestring)
            self.frame.after(1000, self.update_timer)                       # calls itself every 1000 ms = 1 s


def main():                                                                 # MAIN: main function of the program, opens the menu
    Menu()


if __name__ == "__main__":                                                  # only execute program if explicitly ran, not imported as module
    main()
