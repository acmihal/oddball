#!/usr/bin/env bash

mkdir -p benchmarks

# Requires GNU Parallel
parallel << EOF
oddball  7 6 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_tto_zp_7_6.cnf --skip-solver
oddball 16 6 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_tto_zp_16_6.cnf --skip-solver
oddball 18 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_tto_zp_18_5.cnf --skip-solver
oddball 20 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_tto_zp_20_5.cnf --skip-solver
oddball 24 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_tto_zp_24_5.cnf --skip-solver
oddball 25 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_tto_zp_25_5.cnf --skip-solver
oddball 27 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_tto_zp_27_5.cnf --skip-solver
oddball 28 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_tto_zp_28_5.cnf --skip-solver
oddball 36 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_tto_zp_36_5.cnf --skip-solver
oddball 37 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_tto_zp_37_5.cnf --skip-solver
oddball 38 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_tto_zp_38_5.cnf --skip-solver
oddball 40 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_tto_zp_40_5.cnf --skip-solver
oddball 41 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_tto_zp_41_5.cnf --skip-solver
oddball 50 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_tto_zp_50_5.cnf --skip-solver
oddball 54 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_tto_zp_54_5.cnf --skip-solver
oddball 13 4 --strategy TruthTableForced --cnf benchmarks/oddball_ttf_13_4.cnf --skip-solver
oddball 17 4 --strategy TruthTableForced --cnf benchmarks/oddball_ttf_17_4.cnf --skip-solver
oddball 19 4 --strategy TruthTableForced --cnf benchmarks/oddball_ttf_19_4.cnf --skip-solver
oddball 20 4 --strategy TruthTableForced --cnf benchmarks/oddball_ttf_20_4.cnf --skip-solver
oddball 22 4 --strategy TruthTableForced --cnf benchmarks/oddball_ttf_22_4.cnf --skip-solver
oddball 23 4 --strategy TruthTableForced --cnf benchmarks/oddball_ttf_23_4.cnf --skip-solver
oddball 24 4 --strategy TruthTableForced --cnf benchmarks/oddball_ttf_24_4.cnf --skip-solver
oddball 26 4 --strategy TruthTableForced --cnf benchmarks/oddball_ttf_26_4.cnf --skip-solver
oddball 29 4 --strategy TruthTableForced --cnf benchmarks/oddball_ttf_29_4.cnf --skip-solver
oddball 33 4 --strategy TruthTableForced --cnf benchmarks/oddball_ttf_33_4.cnf --skip-solver
EOF

gzip benchmarks/*.cnf

