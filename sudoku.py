import argparse 
import linecache
import random
from Tkinter import Tk, Canvas, Frame, Button, BOTH, TOP, BOTTOM

BOARDS = ["veryeasy", "easy", "medium", "hard", "veryhard"] #Types of sudoku boards
MARGIN = 20 #Margin (pixels) of padding
SIDE = 50 #Width of board cell
WIDTH = 2 * MARGIN + 9 * SIDE
HEIGHT = WIDTH

NUMBOARDS = 10000 # Number of total boards in file

"""
Handle Application Specific Errors
"""
class SudokuError(Exception):
    pass


"""
Repesentation of the Sudoku Board
"""
class SudokuBoard(object):
    def __init__(self, board_file):
        self.board = self.__create_board(board_file)

    """
    Create the board matrix
    """
    def __create_board(self, board_file):
    	# Initialise board matrix
    	board = []

    	# Iterate through board_file
    	for line in board_file:
    		# Convert to usable input
    		line = line.strip()
    		# Check for input errors - Line having more/less than 9 elements
    		if len(line) != 9:
    			raise SudokuError("Line in puzzle does not have 9 numbers")

    		templine = []
    		# Iterate through line checking for numerical errors
    		for number in line:
    			# Check if input is an integer
    			if not number.isdigit():
    				raise SudokuError("Input must be between 0 and 9 (0 for blank square)")
    			# Number is valid, add to temporary list
    			templine.append(int(number))
    		# Add temporary list to board
    		board.append(templine)

    	# Check if board has 9 lines
    	if len(board) != 9:
    		raise SudokuError("Input does not have 9 lines")

    	# Return constructed board
    	return board

"""
Sudoku game class, in charge of checking game states
"""
class SudokuGame(object):
	def __init__(self, board_file):
		self.board_file = board_file
		self.start_board = SudokuBoard(board_file).board
	
	"""
	Initialise the game
	"""
	def start(self):
		self.game_over = False
		self.curr_board = []
		# Need a deep copy of the board
		for i in xrange(9):
			templine = []
			# Iterate through starting board config, adding to current
			# board config
			for j in xrange(9):
				templine.append(self.start_board[i][j])
			self.curr_board.append(templine)

	"""
	Check if board is completed
	"""
	def check_win(self):
		# Check row and column for finished state
		for rowcol in xrange(9):
			if not self.__check_row(rowcol):
				return False
			if not self.__check_column(rowcol):
				return False

		# Check each square for finished state
		for row in xrange(3):
			for col in xrange(3):
				if not self.__check_square(row*3, col*3):
					return False
		# Winning state
		self.game_over = True
		return True

	"""
	Check if row is complete
	"""
	def __check_row(self, row):
		return set(self.curr_board[row]) == set(xrange(1,10))

	"""
	Check is column is complete
	"""
	def __check_column(self, column):
		column_line = [self.curr_board[row][column] for row in xrange(9)]
		return set(column_line) == set(xrange(1,10))

	"""
	Check if square is complete
	"""
	def __check_square(self, row, col):
		square = [self.curr_board[r][c] for r in xrange(row, row+3) for c in xrange(col, col+3)]
		return set(square) == set(xrange(1,10))


"""
Use Tkinter to generate UI for the game
"""
class SudokuUI(Frame):
	def __init__(self, parent, game):
		self.game = game
		self.parent = parent
		Frame.__init__(self, parent)

		self.row = 0
		self.col = 0

		self.__initUI__()

	"""
	Initialise the UI
	"""
	def __initUI__(self):
		# Title Name
	    self.parent.title("Sudoku")
	    # Fill frame's geometry relative to parent
	    self.pack(fill=BOTH, expand=1)
	    # General purpose widget to display board
	    self.canvas = Canvas(self,
	                         width=WIDTH,
	                         height=HEIGHT)
	    # Fill the entire space, place at the top
	    self.canvas.pack(fill=BOTH, side=TOP)
	    # Setup button to clear entire board
	    # Reinitialise to starting board setup
	    clear_button = Button(self,
	                          text="Clear answers",
	                          command=self.__clear_answers)
	    # Fill the entire space, place at the bottom
	    clear_button.pack(fill=BOTH, side=BOTTOM)
	    # Draw the grid
	    self.__draw_grid()
	    # Draw the numbers
	    self.__draw_board()
	    # Callbacks for mouse presses
	    self.canvas.bind("<Button-1>", self.__cell_clicked)
	    self.canvas.bind("<Key>", self.__key_pressed)

	"""
	Draws grid divided with blue lines into 3x3 squares
	"""
	def __draw_grid(self):
		# Fill in all 10 lines
	    for i in xrange(10):
	    	# Use blue to seperate squares
	        color = "blue" if i % 3 == 0 else "gray"

	        x0 = MARGIN + i * SIDE
	        y0 = MARGIN
	        x1 = MARGIN + i * SIDE
	        y1 = HEIGHT - MARGIN
	        # Create vertical line using margins
	        self.canvas.create_line(x0, y0, x1, y1, fill=color)

	        x0 = MARGIN
	        y0 = MARGIN + i * SIDE
	        x1 = WIDTH - MARGIN
	        y1 = MARGIN + i * SIDE
	        # Create horizontal line using margins
	        self.canvas.create_line(x0, y0, x1, y1, fill=color)

	"""
	Draws the numbers
	"""
	def __draw_board(self):
		# Clear canvas of previously inputed numbers
		self.canvas.delete("numbers")
		# Iterate through whole board
		for i in xrange(9):
		    for j in xrange(9):
		    	# Take corresponding starting number position
		        answer = self.game.curr_board[i][j]
		        # If number is present
		        if answer != 0:
		        	# Create a box, using margins
		            x = MARGIN + j * SIDE + SIDE / 2
		            y = MARGIN + i * SIDE + SIDE / 2
		            # If number is present from the start, color black
		            # Otherwise, color green
		            original = self.game.start_board[i][j]
		            color = "black" if answer == original else "green3"
		            # Display the text
		            self.canvas.create_text(
		                x, y, text=answer, tags="numbers", fill=color
		            )
    
	"""
	Clear game board of answers
	"""            
	def __clear_answers(self):
	    self.game.start()
	    self.canvas.delete("victory")
	    self.canvas.delete("winner")
	    self.__draw_board()

	"""
	Allow for input of numbers after clicking cell
	"""    
	def __cell_clicked(self, event):
		# Do nothing if game is completed
	    if self.game.game_over:
	        return
	    # Get x,y coordinates from mouse click
	    x, y = event.x, event.y
	    if (MARGIN < x < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN):
	        self.canvas.focus_set()

	        # Get row and col numbers from x,y coordinates
	        row, col = (y - MARGIN) / SIDE, (x - MARGIN) / SIDE

	        # If cell was selected already - deselect it
	        if (row, col) == (self.row, self.col):
	            self.row, self.col = -1, -1
	        elif self.game.curr_board[row][col] == 0:
	            self.row, self.col = row, col

	    self.__draw_cursor()

	"""
	Takes self.row and self.col and highlight the corresponding cell
	"""
	def __draw_cursor(self):
		# Set to cursor
	    self.canvas.delete("cursor")
	    if self.row >= 0 and self.col >= 0:
	        x0 = MARGIN + self.col * SIDE + 1
	        y0 = MARGIN + self.row * SIDE + 1
	        x1 = MARGIN + (self.col + 1) * SIDE - 1
	        y1 = MARGIN + (self.row + 1) * SIDE - 1
	        # Draw rectangle at corresponding row,col
	        self.canvas.create_rectangle(
	            x0, y0, x1, y1,
	            outline="red", tags="cursor"
	        )

	"""
	Handles user input
	"""
	def __key_pressed(self, event):
		# If game is complete, do nothing
	    if self.game.game_over:
	        return
	    # If box is highlighted, and input is numerical (1,9)
	    if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
	    	# Update the current board
	        self.game.curr_board[self.row][self.col] = int(event.char)
	        # Deselect cell
	        self.col, self.row = -1, -1
	        # Redraw the board
	        self.__draw_board()
	        # Remove cursor box
	        self.__draw_cursor()
	        # Check for finished game state
	        if self.game.check_win():
	        	# Draw victory
	        	self.__draw_victory()

	"""
	Draw the victory end game screen
	"""
	def __draw_victory(self):
	    # Create a circle
	    x0 = y0 = MARGIN + SIDE * 2
	    x1 = y1 = MARGIN + SIDE * 7
	    # Fill circle with victory tag
	    self.canvas.create_oval(
	        x0, y0, x1, y1,
	        tags="victory", fill="dark orange", outline="orange"
	    )
	    # Add victory text
	    x = y = MARGIN + 4 * SIDE + SIDE / 2
	    self.canvas.create_text(
	        x, y,
	        text="You win!", tags="winner",
	        fill="white", font=("Arial", 32)
	    )

"""
Parses arguments of the form:
sudoku.py <board name>
Where <board name> must be in the BOARD list
"""
def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--board",
                            help="Desired board name",
                            type=str,
                            choices=BOARDS,
                            required=True)

    # Creates a dictionary of keys = argument flag, and value = argument
    args = arg_parser.parse_args()
    return args.board

"""
Parses board from txt file containing
different board configurations varying
in difficulty
"""
def parse_board(board_name):
    # Read from sudoku input file, remove trailing whitespace
    board_value = linecache.getline(board_name + ".txt", random.randint(0,NUMBOARDS))[0:9*9]
    # Check if line is valid
    if len(board_value) != 9*9:
    	raise SudokuError("File does not have enough numbers")
    # Convert line to valid format
    board_list = []
    # For each square
    for i in range(9):
    	# Create its own string element
    	tempstr = ""
    	for j in range(9):
    		tempstr += board_value[i*9 + j]
    	board_list.append(tempstr)
    # Return finished board configuration
    return board_list


"""
Main
"""
if __name__ == '__main__':
	# Get input arguments
    board_name = parse_arguments()
    # Read from sudoku input file
    boards_file = parse_board(board_name)
	# Initialise the game
    game = SudokuGame(boards_file)
    game.start()
    # Initialise Tkinter
    root = Tk()
    SudokuUI(root, game)
    root.geometry("%dx%d" % (WIDTH, HEIGHT + 40))
    # Start game loop
    root.mainloop()





