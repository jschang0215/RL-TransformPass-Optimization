#!/bin/sh
# Options declaration
CLANG_BC="clang -c -emit-llvm -Wno-everything"
CLANG_EXEC="clang -Wno-everything"
CSMITH="csmith"
CSMITH_INCLUDE="-I/home/jschang/Desktop/ML_Compiler_Optimization/01_source/csmith/include"
YARPGEN="../yarpgen/build/yarpgen"
MAX_CODE_SIZE=300000
MAX_EXECUTION_TIME=10

if [ "$1" == "-h" ] ; then
    echo "Run to generate random c file and its features"
    echo "Usage: First param of idx of programs to be generated"
    exit 0
fi

# Clean up previous runs
rm -f ./src/*
rm -f ./bin/*
rm -f ./ir/*
rm -f ./feature/*

MAX_ITR=$1
script_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
feature_pass="${script_path}/build/Feature.so"

# Generating with csmith
echo "Random C program with csmith"
export PATH=$PATH:/home/jschang/Desktop/ML_Compiler_Optimization/01_source/csmith/bin # Configuring csmtih path
for idx in $(seq -f "%02g" 1 $1); do
    # Target files
    c_file="src/csmith_${idx}.c"
    bc_file="ir/csmith_${idx}.bc"
    bin_file="bin/csmith_${idx}"
    feature_file="feature/csmith_${idx}.in"

    echo "Csmith ${idx}/${MAX_ITR} Processing..."
    echo "  Generating and verifying random C file with csmith"
    # Valid File
    # 1. Execute in MAX_EXECUTION_TIME second
    # 2. Code size > MAX_CODE_SIZE
    while [ 1 ]; do # Create c file unitll it is valid file
        ${CSMITH} > $c_file
        ${CLANG_EXEC} $c_file -o $bin_file -lm

        # Verify code size
        code_size=$(stat -c%s $bin_file)
        if [[ $code_size -lt ${MAX_CODE_SIZE} ]]; then
            echo "  Too small code ($code_size). Regenerating with csmith..."
            continue
        fi
        echo "  File size verification pass ($code_size)"

        # Verify execution time
        timeout ${MAX_EXECUTION_TIME} ./$bin_file > /dev/null
        exit_status=$?
        if [[ $exit_status -eq 124 ]]; then
            echo "  Too long execution time. Regenerating with csmith..."
            continue
        fi
        echo "  Execution time verification pass"

        break
    done
    echo "  Compile C file to bc and IR file"
    ${CLANG_BC} $c_file ${CSMITH_INCLUDE} -o $bc_file # C to IR
    ${CLANG_EXEC} $bc_file -o $bin_file -lm # IR to bin
    echo "  Extracting feature with LLVM Pass"
    opt -load ./build/Feature.so -enable-new-pm=0 -feature $bc_file -o /dev/null # Feature extraction
    mv ./TMP_FEATURE.txt $feature_file # Move to feature path
done

# echo "Random C program with yarpgen"
# for idx in $(seq -f "%02g" 1 $1); do
#     # Target files
#     c_file="driver.cpp func.cpp"
#     bc_file="ir/yarpgen_${idx}.bc"
#     bin_file="bin/yarpgen_${idx}"
#     feature_file="feature/yarpgen_${idx}.in"

#     echo "Yarpgen ${idx}/${MAX_ITR} Processing..."
#     echo "  Generating and verifying random C file with yarpgen"
#     # Valid File
#     # 1. Execute in 1 second
#     # 2. Code size > 150000
#     while [ 1 ]; do # Create c file unitll it is valid file
#         ${YARPGEN} > /dev/null
#         sleep 0.5 # Delay

#         # Erase printf function
#         python3 Erase_Printf.py driver.cpp
#         ${CLANG_EXEC} $c_file -o $bin_file -lm

#         # Verify code size
#         code_size=$(stat -c%s $bin_file)
#         if [[ $code_size -lt ${MAX_CODE_SIZE} ]]; then
#             echo "  Too small code ($code_size). Regenerating with yarpgen..."
#             continue
#         fi
#         echo "  File size verification pass ($code_size)"

#         # Verify execution time
#         timeout ${MAX_EXECUTION_TIME} ./$bin_file > /dev/null
#         exit_status=$?
#         if [[ $exit_status -eq 124 ]]; then
#             echo "  Too long execution time. Regenerating with yarpgen..."
#             continue
#         fi
#         echo "  Execution time verification pass"

#         break
#     done
#     echo "  Compile C file to bc and IR file"
#     ${CLANG_BC} driver.cpp -o driver.bc # Multiple c files should be converted to bc and merged
#     ${CLANG_BC} func.cpp -o func.bc
#     llvm-link func.bc driver.bc -o ${bc_file} # Merge 2 bc file
#     ${CLANG_EXEC} $bc_file -o $bin_file -lm # IR to bin
#     echo "  Extracting feature with LLVM Pass"
#     opt -load ./build/Feature.so -enable-new-pm=0 -feature $bc_file -o /dev/null # Feature extraction
#     mv ./TMP_FEATURE.txt $feature_file # Move to feature path
#     mv driver.cpp "src/yarpgen_${idx}_driver.cpp" # Move c file to src
#     mv func.cpp "src/yarpgen_${idx}_func.cpp"

#     # Clean up
#     rm -f $c_file
#     rm -f driver.bc func.bc
# done


# echo "C programs from MicroBenches"
# file=$(cat Microbench_Paths.txt)
# idx=1
# for line in $file; do
#     c_file="$line/bench.c"
#     bc_file="ir/microbench_${idx}.bc"
#     bin_file="bin/microbench_${idx}"
#     feature_file="feature/microbench_${idx}.in"
#     echo "Processing ${c_file}"
#     echo "  Compile C file to bc and IR file"
#     ${CLANG_BC} $c_file -o $bc_file
#     ${CLANG_EXEC} $bc_file -o $bin_file -lm
#     echo "  Extracting feature with LLVM Pass"
#     opt -load ./build/Feature.so -enable-new-pm=0 -feature $bc_file -o /dev/null
#     mv ./TMP_FEATURE.txt $feature_file
#     idx=$((idx+1))
# done