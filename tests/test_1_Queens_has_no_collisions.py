import unittest
import sys
import os

# Get path to project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')

# Path to your http/ directory, which contains queens.py
http_dir = os.path.join(project_root, 'http')

# Add http/ to module search path
sys.path.append(http_dir)

# Import Queens from http/queens.py
from queens import Queens

class Test_Queens_has_collision(unittest.TestCase):

  def test_1(self):
    """No conflicts - 1x1"""
    board = [0]
    val = Queens(1).has_collision(board, 0)
    self.assertFalse(val) #
  
  def test_2(self):
    """No conflicts - 8x8, current = 2"""
    board = [3, 6, 4, -1, -1, -1, -1, -1]
    val = Queens(8).has_collision(board, 2)
    self.assertFalse(val)

  def test_3(self):
    """No conflicts - 8x8, current = 7"""
    board = [4, 0, 7, 3, 1, 6, 2, 5]
    val = Queens(8).has_collision(board, 7)
    self.assertFalse(val)

  def test_4(self):
    """No conflicts - 15x15, current = 12"""
    board = [8, 0, 2, 4, 6, 10, 12, 14, 1, 5, 13, 9, 7, -1, -1]
    val = Queens(15).has_collision(board, 12)
    self.assertFalse(val)

  
  def test_6(self):
    """Conflicts - same row"""
    board = [3, 0, 3, -1, -1, -1, -1, -1]
    val = Queens(8).has_collision(board, 2)
    self.assertTrue(val) #

  def test_7(self):
    """Conflicts - diagonal 1"""
    board = [3, 0, 6, 7, -1, -1, -1, -1]
    val = Queens(8).has_collision(board, 3)
    self.assertTrue(val) #

  def test_8(self):
    """Conflicts - diagonal 2"""
    board = [3, 0, 6, 4, 2, 7, 5, 1]
    val = Queens(8).has_collision(board, 7)
    self.assertTrue(val) #

  def test_9(self):
       """Conflicts - diagonal 2"""
       board = [7, 6, 5, 4, 3, 2, 1, 0]
       val = Queens(8).has_collision(board, 7)
       self.assertTrue(val) #

  def test_10(self):
    """Conflicts - diagonal 2"""
    board = [0,1,2,3,4,5,-1,-1]
    val = Queens(8).has_collision(board, 5)
    self.assertTrue(val) #
  
if __name__ == "__main__":
    unittest.main(verbosity=2)
