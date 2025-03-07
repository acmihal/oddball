from oddball import solve

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
