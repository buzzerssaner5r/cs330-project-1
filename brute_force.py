import json
import time
 
TIMEOUT_SECONDS = 30      # max time allowed per puzzle
CHECK_EVERY = 10000       # only look at the clock every 10000 boards
MAX_ROW_BLANKS = 9        # tier 2 skips rows with more blanks than this
SIZES_TO_RUN = None       
 
# these get updated by the solvers so the runner can read them
boards_tried = 0
timed_out = False
skipped = False
 
 
def list_is_complete(numbers, size):
	# a row, column or box is good if it has exactly the numbers 1 to size
	return sorted(numbers) == list(range(1, size + 1))
 
 
def check_rows(board, size):
	for r in range(size):
    	if not list_is_complete(board[r], size):
        	return False
	return True
 
 
def check_cols_and_boxes(board, size, box_rows, box_cols):
	# checking every column
	for c in range(size):
    	col = []
    	for r in range(size):
            col.append(board[r][c])
    	if not list_is_complete(col, size):
        	return False
 
	# check every sub grid
	for start_r in range(0, size, box_rows):
    	for start_c in range(0, size, box_cols):
        	box = []
        	for r in range(start_r, start_r + box_rows):
            	for c in range(start_c, start_c + box_cols):
                    box.append(board[r][c])
        	if not list_is_complete(box, size):
            	return False
	return True
 
 
def check_board(board, size, box_rows, box_cols):
	# full check
	if not check_rows(board, size):
    	return False
	return check_cols_and_boxes(board, size, box_rows, box_cols)
 
 
# Tier 1: pur brute force
def solve_brute_force(board, size, box_rows, box_cols, timeout=None):
	global boards_tried, timed_out, skipped
	boards_tried = 0
	timed_out = False
	skipped = False
 
	# finding all empty cells
	empty_cells = []
	for r in range(size):
    	for c in range(size):
        	if board[r][c] == 0:
                empty_cells.append((r, c))
 
	# one value for each empty cell, start with all 1s
	values = [1] * len(empty_cells)
	start_time = time.perf_counter()
 
	while True:
    	# fill the board with the current combination
    	for i in range(len(empty_cells)):
        	r, c = empty_cells[i]
            board[r][c] = values[i]
    	boards_tried += 1
 
    	# only checking after the whole board is filled
    	if check_board(board, size, box_rows, box_cols):
        	return True
 
    	# stop if it is taking too long
    	if timeout is not None and boards_tried % CHECK_EVERY == 0:
        	if time.perf_counter() - start_time > timeout:
                timed_out = True
            	break
 
    	# move to the next combination
    	i = len(values) - 1
    	while i >= 0 and values[i] == size:
        	values[i] = 1
        	i -= 1
    	if i < 0:
        	break      	# tried every combination
    	values[i] += 1
 
	# nothing worked so put the empty cells back to 0
	for r, c in empty_cells:
    	board[r][c] = 0
	return False
 
#Tier 2: row permutations
def get_permutations(items):
	# returns every possible ordering of the items list
	if len(items) <= 1:
    	return [items[:]]
	result = []
	for i in range(len(items)):
    	rest = items[:i] + items[i + 1:]
    	for perm in get_permutations(rest):
            result.append([items[i]] + perm)
	return result
 
 
def solve_row_permutation(board, size, box_rows, box_cols, timeout=None):
	global boards_tried, timed_out, skipped
	boards_tried = 0
	timed_out = False
	skipped = False
 
	blanks_in_row = [] 	# column positions of the blanks in each row
	options_for_row = []   # every way to fill the blanks of each row
 
	for r in range(size):
    	blanks = []
    	missing = []
    	for c in range(size):
        	if board[r][c] == 0:
                blanks.append(c)
    	for num in range(1, size + 1):
        	if num not in board[r]:
                missing.append(num)
 
   	 # too many blanks means too many orderings to even build
    	if len(blanks) > MAX_ROW_BLANKS:
        	skipped = True
        	return False
    	# the row already has a repeated number so it can't be solved
    	if len(missing) != len(blanks):
        	return False
 
        blanks_in_row.append(blanks)
        options_for_row.append(get_permutations(missing))
 
	choice = [0] * size
	start_time = time.perf_counter()
 
	while True:
    	# fill each row with its chosen ordering
    	for r in range(size):
        	ordering = options_for_row[r][choice[r]]
        	for i in range(len(blanks_in_row[r])):
                board[r][blanks_in_row[r][i]] = ordering[i]
    	boards_tried += 1
 
    	# rows are already correct, so only check columns and boxes
    	if check_cols_and_boxes(board, size, box_rows, box_cols):
        	return True
 
    	if timeout is not None and boards_tried % CHECK_EVERY == 0:
        	if time.perf_counter() - start_time > timeout:
 	           timed_out = True
            	break
 
    	# move to the next combination of row orderings
    	r = size - 1
    	while r >= 0 and choice[r] == len(options_for_row[r]) - 1:
        	choice[r] = 0
        	r -= 1
    	if r < 0:
        	break      	# tried every combination
    	choice[r] += 1
 
	# nothing worked so put the blanks back to 0
	for r in range(size):
    	for c in blanks_in_row[r]:
            board[r][c] = 0
	return False
 
 
# run on the dataset
def run_one(solver, item):
	# make a copy so the original puzzle is not changed
	grid_copy = [row[:] for row in item["puzzle"]]
 
	start_time = time.perf_counter()
	solved = solver(grid_copy, item["size"], item["box_rows"], item["box_cols"], TIMEOUT_SECONDS)
	execution_time = time.perf_counter() - start_time
 
	# checking the result against the expected answer
	if skipped:
    	status = "Skipped"
	elif timed_out:
    	status = "Timeout"
	elif solved and grid_copy == item["solution"]:
    	status = "Passed"
	elif solved:
    	status = "Wrong Solution"
	else:
    	status = "Failed"
	return execution_time, boards_tried, status
 
 
if __name__ == "__main__":
	try:
    	with open('data_set.json', 'r') as file:
        	puzzles = json.load(file)
	except FileNotFoundError:
        print("Error: Please save your dataset as 'data_set.json' in the same folder.")
    	puzzles = []
 
	solvers = [("Tier1-Exhaustive", solve_brute_force),
               ("Tier2-RowPerm", solve_row_permutation)]
 
	# print the formatting header
    print(f"{'Puzzle ID':<18} | {'Size':<4} | {'Difficulty':<10} | {'Solver':<16} | {'Time Taken (s)':<15} | {'Boards Tried':<12} | Status")
    print("-" * 100)
 
	for item in puzzles:
    	if SIZES_TO_RUN is not None and item["size"] not in SIZES_TO_RUN:
        	continue
    	for name, solver in solvers:
        	t, tried, status = run_one(solver, item)
            print(f"{item['id']:<18} | {item['size']:<4} | {item['difficulty']:<10} | {name:<16} | {t:<15.6f} | {tried:<12} | {status}")
