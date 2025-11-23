# Queens
Updated from private repository.

```mermaid
---
config:
  layout: elk
  theme: neo-dark
---
classDiagram
direction LR

class FlaskApp {
    <<Flask>>
    +load_preloaded_puzzles()
    +load_user_puzzles()
    +save_user_puzzles()
    +get_puzzle_ids()
    +login()
    +game()
    +process_results(id)
    +give_hint(id)
}

class Game {
    +int n
    +list board
    +str title
    +dict symbols
    +float start_time
    +list latest_solution

    +create_board(n)
    +html() str
    +__str__() str

    +validate_solution(queen_positions, regions) bool
    +generate_puzzle(easy) dict
    +get_unique_solution() dict
    +find_all_solutions(regions) list

    +save_to_data(data)
    +live_check_solution(board) bool
    +log_user_time(puzzle_id, solve_time)
    +get_hint(current_board, regions) tuple
}

class Queens {
    +int n
    +list board
    +list all_solutions

    +initialize_empty_board()
    +has_collision(board, col) bool
    +solve(num_sol) list
    +search_all(col, max_sol) bool
    +prettify(board) str
}

class PuzzleFile {
    <<JSON file>>
    solution : list[int]
    regions : list[list[int]]
    difficulty : str
    user_times : list[float]
}

FlaskApp --> Game : "creates and uses"
FlaskApp --> PuzzleFile : "reads/writes"
Game --> PuzzleFile : "stores puzzles"
Game --> Queens : "uses solver"
