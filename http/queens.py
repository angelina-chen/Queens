class Queens:
    def __init__(self, n: int):
        """
        Initialize an n-Queens solver.

        Args:
            n (int): Board dimension (n x n).
        """
        self.n = n
        self.board = []  # board[col] = row index of queen in that column
        self.initialize_empty_board()
        self.all_solutions = []

    def initialize_empty_board(self):
        """Reset the board so no queens are placed (-1 in each column)."""
        self.board = [-1] * self.n

    def has_collision(self, board: list[int], current_col: int) -> bool:
        """
        Check whether placing a queen in current_col causes a conflict.

        Only columns 0..current_col-1 are considered, assuming each contains a queen.

        Conflicts checked:
          - same row
          - same diagonal

        Args:
            board (list[int]): board[col] = row position of queen.
            current_col (int): Column where a queen was just placed.

        Returns:
            bool: True if this queen conflicts with any earlier queen.

        Examples:
            >>> q = Queens(8)
            >>> q.has_collision([0, 6, 4, 7, 3, -1, -1, -1], 4)
            True
            >>> q.has_collision([2, 4, 1, 7, 5, 3, 6, 0], 7)
            False
        """
        for col in range(current_col):
            same_row = board[col] == board[current_col]
            same_diag = abs(board[col] - board[current_col]) == abs(col - current_col)
            if same_row or same_diag:
                return True
        return False

    def solve(self, num_sol: int = 1000) -> list[list[int]]:
        """
        Find up to `num_sol` solutions to the n-Queens puzzle.

        Args:
            num_sol (int): Number of requested solutions.

        Returns:
            list[list[int]]: A list of solutions, each a board representation.
        """
        self.initialize_empty_board()
        self.all_solutions = []
        self.search_all(0, num_sol)
        return self.all_solutions

    def search_all(self, current_col: int = 0, max_sol: int = 1000) -> bool:
        """
        Recursive backtracking helper to find solutions.

        Args:
            current_col (int): Current column being filled.
            max_sol (int): Maximum number of solutions to collect.

        Returns:
            bool: True if we already collected `max_sol` solutions.
        """
        # Base case: all columns filled → one full solution found
        if current_col == self.n:
            self.all_solutions.append(self.board.copy())
            return len(self.all_solutions) >= max_sol

        # Try placing a queen in each row of this column
        for row in range(self.n):
            self.board[current_col] = row
            if not self.has_collision(self.board, current_col):
                if self.search_all(current_col + 1, max_sol):
                    return True

        # Backtrack
        self.board[current_col] = -1
        return False

    def prettify(self, board: list[int]) -> str:
        """
        Convert a solution into a human-readable board string.

        'Q' marks queens; '.' marks empty squares.

        Args:
            board (list[int]): board[col] = row where a queen is placed.

        Returns:
            str: Multi-line string representation.
        """
        self.board = board
        pretty_board = [["."] * self.n for _ in range(self.n)]

        for col_index, row_index in enumerate(self.board):
            if 0 <= row_index < self.n:
                pretty_board[row_index][col_index] = "Q"

        # Build the string output
        rows = ["".join(row) for row in pretty_board]
        return "\n".join(rows)

    def __str__(self) -> str:
        """Return a summary of how many solutions exist for this n."""
        return f"{self.n}-Queens has {len(self.solve(100000))} solutions"


if __name__ == "__main__":
    queens = Queens(8)
    sols = queens.solve()
    print(queens.prettify(sols[0]))
    print(queens)
