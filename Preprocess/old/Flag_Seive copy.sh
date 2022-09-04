#!/bin/sh
OPT="opt"
CLANG_EXEC="clang -Wno-everything"
MASSIF="valgrind --quiet --tool=massif --time-unit=i --stacks=yes --massif-out-file=./res/raw_massif.out"
# ls ../Feature_Extraction/ir > ./data/IR_Candidates.in
flag_cand=$(cat ./data/Flag_Candidates.in)
irs=$(cat ./data/IR_Candidates.in)

rm -f ./res/*
rm -f ./bin/*

idx=1
for ir in $irs; do
    echo "Testing at $ir"
    for flag in $flag_cand; do
        ir_file="../Feature_Extraction/ir/${ir}"
        bin_file="./bin/${ir}_${flag}"
        echo "  Profiling with $flag"

        if [ "$flag" == "-no-flag" ]; then
            ${OPT} $ir_file -o ./bin/test.bc
        else
            ${OPT} $flag $ir_file -o ./bin/test.bc
        fi
        ${CLANG_EXEC} ./bin/test.bc -o $bin_file -lm

        # # Profile Memory Usage
        # rm -f ./res/raw_massif.out
        # ${MASSIF} $bin_file > /dev/null
        # profile_res=$(python3 Massif_Parser.py ./res/raw_massif.out)
        # (echo "${flag} ${ir_file} ${profile_res}") >> ./res/mem_size.out

        # Profile Code size
        profile_res=$(stat -c%s $bin_file)
        (echo "${flag} ${ir_file} ${profile_res}") >> ./res/file_size.out

        # rm -f ./bin/*
        idx=$((idx+1))
    done
done

# python3 Result_to_Csv.py ./res/mem_size.out
python3 Result_to_Csv.py ./res/file_size.out