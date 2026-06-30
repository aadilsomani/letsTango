from __future__ import annotations
from typing import List, Tuple, Dict, Any

class BoardSolver:
    def __init__(self, board: List[List[str]], signs: List[Dict[str, Any]]) -> None:
        self.grid_size = len(board)
        # Create a mutable copy of the board
        self.board = [row[:] for row in board]
        self.signs = signs
        self.steps: List[str] = []

    def solve(self) -> Dict[str, Any]:
        """
        Solves the game iteratively using registered rule strategies.
        Returns a dictionary with the solved board, a boolean indicating if it is solved,
        and the steps taken to solve it.
        """
        strategies = [
            self.solve_consecutive_symbols,
            self.solve_balanced_counts,
            self.solve_equality_signs,
            self.solve_difference_signs,
        ]
        
        changed = True
        iterations = 0
        max_iterations = 100  # Safety fallback to prevent infinite loops
        
        while changed and iterations < max_iterations:
            changed = False
            iterations += 1
            for strategy in strategies:
                if strategy():
                    changed = True
                    # Reset the strategy loop to apply simpler/earlier strategies first
                    break
        
        is_solved = not any(self.board[r][c] == "blank" for r in range(self.grid_size) for c in range(self.grid_size))
        return {
            "board": self.board,
            "solved": is_solved,
            "steps": self.steps
        }

    def solve_consecutive_symbols(self) -> bool:
        """
        Enforce that at most 2 consecutive identical symbols are allowed in a row/column.
        For example:
        - [S, S, _] -> [S, S, M]
        - [_, S, S] -> [M, S, S]
        - [S, _, S] -> [S, M, S]
        Returns True if any cells were updated.
        """
        changed = False
        
        def opponent(symbol: str) -> str:
            return "moon" if symbol == "sun" else "sun"

        # Walk rows
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if self.board[r][c] != "blank":
                    continue
                
                # Check pattern XX_ (left of cell)
                if c >= 2:
                    if self.board[r][c - 1] != "blank" and self.board[r][c - 1] == self.board[r][c - 2]:
                        self.board[r][c] = opponent(self.board[r][c - 1])
                        self.steps.append(
                            f"Filled ({r}, {c}) with '{self.board[r][c]}' to avoid 3 consecutive '{self.board[r][c-1]}' in row {r} (cols {c-2} to {c})"
                        )
                        return True
                
                # Check pattern _XX (right of cell)
                if c <= self.grid_size - 3:
                    if self.board[r][c + 1] != "blank" and self.board[r][c + 1] == self.board[r][c + 2]:
                        self.board[r][c] = opponent(self.board[r][c + 1])
                        self.steps.append(
                            f"Filled ({r}, {c}) with '{self.board[r][c]}' to avoid 3 consecutive '{self.board[r][c+1]}' in row {r} (cols {c} to {c+2})"
                        )
                        return True
                
                # Check pattern X_X (middle)
                if c >= 1 and c <= self.grid_size - 2:
                    if self.board[r][c - 1] != "blank" and self.board[r][c - 1] == self.board[r][c + 1]:
                        self.board[r][c] = opponent(self.board[r][c - 1])
                        self.steps.append(
                            f"Filled ({r}, {c}) with '{self.board[r][c]}' to avoid 3 consecutive '{self.board[r][c-1]}' in row {r} (cols {c-1} to {c+1})"
                        )
                        return True

        # Walk columns
        for c in range(self.grid_size):
            for r in range(self.grid_size):
                if self.board[r][c] != "blank":
                    continue
                
                # Check pattern XX_ (above cell)
                if r >= 2:
                    if self.board[r - 1][c] != "blank" and self.board[r - 1][c] == self.board[r - 2][c]:
                        self.board[r][c] = opponent(self.board[r - 1][c])
                        self.steps.append(
                            f"Filled ({r}, {c}) with '{self.board[r][c]}' to avoid 3 consecutive '{self.board[r-1][c]}' in col {c} (rows {r-2} to {r})"
                        )
                        return True
                
                # Check pattern _XX (below cell)
                if r <= self.grid_size - 3:
                    if self.board[r + 1][c] != "blank" and self.board[r + 1][c] == self.board[r + 2][c]:
                        self.board[r][c] = opponent(self.board[r + 1][c])
                        self.steps.append(
                            f"Filled ({r}, {c}) with '{self.board[r][c]}' to avoid 3 consecutive '{self.board[r+1][c]}' in col {c} (rows {r} to {r+2})"
                        )
                        return True
                
                # Check pattern X_X (middle)
                if r >= 1 and r <= self.grid_size - 2:
                    if self.board[r - 1][c] != "blank" and self.board[r - 1][c] == self.board[r + 1][c]:
                        self.board[r][c] = opponent(self.board[r - 1][c])
                        self.steps.append(
                            f"Filled ({r}, {c}) with '{self.board[r][c]}' to avoid 3 consecutive '{self.board[r-1][c]}' in col {c} (rows {r-1} to {r+1})"
                        )
                        return True

        return False

    def solve_balanced_counts(self) -> bool:
        """
        Each row and column must contain exactly grid_size // 2 of each symbol.
        Returns True if any cells were updated.
        """
        target = self.grid_size // 2

        # Check rows
        for r in range(self.grid_size):
            suns = sum(1 for c in range(self.grid_size) if self.board[r][c] == "sun")
            moons = sum(1 for c in range(self.grid_size) if self.board[r][c] == "moon")
            
            if suns == target and moons < target:
                filled = False
                for c in range(self.grid_size):
                    if self.board[r][c] == "blank":
                        self.board[r][c] = "moon"
                        self.steps.append(f"Filled ({r}, {c}) with 'moon' via balanced row {r} (already has {target} suns)")
                        filled = True
                if filled:
                    return True
            
            if moons == target and suns < target:
                filled = False
                for c in range(self.grid_size):
                    if self.board[r][c] == "blank":
                        self.board[r][c] = "sun"
                        self.steps.append(f"Filled ({r}, {c}) with 'sun' via balanced row {r} (already has {target} moons)")
                        filled = True
                if filled:
                    return True

        # Check columns
        for c in range(self.grid_size):
            suns = sum(1 for r in range(self.grid_size) if self.board[r][c] == "sun")
            moons = sum(1 for r in range(self.grid_size) if self.board[r][c] == "moon")
            
            if suns == target and moons < target:
                filled = False
                for r in range(self.grid_size):
                    if self.board[r][c] == "blank":
                        self.board[r][c] = "moon"
                        self.steps.append(f"Filled ({r}, {c}) with 'moon' via balanced col {c} (already has {target} suns)")
                        filled = True
                if filled:
                    return True
            
            if moons == target and suns < target:
                filled = False
                for r in range(self.grid_size):
                    if self.board[r][c] == "blank":
                        self.board[r][c] = "sun"
                        self.steps.append(f"Filled ({r}, {c}) with 'sun' via balanced col {c} (already has {target} moons)")
                        filled = True
                if filled:
                    return True

        return False

    def solve_equality_signs(self) -> bool:
        """
        Enforce '=' equality sign.
        Returns True if any cells were updated.
        """
        for sign in self.signs:
            if sign["type"] != "=":
                continue
            cells = sign["cells"]
            # Convert list of lists to list of tuples if needed
            r1, c1 = cells[0][0], cells[0][1]
            r2, c2 = cells[1][0], cells[1][1]
            
            v1 = self.board[r1][c1]
            v2 = self.board[r2][c2]
            
            if v1 != "blank" and v2 == "blank":
                self.board[r2][c2] = v1
                self.steps.append(f"Filled ({r2}, {c2}) with '{v1}' via '=' sign from ({r1}, {c1})")
                return True
            if v2 != "blank" and v1 == "blank":
                self.board[r1][c1] = v2
                self.steps.append(f"Filled ({r1}, {c1}) with '{v2}' via '=' sign from ({r2}, {c2})")
                return True
        return False

    def solve_difference_signs(self) -> bool:
        """
        Enforce 'x' difference sign.
        Returns True if any cells were updated.
        """
        def opponent(symbol: str) -> str:
            return "moon" if symbol == "sun" else "sun"

        for sign in self.signs:
            if sign["type"] != "x":
                continue
            cells = sign["cells"]
            r1, c1 = cells[0][0], cells[0][1]
            r2, c2 = cells[1][0], cells[1][1]
            
            v1 = self.board[r1][c1]
            v2 = self.board[r2][c2]
            
            if v1 != "blank" and v2 == "blank":
                self.board[r2][c2] = opponent(v1)
                self.steps.append(f"Filled ({r2}, {c2}) with '{self.board[r2][c2]}' via 'x' sign from ({r1}, {c1})")
                return True
            if v2 != "blank" and v1 == "blank":
                self.board[r1][c1] = opponent(v2)
                self.steps.append(f"Filled ({r1}, {c1}) with '{self.board[r1][c1]}' via 'x' sign from ({r2}, {c2})")
                return True
        return False
