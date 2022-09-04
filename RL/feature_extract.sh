#!/bin/sh
SCRIPT_PATH=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
ir="${SCRIPT_PATH}/$1"
feature_file=$2
workspace="./tmp/${RANDOM}${RANDOM}${RANDOM}${RANDOM}"
extractor="${workspace}/Feature.so"

i=0
while ! (test -f $extractor) do
    mkdir $workspace
    cp "../Feature_Extraction/build/Feature.so" $extractor
    sleep 1
    i=$((i+1))
    # echo "Idx: ${i} Path: ${workspace}"
    if [ $i -gt 10 ] 
    then
        echo "$workspace"
        echo "cp Feature.so stuck!"
    fi
done

i=0
cd $workspace
while ! (test -f "TMP_FEATURE.txt") do
    opt -load "./Feature.so" -enable-new-pm=0 -feature $ir -o /dev/null
    i=$((i+1))
    if [ $i -gt 10 ] 
    then
        echo "$workspace"
        echo "opt -load Feature.so stuck!"
    fi
done
cd $SCRIPT_PATH
rm $extractor

mv "${workspace}/TMP_FEATURE.txt" $feature_file
rm -r $workspace