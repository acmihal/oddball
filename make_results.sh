#!/usr/bin/env bash

# Requires GNU Parallel
parallel oddball {} 3 ">" results/oddball_{}_3.out ::: {3..13}
parallel oddball {} 4 ">" results/oddball_{}_4.out ::: {3..40}
parallel oddball {} 5 ">" results/oddball_{}_5.out ::: {3..121}
