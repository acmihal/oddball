from oddball.formulation import Formulation
from z3 import Solver, sat

def solve(num_balls, num_weighings):
    f = Formulation(num_balls, num_weighings)
    solver = Solver()
    solver.add(f.get_constraints())
    result = solver.check()
    return result == sat
    
def test_solve_2_1():
    assert not solve(2, 1)

def test_solve_3_2():
    assert solve(3, 2)

def test_solve_4_2():
    assert not solve(4, 2)

def test_solve_3_3():
    assert solve(3, 3)

def test_solve_4_3():
    assert solve(4, 3)
