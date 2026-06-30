from __future__ import annotations
import argparse
import sys
from pathlib import Path
from app.board_parser import BoardParser
from app.board_solver import BoardSolver

def createSignMap(signs: list[dict]) -> dict:
    signMap = {}
    for sign in signs:
        signMap[tuple(sign["cells"])] = sign["type"]
    return signMap

def print_board(board: list[list[str]], signs: list[dict]) -> None:
    # signMap = createSignMap(signs)
    for row in range(len(board)):
        formatted_row = []
        for cell in range(len(board[row])):
            if board[row][cell] == "sun":
                formatted_row.append("☀️  (sun)")
            elif board[row][cell] == "moon":
                formatted_row.append("🌙 (moon)")
            else:
                formatted_row.append("⬜ (blank)")
        print(" | ".join(formatted_row))

def main() -> None:
    # Safely reconfigure standard streams to use UTF-8 on Windows consoles to print emojis without crashing
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Tango Board Solver Entrypoint")
    parser.add_argument(
        "image_path", 
        nargs="?", 
        default="board.png", 
        help="Path to the board image file (default: board.png)"
    )
    args = parser.parse_args()

    image_path = Path(args.image_path)
    if not image_path.exists():
        print(f"Error: Target image file not found at '{image_path}'", file=sys.stderr)
        sys.exit(1)

    print(f"--- Parsing Board Image: {image_path} ---")
    board_parser = BoardParser()
    try:
        parsed_result = board_parser.parse_image(image_path)
    except Exception as e:
        print(f"Failed to parse board image: {e}", file=sys.stderr)
        sys.exit(1)

    initial_board = parsed_result["board"]
    signs = parsed_result["signs"]

    print("\n[Initial Board]")
    print_board(initial_board, signs)
    print(f"\nDetected {len(signs)} equality '=' and difference 'x' sign constraints.")

    print("\n--- Solving Board Puzzle ---")
    solver = BoardSolver(initial_board, signs)
    solution = solver.solve()

    if solution["solved"]:
        print("\n\nPuzzle Solved Successfully!")
        print("\n[Final Board]")
        print_board(solution["board"], signs)
    else:
        print("\n\nCould not fully resolve the board with current rules.")
        print("\n[Partially Solved Board]")
        print_board(solution["board"], signs)

    print("\n[Deduction Trace Steps]")
    for idx, step in enumerate(solution["steps"], start=1):
        print(f"{idx:02d}. {step}")

if __name__ == "__main__":
    main()
