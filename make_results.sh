#!/usr/bin/env bash

set -x

for i in {3..4}
do
    oddball $i 2 | tee results/oddball_${i}_2.out
done

for i in {3..13}
do
    oddball $i 3 | tee results/oddball_${i}_3.out
done

for i in {3..40}
do
    oddball $i 4 | tee results/oddball_${i}_4.out
done
