import unittest
from app.board_solver import BoardSolver

class BoardSolverTests(unittest.TestCase):
    def test_solve_consecutive_symbols(self):
        # Row test: S S _ -> S S M
        board = [
            ["sun", "sun", "blank", "blank", "blank", "blank"],
            ["blank"] * 6,
            ["blank"] * 6,
            ["blank"] * 6,
            ["blank"] * 6,
            ["blank"] * 6,
        ]
        solver = BoardSolver(board, [])
        changed = solver.solve_consecutive_symbols()
        self.assertTrue(changed)
        self.assertEqual(solver.board[0][2], "moon")

        # Col test: M _ M -> M S M
        board = [
            ["blank"] * 6,
            ["blank"] * 6,
            ["blank"] * 6,
            ["blank"] * 6,
            ["blank"] * 6,
            ["blank"] * 6,
        ]
        board[0][1] = "moon"
        board[1][1] = "blank"
        board[2][1] = "moon"
        solver = BoardSolver(board, [])
        changed = solver.solve_consecutive_symbols()
        self.assertTrue(changed)
        self.assertEqual(solver.board[1][1], "sun")

    def test_solve_balanced_counts(self):
        board = [
            ["sun", "sun", "sun", "blank", "blank", "blank"],
            ["blank"] * 6,
            ["blank"] * 6,
            ["blank"] * 6,
            ["blank"] * 6,
            ["blank"] * 6,
        ]
        solver = BoardSolver(board, [])
        changed = solver.solve_balanced_counts()
        self.assertTrue(changed)
        self.assertEqual(solver.board[0][3], "moon")
        self.assertEqual(solver.board[0][4], "moon")
        self.assertEqual(solver.board[0][5], "moon")

    def test_solve_equality_signs(self):
        board = [
            ["sun", "blank", "blank", "blank", "blank", "blank"],
            ["blank"] * 6,
            ["blank"] * 6,
            ["blank"] * 6,
            ["blank"] * 6,
            ["blank"] * 6,
        ]
        signs = [{"type": "=", "cells": [[0, 0], [0, 1]]}]
        solver = BoardSolver(board, signs)
        changed = solver.solve_equality_signs()
        self.assertTrue(changed)
        self.assertEqual(solver.board[0][1], "sun")

    def test_solve_difference_signs(self):
        board = [
            ["sun", "blank", "blank", "blank", "blank", "blank"],
            ["blank"] * 6,
            ["blank"] * 6,
            ["blank"] * 6,
            ["blank"] * 6,
            ["blank"] * 6,
        ]
        signs = [{"type": "x", "cells": [[0, 0], [0, 1]]}]
        solver = BoardSolver(board, signs)
        changed = solver.solve_difference_signs()
        self.assertTrue(changed)
        self.assertEqual(solver.board[0][1], "moon")

    def test_solve_complete_tango_board(self):
        board = [
            ['blank', 'blank', 'blank', 'blank', 'blank', 'blank'],
            ['blank', 'sun', 'sun', 'blank', 'blank', 'blank'],
            ['blank', 'sun', 'moon', 'blank', 'blank', 'blank'],
            ['blank', 'blank', 'blank', 'sun', 'sun', 'blank'],
            ['blank', 'blank', 'blank', 'sun', 'moon', 'blank'],
            ['blank', 'blank', 'blank', 'blank', 'blank', 'blank']
        ]
        signs = [
            {'cells': [[2, 3], [2, 4]], 'type': 'x'},
            {'cells': [[0, 3], [1, 3]], 'type': 'x'},
            {'cells': [[0, 0], [1, 0]], 'type': 'x'},
            {'cells': [[5, 3], [5, 4]], 'type': '='},
            {'cells': [[4, 5], [5, 5]], 'type': '='},
            {'cells': [[4, 2], [5, 2]], 'type': '='},
            {'cells': [[3, 1], [3, 2]], 'type': '='},
            {'cells': [[2, 5], [3, 5]], 'type': '='},
            {'cells': [[2, 0], [3, 0]], 'type': '='},
            {'cells': [[0, 1], [0, 2]], 'type': '='}
        ]
        
        solver = BoardSolver(board, signs)
        result = solver.solve()
        
        print("\nSolved board:")
        for r in result["board"]:
            print(r)
        
        print("\nSteps taken:")
        for step in result["steps"]:
            print(step)
            
        self.assertTrue(result["solved"])

if __name__ == "__main__":
    unittest.main()
