from flask import Flask, jsonify, request, render_template
import os
import sys
import json
import traceback
import requests

# ----- Supabase config -----
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

PUZZLES_TABLE = "puzzles"
TIMES_TABLE = "puzzle_times"

# ----- Import Game -----
BASE_DIR = os.path.dirname(__file__)
sys.path.append(BASE_DIR)
from helpers.Game import Game  # noqa: E402

app = Flask(__name__, static_url_path="", static_folder="static")


# ---------------- Supabase Helpers ---------------- #

def supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def get_latest_puzzle_id():
    """Fallback: ask Supabase for the most recently inserted puzzle."""
    url = f"{SUPABASE_URL}/rest/v1/{PUZZLES_TABLE}?select=id&order=id.desc&limit=1"
    resp = requests.get(url, headers=supabase_headers())

    print("Fallback fetch status:", resp.status_code, repr(resp.text))

    if resp.ok:
        try:
            latest = resp.json()[0]["id"]
            print("✅ Fallback puzzle ID:", latest)
            return latest
        except Exception as e:
            print("❌ Failed to parse fallback ID:", e)
    else:
        print("❌ Failed to fetch latest puzzle:", resp.text)

    return None


def save_user_puzzle(puzzle_data):
    """Insert puzzle and safely get its ID (with fallback)."""

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Supabase env vars missing")
        return None

    url = f"{SUPABASE_URL}/rest/v1/{PUZZLES_TABLE}"
    row = {
        "solution": puzzle_data["solution"],
        "regions": puzzle_data["regions"],
        "difficulty": puzzle_data.get("difficulty", "easy"),
    }

    print("📤 Inserting puzzle row:", json.dumps(row, indent=2))
    resp = requests.post(url, headers=supabase_headers(), json=row)
    print("📥 Supabase insert response:", resp.status_code, repr(resp.text))

    if not resp.ok:
        print("❌ Error during insert:", resp.text)
        return None

    # Try reading returned JSON
    try:
        inserted = resp.json()
        print("Inserted row returned:", inserted)
        return inserted[0]["id"]
    except Exception as e:
        print("⚠️ Insert returned no JSON. Using fallback.")
        return get_latest_puzzle_id()


def load_user_puzzles():
    """Load all puzzles."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {}

    url = f"{SUPABASE_URL}/rest/v1/{PUZZLES_TABLE}"
    params = {"select": "id,solution,regions,difficulty"}
    resp = requests.get(url, headers=supabase_headers(), params=params)

    if not resp.ok:
        print("Error loading puzzles:", resp.text)
        return {}

    puzzles = {}
    for row in resp.json():
        pid = str(row["id"])
        puzzles[pid] = {
            "solution": row["solution"],
            "regions": row["regions"],
            "difficulty": row.get("difficulty", "easy"),
        }
    return puzzles


def record_solve_time(puzzle_id, solve_time):
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Supabase env vars missing; skipping time log.")
        return

    url = f"{SUPABASE_URL}/rest/v1/{TIMES_TABLE}"
    row = {"puzzle_id": str(puzzle_id), "solve_time": float(solve_time)}
    resp = requests.post(url, headers=supabase_headers(), json=row)
    print("SAVE TIME RESPONSE:", resp.status_code, resp.text)


def get_global_average_time():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return "N/A"

    url = f"{SUPABASE_URL}/rest/v1/{TIMES_TABLE}"
    params = {"select": "solve_time"}
    resp = requests.get(url, headers=supabase_headers(), params=params)

    if not resp.ok:
        print("Error loading times:", resp.text)
        return "N/A"

    rows = resp.json()
    times = [float(r["solve_time"]) for r in rows]
    return round(sum(times) / len(times), 2) if times else "N/A"


# ---------------- Routes ---------------- #

@app.route("/")
def login():
    temp_game = Game()
    return render_template("index.html", title=temp_game.title)


@app.route("/game")
def game():
    username = request.args.get("username_new") or request.args.get("username_existing")
    difficulty = request.args.get("difficulty", "easy")

    size = int(request.args.get("board_size", "7"))

    # Generate puzzle
    my_game = Game(size)
    puzzle_data = my_game.generate_puzzle(easy=(difficulty == "easy"))

    # Save puzzle to Supabase
    puzzle_id = save_user_puzzle(puzzle_data)
    if puzzle_id is None:
        return jsonify({"error": "Failed to save puzzle"}), 500

    # Prepare template
    regions = puzzle_data["regions"]
    board_data = [["☐" for _ in range(size)] for _ in range(size)]

    template_info = {
        "username": username,
        "title": my_game.title,
        "symbols": my_game.symbols,
        "board_id": str(puzzle_id),
        "board_size": size,
        "regions": regions,
        "board_data": board_data,
    }

    return render_template("game.html", info=template_info)


@app.route("/solve/<id>", methods=["POST"])
def process_results(id):
    try:
        data = request.json or {}

        board_data = {k: v for k, v in data.items() if "_" in k}

        board_size = int(len(board_data) ** 0.5)
        board = [["☐" for _ in range(board_size)] for _ in range(board_size)]

        for k, v in board_data.items():
            r, c = map(int, k.split("_"))
            board[r][c] = v

        puzzles = load_user_puzzles()
        if id not in puzzles:
            return jsonify({"result": "Puzzle not found."}), 404

        puzzle = puzzles[id]
        solution = puzzle["solution"]
        regions = puzzle["regions"]

        my_game = Game(board_size)
        my_game.latest_solution = solution

        # Build queen positions
        queen_positions = [-1] * board_size
        for r in range(board_size):
            for c in range(board_size):
                if board[r][c] == "👑":
                    queen_positions[c] = r

        valid = my_game.validate_solution(queen_positions, regions)
        result = "Correct!" if valid else "Incorrect."

        if valid:
            record_solve_time(id, float(data.get("solve_time", 0)))

        avg_time = get_global_average_time()

        return jsonify({"result": result, "user_time": data.get("solve_time"), "average_time": avg_time})

    except Exception:
        print("❌ Error:", traceback.format_exc())
        return jsonify({"result": "Server error."}), 500


@app.route("/hint/<id>", methods=["POST"])
def give_hint(id):
    data = request.json or {}
    board_data = {k: v for k, v in data.items() if "_" in k}

    board_size = int(len(board_data) ** 0.5)
    board = [["☐" for _ in range(board_size)] for _ in range(board_size)]

    for k, v in board_data.items():
        r, c = map(int, k.split("_"))
        board[r][c] = v

    puzzles = load_user_puzzles()
    if id not in puzzles:
        return jsonify({"error": "Puzzle not found"}), 404

    puzzle = puzzles[id]
    my_game = Game(board_size)
    my_game.latest_solution = puzzle["solution"]

    hint = my_game.get_hint(board, puzzle["regions"])
    if hint:
        return jsonify({"row": hint[0], "col": hint[1]})

    return jsonify({"message": "No valid hint found"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, port=port)
