#!/usr/bin/env bash

OUT=results_with_kissat
mkdir -p $OUT

run_with_kissat_sat () {
    oddball $1 $2 --strategy TruthTableOrdering --strategy ZeroPlus --cnf $3/oddball_$1_$2_tto_zp.cnf --skip-solver | tee $3/oddball_$1_$2_tto_zp.txt
    timeout --signal INT 1h kissat $3/oddball_$1_$2_tto_zp.cnf | tee $3/oddball_$1_$2_tto_zp.cert | tee -a $3/oddball_$1_$2_tto_zp.txt
    oddball $1 $2 --cert $3/oddball_$1_$2_tto_zp.cert | tee -a $3/oddball_$1_$2_tto_zp.txt
}
export -f run_with_kissat_sat

run_with_kissat_unsat () {
    oddball $1 $2 --strategy TruthTableForced --cnf $3/oddball_$1_$2_ttf.cnf --skip-solver | tee $3/oddball_$1_$2_ttf.txt
    timeout --signal INT 1h kissat $3/oddball_$1_$2_ttf.cnf | tee $3/oddball_$1_$2_ttf.cert | tee -a $3/oddball_$1_$2_ttf.txt
    oddball $1 $2 --cert $3/oddball_$1_$2_ttf.cert | tee -a $3/oddball_$1_$2_ttf.txt
}
export -f run_with_kissat_unsat

# Requires GNU Parallel
# Run N,W combinations where N <= (3^W - 3) / 2, which are all SAT, plus one more which will be UNSAT.
parallel -j 8 --filter '{1}<=1+(3**{2}-3)/2' {3} {1} {2} $OUT ::: {3..121} ::: {3..5} ::: run_with_kissat_sat run_with_kissat_unsat

# Sort results by Kissat process-time.
find $OUT -type f -name \*.cert \
| xargs -n 128 awk '/SIGINT/{R="SIGINT"} /s UNSAT/{R="UNSAT"} /s SAT/{R="SAT"} /process-time/{print FILENAME,R,$(NF-1)}' \
| sort -nk3 > sorted_runtimes.txt

