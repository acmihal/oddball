from z3 import AtLeast, AtMost, Bool, Implies, Not, Or, Solver, sat

num_balls = 12
num_weighings = 3

HeavyRight = '<'
Balance = '='
HeavyLeft = '>'
Outcomes = [HeavyRight, Balance, HeavyLeft]
Light = '-'
Heavy = '+'
Errors = [Light, Heavy]

def weigh_pair_bvar(weigh, left_ball, right_ball):
    return Bool(f'w{weigh}_l{left_ball}_r{right_ball}')

def weigh_left_expr(weigh, ball):
    return Or([weigh_pair_bvar(weigh, ball, right_ball) for right_ball in range(num_balls)])

def weigh_right_expr(weigh, ball):
    return Or([weigh_pair_bvar(weigh, left_ball, ball) for left_ball in range(num_balls)])

def weigh_holdout_expr(weigh, ball):
    return Not(Or([Or(weigh_pair_bvar(weigh, ball, other_ball), weigh_pair_bvar(weigh, other_ball, ball)) for other_ball in range(num_balls)]))

def truth_table_bvar(ix, ball, error):
    return Bool(f'tt{ix}_b{ball}{error}')

def ix_to_symbols(ix):
    symbols = []
    for _ in range(num_weighings):
        symbols.insert(0, Outcomes[ix % len(Outcomes)])
        ix = ix // len(Outcomes)
    return symbols

def symbols_to_ix(symbols):
    ix = 0
    for symbol in symbols:
        ix = (ix * len(Outcomes)) + Outcomes.index(symbol)
    return ix

def weigh_result(left_set, right_set, ball, error):
    if len(left_set) < len(right_set):
        return HeavyRight
    elif len(left_set) > len(right_set):
        return HeavyLeft
    elif ball in left_set:
        return HeavyLeft if error == Heavy else HeavyRight
    elif ball in right_set:
        return HeavyRight if error == Heavy else HeavyLeft
    else:
        return Balance

def pretty_list(balls):
    return f'[{", ".join([f"{ball:>2}" for ball in balls])}]'

def main():
    print(f'Solving for {num_balls} balls and {num_weighings} weighings')

    tt_rows = len(Outcomes) ** num_weighings

    s = Solver()

    # There is a single instance of each ball. A ball cannot be on the scale multiple times in a single weighing.
    s.add([AtMost(*[weigh_pair_bvar(weigh, ball, other_ball) for other_ball in range(num_balls)],
                  *[weigh_pair_bvar(weigh, other_ball, ball) for other_ball in range(num_balls)], 1)
           for ball in range(num_balls) for weigh in range(num_weighings)])

    # Each weighing must have at least one pair of balls, but can have more than one.
    s.add([AtLeast(*[weigh_pair_bvar(weigh, lball, rball) for lball in range(num_balls) for rball in range(num_balls)], 1) for weigh in range(num_weighings)])

    # Each truth table row implies at most one result, but can imply no result.
    s.add([AtMost(*[truth_table_bvar(ix, ball, error) for ball in range(num_balls) for error in Errors], 1) for ix in range(tt_rows)])

    # Each result must appear in at least one truth table row.
    s.add([AtLeast(*[truth_table_bvar(ix, ball, error) for ix in range(tt_rows)], 1) for ball in range(num_balls) for error in Errors])

    # Weighing outcomes imply truth table results.
    for ix in range(tt_rows):
        for weigh, outcome in enumerate(ix_to_symbols(ix)):
            for ball in range(num_balls):
                if outcome == Balance:
                    # The result is not any of the balls on either side of the scale.
                    s.add(Implies(Not(weigh_holdout_expr(weigh, ball)), Not(Or([truth_table_bvar(ix, ball, error) for error in Errors]))))
                else:
                    # The result is not any of the balls in the holdout group.
                    s.add(Implies(weigh_holdout_expr(weigh, ball), Not(Or([truth_table_bvar(ix, ball, error) for error in Errors]))))
                    if outcome == HeavyRight:
                        # Balls on the left side of the scale are not heavy.
                        s.add(Implies(weigh_left_expr(weigh, ball), Not(truth_table_bvar(ix, ball, Heavy))))
                        # Balls on the right side of the scale are not light.
                        s.add(Implies(weigh_right_expr(weigh, ball), Not(truth_table_bvar(ix, ball, Light))))
                    else:
                        # Balls on the left side of the scale are not light.
                        s.add(Implies(weigh_left_expr(weigh, ball), Not(truth_table_bvar(ix, ball, Light))))
                        # Balls on the right side of the scale are not heavy.
                        s.add(Implies(weigh_right_expr(weigh, ball), Not(truth_table_bvar(ix, ball, Heavy))))

    # Symmetry breaking constraint.
    s.add(weigh_pair_bvar(0, 0, 1))

    # Solve the model.
    solver_result = s.check()

    if solver_result == sat:
        m = s.model()

        print()
        print('Solution:')
        for weigh in range(num_weighings):
            left_balls = [ball for ball in range(num_balls) if m.eval(weigh_left_expr(weigh, ball), model_completion=True)]
            right_balls = [ball for ball in range(num_balls) if m.eval(weigh_right_expr(weigh, ball), model_completion=True)]
            holdout_balls = [ball for ball in range(num_balls) if m.eval(weigh_holdout_expr(weigh, ball), model_completion=True)]
            print(f'Weighing {weigh}: {pretty_list(left_balls)} {"".join(Outcomes)} {pretty_list(right_balls)} holdout={pretty_list(holdout_balls)}')

        print()
        print('Truth Table:')
        print("  ".join(['ix'] + [f'W{weigh}' for weigh in range(num_weighings)] + [' Result']))
        for ix in range(tt_rows):
            outcomes = [f'{ball}{error}' for error in Errors for ball in range(num_balls) if m[truth_table_bvar(ix, ball, error)]]
            print("   ".join([f'{ix:>2}'] + ix_to_symbols(ix) + outcomes))

        # Test the result.
        correct_results = 0
        incorrect_results = 0
        for ball in range(num_balls):
            for error in Errors:
                print()
                print(f'Test {ball}{error}:')
                weigh_results = []
                for weigh in range(num_weighings):
                    left_set = [left_ball for left_ball in range(num_balls) if m.eval(weigh_left_expr(weigh, left_ball), model_completion=True)]
                    right_set = [right_ball for right_ball in range(num_balls) if m.eval(weigh_right_expr(weigh, right_ball), model_completion=True)]
                    weigh_results.append(weigh_result(left_set, right_set, ball, error))
                    print(f'    W{weigh}: {pretty_list(left_set)} {weigh_results[-1]} {pretty_list(right_set)}')
                tt_ix = symbols_to_ix(weigh_results)
                tt_outcome = [f'{tt_ball}{tt_error}' for tt_error in Errors for tt_ball in range(num_balls) if m[truth_table_bvar(tt_ix, tt_ball, tt_error)]]
                if len(tt_outcome) == 1 and tt_outcome[0] == f'{ball}{error}':
                    print(f'    Truth table result: {tt_outcome} is correct')
                    correct_results = correct_results + 1
                else:
                    print(f'    Truth table result: {tt_outcome} is INCORRECT, expected {ball}{error}')
                    incorrect_results = incorrect_results + 1

        print()
        print(f'Total correct results: {correct_results}')
        print(f'Total incorrect results: {incorrect_results}')

        assert (correct_results == len(Errors) * num_balls) and (incorrect_results == 0), "SAT model does not correctly solve the problem"

        return True
    else:
        print(f'No solution exists for {num_balls} balls and {num_weighings} weighings.')
        return False

if __name__ == "__main__":
    main()
