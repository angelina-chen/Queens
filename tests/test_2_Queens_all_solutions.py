import unittest
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)

Queens = None
if not Queens:
    from queens import Queens as Queens 

class Test_Queens_n_queens(unittest.TestCase):
  def setUp(self):
      self.solutions_3=[]
      self.solutions_4=[[1, 3, 0, 2], [2, 0, 3, 1]]
      self.solutions_5=[[0, 2, 4, 1, 3], [0, 3, 1, 4, 2], [1, 3, 0, 2, 4], [1, 4, 2, 0, 3], [2, 0, 3, 1, 4], [2, 4, 1, 3, 0], [3, 0, 2, 4, 1], [3, 1, 4, 2, 0], [4, 1, 3, 0, 2], [4, 2, 0, 3, 1]]
      self.solutions_6=[[1, 3, 5, 0, 2, 4], [2, 5, 1, 4, 0, 3], [3, 0, 4, 1, 5, 2], [4, 2, 0, 5, 3, 1]]
      self.solutions_8=[[0, 4, 7, 5, 2, 6, 1, 3], [0, 5, 7, 2, 6, 3, 1, 4], [0, 6, 3, 5, 7, 1, 4, 2], [0, 6, 4, 7, 1, 3, 5, 2], [1, 3, 5, 7, 2, 0, 6, 4], [1, 4, 6, 0, 2, 7, 5, 3], [1, 4, 6, 3, 0, 7, 5, 2], 
                  [1, 5, 0, 6, 3, 7, 2, 4], [1, 5, 7, 2, 0, 3, 6, 4], [1, 6, 2, 5, 7, 4, 0, 3], [1, 6, 4, 7, 0, 3, 5, 2], [1, 7, 5, 0, 2, 4, 6, 3], [2, 0, 6, 4, 7, 1, 3, 5], [2, 4, 1, 7, 0, 6, 3, 5], 
                  [2, 4, 1, 7, 5, 3, 6, 0], [2, 4, 6, 0, 3, 1, 7, 5], [2, 4, 7, 3, 0, 6, 1, 5], [2, 5, 1, 4, 7, 0, 6, 3], [2, 5, 1, 6, 0, 3, 7, 4], [2, 5, 1, 6, 4, 0, 7, 3], [2, 5, 3, 0, 7, 4, 6, 1], 
                  [2, 5, 3, 1, 7, 4, 6, 0], [2, 5, 7, 0, 3, 6, 4, 1], [2, 5, 7, 0, 4, 6, 1, 3], [2, 5, 7, 1, 3, 0, 6, 4], [2, 6, 1, 7, 4, 0, 3, 5], [2, 6, 1, 7, 5, 3, 0, 4], [2, 7, 3, 6, 0, 5, 1, 4],
                  [3, 0, 4, 7, 1, 6, 2, 5], [3, 0, 4, 7, 5, 2, 6, 1], [3, 1, 4, 7, 5, 0, 2, 6], [3, 1, 6, 2, 5, 7, 0, 4], [3, 1, 6, 2, 5, 7, 4, 0], [3, 1, 6, 4, 0, 7, 5, 2], [3, 1, 7, 4, 6, 0, 2, 5], 
                  [3, 1, 7, 5, 0, 2, 4, 6], [3, 5, 0, 4, 1, 7, 2, 6], [3, 5, 7, 1, 6, 0, 2, 4], [3, 5, 7, 2, 0, 6, 4, 1], [3, 6, 0, 7, 4, 1, 5, 2], [3, 6, 2, 7, 1, 4, 0, 5], [3, 6, 4, 1, 5, 0, 2, 7], 
                  [3, 6, 4, 2, 0, 5, 7, 1], [3, 7, 0, 2, 5, 1, 6, 4], [3, 7, 0, 4, 6, 1, 5, 2], [3, 7, 4, 2, 0, 6, 1, 5], [4, 0, 3, 5, 7, 1, 6, 2], [4, 0, 7, 3, 1, 6, 2, 5], [4, 0, 7, 5, 2, 6, 1, 3], 
                  [4, 1, 3, 5, 7, 2, 0, 6], [4, 1, 3, 6, 2, 7, 5, 0], [4, 1, 5, 0, 6, 3, 7, 2], [4, 1, 7, 0, 3, 6, 2, 5], [4, 2, 0, 5, 7, 1, 3, 6], [4, 2, 0, 6, 1, 7, 5, 3], [4, 2, 7, 3, 6, 0, 5, 1],
                  [4, 6, 0, 2, 7, 5, 3, 1], [4, 6, 0, 3, 1, 7, 5, 2], [4, 6, 1, 3, 7, 0, 2, 5], [4, 6, 1, 5, 2, 0, 3, 7], [4, 6, 1, 5, 2, 0, 7, 3], [4, 6, 3, 0, 2, 7, 5, 1], [4, 7, 3, 0, 2, 5, 1, 6], 
                  [4, 7, 3, 0, 6, 1, 5, 2], [5, 0, 4, 1, 7, 2, 6, 3], [5, 1, 6, 0, 2, 4, 7, 3], [5, 1, 6, 0, 3, 7, 4, 2], [5, 2, 0, 6, 4, 7, 1, 3], [5, 2, 0, 7, 3, 1, 6, 4], [5, 2, 0, 7, 4, 1, 3, 6], 
                  [5, 2, 4, 6, 0, 3, 1, 7], [5, 2, 4, 7, 0, 3, 1, 6], [5, 2, 6, 1, 3, 7, 0, 4], [5, 2, 6, 1, 7, 4, 0, 3], [5, 2, 6, 3, 0, 7, 1, 4], [5, 3, 0, 4, 7, 1, 6, 2], [5, 3, 1, 7, 4, 6, 0, 2], 
                  [5, 3, 6, 0, 2, 4, 1, 7], [5, 3, 6, 0, 7, 1, 4, 2], [5, 7, 1, 3, 0, 6, 4, 2], [6, 0, 2, 7, 5, 3, 1, 4], [6, 1, 3, 0, 7, 4, 2, 5], [6, 1, 5, 2, 0, 3, 7, 4], [6, 2, 0, 5, 7, 4, 1, 3], 
                  [6, 2, 7, 1, 4, 0, 5, 3], [6, 3, 1, 4, 7, 0, 2, 5], [6, 3, 1, 7, 5, 0, 2, 4], [6, 4, 2, 0, 5, 7, 1, 3], [7, 1, 3, 0, 6, 4, 2, 5], [7, 1, 4, 2, 0, 6, 3, 5], [7, 2, 0, 5, 1, 4, 6, 3], [7, 3, 0, 2, 5, 1, 6, 4]]
  
  def test_1(self):
    """4 queens, num_sol=2"""
    n = 4
    num_sol = 2
    queens=Queens(n)
    queens.solve(num_sol)
    actual=queens.all_solutions
    expected = self.solutions_4
    self.assertEqual(len(actual), min(num_sol, len(expected)))
    for solution in actual:
      self.assertIn(solution, expected, f"{solution} should be one of the calculated solutions")
  
  def test_2(self):
    """4 queens, num_sol=1"""
    n = 4
    num_sol = 1
    queens=Queens(n)
    queens.solve(num_sol)
    actual=queens.all_solutions
    expected = self.solutions_4
    self.assertEqual(len(actual), min(num_sol, len(expected)))
    for solution in actual:
      self.assertIn(solution, expected, f"{solution} should be one of the calculated solutions")
  
  def test_3(self):
    """4 queens, num_sol=29"""
    n = 4
    num_sol = 29
    queens=Queens(n)
    queens.solve(num_sol)
    actual=queens.all_solutions
    expected = self.solutions_4
    self.assertEqual(len(actual), min(num_sol, len(expected)))
    for solution in actual:
      self.assertIn(solution, expected, f"{solution} should be one of the calculated solutions")
  
  def test_4(self):
    """8 queens, num_sol=50"""
    n = 8
    num_sol = 50
    queens=Queens(n)
    queens.solve(num_sol)
    actual=queens.all_solutions
    expected = self.solutions_8
    self.assertEqual(len(actual), min(num_sol, len(expected)))
    for solution in actual:
      self.assertIn(solution, expected, f"{solution} should be one of the calculated solutions")

  def test_5(self):
    """8 queens, num_sol=1000"""
    n = 8
    num_sol = 1000
    queens=Queens(n)
    queens.solve(num_sol)
    actual=queens.all_solutions
    expected = self.solutions_8
    self.assertEqual(len(actual), min(num_sol, len(expected)))
    for solution in actual:
      self.assertIn(solution, expected, f"{solution} should be one of the calculated solutions")

  def test_6(self):
    """8 queens, num_sol=1"""
    n = 8
    num_sol = 1
    queens=Queens(n)
    queens.solve(num_sol)
    actual=queens.all_solutions
    expected = self.solutions_8
    self.assertEqual(len(actual), min(num_sol, len(expected)))
    for solution in actual:
      self.assertIn(solution, expected, f"{solution} should be one of the calculated solutions")

  def test_7(self):
    """6 queens, num_sol=1"""
    n = 6
    num_sol = 1
    queens=Queens(n)
    queens.solve(num_sol)
    actual=queens.all_solutions
    expected = self.solutions_6
    self.assertEqual(len(actual), min(num_sol, len(expected)))
    for solution in actual:
      self.assertIn(solution, expected, f"{solution} should be one of the calculated solutions")

  def test_8(self):
    """6 queens, num_sol=500"""
    n = 6
    num_sol = 500
    queens=Queens(n)
    queens.solve(num_sol)
    actual=queens.all_solutions
    expected = self.solutions_6
    self.assertEqual(len(actual), min(num_sol, len(expected)))
    for solution in actual:
      self.assertIn(solution, expected, f"{solution} should be one of the calculated solutions")

  def test_9(self):
    """5 queens, num_sol=5"""
    n = 5
    num_sol = 5
    queens=Queens(n)
    queens.solve(num_sol)
    actual=queens.all_solutions
    expected = self.solutions_5
    self.assertEqual(len(actual), min(num_sol, len(expected)))
    for solution in actual:
      self.assertIn(solution, expected, f"{solution} should be one of the calculated solutions")

  def test_10(self):
    """5 queens, num_sol=555"""
    n = 5
    num_sol = 555
    queens=Queens(n)
    queens.solve(num_sol)
    actual=queens.all_solutions
    expected = self.solutions_5
    self.assertEqual(len(actual), min(num_sol, len(expected)))
    for solution in actual:
      self.assertIn(solution, expected, f"{solution} should be one of the calculated solutions")

  def test_11(self):
    """3 queens, num_sol=10"""
    n = 3
    num_sol = 10
    queens=Queens(n)
    queens.solve(num_sol)
    actual=queens.all_solutions
    expected = self.solutions_3
    self.assertEqual(len(actual), min(num_sol, len(expected)))
    for solution in actual:
      self.assertIn(solution, expected, f"{solution} should be one of the calculated solutions")

  def test_12(self):
    """9, 10, 11, 12 queens"""
    ns = [9, 10, 11, 12]
    num_sols = [352, 724, 2680, 14200]

    for n, num_sol in zip(ns, num_sols):
        queens = Queens(n)
        actual = queens.solve(num_sol)
        expected = num_sol
        self.assertEqual(len(actual), expected)

if __name__ == "__main__":
    unittest.main(verbosity=2)
