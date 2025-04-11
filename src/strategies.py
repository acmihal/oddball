from itertools import product
from z3 import Implies, Not, Or

def strategy_truth_table_ordering(formulation):
    # TruthTableOrdering strategy:
    #   The results in the top half of the truth table should run sequentially increasing by ball number.
    #   The second half of the truth table will have the opposite errors in decreasing sequence by ball number.

    # Ball N may not appear in row R if N > R, because then there are not enough earlier rows [0, R) for balls [0, N).
    # Likewise, if N + slack > R, then there aren't enough later rows [R+1, half_tt_rows) for balls [N+1, num_balls).
    # Example: num_balls=6, num_weighings=3, half_tt_rows=13, slack=7
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

    # Maximum number of rows without any result in the top half of the truth table.
    slack = formulation.half_tt_rows - formulation.num_balls

    # List of all possible truth_table_bvar index tuples.
    tt_bvar_list = list(product(range(formulation.half_tt_rows), range(formulation.num_balls), formulation.Errors))

    constraints = []

    constraints.extend([Not(formulation.truth_table_bvar(ix, ball, error)) for ix, ball, error in tt_bvar_list if ball > ix or ix > ball + slack])

    # If ball N appears in row R (with either error), then no lower row may have a higher-numbered ball (with either error).
    constraints.extend([Implies(formulation.truth_table_bvar(ix, ball, error),
                                Not(Or([formulation.truth_table_bvar(lower_ix, higher_ball, any_error)
                                       for lower_ix in range(ix)
                                       for higher_ball in range(ball + 1, formulation.num_balls)
                                       for any_error in formulation.Errors])))
                       for ix, ball, error in tt_bvar_list])

    return constraints

def strategy_zero_plus(formulation):
    # A symmetry-breaking constraint that the outcome 0+ (ball zero is heavy) must appear in the top half of the truth table.
    return [Not(formulation.truth_table_bvar(ix, 0, formulation.Light)) for ix in range(formulation.half_tt_rows)]

def strategy_weigh_zero_ascending(formulation):
    # Weigh0Ascending strategy:
    #   Balls in the 0'th weighing should be added to the scale in ascending order.
    #   Weighing 0 must have (at least) ball 0 on the left side and ball 1 on the right side.
    #   The next allowable pair is (2, 3), followed by (4, 5) and so on.

    constraints = []

    # The 0'th weighing should have (at least) ball 0 on the left side and ball 1 on the right side.
    constraints.append(formulation.weigh_pair_bvar(0, 0, 1))

    # The 0'th weighing should have (at least) ball N-1 in the holdout set.
    constraints.append(formulation.weigh_holdout_expr(0, formulation.num_balls - 1))

    # Any additional balls in weighing 0 should be added to the scale in ascending order.
    # Pair (0,1) is already on the scale. Next is (2,3), then (4,5), and so forth.
    # This is accomplished by adding a constraint that each pair implies the previous pair.
    constraints.extend([Implies(formulation.weigh_pair_bvar(0, ball - 1, ball),
                                formulation.weigh_pair_bvar(0, ball - 3, ball - 2))
                       for ball in range(3, formulation.num_balls, 2)])

    # Pairs of the form (m odd, *), (*, n even), (m, n != m+1) should never be weighed in weighing 0.
    constraints.extend([Not(formulation.weigh_pair_bvar(0, m, n)) for m in range(formulation.num_balls) for n in range(formulation.num_balls) if (m % 2 == 1) or (n % 2 == 0) or (n != m + 1)])

    return constraints

StrategyMap = {'TruthTableOrdering': strategy_truth_table_ordering,
               'ZeroPlus': strategy_zero_plus,
               'Weigh0Ascending': strategy_weigh_zero_ascending}

