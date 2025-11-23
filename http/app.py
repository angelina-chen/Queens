from flask import Flask, jsonify, request, render_template
import os
import sys
import json
import traceback
import requests

# ----- Supabase config (read from environment variables) -----
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

PUZZLES_TABLE = "puzzles"
TIMES_TABLE = "puzzle_times"

# ----- Import Game from helpers/Game.py -----
BASE_DIR = os.path.dirname(__file__)
sys.path.append(BASE_DIR)
from helpers.Game import Game  # noqa: E402

app = Flask(__name__, static_url_path="", static_folder="static")

# Still use local JSON for slide/preloaded puzzles
DATA_DIR = "data"
PUZZLE_FILE_SLIDES = os.path.join(DATA_DIR, "puzzle_slides.json")


# ---------------- Supabase helpers ---------------- #

def supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }


def load_preloaded_puzzles():
    """Load puzzles bundled with the app from local JSON."""
    if not os.path.exists(PUZZLE_FILE_SLIDES):
        return {}
    with open(PUZZLE_FILE_SLIDES, "r") as f:
        return json.load(f)


def load_user_puzzles():
    """
    Load all user puzzles from Supabase `puzzles` table.

    Returns:
        dict[str, dict]: {id: {"solution": [...], "regions": [...], "difficulty": str}}
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {}

    url = f"{SUPABASE_URL}/rest/v1/{PUZZLES_TABLE}"
    params = {"select": "id,solution,regions,difficulty"}
    resp = requests.get(url, headers=supabase_headers(), params=params)

    if not resp.ok:
        print("Error loading puzzles from Supabase:", resp.text)
        return {}

    puzzles = {}
    for row in resp.json():
        pid = row["id"]
        puzzles[pid] = {
            "solution": row["solution"],
            "regions": row["regions"],
            "difficulty": row.get("difficulty", "easy"),
        }
    return puzzles


def save_user_puzzle(puzzle_id, puzzle_data):
    """
    Insert a new puzzle into Supabase `puzzles` table.

    Args:
        puzzle_id (str): ID to use in the puzzles table.
        puzzle_data (dict): Must contain "solution", "regions", and optional "difficulty".
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Supabase env vars missing; skipping save.")
        return

    url = f"{SUPABASE_URL}/rest/v1/{PUZZLES_TABLE}"
    row = {
        "id": puzzle_id,
        "solution": puzzle_data["solution"],
        "regions": puzzle_data["regions"],
        "difficulty": puzzle_data.get("difficulty", "easy"),
    }
    resp = requests.post(url, headers=supabase_headers(), json=row)
    if not resp.ok:
        print("Error saving puzzle to Supabase:", resp.text)


def record_solve_time(puzzle_id, solve_time):
    """
    Insert a solve time into `puzzle_times` table.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Supabase env vars missing; skipping time log.")
        return

    url = f"{SUPABASE_URL}/rest/v1/{TIMES_TABLE}"
    row = {"puzzle_id": str(puzzle_id), "solve_time": float(solve_time)}
    resp = requests.post(url, headers=supabase_headers(), json=row)
    if not resp.ok:
        print("Error saving solve_time to Supabase:", resp.text)


def get_global_average_time():
    """
    Compute global average solve time from `puzzle_times`.
    Returns "N/A" if no data.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return "N/A"

    url = f"{SUPABASE_URL}/rest/v1/{TIMES_TABLE}"
    params = {"select": "solve_time"}
    resp = requests.get(url, headers=supabase_headers(), params=params)

    if not resp.ok:
        print("Error loading times from Supabase:", resp.text)
        return "N/A"

    rows = resp.json()
    times = [float(r["solve_time"]) for r in rows if "solve_time" in r]
    if not times:
        return "N/A"
    return round(sum(times) / len(times), 2)


def get_puzzle_ids():
    """
    Return metadata (size, difficulty) for all *preloaded* puzzles (for dropdown).
    """
    puzzles = load_preloaded_puzzles()
    ids = {}
    for id_, data in puzzles.items():
        regions = data.get("regions", [])
        rows = len(regions)
        cols = len(regions[0]) if regions else 0

        ids[id_] = {
            "difficulty": data.get("difficulty", "unknown"),
            "rows": rows,
            "cols": cols,
        }
    return ids


# ---------------- Routes ---------------- #

@app.route("/")
def login():
    puzzle_ids = get_puzzle_ids()
    temp_game = Game()
    return render_template("index.html", title=temp_game.title, puzzle_ids=puzzle_ids)


@app.route("/board")
def board():
    temp_game = Game()
    return str(temp_game)


@app.route("/board_json")
def board_json():
    temp_game = Game()
    return jsonify(temp_game.board)


@app.route("/game")
def game():
    """
    Render the main puzzle page.

    Handles:
      - Loading a selected puzzle (preloaded or user-created)
      - Generating a new puzzle if no ID is provided
    """
    username = request.args.get("username_new") or request.args.get("username_existing")
    puzzle_id = request.args.get("puzzle_id")
    difficulty = request.args.get("difficulty", "easy")

    preloaded_puzzles = load_preloaded_puzzles()
    user_puzzles = load_user_puzzles()

    # Decide which puzzle to use
    if puzzle_id and puzzle_id in preloaded_puzzles:
        puzzle_data = preloaded_puzzles[puzzle_id]
    elif puzzle_id and puzzle_id in user_puzzles:
        puzzle_data = user_puzzles[puzzle_id]
    else:
        # Generate a brand new puzzle
        size_str = request.args.get("board_size", "7")
        try:
            size = int(size_str)
        except ValueError:
            return jsonify({"error": f"Invalid board size '{size_str}'"}), 400

        my_game = Game(size)
        puzzle_data = my_game.generate_puzzle(easy=(difficulty == "easy"))

        # Pick a new numeric ID >= 1000 that doesn't collide
        existing_ids = set(preloaded_puzzles.keys()) | set(user_puzzles.keys())
        next_id_num = 1000
        while str(next_id_num) in existing_ids:
            next_id_num += 1
        new_id = str(next_id_num)

        # Save to Supabase
        save_user_puzzle(new_id, puzzle_data)
        puzzle_id = new_id

    # Prepare board for display
    size = len(puzzle_data["regions"])
    my_game = Game(size)
    my_game.latest_solution = puzzle_data.get("solution")

    board_data = [["☐" for _ in range(size)] for _ in range(size)]

    template_info = {
        "username": username,
        "title": my_game.title,
        "symbols": my_game.symbols,
        "board_id": puzzle_id,
        "board_size": size,
        "regions": puzzle_data["regions"],
        "board_data": board_data,
    }

    return render_template("game.html", info=template_info)


@app.route("/solve/<id>", methods=["POST"])
def process_results(id):
    """
    Validate a submitted puzzle solution and record timing stats.
    """
    try:
        data = request.json or {}

        # Extract grid entries ("row_col")
        board_data = {k: v for k, v in data.items() if "_" in k and k.count("_") == 1}
        solve_time = float(data.get("solve_time", 0))

        board_size = int(len(board_data) ** 0.5)
        board = [["☐" for _ in range(board_size)] for _ in range(board_size)]
        for k, v in board_data.items():
            try:
                r, c = map(int, k.split("_"))
                board[r][c] = v
            except ValueError:
                continue

        preloaded = load_preloaded_puzzles()
        user_puzzles = load_user_puzzles()

        # Merge preloaded + user puzzles for lookup
        all_puzzles = preloaded.copy()
        all_puzzles.update(user_puzzles)

        if id not in all_puzzles:
            return jsonify({"result": "Puzzle not found."}), 404

        puzzle_data = all_puzzles[id]

        if "solution" not in puzzle_data or "regions" not in puzzle_data:
            return jsonify({"result": f"Puzzle {id} missing required fields"}), 500

        solution = puzzle_data["solution"]
        regions = puzzle_data["regions"]

        my_game = Game(board_size)
        my_game.latest_solution = solution

        # Build queen_positions[col] = row
        queen_positions = [-1] * board_size
        for r in range(board_size):
            for c in range(board_size):
                if board[r][c] == "👑":
                    queen_positions[c] = r

        valid = my_game.validate_solution(queen_positions, regions)
        result = "Correct!" if valid else "Incorrect."

        if valid:
            record_solve_time(id, solve_time)

        avg_time = get_global_average_time()

        return jsonify(
            {
                "result": result,
                "user_time": solve_time,
                "average_time": avg_time,
            }
        )

    except Exception:
        print("❌ Error during submission:", traceback.format_exc())
        return jsonify({"result": "Server error."}), 500


@app.route("/hint/<id>", methods=["POST"])
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

    preloaded = load_preloaded_puzzles()
    user_puzzles = load_user_puzzles()
    puzzle_data = preloaded.get(id) or user_puzzles.get(id)

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
    # Local dev only; Vercel will ignore this block
    os.makedirs(DATA_DIR, exist_ok=True)
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, port=port)
