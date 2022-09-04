#!/bin/sh
MASSIF_PARSER_PATH="/home/jschang/Desktop/ML_Compiler_Optimization/01_source/Preprocess"
OPT="opt"
CLANG_EXEC="clang -Wno-everything"
SCRIPT_PATH=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

ir=$1
ir_file=$ir
flag=$2

# Compile ir with given option
#   Use random file name to avoid duplication
new_ir_file="${SCRIPT_PATH}/tmp/${RANDOM}${RANDOM}${RANDOM}${RANDOM}.bc"
bin_file="${SCRIPT_PATH}/tmp/${RANDOM}${RANDOM}${RANDOM}${RANDOM}"
massif_file="${SCRIPT_PATH}/tmp/massif_${RANDOM}${RANDOM}${RANDOM}${RANDOM}.out"

if [ "$flag" == "-no-flag" ]; then
    ${CLANG_EXEC} $ir_file -o $bin_file -lm
elif  [ "$flag" == "-o3" ]; then
    ${CLANG_EXEC} -o3 $ir_file -o $bin_file -lm
elif  [ "$flag" == "-o2" ]; then
    ${CLANG_EXEC} -o2 $ir_file -o $bin_file -lm
elif  [ "$flag" == "-o1" ]; then
    ${CLANG_EXEC} -o1 $ir_file -o $bin_file -lm
elif  [ "$flag" == "-o0" ]; then
    ${CLANG_EXEC} -o0 $ir_file -o $bin_file -lm
else
    ${OPT} $flag $ir_file -o $new_ir_file
    ${CLANG_EXEC} $new_ir_file -o $bin_file -lm
    cp $new_ir_file $ir_file
fi

# Profile Memory Usage
MASSIF="valgrind --quiet --tool=massif --time-unit=i --stacks=yes --massif-out-file=${massif_file}"
${MASSIF} $bin_file > /dev/null
cd ${MASSIF_PARSER_PATH}
python3 Massif_Parser.py ${massif_file}
cd ${SCRIPT_PATH}

# Clean up
rm -f $new_ir_file
rm -f $bin_file
rm -f $massif_file