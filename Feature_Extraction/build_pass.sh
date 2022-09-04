#!/bin/bash

if [ "$1" == "-h" ] ; then
    echo "Usage: Run to compile Feature Extract Pass"
    exit 0
fi

TEST_C_FILE="../Benchmark/mibench/network/dijkstra/dijkstra_large.c"
TEST_BC_FILE="../Benchmark/mibench/network/dijkstra/dijkstra_large.bc"
TEST_IN_FILE="../Benchmark/mibench/network/dijkstra/input.dat"

clang++ -c -fpic -fno-rtti `llvm-config --cppflags` Feature.cpp -o ./build/Feature.o
clang++ -shared -o ./build/Feature.so ./build/Feature.o