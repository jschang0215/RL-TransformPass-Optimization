#!/bin/sh
MODE="M"

if [ "$1" == "-h" ] ; then
    echo "RUN <Flag_Seive.sh>, NOT THIS FILE"
    ehco ""
    echo "Test input ir with flags"
    echo "Usage: First param IR to be tested"
    echo "Usage: Second param -m (memory usage) -c (code size)"
    exit 0
fi

OPT="opt"
CLANG_EXEC="clang -Wno-everything"
flag_cand=$(cat ./data/Flag_Candidates.in)

echo $1
ir=$1
echo "Testing at $ir"
for flag in $flag_cand; do
    ir_file="../Feature_Extraction/ir/${ir}"
    ir_file_name="${ir%.*}"
    opt_ir_file="./ir/${ir_file_name}_${flag}.bc"
    bin_file="./bin/${ir_file_name}_${flag}"
    massif_file="./res/massif_${ir_file_name}_${flag}.out"
    MASSIF="valgrind --quiet --tool=massif --time-unit=i --stacks=yes --massif-out-file=./res/massif_${ir_file_name}_${flag}.out"
    echo "  Profiling with $flag"

    if [ "$flag" == "-no-flag" ]; then
        ${OPT} $ir_file -o $opt_ir_file
    else
        ${OPT} $flag $ir_file -o $opt_ir_file
    fi
    ${CLANG_EXEC} $opt_ir_file -o $bin_file -lm

    # Profile Memory Usage
    if [ "$MODE" == "M" ] ; then
        ${MASSIF} $bin_file > /dev/null
        profile_res=$(python3 Massif_Parser.py "${massif_file}")
        (echo "${flag} ${ir_file_name} ${profile_res}") >> ./res/mem_size.out
    fi

    # Profile Code size
    if [ "$MODE" == "C" ] ; then
        profile_res=$(stat -c%s $bin_file)
        (echo "${flag} ${ir_file_name} ${profile_res}") >> ./res/code_size.out
    fi

    rm -f $bin_file
    rm -f $opt_ir_file
    rm -f $massif_file
done

if [ "$MODE" == "M" ] ; then
    python3 Result_to_Csv.py ./res/mem_size.out
fi

if [ "$MODE" == "C" ] ; then
    python3 Result_to_Csv.py ./res/code_size.out
fi

# python3 Flag_ZTest.py