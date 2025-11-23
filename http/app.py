from flask import Flask, jsonify, request, render_template
import os, sys, json, traceback

# Add the http/ directory itself to sys.path so "helpers" is importable as a package/module
BASE_DIR = os.path.dirname(__file__)
sys.path.append(BASE_DIR)

from helpers.Game import Game  # import the Game class directly

app = Flask(__name__, static_url_path='', static_folder='static')

# Data file locations
DATA_DIR = "data"
PUZZLE_FILE_SLIDES = os.path.join(DATA_DIR, "puzzle_slides.json")   # Preloaded puzzle set
PUZZLE_FILE_USER = os.path.join(DATA_DIR, "puzzles.json")           # User-generated puzzles


def load_preloaded_puzzles():
    """Load puzzles bundled with the app."""
    if not os.path.exists(PUZZLE_FILE_SLIDES):
        return {}
    with open(PUZZLE_FILE_SLIDES, "r") as f:
        return json.load(f)


def load_user_puzzles():
    """Load puzzles created by players."""
    if not os.path.exists(PUZZLE_FILE_USER):
        return {}
    with open(PUZZLE_FILE_USER, "r") as f:
        return json.load(f)


def save_user_puzzles(puzzles):
    """Save user puzzle data to disk."""
    with open(PUZZLE_FILE_USER, "w") as f:
        json.dump(puzzles, f, indent=2)


def get_puzzle_ids():
    """Return metadata (size, difficulty) for all *preloaded* puzzles."""
    puzzles = load_preloaded_puzzles()
    ids = {}
    for id_, data in puzzles.items():
        regions = data.get("regions", [])
        rows = len(regions)
        cols = len(regions[0]) if regions else 0

        ids[id_] = {
            "difficulty": data.get("difficulty", "unknown"),
            "rows": rows,
            "cols": cols
        }
    return ids


@app.route('/')
@app.route('/')
def login():
    puzzle_ids = get_puzzle_ids()
    temp_game = Game()
    return render_template('index.html', title=temp_game.title, puzzle_ids=puzzle_ids)

@app.route('/board')
def board():
    temp_game = Game()
    return str(temp_game)

@app.route('/board_json')
def board_json():
    temp_game = Game()
    return jsonify(temp_game.board)


@app.route('/game')
def game():
    """
    Render the main puzzle page.

    Handles:
      - Loading a selected puzzle (preloaded or user-created)
      - Generating a new puzzle if no ID is provided
    """
    username = request.args.get('username_new') or request.args.get('username_existing')
    puzzle_id = request.args.get('puzzle_id')
    difficulty = request.args.get('difficulty', 'easy')

    preloaded_puzzles = load_preloaded_puzzles()
    user_puzzles = load_user_puzzles()

    # Determine puzzle data source
    if puzzle_id and puzzle_id in preloaded_puzzles:
        puzzle_data = preloaded_puzzles[puzzle_id]
    elif puzzle_id and puzzle_id in user_puzzles:
        puzzle_data = user_puzzles[puzzle_id]
    else:
        # Generate a new puzzle if none was selected
        size_str = request.args.get('board_size', '7')
        try:
            size = int(size_str)
        except ValueError:
            return jsonify({"error": f"Invalid board size '{size_str}'"}), 400

        my_game = Game(size)
        puzzle_data = my_game.generate_puzzle(easy=(difficulty == "easy"))

        # Assign a unique new puzzle ID
        existing_ids = set(preloaded_puzzles.keys()) | set(user_puzzles.keys())
        next_id_num = 1000
        while str(next_id_num) in existing_ids:
            next_id_num += 1
        new_id = str(next_id_num)

        user_puzzles[new_id] = puzzle_data
        save_user_puzzles(user_puzzles)
        puzzle_id = new_id

    # Set up board for display
    size = len(puzzle_data["regions"])
    my_game = Game(size)
    my_game.latest_solution = puzzle_data.get("solution")

    board_data = [['☐' for _ in range(size)] for _ in range(size)]

    template_info = {
        "username": username,
        "title": my_game.title,
        "symbols": my_game.symbols,
        "board_id": puzzle_id,
        "board_size": size,
        "regions": puzzle_data["regions"],
        "board_data": board_data
    }

    return render_template('game.html', info=template_info)


@app.route('/solve/<id>', methods=['POST'])
def process_results(id):
    """
    Validate a submitted puzzle solution and record timing stats.
    """
    try:
        data = request.json or {}

        # Extract only grid entries ("row_col")
        board_data = {k: v for k, v in data.items() if "_" in k and k.count("_") == 1}
        solve_time = float(data.get("solve_time", 0))

        # Reconstruct the 2D board
        board_size = int(len(board_data) ** 0.5)
        board = [["☐" for _ in range(board_size)] for _ in range(board_size)]
        for k, v in board_data.items():
            try:
                r, c = map(int, k.split("_"))
                board[r][c] = v
            except ValueError:
                continue

        # Merge preloaded + user puzzles for lookup
        preloaded = load_preloaded_puzzles()
        user_puzzles = load_user_puzzles()

        all_puzzles = preloaded.copy()
        for pid, pdata in user_puzzles.items():
            if pid not in preloaded or "solution" not in preloaded.get(pid, {}):
                all_puzzles[pid] = pdata

        if id not in all_puzzles:
            return jsonify({"result": "Puzzle not found."}), 404

        puzzle_data = all_puzzles[id]

        if "solution" not in puzzle_data or "regions" not in puzzle_data:
            return jsonify({"result": f"Puzzle {id} missing required fields"}), 500

        solution = puzzle_data["solution"]
        regions = puzzle_data["regions"]

        # Validate the submitted queen positions
        my_game = Game(board_size)
        my_game.latest_solution = solution

        queen_positions = [-1] * board_size
        for r in range(board_size):
            for c in range(board_size):
                if board[r][c] == '👑':
                    queen_positions[c] = r

        valid = my_game.validate_solution(queen_positions, regions)
        result = "Correct!" if valid else "Incorrect."

        # Save timing data only for correct solutions
        if valid:
            if id not in user_puzzles:
                user_puzzles[id] = {"user_times": []}
            user_puzzles[id].setdefault("user_times", []).append(solve_time)
            save_user_puzzles(user_puzzles)

        # Compute global average solve time
        all_times = []
        for pdata in user_puzzles.values():
            all_times.extend(pdata.get("user_times", []))

        avg_time = round(sum(all_times) / len(all_times), 2) if all_times else "N/A"

        return jsonify({
            "result": result,
            "user_time": solve_time,
            "average_time": avg_time
        })

    except Exception:
        print("❌ Error during submission:", traceback.format_exc())
        return jsonify({"result": "Server error."}), 500


@app.route('/hint/<id>', methods=['POST'])
def give_hint(id):
    """
    Return a hint (row, col) for the current puzzle state.
    """
    data = request.json or {}
    board_data = {k: v for k, v in data.items() if "_" in k and k.count("_") == 1}

    board_size = int(len(board_data) ** 0.5)
    board = [["☐" for _ in range(board_size)] for _ in range(board_size)]
    for k, v in board_data.items():
        try:
            r, c = map(int, k.split("_"))
            board[r][c] = v
        except ValueError:
            continue

    puzzle_data = load_preloaded_puzzles().get(id) or load_user_puzzles().get(id)

    if not puzzle_data:
        return jsonify({"error": f"Puzzle {id} not found"}), 404
    if "regions" not in puzzle_data or "solution" not in puzzle_data:
        return jsonify({"error": f"Puzzle {id} missing required fields"}), 500

    regions = puzzle_data["regions"]
    solution = puzzle_data["solution"]

    my_game = Game(board_size)
    my_game.latest_solution = solution

    hint = my_game.get_hint(board, regions)

    if hint:
        return jsonify({"row": hint[0], "col": hint[1]})
    return jsonify({"message": "No valid hint found"})


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, port=port)
