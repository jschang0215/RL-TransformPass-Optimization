#!/bin/sh
CLANG_EXEC="clang -Wno-everything"
OPT="opt"
REPEAT_NUM=100
ir_file=$1
flag=$2

# Compile ir with given option
#   Use random file name to avoid duplication
new_ir_file="./tmp/${RANDOM}${RANDOM}${RANDOM}${RANDOM}.bc"
bin_file="./tmp/${RANDOM}${RANDOM}${RANDOM}${RANDOM}"

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

start_time=`date +%s.%N`

for ((idx=1; idx<=$REPEAT_NUM; idx++)) 
do
    ${bin_file}
done

end_time=`date +%s.%N`
runtime=$(echo "$end_time-$start_time" | bc -l)
echo $runtime

rm -f $bin_file