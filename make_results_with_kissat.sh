#!/usr/bin/env bash

OUT=results_with_kissat
mkdir -p $OUT

run_with_kissat () {
    oddball $1 $2 --strategy TruthTableOrdering --strategy ZeroPlus --cnf $3/oddball_$1_$2.cnf --skip-solver | tee $3/oddball_$1_$2.txt
    #oddball $1 $2 --strategy TruthTableForced --cnf $3/oddball_$1_$2.cnf --skip-solver | tee $3/oddball_$1_$2.txt
    timeout --signal INT 1h kissat $3/oddball_$1_$2.cnf | tee $3/oddball_$1_$2.cert | tee -a $3/oddball_$1_$2.txt
    oddball $1 $2 --cert $3/oddball_$1_$2.cert | tee -a $3/oddball_$1_$2.txt
}

export -f run_with_kissat

# Requires GNU Parallel
# Run N,W combinations where N <= (3^W - 3) / 2, which are all SAT, plus one more which will be UNSAT.
parallel -j 8 --filter '{1}<=1+(3**{2}-3)/2' run_with_kissat {1} {2} $OUT ::: {3..121} ::: {3..5}

# Sort results by Kissat process-time.
grep -H process-time $OUT/*.cert | awk '{print $1, $(NF-1)}' | sort -n -k 2

