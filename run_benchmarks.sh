#!/usr/bin/env bash

ls benchmarks/*.cnf.gz | parallel timeout --signal INT 1h kissat {} ">" {.}.cert
