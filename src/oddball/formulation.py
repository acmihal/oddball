from itertools import product
from z3 import AtMost, Bool, Implies, Not, Or

class Formulation:

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

    def __init__(self, num_balls, num_weighings):
        self.num_balls = num_balls
        self.num_weighings = num_weighings

        # List of all possible ball-error combinations.
        self.ball_error_list = list(product(range(self.num_balls), self.Errors))

        # Number of rows in the truth table.
        self.tt_rows = len(self.Outcomes) ** self.num_weighings

        # Number of rows in the top half on the truth table.
        # The truth table is symmetrical so we only solve for the top half.
        # FIXME: explain why the truth table is symmetrical.
        # Inverting the outcome of each weighing identifies the same error ball but with the opposite error.
        self.half_tt_rows = self.tt_rows // 2

        if len(self.ball_error_list) > (self.tt_rows - 3):
            # There are more potential errors than there are possible outcomes of the weighings. Trivially unsolvable.
            # Explanation of why 3 tt_rows are not possible:
            # 1. The center row of the truth table, corresponding to all weighings returning Balance (=, =, =, ...)
            #    only identifies that the error ball is in the holdout set for every weighing but does not determine
            #    whether the error ball is Heavy or Light. Therefore this truth table row cannot provide a result.
            # 2. FIXME
            # 3. FIXME
            print(f'No solution exists for {self.num_balls} balls and {self.num_weighings} weighings (trivially unsolvable).')

    # Boolean variable, when true, indicates that weighing #weigh features
    # left_ball on the left side of the balance scale and right_ball on the right side.
    def weigh_pair_bvar(self, weigh, left_ball, right_ball):
        return Bool(f'w{weigh}_l{left_ball}_r{right_ball}')

    # Boolean expression, when true, indicates that weighing #weigh features
    # ball on the left side of the balance scale.
    def weigh_left_expr(self, weigh, ball):
        return Or([self.weigh_pair_bvar(weigh, ball, other) for other in range(self.num_balls)])

    # Boolean expression, when true, indicates that weighing #weigh features
    # ball on the right side of the balance scale.
    def weigh_right_expr(self, weigh, ball):
        return Or([self.weigh_pair_bvar(weigh, other, ball) for other in range(self.num_balls)])

    # Boolean expression, when true, indicates that weighing #weigh does not include ball.
    # Ball is instead in the holdout set during weighing #weigh.
    def weigh_holdout_expr(self, weigh, ball):
        return Not(Or(self.weigh_left_expr(weigh, ball), self.weigh_right_expr(weigh, ball)))

    # Boolean variable, when true, indicates that truth table row ix has the result of ball with error.
    def truth_table_bvar(self, ix, ball, error):
        return Bool(f'tt{ix}_b{ball}{error}')

    # Ball is good expression.
    def good(self, ix, ball):
        return Not(Or([self.truth_table_bvar(ix, ball, error) for error in self.Errors]))

    # Returns a list of all variables in the formulation.
    def all_vars(self):
        return ([self.weigh_pair_bvar(weigh, left_ball, right_ball) for weigh in range(self.num_weighings) for left_ball in range(self.num_balls) for right_ball in range(self.num_balls)] +
                [self.truth_table_bvar(ix, ball, error) for ix in range(self.half_tt_rows) for ball, error in self.ball_error_list])

    # Converts a truth table row index to a list of Outcomes symbols.
    # e.g. ix=0 symbols=['<', ...]
    def ix_to_symbols(self, ix):
        symbols = []
        for _ in range(self.num_weighings):
            symbols.insert(0, self.Outcomes[ix % len(self.Outcomes)])
            ix = ix // len(self.Outcomes)
        return symbols

    # Converts a list of Outcomes symbols to a truth table row index.
    def symbols_to_ix(self, symbols):
        ix = 0
        for symbol in symbols:
            ix = (ix * len(self.Outcomes)) + self.Outcomes.index(symbol)
        return ix

    # Returns the result of weighing the balls in left_set against the balls in right_set,
    # given the incorrectly-weighted ball and error.
    # Used to test that solutions are correct.
    def weigh_outcome(self, left_set, right_set, ball, error):
        if len(left_set) < len(right_set):
            return self.HeavyRight
        elif len(left_set) > len(right_set):
            return self.HeavyLeft
        elif ball in left_set:
            return self.HeavyLeft if error == self.Heavy else self.LightLeft
        elif ball in right_set:
            return self.HeavyRight if error == self.Heavy else self.LightRight
        else:
            return self.Balance

    # Pretty-prints a list of balls with appropriate spacing.
    def pretty_list(self, ball_list):
        return f'[{", ".join([f"{ball:>2}" for ball in ball_list])}]'

    def get_constraints(self):
        # There is a single instance of each ball. A ball cannot be on the scale multiple times in a single weighing.
        self.single_ball_instance_constraints = [AtMost(*self.weigh_left_expr(weigh, ball).children(),
                                                        *self.weigh_right_expr(weigh, ball).children(), 1)
                                                 for weigh in range(self.num_weighings)
                                                 for ball in range(self.num_balls)]

        # Each truth table row implies at most one result, but can imply no result.
        self.single_truth_table_result_constraints = [AtMost(*[self.truth_table_bvar(ix, ball, error) for ball, error in self.ball_error_list], 1)
                                                      for ix in range(self.half_tt_rows)]

        # Each ball (with either error) must appear in at least one truth table row.
        self.truth_table_completeness_constraints = [Or([self.truth_table_bvar(ix, ball, error) for ix in range(self.half_tt_rows) for error in self.Errors])
                                                     for ball in range(self.num_balls)]

        self.balance_implications = []
        self.holdout_implications = []
        self.not_light_implications = []
        self.not_heavy_implications = []

        # Weighing outcomes imply truth table results.
        for ix in range(self.half_tt_rows):
            for weigh, outcome in enumerate(self.ix_to_symbols(ix)):
                for ball in range(self.num_balls):
                    if outcome == self.Balance:
                        # The result is not any of the balls on either side of the scale.
                        self.balance_implications.append(Implies(Not(self.weigh_holdout_expr(weigh, ball)), self.good(ix, ball)))
                    else:
                        # The result is not any of the balls in the holdout group.
                        self.holdout_implications.append(Implies(self.weigh_holdout_expr(weigh, ball), self.good(ix, ball)))

                        # Balls on the heavy side of the scale are not light.
                        heavy_side_expr = self.weigh_left_expr(weigh, ball) if outcome == self.HeavyLeft else self.weigh_right_expr(weigh, ball)
                        self.not_light_implications.append(Implies(heavy_side_expr, Not(self.truth_table_bvar(ix, ball, self.Light))))

                        # Balls on the light side of the scale are not heavy.
                        light_side_expr = self.weigh_left_expr(weigh, ball) if outcome == self.LightLeft else self.weigh_right_expr(weigh, ball)
                        self.not_heavy_implications.append(Implies(light_side_expr, Not(self.truth_table_bvar(ix, ball, self.Heavy))))

        return (self.single_ball_instance_constraints +
                self.single_truth_table_result_constraints +
                self.truth_table_completeness_constraints +
                self.balance_implications +
                self.holdout_implications +
                self.not_light_implications +
                self.not_heavy_implications)

    def model_results(self, model):
        # Extract the sets of left and right balls for each weighing.
        weigh_left_right = [([ball for ball in range(self.num_balls) if model.eval(self.weigh_left_expr(weigh, ball))],
                             [ball for ball in range(self.num_balls) if model.eval(self.weigh_right_expr(weigh, ball))])
                            for weigh in range(self.num_weighings)]

        # Extract the result for each truth table row.
        tt_result = [[(ball, error) for ball, error in self.ball_error_list if model[self.truth_table_bvar(ix, ball, error)]] for ix in range(self.half_tt_rows)]

        # The second half of the truth table is the reverse of the first half, and implies the opposite errors in each row.
        # The center row of the truth table (all weighing outcomes are Balance) is included with no results.
        opposite = {self.Light: self.Heavy, self.Heavy: self.Light}
        tt_result.extend([[]] + [[(ball, opposite[error]) for ball, error in row] for row in tt_result[::-1]])

        return weigh_left_right, tt_result

    def validate_model(self, model):
        # Extract weighing schedule and truth table from model.
        weigh_left_right, tt_result = self.model_results(model)

        # Test the solution.
        correct_results = 0
        incorrect_results = 0

        # Test each ball-error combination.
        for ball, error in self.ball_error_list:
            print()
            print(f'Test {ball}{error}:')

            # Simulate each weighing.
            weigh_outcomes = [self.weigh_outcome(left, right, ball, error) for left, right in weigh_left_right]

            for weigh, (left, right) in enumerate(weigh_left_right):
                print(f'    W{weigh}: {self.pretty_list(left)} {weigh_outcomes[weigh]} {self.pretty_list(right)}')

            # Look up the ball-error combination in the truth table.
            tt_ix = self.symbols_to_ix(weigh_outcomes)

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
        return (correct_results == len(self.Errors) * self.num_balls) and (incorrect_results == 0)

    def print_parameters(self):
        print(f'Parameters:')
        print(f'    Balls: {self.num_balls}')
        print(f'    Weighings: {self.num_weighings}', flush=True)

    def print_variable_stats(self):
        print(f'Variables:')
        print(f'    Weigh Pair Variables: {self.num_weighings * self.num_balls * self.num_balls}')
        print(f'    Truth Table Variables: {self.half_tt_rows * len(self.ball_error_list)}', flush=True)

    def print_constraint_stats(self):
        print(f'Constraints:')
        print(f'    Single Ball Instance Constraints: {len(self.single_ball_instance_constraints)}')
        print(f'    Single Truth Table Result Constraints: {len(self.single_truth_table_result_constraints)}')
        print(f'    Truth Table Completeness Constraints: {len(self.truth_table_completeness_constraints)}')
        print(f'    Balance Implications: {len(self.balance_implications)}')
        print(f'    Holdout Implications: {len(self.holdout_implications)}')
        print(f'    Not Light Implications: {len(self.not_light_implications)}')
        print(f'    Not Heavy Implications: {len(self.not_heavy_implications)}', flush=True)

    def print_model(self, model):
        # Extract weighing schedule and truth table from model.
        weigh_left_right, tt_result = self.model_results(model)

        # Print the solution.
        print('Solution:')

        # Print the balls involved in each weighing.
        for weigh, (left, right) in enumerate(weigh_left_right):
            print(f'W{weigh}: {self.pretty_list(left)} {"".join(self.Outcomes)} {self.pretty_list(right)}')

        # Print the truth table mapping weighing outcomes to ball-error combinations.
        print()
        print('Truth Table:')
        print("  ".join(['ix'] + [f'W{weigh}' for weigh in range(self.num_weighings)] + [' Result']))
        for ix, result in enumerate(tt_result):
            print("   ".join([f'{ix:>2}'] + self.ix_to_symbols(ix) + [f'{ball}{error}' for ball, error in result]))

