import random
import json
import os
from copy import deepcopy
from collections import deque, Counter
import time

class Game:
    """
    Core game engine for LinkedIn Queens (regional N-Queens puzzle).
    Handles puzzle generation, validation, hints, and puzzle persistence.
    """

    def __init__(self, n=4):
        """
        Initialize a new game engine.

        Args:
            n (int): Board size (n x n).
        """
        self.n = n
        self.total_spots = n ** 2
        self.__board = [0] * self.total_spots  # not the logical puzzle board
        self.title = "LinkedIn Queens"
        self.symbols = {
            '☐': '👑',
            '👑': '🖾',
            '❌': '🖾'
        }
        self.start_time = time.time()
        self.latest_solution = None

    @property
    def board(self):
        """
        Get the underlying board array.

        Returns:
            list[int]: Flattened n*n board of integer states.
        """
        return self.__board

    def create_board(self, n: int):
        """
        Reset the board to a new size.

        Args:
            n (int): New board size.
        """
        self.n = n
        self.total_spots = n ** 2
        self.__board = [0] * self.total_spots
        self.start_time = time.time()

    def html(self):
        """
        Generate an HTML table representing the board.

        Returns:
            str: HTML markup string.
        """
        symbols_list = list(self.symbols.keys())
        board_str = "<table>"
        for i in range(self.n):
            board_str += "<tr>"
            for c in range(self.n):
                board_str += f"<td id='{i}_{c}'>" + symbols_list[self.__board[self.n*i+c]] + "</td>"
            board_str += "</tr>"
        board_str += "</table>"
        return board_str

    def __str__(self):
        """
        Return a printable ASCII version of the board.

        Returns:
            str: Multi-line text grid representing the board.
        """
        symbols_list = list(self.symbols.keys())
        board_str = ""
        for i in range(self.n):
            for c in range(self.n):
                board_str += symbols_list[self.__board[self.n*i+c]]
                board_str += "|" if c < self.n - 1 else "\n"
            if i < self.n - 1:
                board_str += "-" * ((self.n - 1) * 3 + 2) + "\n"
        return board_str

    def validate_solution(self, queen_positions, regions):
        """
        Validate whether a placement satisfies both N-Queens and region constraints.

        Args:
            queen_positions (list[int]): queen_positions[col] = row index.
            regions (list[list[int]]): region IDs for each board cell.

        Returns:
            bool: True if valid, False otherwise.
        """
        seen_rows, seen_diag1, seen_diag2, region_use = set(), set(), set(), {}

        for col, row in enumerate(queen_positions):
            reg = regions[row][col]

            # N-Queens constraints + region uniqueness
            if (
                row in seen_rows or
                (row - col) in seen_diag1 or
                (row + col) in seen_diag2 or
                region_use.get(reg, 0) >= 1
            ):
                return False

            seen_rows.add(row)
            seen_diag1.add(row - col)
            seen_diag2.add(row + col)
            region_use[reg] = region_use.get(reg, 0) + 1

        return True

    def generate_puzzle(self, easy=True):
        """
        Generate a complete N-Queens puzzle with regions.

        Args:
            easy (bool): Whether to use easier region assignment rules.

        Returns:
            dict: {
                "solution": list[int],
                "regions": list[list[int]],
                "difficulty": str,
                "user_times": list[float]
            }
        """

        # ------------------------------------------
        # Helper: is position safe?
        # ------------------------------------------
        def is_safe(board, row, col):
            for c in range(col):
                r = board[c]
                if r == row or abs(r - row) == abs(c - col):
                    return False
            return True

        # ------------------------------------------
        # Solve N-Queens
        # ------------------------------------------
        def solve(board, col):
            if col == self.n:
                return deepcopy(board)
            rows = list(range(self.n))
            random.shuffle(rows)
            for row in rows:
                board[col] = row
                if is_safe(board, row, col):
                    result = solve(board, col + 1)
                    if result:
                        return result
            return None

        # Generate solution
        solution = solve([-1] * self.n, 0)
        self.latest_solution = solution

        # Board (0 = empty, 1 = queen)
        board = [[0] * self.n for _ in range(self.n)]
        for col, row in enumerate(solution):
            board[row][col] = 1

        # Regions start as empty
        regions = [[-1] * self.n for _ in range(self.n)]
        region_id = 0

        # Assign unique region for each queen
        for col, row in enumerate(solution):
            regions[row][col] = region_id
            region_id += 1

        # ================================================
        # EASY MODE (random region shapes + smoothing)
        # ================================================
        if easy:
            def mark_shape(cells):
                """Assign region_id to all cells in shape."""
                nonlocal region_id
                if all(
                    0 <= r < self.n and 0 <= c < self.n and
                    regions[r][c] == -1 and board[r][c] == 0
                    for r, c in cells
                ):
                    for r, c in cells:
                        regions[r][c] = region_id
                    region_id += 1

            # Random shapes list
            shapes = [
                lambda i, j: [(i, j)],
                lambda i, j: [(i, j), (i, j+1)],
                lambda i, j: [(i, j), (i+1, j)],
                lambda i, j: [(i, j), (i+1, j), (i+1, j+1)],
                lambda i, j: [(i, j+1), (i+1, j+1), (i+1, j)],
                lambda i, j: [(i, j+1), (i+1, j), (i+1, j+1), (i+1, j+2)],
                lambda i, j: [(i, j), (i, j+1), (i+1, j), (i+1, j+1)],
            ]

            # Apply shapes
            attempts = 0
            while region_id < self.n and attempts < 500:
                i, j = random.randint(0, self.n - 2), random.randint(0, self.n - 2)
                mark_shape(random.choice(shapes)(i, j))
                attempts += 1

            # Fill remaining using neighbor-majority
            def get_neighbors(r, c):
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.n and 0 <= nc < self.n:
                        yield nr, nc

            changed = True
            while changed:
                changed = False
                for r in range(self.n):
                    for c in range(self.n):
                        if regions[r][c] == -1:
                            neighbors = [regions[nr][nc] for nr, nc in get_neighbors(r, c) if regions[nr][nc] != -1]
                            if neighbors:
                                regions[r][c] = Counter(neighbors).most_common(1)[0][0]
                                changed = True

        # ================================================
        # HARD MODE (strict region expansion)
        # ================================================
        else:
            def get_neighbors(r, c):
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.n and 0 <= nc < self.n:
                        yield nr, nc

            changed = True
            while changed:
                changed = False
                for r in range(self.n):
                    for c in range(self.n):
                        if regions[r][c] == -1:
                            neighbors = [regions[nr][nc] for nr, nc in get_neighbors(r, c) if regions[nr][nc] != -1]
                            if neighbors:
                                regions[r][c] = Counter(neighbors).most_common(1)[0][0]
                                changed = True

        return {
            "solution": solution,
            "regions": regions,
            "difficulty": "easy" if easy else "hard",
            "user_times": []
        }

    def get_unique_solution(self):
        """
        Generate puzzles until one has exactly one valid solution.

        Returns:
            dict | None: Puzzle data dict, or None if unsuccessful.
        """
        for _ in range(100):
            puzzle = self.generate_puzzle(easy=False)
            region_ids = {reg for row in puzzle["regions"] for reg in row}
            if len(region_ids) == self.n:
                sols = self.find_all_solutions(puzzle["regions"])
                if len(sols) == 1:
                    return puzzle
        return None

    def find_all_solutions(self, regions):
        """
        Find all solutions that satisfy N-Queens + region rules.

        Args:
            regions (list[list[int]]): Region map.

        Returns:
            list[list[int]]: All valid queen position arrays.
        """

        def backtrack(col=0, queen_positions=[], used_rows=set(),
                      used_diag1=set(), used_diag2=set(), used_regions={}):
            if col == self.n:
                solutions.append(list(queen_positions))
                return

            for row in range(self.n):
                reg = regions[row][col]
                d1, d2 = row - col, row + col

                if (
                    row not in used_rows and
                    d1 not in used_diag1 and
                    d2 not in used_diag2 and
                    used_regions.get(reg, 0) < 1
                ):
                    queen_positions.append(row)
                    used_rows.add(row)
                    used_diag1.add(d1)
                    used_diag2.add(d2)
                    used_regions[reg] = used_regions.get(reg, 0) + 1

                    backtrack(col + 1, queen_positions, used_rows, used_diag1, used_diag2, used_regions)

                    queen_positions.pop()
                    used_rows.remove(row)
                    used_diag1.remove(d1)
                    used_diag2.remove(d2)
                    used_regions[reg] -= 1

        solutions = []
        backtrack()
        return solutions

    def save_to_data(self, data):
        """
        Save puzzle data to data/puzzles.json.

        Args:
            data (dict): Puzzle dictionary.

        Returns:
            str: Filename of saved puzzle.
        """
        os.makedirs("data", exist_ok=True)
        filepath = os.path.join("data", "puzzles.json")

        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                all_data = json.load(f)
        else:
            all_data = {}

        ids = [int(k) for k in all_data.keys()] if all_data else []
        next_id = str(max(ids) + 1) if ids else "1"
        all_data[next_id] = data

        with open(filepath, "w") as f:
            json.dump(all_data, f, indent=2)

        return f"puzzle_{next_id}.json"

    def live_check_solution(self, board):
        """
        Quickly check if each column has exactly one queen.

        Args:
            board (list[list[str]]): Visual board with emojis.

        Returns:
            bool: True if placement is structurally valid.
        """
        positions = [-1] * self.n
        for r in range(self.n):
            for c in range(self.n):
                if board[r][c] == '👑':
                    if positions[c] != -1:
                        return False
                    positions[c] = r
        return all(p != -1 for p in positions)

    def log_user_time(self, puzzle_id, solve_time):
        """
        Record a user's solve time into puzzles.json.

        Args:
            puzzle_id (str): Puzzle key.
            solve_time (float): Time in seconds.
        """
        filepath = os.path.join("data", "puzzles.json")
        if not os.path.exists(filepath):
            print("puzzles.json not found.")
            return

        with open(filepath, "r") as f:
            all_data = json.load(f)

        pid = puzzle_id.replace("puzzle_", "").replace(".json", "")
        if pid in all_data:
            all_data[pid].setdefault("user_times", []).append(solve_time)
            with open(filepath, "w") as f:
                json.dump(all_data, f, indent=2)

    def get_hint(self, current_board, regions):
        """
        Return the next queen's correct position.

        Args:
            current_board (list[list[str]]): Player's current board.
            regions (list[list[int]]): Region map (unused here but kept for symmetry).

        Returns:
            tuple[int, int] | None: (row, col) or None if completed.
        """
        if not self.latest_solution:
            return None

        for col, row in enumerate(self.latest_solution):
            if current_board[row][col] != '👑':
                return (row, col)
        return None


if __name__ == "__main__":
    game = Game(6)
    sample = game.generate_puzzle(easy=True)
    print("Sample Puzzle:", json.dumps(sample, indent=2))
    print("Valid solution:", game.validate_solution(sample["solution"], sample["regions"]))
    game.save_to_data(sample)
