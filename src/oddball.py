import argparse
from z3 import And, Const, EnumSort, Goal, If, Implies, Int, Or, sat, Sum, Tactic, Then

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

def print_formula(formula, indent=0, recursive=True):
    i0 = '  ' * (indent)
    i1 = '  ' * (indent + 1)

    formula_str_single_line = ''.join(str(formula).splitlines())
    print(f'{i0}f = {formula_str_single_line}')

    if (recursive):
        print(f'{i1}decl = {formula.decl()}')
        print(f'{i1}num_args = {formula.num_args()}')
        print(f'{i1}params = {formula.params()}')

        arg_list = [formula.arg(arg_ix) for arg_ix in range(formula.num_args())]
        print(f'{i1}args = {arg_list}')

        for arg_ix, arg in enumerate(arg_list):
            print(f'{i1}arg {arg_ix}')
            print_formula(arg, indent+2)

def export_smt2(solver, filename):
    with open(filename, 'w', encoding='ascii') as smt2_file:
        smt2_file.write(solver.to_smt2())

def export_cnf(solver, filename):
    # Create a goal and add constraints.
    goal = Goal()
    goal.add(solver.assertions())

    # Apply a set of tactics to convert a purely CNF formulation.
    tactic = Then('lia2card', 'dt2bv', 'bit-blast', 'card2bv', 'tseitin-cnf', 'sat-preprocess')
    subgoal = tactic(goal)
    formulas = subgoal[0]

    # Collect all variables in all formulas.
    all_vars = set()
    for f in formulas:
        print_formula(f)

# Solve for the given number of balls and weighings.
def solve(num_balls, num_weighings):
    print(f'Solving for {num_balls} balls and {num_weighings} weighings.')

    s = Tactic('qffd').solver()

    location_sort, (left, right, hold) = EnumSort('location', ['L', 'R', 'H'])

    # Where is each ball for each weighing.
    loc_vars = [[Const(f'b{ball}_w{weighing}', location_sort) for weighing in range(num_weighings)] for ball in range(num_balls)]

    # Truth Table row result: [light results in decreasing ball order], [no result], [heavy results in increasing ball order]
    tt_sort, tt_tuple = EnumSort('tt', [f'{x}{Light}' for x in range(num_balls-1, -1, -1)] + [' '] + [f'{x}{Heavy}' for x in range(num_balls)])

    tt_no_outcome = tt_tuple[num_balls]

    def tt_light(ball):
        return tt_tuple[num_balls - (ball+1)]

    def tt_heavy(ball):
        return tt_tuple[num_balls + (ball+1)]

    def tt_opposite(tt):
        ix = tt_tuple.index(tt) - num_balls
        return tt_tuple[num_balls - ix]

    def tt_to_ball_error(tt):
        ix = tt_tuple.index(tt) - num_balls
        if ix < 0:
            return (-ix - 1, Light)
        elif ix > 0:
            return (ix - 1, Heavy)
        else:
            return (0, Balance)

    # Number of rows in the truth table.
    tt_rows = len(Outcomes) ** num_weighings

    # Number of rows in the top half on the truth table.
    # The truth table is symmetrical so we only solve for the top half.
    # FIXME: explain why the truth table is symmetrical.
    # Inverting the outcome of each weighing identifies the same error ball but with the opposite error.
    half_tt_rows = tt_rows // 2

    tt_vars = [Const(f'tt{row}', tt_sort) for row in range(half_tt_rows)]

    # Each ball (with either error) must appear in at least one truth table row.
    s.add([Or([Or(tt_vars[row]==tt_light(ball), tt_vars[row]==tt_heavy(ball)) for row in range(half_tt_rows)]) for ball in range(num_balls)])

    # Each weighing must have the same number of balls on each side of the scale.
    sum_left_vars = [Int(f'l{weighing}') for weighing in range(num_weighings)]
    sum_right_vars = [Int(f'r{weighing}') for weighing in range(num_weighings)]
    s.add([sum_left_vars[weighing] == sum_right_vars[weighing] for weighing in range(num_weighings)])
    s.add([And(0 <= sum_left_vars[weighing], sum_left_vars[weighing] <= num_balls//2) for weighing in range(num_weighings)])
    s.add([And(0 <= sum_right_vars[weighing], sum_right_vars[weighing] <= num_balls//2) for weighing in range(num_weighings)])

    #s.add([Sum([loc_vars[ball][weighing]==left for ball in range(num_balls)]) == Sum([loc_vars[ball][weighing]==right for ball in range(num_balls)]) for weighing in range(num_weighings)])
    s.add([sum_left_vars[weighing] == Sum([loc_vars[ball][weighing]==left for ball in range(num_balls)]) for weighing in range(num_weighings)])
    s.add([sum_right_vars[weighing] == Sum([loc_vars[ball][weighing]==right for ball in range(num_balls)]) for weighing in range(num_weighings)])

    # Weighing outcomes imply truth table results.
    for ix in range(half_tt_rows):
        for weigh, outcome in enumerate(ix_to_symbols(ix, num_weighings)):
            for ball in range(num_balls):
                if outcome == Balance:
                    # The result is not any of the balls on either side of the scale.
                    s.add(Implies(loc_vars[ball][weigh]!=hold, And(tt_vars[ix]!=tt_light(ball), tt_vars[ix]!=tt_heavy(ball))))
                else:
                    # The result is not any of the balls in the holdout group.
                    s.add(Implies(loc_vars[ball][weigh]==hold, And(tt_vars[ix]!=tt_light(ball), tt_vars[ix]!=tt_heavy(ball))))

                    # Balls on the heavy side of the scale are not light.
                    s.add(Implies(loc_vars[ball][weigh]==(left if outcome==HeavyLeft else right), tt_vars[ix]!=tt_light(ball)))

                    # Balls on the light side of the scale are not heavy.
                    s.add(Implies(loc_vars[ball][weigh]==(left if outcome==LightLeft else right), tt_vars[ix]!=tt_heavy(ball)))

    # Symmetry breaking constraints:

    # Last-ball-heavy should not appear in the top half of the truth table.
    s.add([tt_vars[ix] != tt_tuple[-1] for ix in range(half_tt_rows)])

    # Tracking variable for the most recent ball error result.
    max_vars = [Const(f'max{row}', tt_sort) for row in range(half_tt_rows)]
    s.add(max_vars[0]==tt_vars[0])
    s.add([If(tt_vars[ix]==tt_no_outcome, max_vars[ix]==max_vars[ix-1], max_vars[ix]==tt_vars[ix]) for ix in range(1, half_tt_rows)])

    def successor(lhs, rhs, ix=num_balls-1):
        if ix == 0:
            return If(Or(rhs==tt_light(ix), rhs==tt_heavy(ix)), lhs==tt_no_outcome, Or(lhs==tt_light(num_balls-1), lhs==tt_heavy(num_balls-1)))
        else:
            return If(Or(rhs==tt_light(ix), rhs==tt_heavy(ix)), Or(lhs==tt_light(ix-1), lhs==tt_heavy(ix-1)), successor(lhs, rhs, ix-1))

    # Truth table rows can be either no-outcome, or the successor to the most recent ball.
    s.add([Or(tt_vars[ix]==tt_no_outcome, successor(tt_vars[ix], max_vars[ix-1])) for ix in range(1, half_tt_rows)])

    #export_cnf(s, 'odd.cnf')

    # Solve the model.
    solver_result = s.check()

    if solver_result == sat:
        # The problem is solvable for num_balls and num_weighings.
        m = s.model()

        # Extract the sets of left and right balls for each weighing.
        weigh_left_right = [([ball for ball in range(num_balls) if m.eval(loc_vars[ball][weigh]==left)],
                             [ball for ball in range(num_balls) if m.eval(loc_vars[ball][weigh]==right)])
                            for weigh in range(num_weighings)]

        # Extract the result for each truth table row.
        tt_result = [m.eval(tt_vars[row]) for row in range(half_tt_rows)]

        # The second half of the truth table is the reverse of the first half, and implies the opposite errors in each row.
        # The center row of the truth table (all weighing outcomes are Balance) is included with no results.
        tt_result.extend([tt_tuple[num_balls]] + [tt_opposite(tt) for tt in tt_result[::-1]])

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
            print("   ".join([f'{ix:>2}'] + ix_to_symbols(ix, num_weighings) + [str(result)]))

        # Test the solution.
        correct_results = 0
        incorrect_results = 0

        # Test each ball-error combination.
        for tt in tt_tuple:
            if tt == tt_no_outcome:
                continue

            ball, error = tt_to_ball_error(tt)

            print()
            print(f'Test {ball}{error}:')

            # Simulate each weighing.
            weigh_outcomes = [weigh_outcome(left, right, ball, error) for left, right in weigh_left_right]

            for weigh, (left, right) in enumerate(weigh_left_right):
                print(f'    W{weigh}: {pretty_list(left)} {weigh_outcomes[weigh]} {pretty_list(right)}')

            # Look up the ball-error combination in the truth table.
            tt_ix = symbols_to_ix(weigh_outcomes)

            # Confirm the result is the ball-error combination being tested.
            pretty_tt_result = str(tt_result[tt_ix])
            pretty_outcomes = "[" + ", ".join(weigh_outcomes) + "]"
            if tt_result[tt_ix] == tt:
                print(f'    Truth table row={pretty_outcomes} ix={tt_ix} result={pretty_tt_result} is correct')
                correct_results = correct_results + 1
            else:
                print(f'    Truth table row={pretty_outcomes} ix={tt_ix} result={pretty_tt_result} is INCORRECT, expected {tt}')
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

