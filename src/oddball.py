import argparse
from itertools import product
from functools import partial
from z3 import AtLeast, AtMost, Bool, Implies, Not, Or, Solver, sat

# Possible outcomes of a weighing.
HeavyRight = '<'
LightLeft = HeavyRight
Balance = '='
HeavyLeft = '>'
LightRight = HeavyLeft
Outcomes = [HeavyRight, Balance, HeavyLeft]

# Ball weight errors.
Light = '-'
Heavy = '+'
Errors = [Light, Heavy]

# Boolean variable, when true, indicates that weighing #weigh features
# left_ball on the left side of the balance scale and right_ball on the right side.
def weigh_pair_bvar(weigh, left_ball, right_ball):
    return Bool(f'w{weigh}_l{left_ball}_r{right_ball}')

# Boolean expression, when true, indicates that weighing #weigh features
# ball on the left side of the balance scale.
def weigh_left_expr(weigh, ball, num_balls):
    return Or([weigh_pair_bvar(weigh, ball, other) for other in range(num_balls)])

# Boolean expression, when true, indicates that weighing #weigh features
# ball on the right side of the balance scale.
def weigh_right_expr(weigh, ball, num_balls):
    return Or([weigh_pair_bvar(weigh, other, ball) for other in range(num_balls)])

# Boolean expression, when true, indicates that weighing #weigh does not include ball.
# Ball is instead in the holdout set during weighing #weigh.
def weigh_holdout_expr(weigh, ball, num_balls):
    return Not(Or(weigh_left_expr(weigh, ball, num_balls), weigh_right_expr(weigh, ball, num_balls)))

# Boolean variable, when true, indicates that truth table row ix has the result of ball with error.
def truth_table_bvar(ix, ball, error):
    return Bool(f'tt{ix}_b{ball}{error}')

# Converts a truth table row index to a list of Outcomes symbols.
# e.g. ix=0 symbols=['<', ...]
def ix_to_symbols(ix, num_weighings):
    symbols = []
    for _ in range(num_weighings):
        symbols.insert(0, Outcomes[ix % len(Outcomes)])
        ix = ix // len(Outcomes)
    return symbols

# Converts a list of Outcomes symbols to a truth table row index.
def symbols_to_ix(symbols):
    ix = 0
    for symbol in symbols:
        ix = (ix * len(Outcomes)) + Outcomes.index(symbol)
    return ix

# Returns the result of weighing the balls in left_set against the balls in right_set,
# given the incorrectly-weighted ball and error.
# Used to test that solutions are correct.
def weigh_outcome(left_set, right_set, ball, error):
    if len(left_set) < len(right_set):
        return HeavyRight
    elif len(left_set) > len(right_set):
        return HeavyLeft
    elif ball in left_set:
        return HeavyLeft if error == Heavy else LightLeft
    elif ball in right_set:
        return HeavyRight if error == Heavy else LightRight
    else:
        return Balance

# Pretty-prints a list of balls with appropriate spacing.
def pretty_list(ball_list):
    return f'[{", ".join([f"{ball:>2}" for ball in ball_list])}]'

# Solve for the given number of balls and weighings.
def solve(num_balls, num_weighings):
    print(f'Solving for {num_balls} balls and {num_weighings} weighings')

    # Partials for commonly used functions dependent on the num_balls parameter.
    wl_expr = partial(weigh_left_expr, num_balls=num_balls)
    wr_expr = partial(weigh_right_expr, num_balls=num_balls)
    wh_expr = partial(weigh_holdout_expr, num_balls=num_balls)

    # Number of rows in the truth table.
    tt_rows = len(Outcomes) ** num_weighings

    # List of all possible ball-error combinations.
    ball_error_list = list(product(range(num_balls), Errors))

    # Initialize the solver and begin to add constraints.
    s = Solver()

    # There is a single instance of each ball. A ball cannot be on the scale multiple times in a single weighing.
    s.add([AtMost(*wl_expr(weigh, ball).children(), *wr_expr(weigh, ball).children(), 1)
           for ball in range(num_balls) for weigh in range(num_weighings)])

    # Each truth table row implies at most one result, but can imply no result.
    s.add([AtMost(*[truth_table_bvar(ix, ball, error) for ball, error in ball_error_list], 1) for ix in range(tt_rows)])

    # Each result must appear in at least one truth table row.
    s.add([AtLeast(*[truth_table_bvar(ix, ball, error) for ix in range(tt_rows)], 1) for ball, error in ball_error_list])

    # Weighing outcomes imply truth table results.
    for ix in range(tt_rows):
        for weigh, outcome in enumerate(ix_to_symbols(ix, num_weighings)):
            for ball in range(num_balls):
                if outcome == Balance:
                    # The result is not any of the balls on either side of the scale.
                    s.add(Implies(Not(wh_expr(weigh, ball)), Not(Or([truth_table_bvar(ix, ball, error) for error in Errors]))))
                else:
                    # The result is not any of the balls in the holdout group.
                    s.add(Implies(wh_expr(weigh, ball), Not(Or([truth_table_bvar(ix, ball, error) for error in Errors]))))

                    # Balls on the heavy side of the scale are not light.
                    heavy_side_expr = wl_expr(weigh, ball) if outcome == HeavyLeft else wr_expr(weigh, ball)
                    s.add(Implies(heavy_side_expr, Not(truth_table_bvar(ix, ball, Light))))

                    # Balls on the light side of the scale are not heavy.
                    light_side_expr = wl_expr(weigh, ball) if outcome == LightLeft else wr_expr(weigh, ball)
                    s.add(Implies(light_side_expr, Not(truth_table_bvar(ix, ball, Heavy))))

    # Symmetry breaking constraint. The 0'th weighing should have (at least) ball 0 on the left side and ball 1 on the right side.
    s.add(weigh_pair_bvar(0, 0, 1))

    # Solve the model.
    solver_result = s.check()

    if solver_result == sat:
        # The problem is solvable for num_balls and num_weighings.
        m = s.model()

        # Extract the sets of left and right balls for each weighing.
        weigh_left_right = [([ball for ball in range(num_balls) if m.eval(wl_expr(weigh, ball))],
                             [ball for ball in range(num_balls) if m.eval(wr_expr(weigh, ball))])
                            for weigh in range(num_weighings)]

        # Extract the result for each truth table row.
        tt_result = [[f'{ball}{error}' for ball, error in ball_error_list if m[truth_table_bvar(ix, ball, error)]] for ix in range(tt_rows)]

        # Print the solution.
        print()
        print('Solution:')

        # Print the balls involved in each weighing.
        for weigh in range(num_weighings):
            print(f'W{weigh}: {pretty_list(weigh_left_right[weigh][0])} {"".join(Outcomes)} {pretty_list(weigh_left_right[weigh][1])}')

        # Print the truth table mapping weighing outcomes to ball-error combinations.
        print()
        print('Truth Table:')
        print("  ".join(['ix'] + [f'W{weigh}' for weigh in range(num_weighings)] + [' Result']))
        for ix, result in enumerate(tt_result):
            print("   ".join([f'{ix:>2}'] + ix_to_symbols(ix, num_weighings) + result))

        # Test the solution.
        correct_results = 0
        incorrect_results = 0

        # Test each ball-error combination.
        for ball, error in ball_error_list:
            print()
            print(f'Test {ball}{error}:')

            # Simulate each weighing.
            weigh_outcomes = [weigh_outcome(*weigh_left_right[weigh], ball, error) for weigh in range(num_weighings)]

            for weigh in range(num_weighings):
                print(f'    W{weigh}: {pretty_list(weigh_left_right[weigh][0])} {weigh_outcomes[weigh]} {pretty_list(weigh_left_right[weigh][1])}')

            # Look up the ball-error combination in the truth table.
            tt_ix = symbols_to_ix(weigh_outcomes)

            # Confirm the result is the ball-error combination being tested.
            if len(tt_result[tt_ix]) == 1 and tt_result[tt_ix][0] == f'{ball}{error}':
                print(f'    Truth table result: {tt_result[tt_ix]} is correct')
                correct_results = correct_results + 1
            else:
                print(f'    Truth table result: {tt_result[tt_ix]} is INCORRECT, expected {ball}{error}')
                incorrect_results = incorrect_results + 1

        print()
        print(f'Total correct results: {correct_results}')
        print(f'Total incorrect results: {incorrect_results}')

        # Check that all tests pass.
        assert (correct_results == len(Errors) * num_balls) and (incorrect_results == 0), "SAT model does not correctly solve the problem"

        return True
    else:
        # The problem is not solvable for num_balls and num_weighings.
        print(f'No solution exists for {num_balls} balls and {num_weighings} weighings.')
        return False

def main():
    parser = argparse.ArgumentParser(description="Find the incorrectly-weighted ball out of a set of N, using only W weighings")
    parser.add_argument("N", type=int, help="number of balls in the set")
    parser.add_argument("W", type=int, help="number of weighings allowed")
    args = parser.parse_args()
    solve(args.N, args.W)

