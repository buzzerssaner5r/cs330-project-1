def print_board(board):
    """Print the Sudoku board in a readable format."""
    for row in board:
        print(" ".join(str(value) for value in row))


def is_valid(board, row, col, num):
    """Check whether num can be placed at board[row][col]."""

    for current_col in range(9):
        if board[row][current_col] == num:
            return False

    for current_row in range(9):
        if board[current_row][col] == num:
            return False

    box_row = (row // 3) * 3
    box_col = (col // 3) * 3

    for current_row in range(box_row, box_row + 3):
        for current_col in range(box_col, box_col + 3):
            if board[current_row][current_col] == num:
                return False

    return True


def find_empty(board):
    """Find the next empty cell.

    Returns:
        (row, col) if an empty cell exists.
        None if the board is full.
    """
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                return row, col

    return None


def solve_brute_force(board):
    """Solve the Sudoku puzzle using brute force."""

    empty_cell = find_empty(board)

    if empty_cell is None:
        return True

    row, col = empty_cell

    for num in range(1, 10):

        if is_valid(board, row, col, num):
            board[row][col] = num

            if solve_brute_force(board):
                return True

            board[row][col] = 0

    return False


if __name__ == "__main__":

    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],

        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],

        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]

    print("Original Sudoku:")
    print_board(puzzle)

    print("\nSolving...")

    if solve_brute_force(puzzle):
        print("\nSolved Sudoku:")
        print_board(puzzle)
    else:
        print("\nNo solution exists.")
