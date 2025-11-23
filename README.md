# Queens

## A Flask-powered N-Queens puzzle generator and solver

Updated from private repository. Play it here: [queens-bay.vercel.app](url)

```mermaid
---
config:
  layout: elk
  theme: neo-dark
---
classDiagram
direction LR

%% =========================
%% Core Backend
%% =========================

class FlaskApp {
    <<Flask>>
    +login(): Response
    +game(): Response
    +process_results(id: str): JSON
    +give_hint(id: str): JSON

    -supabase_headers(): dict
    -get_latest_puzzle_id(): int | None
    -save_user_puzzle(puzzle_data: dict): int | None
    -load_user_puzzles(): dict[str, dict]
    -record_solve_time(puzzle_id: str | int, solve_time: float): void
    -get_global_average_time(): float | "N/A"
}

class Game {
    +n: int
    +total_spots: int
    -__board: list[int]
    +title: str
    +symbols: dict[str, str]
    +start_time: float
    +latest_solution: list[int] | None

    +board: list[int]
    +create_board(n: int): void
    +html(): str
    +__str__(): str

    +validate_solution(queen_positions: list[int], regions: list[list[int]]): bool
    +generate_puzzle(easy: bool = True): dict
    +get_unique_solution(): dict | None
    +find_all_solutions(regions: list[list[int]]): list[list[int]]

    +save_to_data(data: dict): str
    +live_check_solution(board: list[list[str]]): bool
    +log_user_time(puzzle_id: str, solve_time: float): void
    +get_hint(current_board: list[list[str]], regions: list[list[int]]): tuple[int,int] | None
}

class Queens {
    <<Utility>>
    +n: int
    +board: list[int]
    +all_solutions: list[list[int]]

    +initialize_empty_board(): void
    +has_collision(board: list[int], current_col: int): bool
    +solve(num_sol: int = 1000): list[list[int]]
    +search_all(current_col: int = 0, max_sol: int = 1000): bool
    +prettify(board: list[int]): str
    +__str__(): str
}

%% =========================
%% Persistence Layer
%% =========================

class SupabasePuzzles {
    <<Supabase table: "puzzles">>
    id: int
    solution: list[int]
    regions: list[list[int]]
    difficulty: str
}

class SupabaseTimes {
    <<Supabase table: "puzzle_times">>
    id: int
    puzzle_id: str
    solve_time: float
}

class LocalPuzzlesJSON {
    <<Legacy JSON file>>
    +puzzles.json
    +save_to_data(data: dict): str
    +log_user_time(puzzle_id: str, solve_time: float): void
}

%% =========================
%% Frontend / Templates
%% =========================

class IndexTemplate {
    <<Jinja2: index.html>>
    +form /game?username_new&board_size&difficulty
}

class GameTemplate {
    <<Jinja2: game.html>>
    +render board (table)
    +inject info: username, board_id, board_size, regions, symbols
    +includes footer.html
}

class BrowserClient {
    <<JavaScript>>
    +handleClick(e): void
    +countQueens(): int
    +prepareData(): dict
    +submitSolution(): Promise
    +requestHint(): Promise
}

class Styles {
    <<CSS: styles.css>>
    +board + regions styling
    +responsive layout
}

class VercelConfig {
    <<vercel.json>>
    builds: @vercel/python
    routes: /(.*) -> http/app.py
}


%% =========================
%% Relationships
%% =========================

FlaskApp --> Game : uses
Game ..> Queens : optional solver utility

FlaskApp --> SupabasePuzzles : REST /rest/v1/puzzles
FlaskApp --> SupabaseTimes : REST /rest/v1/puzzle_times
Game --> LocalPuzzlesJSON : legacy file I/O

FlaskApp --> IndexTemplate : render_template("index.html")
FlaskApp --> GameTemplate : render_template("game.html")

BrowserClient --> FlaskApp : /game (GET)
BrowserClient --> FlaskApp : /solve/{id} (POST)
BrowserClient --> FlaskApp : /hint/{id} (POST)

GameTemplate --> BrowserClient : inline <script>
IndexTemplate --> Styles
GameTemplate --> Styles

VercelConfig --> FlaskApp : deployment entry
