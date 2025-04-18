#!/usr/bin/env bash

ls benchmarks/*.cnf.gz | parallel --plus timeout --signal INT 1h kissat {} ">" {..}.cert

# Sort results by Kissat process-time.
grep -H process-time benchmarks/*.cert | awk '{print $1, $(NF-1)}' | sort -n -k 2 > benchmarks/sorted_runtimes.txt
