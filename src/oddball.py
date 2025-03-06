from z3 import And, AtLeast, AtMost, Bool, Implies, Not, Or, PbEq, Solver, sat

num_balls = 12
num_weighings = 3
weigh_outcomes = ['<', '=', '>']
errors = ['-', '+']

def weigh_left_bvar(weigh, ball):
    return Bool(f'w{weigh}_left_b{ball}')

def weigh_right_bvar(weigh, ball):
    return Bool(f'w{weigh}_right_b{ball}')

def weigh_holdout_bvar(weigh, ball):
    return Bool(f'w{weigh}_holdout_b{ball}')

def truth_table_bvar(ix, ball, error):
    return Bool(f'tt{ix}_b{ball}{error}')

def ix_to_symbols(ix):
    symbols = []
    for _ in range(num_weighings):
        symbols.insert(0, weigh_outcomes[ix % len(weigh_outcomes)])
        ix = ix // len(weigh_outcomes)
    return symbols

def symbols_to_ix(symbols):
    ix = 0
    for symbol in symbols:
        ix = (ix * len(weigh_outcomes)) + weigh_outcomes.index(symbol)
    return ix

def weigh_result(left_set, right_set, ball, error):
    if len(left_set) < len(right_set):
        return '<'
    elif len(left_set) > len(right_set):
        return '>'
    elif ball in left_set:
        if error == '-':
            return '<'
        else:
            return '>'
    elif ball in right_set:
        if error == '-':
            return '>'
        else:
            return '<'
    else:
        return '='

def main():
    print(f'Solving for {num_balls} balls and {num_weighings} weighings')

    tt_rows = len(weigh_outcomes) ** num_weighings

    s = Solver()

    # Each weighing must have the same number of balls on each side.
    for weigh in range(num_weighings):
        # FIXME: number of balls on each side can be different per weighing.
        s.add(PbEq([(weigh_left_bvar(weigh, ball), 1) for ball in range(num_balls)], num_balls // len(weigh_outcomes)))
        s.add(PbEq([(weigh_right_bvar(weigh, ball), 1) for ball in range(num_balls)], num_balls // len(weigh_outcomes)))
        s.add(PbEq([(weigh_holdout_bvar(weigh, ball), 1) for ball in range(num_balls)], num_balls // len(weigh_outcomes)))

        # Each ball must be on the left side, the right side, or in the holdout group.
        for ball in range(num_balls):
            s.add(PbEq([(weigh_left_bvar(weigh, ball), 1),
                        (weigh_right_bvar(weigh, ball), 1),
                        (weigh_holdout_bvar(weigh, ball), 1)], 1))

    # Each truth table row implies at most one result, but can imply no result.
    for ix in range(tt_rows):
        s.add(AtMost(*[truth_table_bvar(ix, ball, error) for ball in range(num_balls) for error in errors], 1))

    # Each result must appear in at least one truth table row.
    for ball in range(num_balls):
        for error in errors:
            s.add(AtLeast(*[truth_table_bvar(ix, ball, error) for ix in range(tt_rows)], 1))

    # Weighing outcomes imply truth table results.
    for ix in range(tt_rows):
        for weigh, outcome in enumerate(ix_to_symbols(ix)):
            for ball in range(num_balls):
                if outcome == '=':
                    # The result is not any of the balls on either side of the scale.
                    s.add(Implies(weigh_left_bvar(weigh, ball), Not(Or([truth_table_bvar(ix, ball, error) for error in errors]))))
                    s.add(Implies(weigh_right_bvar(weigh, ball), Not(Or([truth_table_bvar(ix, ball, error) for error in errors]))))
                else:
                    # The result is not any of the balls in the holdout group.
                    s.add(Implies(weigh_holdout_bvar(weigh, ball), Not(Or([truth_table_bvar(ix, ball, error) for error in errors]))))
                    if outcome == '<':
                        # Balls on the left side of the scale are not heavy.
                        s.add(Implies(weigh_left_bvar(weigh, ball), Not(truth_table_bvar(ix, ball, '+'))))
                        # Balls on the right side of the scale are not light.
                        s.add(Implies(weigh_right_bvar(weigh, ball), Not(truth_table_bvar(ix, ball, '-'))))
                    else:
                        # Balls on the left side of the scale are not light.
                        s.add(Implies(weigh_left_bvar(weigh, ball), Not(truth_table_bvar(ix, ball, '-'))))
                        # Balls on the right side of the scale are not heavy.
                        s.add(Implies(weigh_right_bvar(weigh, ball), Not(truth_table_bvar(ix, ball, '+'))))

    # Symmetry breaking constraint.
    s.add(And([weigh_left_bvar(0, ball) for ball in range(num_balls // len(weigh_outcomes))]))
    s.add(And([weigh_right_bvar(0, ball) for ball in range(num_balls // len(weigh_outcomes), 2 * num_balls // len(weigh_outcomes))]))

    # Solve the model.
    solver_result = s.check()

    if solver_result == sat:
        m = s.model()

        print()
        print('Solution:')
        for weigh in range(num_weighings):
            left_balls = [ball for ball in range(num_balls) if m[weigh_left_bvar(weigh, ball)]]
            right_balls = [ball for ball in range(num_balls) if m[weigh_right_bvar(weigh, ball)]]
            holdout_balls = [ball for ball in range(num_balls) if not m[weigh_left_bvar(weigh, ball)] and not m[weigh_right_bvar(weigh, ball)]]
            print(f'Weighing {weigh}: {left_balls} {"".join(weigh_outcomes)} {right_balls} holdout={holdout_balls}')
            #print(f'    left = {left_balls}')
            #print(f'    right = {right_balls}')
            #print(f'    holdout = {holdout_balls}')

        print()
        print('Truth Table:')
        print("  ".join(['ix'] + [f'W{weigh}' for weigh in range(num_weighings)] + [' Result']))
        for ix in range(tt_rows):
            outcomes = [f'{ball}{error}' for error in errors for ball in range(num_balls) if m[truth_table_bvar(ix, ball, error)]]
            if len(outcomes) == 0:
                outcomes = [' ']

            print("   ".join([f'{ix:>2}'] + ix_to_symbols(ix) + outcomes))

        # Test the result.
        correct_results = 0
        incorrect_results = 0
        for ball in range(num_balls):
            for error in errors:
                print()
                print(f'Test {ball}{error}:')
                weigh_results = []
                for weigh in range(num_weighings):
                    left_set = [left_ball for left_ball in range(num_balls) if m[weigh_left_bvar(weigh, left_ball)]]
                    right_set = [right_ball for right_ball in range(num_balls) if m[weigh_right_bvar(weigh, right_ball)]]
                    weigh_results.append(weigh_result(left_set, right_set, ball, error))
                    print(f'    W{weigh}: {left_set} {weigh_results[-1]} {right_set}')
                tt_ix = symbols_to_ix(weigh_results)
                tt_outcome = [f'{tt_ball}{tt_error}' for tt_error in errors for tt_ball in range(num_balls) if m[truth_table_bvar(tt_ix, tt_ball, tt_error)]]
                if len(tt_outcome) == 1 and tt_outcome[0] == f'{ball}{error}':
                    print(f'    Truth table result: {tt_outcome} correct')
                    correct_results = correct_results + 1
                else:
                    print(f'    Truth table result: {tt_outcome} INCORRECT, expected {ball}{error}')
                    incorrect_results = incorrect_results + 1

        print()
        print(f'Total correct results: {correct_results}')
        print(f'Total incorrect results: {incorrect_results}')

        assert (correct_results == len(errors) * num_balls) and (incorrect_results == 0), "SAT model does not correctly solve the problem"

        return True
    else:
        print(f'No solution exists for {num_balls} balls and {num_weighings} weighings.')
        return False

if __name__ == "__main__":
    main()
