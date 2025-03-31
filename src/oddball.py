import argparse
from itertools import product
from functools import partial
from z3 import AtMost, Bool, Implies, Not, Or, Solver, sat

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

# Symmetry breaking strategies
StrategyWeigh0Ascending = 'Weigh0Ascending'
StrategyTruthTableAscending = 'TruthTableAscending'
StrategyNone = 'NoSymmetryBreaking'
SymmetryBreakingStrategies = [StrategyWeigh0Ascending, StrategyTruthTableAscending, StrategyNone]

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
def solve(num_balls, num_weighings, symmetry_breaking_strategy=SymmetryBreakingStrategies[0]):
    print(f'Solving for {num_balls} balls and {num_weighings} weighings.')
    print(f'Using symmetry breaking strategy {symmetry_breaking_strategy}.')

    # Partials for commonly used functions dependent on the num_balls parameter.
    wl_expr = partial(weigh_left_expr, num_balls=num_balls)
    wr_expr = partial(weigh_right_expr, num_balls=num_balls)
    wh_expr = partial(weigh_holdout_expr, num_balls=num_balls)

    # Number of rows in the truth table.
    tt_rows = len(Outcomes) ** num_weighings

    # List of all possible ball-error combinations.
    ball_error_list = list(product(range(num_balls), Errors))

    if len(ball_error_list) > (tt_rows - 3):
        # There are more potential errors than there are possible outcomes of the weighings. Trivially unsolvable.
        # Explanation of why 3 tt_rows are not possible:
        # 1. The center row of the truth table, corresponding to all weighings returning Balance (=, =, =, ...)
        #    only identifies that the error ball is in the holdout set for every weighing but does not determine
        #    whether the error ball is Heavy or Light. Therefore this truth table row cannot provide a result.
        # 2. FIXME
        # 3. FIXME
        print(f'No solution exists for {num_balls} balls and {num_weighings} weighings (trivially unsolvable).')
        return False

    # Number of rows in the top half on the truth table.
    # The truth table is symmetrical so we only solve for the top half.
    # FIXME: explain why the truth table is symmetrical.
    # Inverting the outcome of each weighing identifies the same error ball but with the opposite error.
    half_tt_rows = tt_rows // 2

    # Maximum number of rows without any result in the top half of the truth table.
    half_slack = half_tt_rows - num_balls

    # List of all possible truth_table_bvar index tuples.
    tt_bvar_list = list(product(range(half_tt_rows), range(num_balls), Errors))

    # Initialize the solver and begin to add constraints.
    s = Solver()

    # There is a single instance of each ball. A ball cannot be on the scale multiple times in a single weighing.
    s.add([AtMost(*wl_expr(weigh, ball).children(), *wr_expr(weigh, ball).children(), 1)
           for ball in range(num_balls) for weigh in range(num_weighings)])

    # Each truth table row implies at most one result, but can imply no result.
    s.add([AtMost(*[truth_table_bvar(ix, ball, error) for ball, error in ball_error_list], 1) for ix in range(half_tt_rows)])

    # Each ball (with either error) must appear in at least one truth table row.
    s.add([Or([truth_table_bvar(ix, ball, error) for ix in range(half_tt_rows) for error in Errors]) for ball in range(num_balls)])

    # Weighing outcomes imply truth table results.
    for ix in range(half_tt_rows):
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

    # Symmetry breaking constraints:

    if symmetry_breaking_strategy == StrategyWeigh0Ascending:
        # Weigh0Ascending strategy:
        #   Balls in the 0'th weighing should be added to the scale in ascending order.
        #   Weighing 0 must have (at least) ball 0 on the left side and ball 1 on the right side.
        #   The next allowable pair is (2, 3), followed by (4, 5) and so on.

        # The 0'th weighing should have (at least) ball 0 on the left side and ball 1 on the right side.
        s.add(weigh_pair_bvar(0, 0, 1))

        # The 0'th weighing should have (at least) ball N-1 in the holdout set.
        s.add(wh_expr(0, num_balls - 1))

        # Any additional balls in weighing 0 should be added to the scale in ascending order.
        # Pair (0,1) is already on the scale. Next is (2,3), then (4,5), and so forth.
        # This is accomplished by adding a constraint that each pair implies the previous pair.
        s.add([Implies(weigh_pair_bvar(0, ball - 1, ball), weigh_pair_bvar(0, ball - 3, ball - 2)) for ball in range(3, num_balls, 2)])

        # Pairs of the form (m odd, *), (*, n even), (m, n != m+1) should never be weighed in weighing 0.
        s.add([Not(weigh_pair_bvar(0, m, n)) for m in range(num_balls) for n in range(num_balls) if (m % 2 == 1) or (n % 2 == 0) or (n != m + 1)])

    elif symmetry_breaking_strategy == StrategyTruthTableAscending:
        # TruthTableAscending strategy:
        #   The results in the top half of the truth table should run sequentially increasing by ball number.
        #   The outcome 0- should always appear in the top half.
        #   The second half of the truth table will have the opposite errors in decreasing sequence by ball number.

        # Ball N may not appear in row R if N > R, because then there are not enough earlier rows [0, R) for balls [0, N).
        # Likewise, if N + half_slack > R, then there aren't enough later rows [R+1, half_tt_rows) for balls [N+1, num_balls).
        # Example: num_balls=6, num_weighings=3, half_tt_rows=13, half_slack=7
        #      0   1   2   3   4   5
        # 0        X   X   X   X   X
        # 1            X   X   X   X
        # 2    s           X   X   X
        # 3    l   s           X   X
        # 4    a   l   s           X
        # 5    c   a   l   s        
        # 6    k   c   a   l   s    
        # 7        k   c   a   l   s
        # 8    X       k   c   a   l
        # 9    X   X       k   c   a
        # 10   X   X   X       k   c
        # 11   X   X   X   X       k
        # 12   X   X   X   X   X    
        s.add([Not(truth_table_bvar(ix, ball, error)) for ix, ball, error in tt_bvar_list if ball > ix or ix > ball + half_slack])

        # If ball N appears in row R (with either error), then no lower row may have a higher-numbered ball (with either error).
        s.add([Implies(truth_table_bvar(ix, ball, error),
                       Not(Or([truth_table_bvar(lower_ix, higher_ball, any_error)
                               for lower_ix in range(ix) for higher_ball in range(ball + 1, num_balls) for any_error in Errors])))
               for ix, ball, error in tt_bvar_list])

        # The error 0+ should not occur in the top half of the truth table. Instead, 0- must be in the top half and 0+ in the bottom half.
        s.add([Not(truth_table_bvar(ix, 0, Heavy)) for ix in range(half_tt_rows)])

    with open("odd.smt2", "w", encoding="ascii") as smt2_file:
        smt2_file.write(s.to_smt2())

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
        tt_result = [[(ball, error) for ball, error in ball_error_list if m[truth_table_bvar(ix, ball, error)]] for ix in range(half_tt_rows)]

        # The second half of the truth table is the reverse of the first half, and implies the opposite errors in each row.
        # The center row of the truth table (all weighing outcomes are Balance) is included with no results.
        opposite = {Light: Heavy, Heavy: Light}
        tt_result.extend([[]] + [[(ball, opposite[error]) for ball, error in row] for row in tt_result[::-1]])

        # Print the solution.
        print()
        print('Solution:')

        # Print the balls involved in each weighing.
        for weigh, (left, right) in enumerate(weigh_left_right):
            print(f'W{weigh}: {pretty_list(left)} {"".join(Outcomes)} {pretty_list(right)}')

        # Print the truth table mapping weighing outcomes to ball-error combinations.
        print()
        print('Truth Table:')
        print("  ".join(['ix'] + [f'W{weigh}' for weigh in range(num_weighings)] + [' Result']))
        for ix, result in enumerate(tt_result):
            print("   ".join([f'{ix:>2}'] + ix_to_symbols(ix, num_weighings) + [f'{ball}{error}' for ball, error in result]))

        # Test the solution.
        correct_results = 0
        incorrect_results = 0

        # Test each ball-error combination.
        for ball, error in ball_error_list:
            print()
            print(f'Test {ball}{error}:')

            # Simulate each weighing.
            weigh_outcomes = [weigh_outcome(left, right, ball, error) for left, right in weigh_left_right]

            for weigh, (left, right) in enumerate(weigh_left_right):
                print(f'    W{weigh}: {pretty_list(left)} {weigh_outcomes[weigh]} {pretty_list(right)}')

            # Look up the ball-error combination in the truth table.
            tt_ix = symbols_to_ix(weigh_outcomes)

            # Confirm the result is the ball-error combination being tested.
            pretty_tt_result = "[" + ", ".join([f'{ball}{error}' for ball, error in tt_result[tt_ix]]) + "]"
            pretty_outcomes = "[" + ", ".join(weigh_outcomes) + "]"
            if len(tt_result[tt_ix]) == 1 and tt_result[tt_ix][0] == (ball, error):
                print(f'    Truth table row={pretty_outcomes} ix={tt_ix} result={pretty_tt_result} is correct')
                correct_results = correct_results + 1
            else:
                print(f'    Truth table row={pretty_outcomes} ix={tt_ix} result={pretty_tt_result} is INCORRECT, expected [{ball}{error}]')
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
    parser.add_argument("--strategy", choices=SymmetryBreakingStrategies, default=StrategyTruthTableAscending, help="symmetry breaking strategy")
    args = parser.parse_args()
    solve(args.N, args.W, args.strategy)

