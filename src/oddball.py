import argparse
from export import export_cnf, export_smt2, import_certificate
from formulation import Formulation
from strategies import StrategyMap
import time
from z3 import Solver, Tactic, sat

UsableTactics = ['z3-default', 'qffd', 'qflia']

def main():
    # Parse arguments.
    parser = argparse.ArgumentParser(description="Find the incorrectly-weighted ball out of a set of N, using only W weighings")
    parser.add_argument("N", type=int, help="number of balls in the set")
    parser.add_argument("W", type=int, help="number of weighings allowed")
    parser.add_argument("--strategy", choices=StrategyMap.keys(), action="append", help="symmetry breaking strategy")
    parser.add_argument("--tactic", choices=UsableTactics, default=UsableTactics[0], help="solver tactic")
    parser.add_argument("--smt2", type=str, help="export formulation to SMT2 file")
    parser.add_argument("--cnf", type=str, help="export formulation to CNF file")
    parser.add_argument("--certificate", type=str, help="import certificate from file")
    parser.add_argument("--skip-solver", action="store_true", help="exit before solving the formulation")
    args = parser.parse_args()

    # Validate arguments.
    assert args.N >= 3, 'Number of balls must be >= 3'
    assert args.W >= 1, 'Number of weighings must be >= 1'

    print(f'Solving for {args.N} balls and {args.W} weighings.', flush=True)

    # Initialize the formulation.
    f = Formulation(args.N, args.W)

    print()
    f.print_parameters()

    print()
    f.print_variable_stats()

    # Construct the Z3 solver.
    if args.tactic == 'z3-default':
        solver = Solver()
    else:
        solver = Tactic(args.tactic).solver()

    # Add constraints from the formulation to the solver.
    constraints_start_time = time.process_time()
    solver.add(f.get_constraints())

    print()
    f.print_constraint_stats()

    # Apply strategies in order.
    if args.strategy is not None:
        print()
        print(f'Strategies:')
        for strategy in args.strategy:
            constraints = StrategyMap[strategy](f)
            solver.add(constraints)
            print(f'    {strategy} applied {len(constraints)} constraint(s).', flush=True)

    constraints_end_time = time.process_time()
    constraints_elapsed_time = constraints_end_time - constraints_start_time

    print()
    print(f'Constraint formulation built in {constraints_elapsed_time:.2f} seconds.', flush=True)

    if args.smt2 is not None:
        print()
        print(f'Exporting formulation to SMT2 file "{args.smt2}".', flush=True)
        export_smt2(solver, args.smt2)

    if args.cnf is not None:
        print()
        print(f'Exporting formulation to CNF file "{args.cnf}".', flush=True)
        cnf_start_time = time.process_time()
        export_cnf(f, solver, args.cnf)
        cnf_end_time = time.process_time()
        cnf_elapsed_time = cnf_end_time - cnf_start_time
        print(f'CNF exported in {cnf_elapsed_time:.2f} seconds.', flush=True)

    if args.certificate is not None:
        print()
        print(f'Importing certificate from file "{args.certificate}".', flush=True)
        certificate_assertions = import_certificate(f, args.certificate)
        solver.add(certificate_assertions)
        print(f'Certificate applied {len(certificate_assertions)} assertion(s).', flush=True)
        if len(certificate_assertions) == 0:
            print(f'No assertions found in certificate. Skipping solver.')
            return

    if args.skip_solver:
        print()
        print(f'Skipping the solver.')
        return

    print()
    print(f'Starting solver with tactic "{args.tactic}".', flush=True)
    solver_start_time = time.process_time()
    result = solver.check()
    solver_end_time = time.process_time()
    solver_elapsed_time = solver_end_time - solver_start_time
    print(f'Solver finished in {solver_elapsed_time:.2f} seconds.', flush=True)

    if result == sat:
        # The problem is solvable for (N, W).
        model = solver.model()

        print()
        f.print_model(model)

        assert f.validate_model(model), "Solution validation failed."

    else:
        # The problem is not solvable for (N, W).
        print(f'No solution exists for {args.N} balls and {args.W} weighings.')

