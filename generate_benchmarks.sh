#!/usr/bin/env bash
mkdir -p benchmarks
parallel -j 8 << EOF
oddball 17 5 --strategy TruthTableForced --cnf benchmarks/oddball_17_5_ttf.cnf --skip-solver
oddball 19 5 --strategy TruthTableForced --cnf benchmarks/oddball_19_5_ttf.cnf --skip-solver
oddball 20 4 --strategy TruthTableForced --cnf benchmarks/oddball_20_4_ttf.cnf --skip-solver
oddball 20 5 --strategy TruthTableForced --cnf benchmarks/oddball_20_5_ttf.cnf --skip-solver
oddball 22 5 --strategy TruthTableForced --cnf benchmarks/oddball_22_5_ttf.cnf --skip-solver
oddball 13 4 --strategy TruthTableForced --cnf benchmarks/oddball_13_4_ttf.cnf --skip-solver
oddball 13 5 --strategy TruthTableForced --cnf benchmarks/oddball_13_5_ttf.cnf --skip-solver
oddball 22 4 --strategy TruthTableForced --cnf benchmarks/oddball_22_4_ttf.cnf --skip-solver
oddball 19 4 --strategy TruthTableForced --cnf benchmarks/oddball_19_4_ttf.cnf --skip-solver
oddball 23 4 --strategy TruthTableForced --cnf benchmarks/oddball_23_4_ttf.cnf --skip-solver
oddball 24 5 --strategy TruthTableForced --cnf benchmarks/oddball_24_5_ttf.cnf --skip-solver
oddball 24 4 --strategy TruthTableForced --cnf benchmarks/oddball_24_4_ttf.cnf --skip-solver
oddball 23 5 --strategy TruthTableForced --cnf benchmarks/oddball_23_5_ttf.cnf --skip-solver
oddball 26 5 --strategy TruthTableForced --cnf benchmarks/oddball_26_5_ttf.cnf --skip-solver
oddball 26 4 --strategy TruthTableForced --cnf benchmarks/oddball_26_4_ttf.cnf --skip-solver
oddball 28 5 --strategy TruthTableForced --cnf benchmarks/oddball_28_5_ttf.cnf --skip-solver
oddball 28 4 --strategy TruthTableForced --cnf benchmarks/oddball_28_4_ttf.cnf --skip-solver
oddball 33 4 --strategy TruthTableForced --cnf benchmarks/oddball_33_4_ttf.cnf --skip-solver
oddball 29 5 --strategy TruthTableForced --cnf benchmarks/oddball_29_5_ttf.cnf --skip-solver
oddball 29 4 --strategy TruthTableForced --cnf benchmarks/oddball_29_4_ttf.cnf --skip-solver
oddball 57 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_57_5_tto_zp.cnf --skip-solver
oddball 53 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_53_5_tto_zp.cnf --skip-solver
oddball 51 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_51_5_tto_zp.cnf --skip-solver
oddball 67 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_67_5_tto_zp.cnf --skip-solver
oddball 43 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_43_5_tto_zp.cnf --skip-solver
oddball 69 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_69_5_tto_zp.cnf --skip-solver
oddball 80 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_80_5_tto_zp.cnf --skip-solver
oddball 74 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_74_5_tto_zp.cnf --skip-solver
oddball 79 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_79_5_tto_zp.cnf --skip-solver
oddball 54 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_54_5_tto_zp.cnf --skip-solver
oddball 50 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_50_5_tto_zp.cnf --skip-solver
oddball 112 5 --strategy TruthTableForced --cnf benchmarks/oddball_112_5_ttf.cnf --skip-solver
oddball 56 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_56_5_tto_zp.cnf --skip-solver
oddball 76 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_76_5_tto_zp.cnf --skip-solver
oddball 44 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_44_5_tto_zp.cnf --skip-solver
oddball 78 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_78_5_tto_zp.cnf --skip-solver
oddball 70 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_70_5_tto_zp.cnf --skip-solver
oddball 47 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_47_5_tto_zp.cnf --skip-solver
oddball 52 5 --strategy TruthTableOrdering --strategy ZeroPlus --cnf benchmarks/oddball_52_5_tto_zp.cnf --skip-solver
oddball 97 5 --strategy TruthTableForced --cnf benchmarks/oddball_97_5_ttf.cnf --skip-solver
EOF
gzip benchmarks/*.cnf
