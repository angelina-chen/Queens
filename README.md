# Queens: A Flask-powered N-Queens puzzle generator and solver
## Live Demo: https://queens-bay.vercel.app
## Rules
Based on LinkedIn Queens:
1. Each row, column, and colored region must contain exactly one Crown symbol (Queen).
2. Crown symbols cannot be placed in adjacent cells, including diagonally.
3. Click or tap on cells to toggle between empty cells, marked (bolded box) symbol, and Crown symbol.

## Features
- Procedurally generated LinkedIn Queens puzzles  
- Region-based N-Queens constraints  
- Auto-validation engine  
- Supabase integration for puzzle storage and stats  
- Hint engine powered by solution backtracking  

## Tech Stack
- Frontend: HTML/CSS, vanilla JS
- Backend: Flask (Python), REST endpoints
- Database: Supabase (Postgres) via REST API
- Deployment: Vercel (frontend)


```mermaid
---
config:
  layout: elk
  theme: neo-dark
---
%%{init: {'theme': 'dark', 'scale': 1.25}}%%
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
```
## Sample Gameplay
Creating a new puzzle:

<img width="592" height="702" alt="image" src="https://github.com/user-attachments/assets/06b49c91-c0b7-4840-b384-43aa55eb1c86" />

Placing queens and marking feature:

<img width="594" height="603" alt="image" src="https://github.com/user-attachments/assets/439a1c7e-7ae6-414b-b9c6-18b1b59feaea" />

Getting a hint: 

<img width="544" height="617" alt="image" src="https://github.com/user-attachments/assets/689507de-3214-47c9-acea-0a0b615553bc" />

Sample win scenario:

<img width="559" height="639" alt="image" src="https://github.com/user-attachments/assets/e8807ce1-8cb7-4b14-9f79-83f17888fa7f" />

Sample loss scenario:

<img width="541" height="611" alt="image" src="https://github.com/user-attachments/assets/98006548-6a4f-4699-8b34-c70a8d3ed5d7" />
