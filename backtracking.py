import json

import time


def solve_sudoku(board, size, box_rows, box_cols):

   # track numbers already used in each row, column and sub grid

   rows = [set() for _ in range(size)]

   cols = [set() for _ in range(size)]

   boxes = [[set() for _ in range(size // box_cols)] for _ in range(size // box_rows)]


   empty_cells = []


   # record all initial numbers and keep track of empty cells

   for r in range(size):

       for c in range(size):

           val = board[r][c]

           if val != 0:

               rows[r].add(val)

               cols[c].add(val)

               boxes[r // box_rows][c // box_cols].add(val)

           else:

               empty_cells.append((r, c))


   def backtrack():

       # if there are no empty cells then the board is solved

       if not empty_cells:

           return True


       # find the empty cell with the fewest possible valid choices left

       min_options = float('inf')

       best_idx = -1

       best_options = []


       for idx, (r, c) in enumerate(empty_cells):

           br, bc = r // box_rows, c // box_cols

           # combine row, col and box rule to see what numbers are taken

           forbidden = rows[r] | cols[c] | boxes[br][bc]

           allowed = [num for num in range(1, size + 1) if num not in forbidden]


           # dead end so we backtrack

           if len(allowed) == 0:

               return False

           # pick the spot with the fewest valid options

           if len(allowed) < min_options:

               min_options = len(allowed)

               best_idx = idx

               best_options = allowed

               # if a cell only has one option, pick it

               if min_options == 1:

                   break


       if best_idx == -1:

           return False


       # remove this cell from list temporarily

       r, c = empty_cells.pop(best_idx)

       br, bc = r // box_rows, c // box_cols


       # try each valid choice for this cell

       for num in best_options:

           # place the choice

           board[r][c] = num

           rows[r].add(num)

           cols[c].add(num)

           boxes[br][bc].add(num)


           # move to the next empty cell recursively

           if backtrack():

               return True


           # if it didn't lead to a solution, backtrack

           rows[r].remove(num)

           cols[c].remove(num)

           boxes[br][bc].remove(num)

           board[r][c] = 0


       # if no numbers worked, put the cell back and return false

       empty_cells.insert(best_idx, (r, c))

       return False


   return backtrack()


#load puzzles from dataset

try:

   with open('data_set.json', 'r') as file:

       puzzles = json.load(file)

except FileNotFoundError:

   print("Error: Please save your dataset as 'data_set.json' in the same folder.")

   puzzles = []


#print the formatting header

print(f"{'Puzzle ID':<18} | {'Size':<4} | {'Difficulty':<10} | {'Time Taken (s)':<15} | Status")

print("-" * 65)


#run the solver on each puzzle and note execution time

for item in puzzles:

   puzzle_id = item["id"]

   size = item["size"]

   difficulty = item["difficulty"]

   box_rows = item["box_rows"]

   box_cols = item["box_cols"]


#make a copy of the puzzle so it doesn't overwrite original data

   grid_copy = [row[:] for row in item["puzzle"]]

   expected_solution = item["solution"]


#start timer, solve, stop timer

   start_time = time.perf_counter()

   solved = solve_sudoku(grid_copy, size, box_rows, box_cols)

   end_time = time.perf_counter()


   execution_time = end_time - start_time


# check the results against the expected output

   if solved and grid_copy == expected_solution:

       status = "Passed"

   elif solved:

       status = "Wrong Solution"

   else:

       status = "Failed"

   print(f"{puzzle_id:<18} | {size:<4} | {difficulty:<10} | {execution_time:.6f}s | {status}")
