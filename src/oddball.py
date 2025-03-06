from z3 import And, AtLeast, AtMost, Bool, Distinct, Implies, Not, Or, PbEq, Solver

num_balls = 12
num_weighings = 3
weigh_outcomes = ['<', '=', '>']
errors = ['-', '+']

def weigh_left_bvar(weigh, ball):
    return Bool(f'w{weigh}_left_b{ball}')

def weigh_right_bvar(weigh, ball):
    return Bool(f'w{weigh}_right_b{ball}')

def truth_table_bvar(ix, ball, error):
    return Bool(f'tt_ix{ix}_b{ball}{error}')

def ix_to_symbols(ix):
    symbols = ['0'] * num_weighings
    for j in range(-1, -(num_weighings + 1), -1):
        symbols[j] = weigh_outcomes[ix % len(weigh_outcomes)]
        ix = ix // len(weigh_outcomes)
    return symbols

def main():
    print("Hello, world!")

    tt_rows = len(weigh_outcomes) ** num_weighings

    s = Solver()

    # Each weighing must have the same number of balls on each side.
    for weigh in range(num_weighings):
        # FIXME: number of balls on each side can be different per weighing.
        s.add(PbEq([(weigh_left_bvar(weigh, ball), 1) for ball in range(num_balls)], num_balls // len(weigh_outcomes)))
        s.add(PbEq([(weigh_right_bvar(weigh, ball), 1) for ball in range(num_balls)], num_balls // len(weigh_outcomes)))

        # No ball can be on both sides.
        for ball in range(num_balls):
            s.add(AtMost(weigh_left_bvar(weigh, ball), weigh_right_bvar(weigh, ball), 1))

    # Each truth table row implies at most one result, but can imply no result.
    for ix in range(tt_rows):
        s.add(AtMost(*[truth_table_bvar(ix, ball, error) for ball in range(num_balls) for error in errors], 1))

    # Each result must appear in at least one truth table row.
    for error in errors:
        for ball in range(num_balls):
            s.add(AtLeast(*[Bool(f'tt_ix{ix}_b{ball}{error}') for ix in range(tt_rows)], 1))

    # Weighing outcomes imply truth table results.
    for weigh in range(num_weighings):
        for ix in range(tt_rows):
            outcome = ix_to_symbols(ix)[weigh]
            if outcome == '=':
                # The result is not any of the balls on either side of the scale.
                for ball in range(num_balls):
                    s.add(Implies(weigh_left_bvar(weigh, ball), Not(Or([truth_table_bvar(ix, ball, error) for error in errors]))))
                    s.add(Implies(weigh_right_bvar(weigh, ball), Not(Or([truth_table_bvar(ix, ball, error) for error in errors]))))
            else:
                # The result is not any of the balls in the holdout group.
                for ball in range(num_balls):
                    s.add(Implies(Not(Or(weigh_left_bvar(weigh, ball), weigh_right_bvar(weigh, ball))), Not(Or([truth_table_bvar(ix, ball, error) for error in errors]))))
                if outcome == '<':
                    for ball in range(num_balls):
                        # Balls on the left side of the scale are not heavy.
                        s.add(Implies(weigh_left_bvar(weigh, ball), Not(truth_table_bvar(ix, ball, '+'))))
                        # Balls on the right side of the scale are not light.
                        s.add(Implies(weigh_right_bvar(weigh, ball), Not(truth_table_bvar(ix, ball, '-'))))
                else:
                    for ball in range(num_balls):
                        # Balls on the left side of the scale are not light.
                        s.add(Implies(weigh_left_bvar(weigh, ball), Not(truth_table_bvar(ix, ball, '-'))))
                        # Balls on the right side of the scale are not heavy.
                        s.add(Implies(weigh_right_bvar(weigh, ball), Not(truth_table_bvar(ix, ball, '+'))))

    # Symmetry breaking constraint.
    s.add(And([weigh_left_bvar(0, ball) for ball in range(num_balls // len(weigh_outcomes))]))
    s.add(And([weigh_right_bvar(0, ball) for ball in range(num_balls // len(weigh_outcomes), 2 * num_balls // len(weigh_outcomes))]))

    print(s.check())

    m = s.model()

    for weigh in range(num_weighings):
        print(f'Weighing {weigh}')
        left_balls = [ball for ball in range(num_balls) if m[weigh_left_bvar(weigh, ball)]]
        print(f'    left = {left_balls}')
        right_balls = [ball for ball in range(num_balls) if m[weigh_right_bvar(weigh, ball)]]
        print(f'    right = {right_balls}')
        holdout_balls = [ball for ball in range(num_balls) if not m[weigh_left_bvar(weigh, ball)] and not m[weigh_right_bvar(weigh, ball)]]
        print(f'    holdout = {holdout_balls}')

    print('Truth Table')
    print("  ".join(['ix'] + [f'W{weigh}' for weigh in range(num_weighings)] + ['Result']))
    for ix in range(tt_rows):
        outcomes = [f'{ball}{error}' for error in errors for ball in range(num_balls) if m[truth_table_bvar(ix, ball, error)]]
        if len(outcomes) == 0:
            outcomes = [' ']

        print("  ".join([f'{ix:>2}'] + [f' {ix_to_symbols(ix)[j]}' for j in range(num_weighings)] + outcomes))

if __name__ == "__main__":
    main()
