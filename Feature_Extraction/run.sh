#!/bin/sh
if [ "$1" == "-h" ] ; then
    echo "Run to generate random c file and its features"
    echo "Usage: First param of # of programs to be generated"
    exit 0
fi

# Clean up previous runs
clear
# rm -f ./src/*
# rm -f ./bin/*
# rm -f ./ir/*
# rm -f ./feature/*

# Configure GNU parallel
seq 301 $1 > ./etc/feature_extract_parallel_param.txt

# Generating with csmith
echo "Random C program with csmith"
export PATH=$PATH:/home/jschang/Desktop/ML_Compiler_Optimization/01_source/csmith/bin # Configuring csmtih path

cat ./etc/feature_extract_parallel_param.txt | parallel -j 12 bash feature_extract_core.sh
