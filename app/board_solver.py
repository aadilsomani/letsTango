from __future__ import annotations
from typing import List, Tuple, Dict, Any

from app.board_parser import BoardParser

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
            self.solve_2_against_edge,
            self.solve_balanced_counts,
            self.solve_adjacent_to_equality_signs,
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
    
    @staticmethod
    def opponent(symbol: str) -> str:
        return "moon" if symbol == "sun" else "sun"
    
    def solve_adjacent_to_equality_signs(self) -> bool:
        """
        If an '=' sign connects two cells, propagate known values to the other linked
        cell, and if a nearby cell already holds a value, fill the sign-linked cells
        with the opposite symbol to avoid local conflicts.
        """
        for sign in self.signs:
            if sign["type"] != "=":
                continue

            cell1, cell2 = sign["cells"]
            r1, c1 = cell1
            r2, c2 = cell2

            v1 = self.board[r1][c1]
            v2 = self.board[r2][c2]

            if v1 != "blank" and v2 == "blank":
                self.board[r2][c2] = v1
                if c1 == c2 and c1 + 1 < self.grid_size and self.board[r2][c1 + 1] == "blank":
                    self.board[r2][c1 + 1] = v1
                self.steps.append(
                    f"Filled ({r2}, {c2}) with '{v1}' via '=' sign from ({r1}, {c1})"
                )
                return True

            if v2 != "blank" and v1 == "blank":
                self.board[r1][c1] = v2
                if c1 == c2 and c1 + 1 < self.grid_size and self.board[r1][c1 + 1] == "blank":
                    self.board[r1][c1 + 1] = v2
                self.steps.append(
                    f"Filled ({r1}, {c1}) with '{v2}' via '=' sign from ({r2}, {c2})"
                )
                return True

            if r1 == r2:
                row = r1
                if c1 > 0 and self.board[row][c1 - 1] != "blank":
                    value = self.opponent(self.board[row][c1 - 1])
                    changed = False
                    if self.board[row][c1] == "blank":
                        self.board[row][c1] = value
                        changed = True
                    if self.board[row][c2] == "blank":
                        self.board[row][c2] = value
                        changed = True
                    if changed:
                        self.steps.append(
                            f"Filled ({row}, {c1}) and ({row}, {c2}) with '{value}' due to '=' sign and adjacent cell at ({row}, {c1 - 1})"
                        )
                        return True

                if c2 < self.grid_size - 1 and self.board[row][c2 + 1] != "blank":
                    value = self.opponent(self.board[row][c2 + 1])
                    changed = False
                    if self.board[row][c1] == "blank":
                        self.board[row][c1] = value
                        changed = True
                    if self.board[row][c2] == "blank":
                        self.board[row][c2] = value
                        changed = True
                    if changed:
                        self.steps.append(
                            f"Filled ({row}, {c1}) and ({row}, {c2}) with '{value}' due to '=' sign and adjacent cell at ({row}, {c2 + 1})"
                        )
                        return True

            elif c1 == c2:
                col = c1
                if r1 > 0 and self.board[r1 - 1][col] != "blank":
                    value = self.opponent(self.board[r1 - 1][col])
                    changed = False
                    if self.board[r1][col] == "blank":
                        self.board[r1][col] = value
                        changed = True
                    if self.board[r2][col] == "blank":
                        self.board[r2][col] = value
                        changed = True
                    if changed:
                        self.steps.append(
                            f"Filled ({r1}, {col}) and ({r2}, {col}) with '{value}' due to '=' sign and adjacent cell at ({r1 - 1}, {col})"
                        )
                        return True

                if r2 < self.grid_size - 1 and self.board[r2 + 1][col] != "blank":
                    value = self.opponent(self.board[r2 + 1][col])
                    changed = False
                    if self.board[r1][col] == "blank":
                        self.board[r1][col] = value
                        changed = True
                    if self.board[r2][col] == "blank":
                        self.board[r2][col] = value
                        changed = True
                    if changed:
                        self.steps.append(
                            f"Filled ({r1}, {col}) and ({r2}, {col}) with '{value}' due to '=' sign and adjacent cell at ({r2 + 1}, {col})"
                        )
                        return True

        return False

    def solve_same_on_each_end(self) -> bool:
        """
        Enforce that if a row/column has the same symbol at both ends, the adjacents must be the opposite symbol.
        For example:
        - [S, _, _, _, _, S] -> [S, M, _, _, M, S]
        Returns True if any cells were updated.
        """
        # Check rows
        for r in range(self.grid_size):
            if self.board[r][0] != "blank" and self.board[r][0] == self.board[r][self.grid_size - 1]:
                symbol = self.opponent(self.board[r][0])
                if self.board[r][1] == "blank":
                    self.board[r][1] = symbol
                    self.steps.append(f"Filled ({r}, 1) with '{symbol}' because row {r} has same symbols at both ends")
                    return True
                if self.board[r][self.grid_size - 2] == "blank":
                    self.board[r][self.grid_size - 2] = symbol
                    self.steps.append(f"Filled ({r}, {self.grid_size - 2}) with '{symbol}' because row {r} has same symbols at both ends")
                    return True

        # Check columns
        for c in range(self.grid_size):
            if self.board[0][c] != "blank" and self.board[0][c] == self.board[self.grid_size - 1][c]:
                symbol = self.opponent(self.board[0][c])
                if self.board[1][c] == "blank":
                    self.board[1][c] = symbol
                    self.steps.append(f"Filled (1, {c}) with '{symbol}' because col {c} has same symbols at both ends")
                    return True
                if self.board[self.grid_size - 2][c] == "blank":
                    self.board[self.grid_size - 2][c] = symbol
                    self.steps.append(f"Filled ({self.grid_size - 2}, {c}) with '{symbol}' because col {c} has same symbols at both ends")
                    return True

        return False

    def solve_2_against_edge(self) -> bool:
        """
        Enforce that if a row/column has 2 identical symbols at one end of a row or column,
        the opposite end must be the opposite symbol.
        For example:
        - [S, S, M, _, _, _] -> [S, S, M, _, _, M]
        
        Returns True if any cells were updated.
        """
        # Check rows
        for r in range(self.grid_size):
            if self.board[r][0] != "blank" and self.board[r][0] == self.board[r][1]:
                if self.board[r][self.grid_size - 1] == "blank":
                    symbol = self.opponent(self.board[r][0])
                    self.board[r][self.grid_size - 1] = symbol
                    self.steps.append(
                        f"Filled ({r}, {self.grid_size - 1}) with '{symbol}' because row {r} starts with two '{self.board[r][0]}'"
                    )
                    return True
            if self.board[r][self.grid_size - 1] != "blank" and self.board[r][self.grid_size - 1] == self.board[r][self.grid_size - 2]:
                if self.board[r][0] == "blank":
                    symbol = self.opponent(self.board[r][self.grid_size - 1])
                    self.board[r][0] = symbol
                    self.steps.append(
                        f"Filled ({r}, 0) with '{symbol}' because row {r} ends with two '{self.board[r][self.grid_size - 1]}'"
                    )
                    return True

        # Check columns
        for c in range(self.grid_size):
            if self.board[0][c] != "blank" and self.board[0][c] == self.board[1][c]:
                if self.board[self.grid_size - 1][c] == "blank":
                    symbol = self.opponent(self.board[0][c])
                    self.board[self.grid_size - 1][c] = symbol
                    self.steps.append(
                        f"Filled ({self.grid_size - 1}, {c}) with '{symbol}' because col {c} starts with two '{self.board[0][c]}'"
                    )
                    return True
            if self.board[self.grid_size - 1][c] != "blank" and self.board[self.grid_size - 1][c] == self.board[self.grid_size - 2][c]:
                if self.board[0][c] == "blank":
                    symbol = self.opponent(self.board[self.grid_size - 1][c])
                    self.board[0][c] = symbol
                    self.steps.append(
                        f"Filled (0, {c}) with '{symbol}' because col {c} ends with two '{self.board[self.grid_size - 1][c]}'"
                    )
                    return True

        return False

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

        # Walk rows
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if self.board[r][c] != "blank":
                    continue
                
                # Check pattern XX_ (left of cell)
                if c >= 2:
                    if self.board[r][c - 1] != "blank" and self.board[r][c - 1] == self.board[r][c - 2]:
                        self.board[r][c] = self.opponent(self.board[r][c - 1])
                        self.steps.append(
                            f"Filled ({r}, {c}) with '{self.board[r][c]}' to avoid 3 consecutive '{self.board[r][c-1]}' in row {r} (cols {c-2} to {c})"
                        )
                        return True
                
                # Check pattern _XX (right of cell)
                if c <= self.grid_size - 3:
                    if self.board[r][c + 1] != "blank" and self.board[r][c + 1] == self.board[r][c + 2]:
                        self.board[r][c] = self.opponent(self.board[r][c + 1])
                        self.steps.append(
                            f"Filled ({r}, {c}) with '{self.board[r][c]}' to avoid 3 consecutive '{self.board[r][c+1]}' in row {r} (cols {c} to {c+2})"
                        )
                        return True
                
                # Check pattern X_X (middle)
                if c >= 1 and c <= self.grid_size - 2:
                    if self.board[r][c - 1] != "blank" and self.board[r][c - 1] == self.board[r][c + 1]:
                        self.board[r][c] = self.opponent(self.board[r][c - 1])
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
                        self.board[r][c] = self.opponent(self.board[r - 1][c])
                        self.steps.append(
                            f"Filled ({r}, {c}) with '{self.board[r][c]}' to avoid 3 consecutive '{self.board[r-1][c]}' in col {c} (rows {r-2} to {r})"
                        )
                        return True
                
                # Check pattern _XX (below cell)
                if r <= self.grid_size - 3:
                    if self.board[r + 1][c] != "blank" and self.board[r + 1][c] == self.board[r + 2][c]:
                        self.board[r][c] = self.opponent(self.board[r + 1][c])
                        self.steps.append(
                            f"Filled ({r}, {c}) with '{self.board[r][c]}' to avoid 3 consecutive '{self.board[r+1][c]}' in col {c} (rows {r} to {r+2})"
                        )
                        return True
                
                # Check pattern X_X (middle)
                if r >= 1 and r <= self.grid_size - 2:
                    if self.board[r - 1][c] != "blank" and self.board[r - 1][c] == self.board[r + 1][c]:
                        self.board[r][c] = self.opponent(self.board[r - 1][c])
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

if __name__ == "__main__":
    board = BoardParser().parse_image("boards/IMG_1308.png")
    solver = BoardSolver(board["board"], board["signs"])
    solver.solve()
    print(solver.board)