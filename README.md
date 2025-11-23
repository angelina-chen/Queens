# Queens

## A Flask-powered N-Queens puzzle generator and solver

Updated from private repository. Play it here: [queens-bay.vercel.app](url)

```mermaid
%%{init: {'theme': 'dark', 'scale': 1.25}}%%
---
config:
  layout: elk
  theme: neo-dark
---
classDiagram
direction TB

class FlaskApp {
    <<Flask>>
    +login(): Response
    +game(): Response
    +process_results(id): JSON
    +give_hint(id): JSON

    -supabase_headers(): dict
    -get_latest_puzzle_id(): int | None
    -save_user_puzzle(puzzle_data): int | None
    -load_user_puzzles(): dict
    -record_solve_time(puzzle_id, solve_time): void
    -get_global_average_time(): float | N/A
}

class Game {
    +n: int
    +total_spots: int
    -board_internal: list
    +title: str
    +symbols: dict
    +start_time: float
    +latest_solution: list | None
    +board: list

    +create_board(n: int): void
    +html(): str
    +__str__(): str
    +validate_solution(queen_positions, regions): bool
    +generate_puzzle(easy: bool = True): dict
    +get_unique_solution(): dict | None
    +find_all_solutions(regions): list
    +save_to_data(data): str
    +live_check_solution(board): bool
    +log_user_time(puzzle_id, solve_time): void
    +get_hint(current_board, regions): (int, int) | None
}

class Queens {
    <<Utility>>
    +n: int
    +board: list
    +all_solutions: list

    +initialize_empty_board(): void
    +has_collision(board, col): bool
    +solve(max_solutions: int = 1000): list
    +search_all(col, max_solutions): bool
    +prettify(board): str
    +__str__(): str
}

class SupabasePuzzles {
    <<Supabase: puzzles>>
    id: int
    solution: list
    regions: list
    difficulty: str
}

class SupabaseTimes {
    <<Supabase: puzzle_times>>
    id: int
    puzzle_id: str
    solve_time: float
}

class LocalPuzzlesJSON {
    <<Legacy JSON file>>
    +puzzles.json
    +save_to_data(data): str
    +log_user_time(puzzle_id, solve_time): void
}

class IndexTemplate {
    <<Jinja2: index.html>>
    +form /game
}

class GameTemplate {
    <<Jinja2: game.html>>
    +render board
    +inject info
}

class BrowserClient {
    <<JavaScript>>
    +handleClick(e)
    +countQueens()
    +prepareData()
    +submitSolution()
    +requestHint()
}

class Styles {
    <<CSS>>
}

class VercelConfig {
    <<vercel.json>>
    builds
    routes
}

FlaskApp --> Game
Game ..> Queens

FlaskApp --> SupabasePuzzles
FlaskApp --> SupabaseTimes
Game --> LocalPuzzlesJSON

FlaskApp --> IndexTemplate
FlaskApp --> GameTemplate

BrowserClient --> FlaskApp 
GameTemplate --> BrowserClient

IndexTemplate --> Styles
GameTemplate --> Styles

VercelConfig --> FlaskApp
