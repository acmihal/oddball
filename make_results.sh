#!/usr/bin/env bash

OUT=results_with_z3
mkdir -p $OUT

# Requires GNU Parallel
parallel oddball {} 3 ">" $OUT/oddball_{}_3.out ::: {3..13}
parallel oddball {} 4 ">" $OUT/oddball_{}_4.out ::: {3..40}
parallel oddball {} 5 ">" $OUT/oddball_{}_5.out ::: {3..121}
#parallel oddball {} 6 ">" $OUT/oddball_{}_5.out ::: {3..364}

